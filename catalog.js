let tg = null;
if (window.Telegram && window.Telegram.WebApp) {
    tg = window.Telegram.WebApp;
    try {
        tg.expand();
        if (tg.themeParams && tg.themeParams.bg_color) {
            document.documentElement.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color);
            document.documentElement.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color);
            document.documentElement.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color);
            document.documentElement.style.setProperty('--tg-theme-link-color', tg.themeParams.link_color);
            document.documentElement.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color);
            document.documentElement.style.setProperty('--tg-theme-button-text-color', tg.themeParams.button_text_color);
            document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', tg.themeParams.secondary_bg_color);
        }
    } catch (e) {
        console.log("Помилка теми:", e);
    }
}

const isTelegram = tg !== null && tg.initData !== "";
let cart = {};
let productsData = [];

try {
    const productDataElement = document.getElementById('products-data');
    productsData = JSON.parse(decodeURIComponent(productDataElement.textContent));
} catch (e) {
    console.error('Failed to parse products JSON:', e);
}

function renderCatalog() {
    const catalogContainer = document.getElementById('catalog');
    catalogContainer.innerHTML = '';
    productsData.forEach((product, index) => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <div>
                <img class="product-img" src="${product.image || 'placeholder.svg'}" alt="${(product.title || '').replace(/"/g, '&quot;')}" loading="lazy" onerror="this.onerror=null; this.src='placeholder.svg'">
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
    let totalItems = 0;
    let totalPrice = 0;

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
    } else if (isTelegram) {
        tg.MainButton.hide();
    } else {
        document.getElementById('pc-order-btn').style.display = 'none';
    }
}

if (isTelegram) {
    tg.MainButton.onClick(() => { sendOrderData(); });
}

function getOrderText() {
    let orderDetails = [];
    let totalPrice = 0;
    for (const title in cart) {
        const product = productsData.find(p => p.title === title);
        if (product) {
            totalPrice += product.price * cart[title];
            orderDetails.push(`🔹 ${title} x${cart[title]} (${product.price * cart[title]} грн)`);
        }
    }
    return `📦 НОВЕ ЗАМОВЛЕННЯ:\n\n${orderDetails.join('\n')}\n\n💰 Разом: ${totalPrice} грн`;
}

function sendOrderData() {
    if (isTelegram) {
        tg.sendData(getOrderText());
        tg.close();
    }
}

window.sendOrderPC = function() {
    alert(getOrderText() + '\n\n(В Telegram це замовлення автоматично надійде в бот!)');
};

renderCatalog();
