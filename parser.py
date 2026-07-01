import os
import json
import requests
import re
import io
import urllib.parse
from bs4 import BeautifulSoup

# === НАЛАШТУВАННЯ ===
NATSINKA = 50                 # Наша націнка в гривнях
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')  # Ваш особистий ID
FILE_PATH = 'source.html'     
# ====================


def validate_products(products):
    """Простейшая валидация и нормализация списка товаров.
    Оставляет только объекты с title (str) и price (number).
    """
    clean = []
    for i, p in enumerate(products or []):
        if not isinstance(p, dict):
            continue
        title = p.get('title')
        price = p.get('price')
        if title is None or price is None:
            continue
        try:
            price_num = float(price)
        except Exception:
            continue
        image = p.get('image') or ''
        if not isinstance(image, str):
            image = ''
        base_price = p.get('base_price')
        description = p.get('description') or ''
        clean.append({
            'title': str(title).strip(),
            'price': int(price_num) if price_num.is_integer() else price_num,
            'base_price': base_price,
            'image': image,
            'description': str(description).strip()
        })
    return clean

def generate_autonomous_html(catalog_data):
    """Генерує автономний index.html, де товари зашиті в код без використання f-string"""
    # Валідуємо та нормалізуємо вхідні дані
    catalog_data = validate_products(catalog_data)
    json_products = json.dumps(catalog_data, ensure_ascii=False, indent=2)
    # Якщо поруч існує шаблон index.template.html — використовуємо його, інакше вбудований шаблон
    template_path = 'index.template.html'
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as tf:
            html_template = tf.read()
    else:
        # Використовуємо звичайний текст, де замість динамічних даних ставимо унікальну мітку __PRODUCTS_DATA_JSON__
        html_template = """<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Вітрина - Tabakerka</title>
    <script src="https://telegram.org"></script>
    <style>
        :root {
            --tg-theme-bg-color: #ffffff;
            --tg-theme-text-color: #222222;
            --tg-theme-hint-color: #707579;
            --tg-theme-link-color: #2481cc;
            --tg-theme-button-color: #2481cc;
            --tg-theme-button-text-color: #ffffff;
            --tg-theme-secondary-bg-color: #f4f4f5;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--tg-theme-bg-color);
            color: var(--tg-theme-text-color);
            margin: 0; padding: 10px; box-sizing: border-box;
        }
        .header { text-align: center; padding: 15px 0; border-bottom: 1px solid var(--tg-theme-secondary-bg-color); margin-bottom: 15px; }
        .header h1 { margin: 0; font-size: 20px; }
        .header p { margin: 5px 0 0 0; font-size: 14px; color: var(--tg-theme-hint-color); }
        .catalog { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding-bottom: 80px; }
        .product-card {
            background-color: var(--tg-theme-secondary-bg-color);
            border-radius: 12px; padding: 10px; display: flex; flex-direction: column;
            justify-content: space-between; overflow: hidden; border: 1px solid rgba(0,0,0,0.05);
        }
        .product-img { width: 100%; height: 120px; object-fit: contain; border-radius: 8px; background-color: #ffffff; }
        .product-title { font-size: 13px; font-weight: 600; margin: 8px 0 4px 0; display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 34px; }
        .product-price { font-size: 15px; font-weight: bold; color: var(--tg-theme-link-color); margin-bottom: 8px; }
        .btn-add { background-color: var(--tg-theme-button-color); color: var(--tg-theme-button-text-color); border: none; border-radius: 8px; padding: 8px; font-size: 13px; font-weight: bold; cursor: pointer; width: 100%; }
        .quantity-control { display: flex; align-items: center; justify-content: space-between; background-color: var(--tg-theme-bg-color); border-radius: 8px; border: 1px solid var(--tg-theme-button-color); }
        .btn-qty { background-color: transparent; color: var(--tg-theme-button-color); border: none; width: 32px; height: 32px; font-size: 18px; font-weight: bold; cursor: pointer; }
        .qty-num { font-weight: bold; font-size: 14px; }
        #pc-order-btn { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background-color: #2481cc; color: white; padding: 12px 24px; border-radius: 20px; border: none; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.2); cursor: pointer; display: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Вітрина Tabakerka</h1>
        <p>Швидка доставка Новою Поштою</p>
    </div>
    <div id="catalog" class="catalog"></div>
    <button id="pc-order-btn" onclick="sendOrderPC()">Оформити замовлення</button>

    <script>
        let tg = null;
        if (window.Telegram && window.Telegram.WebApp) {
            tg = window.Telegram.WebApp;
            try {
                tg.expand();
                if (tg.themeParams.bg_color) {
                    document.documentElement.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color);
                    document.documentElement.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color);
                    document.documentElement.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color);
                    document.documentElement.style.setProperty('--tg-theme-link-color', tg.themeParams.link_color);
                    document.documentElement.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color);
                    document.documentElement.style.setProperty('--tg-theme-button-text-color', tg.themeParams.button_text_color);
                    document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', tg.themeParams.secondary_bg_color);
                }
            } catch(e) { console.log("Помилка теми:", e); }
        }

        const isTelegram = tg !== null && tg.initData !== "";
        let cart = {};
        
        // Мітка буде замінена на реальний масив товарів за допомогою Python
        const productsData = __PRODUCTS_DATA_JSON__;

        function renderCatalog() {
            const catalogContainer = document.getElementById('catalog');
            catalogContainer.innerHTML = '';
            productsData.forEach((product, index) => {
                const card = document.createElement('div');
                card.className = 'product-card';
                card.innerHTML = `
                    <div>
                        <img class="product-img" src="${product.image}" onerror="this.src='https://placeholder.com'">
                        <div class="product-title">${product.title}</div>
                    </div>
                    <div>
                        <div class="product-price">${product.price} грн</div>
                        <div id="btn-block-${index}">
                            <button class="btn-add" onclick="addToCart('${product.title.replace(/'/g, "\\'")}', ${index})">Купити</button>
                        </div>
                    </div>
                `;
                catalogContainer.appendChild(card);
            });
        }

        window.addToCart = function(title, index) {
            cart[title] = 1;
            updateCardButton(title, index);
            updateCartStatus();
        };

        window.changeQty = function(title, index, delta) {
            cart[title] += delta;
            if (cart[title] <= 0) {
                delete cart[title];
                document.getElementById(`btn-block-${index}`).innerHTML = `
                    <button class="btn-add" onclick="addToCart('${title.replace(/'/g, "\\'")}', ${index})">Купити</button>
                `;
            } else {
                document.getElementById(`qty-${index}`).innerText = cart[title];
            }
            updateCartStatus();
        };

        function updateCardButton(title, index) {
            document.getElementById(`btn-block-${index}`).innerHTML = `
                <div class="quantity-control">
                    <button class="btn-qty" onclick="changeQty('${title.replace(/'/g, "\\'")}', ${index}, -1)">-</button>
                    <span class="qty-num" id="qty-${index}">${cart[title]}</span>
                    <button class="btn-qty" onclick="changeQty('${title.replace(/'/g, "\\'")}', ${index}, 1)">+</button>
                </div>
            `;
        }

        function updateCartStatus() {
            let totalItems = 0, totalPrice = 0;
            for (const title in cart) {
                const product = productsData.find(p => p.title === title);
                if (product) {
                    totalItems += cart[title];
                    totalPrice += product.price * cart[title];
                }
            }
            if (totalItems > 0) {
                if (isTelegram) {
                    tg.MainButton.text = `Переглянути замовлення (${totalPrice} грн)`;
                    tg.MainButton.show();
                } else {
                    const pcBtn = document.getElementById('pc-order-btn');
                    pcBtn.innerText = `Оформити замовлення (${totalPrice} грн)`;
                    pcBtn.style.display = 'block';
                }
            } else {
                if (isTelegram) { tg.MainButton.hide(); }
                else { document.getElementById('pc-order-btn').style.display = 'none'; }
            }
        }

        if (isTelegram) {
            tg.MainButton.onClick(() => { sendOrderData(); });
        }

        function getOrderText() {
            let orderDetails = [], totalPrice = 0;
            for (const title in cart) {
                const product = productsData.find(p => p.title === title);
                if (product) {
                    totalPrice += product.price * cart[title];
                    orderDetails.push(`🔹 ${title} x${cart[title]} (${product.price * cart[title]} грн)`);
                }
            }
            return `📦 НОВЕ ЗАМОВЛЕННЯ:\\n\\n${orderDetails.join('\\n')}\\n\\n💰 Разом: ${totalPrice} грн`;
        }

        function sendOrderData() {
            if (isTelegram) { tg.sendData(getOrderText()); tg.close(); }
        }

        window.sendOrderPC = function() {
            alert(getOrderText() + "\\n\\n(В Telegram це замовлення автоматично надійде в бот!)");
        };

        renderCatalog();
    </script>
</body>
</html>"""
    
    # Кодируем JSON чтобы избежать встраивания непредсказуемых символов в JS
    encoded = urllib.parse.quote(json_products, safe='')
    # Безпечно замінюємо мітку текстовим JSON-масивом (закодированным)
    final_html = html_template.replace('__PRODUCTS_DATA_JSON__', encoded)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)

    return True


if __name__ == '__main__':
    # Зчитати товари з products.json (як за замовчуванням)
    data_file = 'products.json'
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as pf:
            products = json.load(pf)
    else:
        products = []

    success = generate_autonomous_html(products)
    if success is None:
        # Функція повертає None — просто повідомимо про завершення
        print('index.html згенеровано.')
    else:
        print('index.html згенеровано.')
