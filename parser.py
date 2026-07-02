import json
import os
import re
import urllib.parse
from typing import List

from bs4 import BeautifulSoup

NATSINKA = int(os.getenv("NATSINKA", "50"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
FILE_PATH = os.getenv("FILE_PATH", "source.html")


def _normalize_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return re.sub(r"\s+", " ", text)


def _parse_price(value: object) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    match = re.search(r"(-?\d+(?:[.,]\d+)?)", text.replace(" ", ""))
    if not match:
        return 0.0
    return float(match.group(1).replace(",", "."))


def _serialize_number(value: float):
    return int(value) if float(value).is_integer() else value


def validate_products(products):
    clean = []
    seen = set()
    for item in products or []:
        if not isinstance(item, dict):
            continue
        title = _normalize_text(item.get("title"))
        price = item.get("price")
        if not title or price is None:
            continue
        try:
            price_num = float(price)
        except Exception:
            continue
        image = _normalize_text(item.get("image")) if isinstance(item.get("image"), str) else ""
        base_price = item.get("base_price")
        if base_price is None:
            base_price = price_num
        try:
            base_price_num = float(base_price)
        except Exception:
            base_price_num = price_num
        normalized = {
            "title": title,
            "price": _serialize_number(price_num),
            "base_price": _serialize_number(base_price_num),
            "image": image,
            "description": _normalize_text(item.get("description")),
        }
        key = (title.lower(), normalized["price"])
        if key in seen:
            continue
        seen.add(key)
        clean.append(normalized)
    return clean


def extract_products_from_html(html_content: str, markup: int = NATSINKA) -> List[dict]:
    soup = BeautifulSoup(html_content, "html.parser")
    product_nodes = soup.select(".js-product")
    if not product_nodes:
        product_nodes = soup.select("[data-product-url]")

    products = []
    for node in product_nodes:
        title = None
        for selector in [".js-store-prod-name", ".js-product-name", ".t-store__card__title"]:
            title_node = node.select_one(selector)
            if title_node:
                title = _normalize_text(title_node.get_text(" ", strip=True))
                break
        if not title:
            continue

        price_node = None
        for selector in [".js-product-price", ".js-store-prod-price-val"]:
            candidate = node.select_one(selector)
            if candidate:
                price_node = candidate
                break
        price_raw = None
        if price_node:
            price_raw = price_node.get("data-product-price-def") or price_node.get_text(" ", strip=True)
        elif node.has_attr("data-product-price-def"):
            price_raw = node.get("data-product-price-def")

        base_price = _parse_price(price_raw)
        if base_price <= 0:
            continue

        image = None
        for attr in ["data-product-img", "data-original"]:
            value = node.get(attr)
            if value:
                image = _normalize_text(value)
                break
        if not image:
            img_tag = node.select_one("img")
            if img_tag:
                image = _normalize_text(img_tag.get("src"))

        description = ""
        description_node = node.select_one(".js-store-prod-descr, .t-store__card__descr")
        if description_node:
            description = _normalize_text(description_node.get_text(" ", strip=True))

        products.append({
            "title": title,
            "price": _serialize_number(base_price + markup),
            "base_price": _serialize_number(base_price),
            "image": image or "",
            "description": description,
        })

    return validate_products(products)


def load_products_from_source(source_path: str = FILE_PATH):
    if os.path.exists(source_path):
        with open(source_path, "r", encoding="utf-8") as fh:
            html = fh.read()
        return extract_products_from_html(html)

    if os.path.exists("products.json"):
        with open("products.json", "r", encoding="utf-8") as fh:
            return json.load(fh)

    return []


def save_products(products, output_path: str = "products.json"):
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(validate_products(products), fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def generate_autonomous_html(catalog_data, output_path: str = "index.html"):
    catalog_data = validate_products(catalog_data)
    json_products = json.dumps(catalog_data, ensure_ascii=False, indent=2)

    template_path = "index.template.html"
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as fh:
            html_template = fh.read()
    else:
        html_template = """<!DOCTYPE html><html lang=\"uk\"><body><script>window.__PRODUCTS__ = __PRODUCTS_DATA_JSON__;</script></body></html>"""

    encoded = urllib.parse.quote(json_products, safe="")
    final_html = html_template.replace("__PRODUCTS_DATA_JSON__", encoded)

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(final_html)

    return True


def build_catalog(source_path: str = FILE_PATH, products_path: str = "products.json", html_path: str = "index.html"):
    products = load_products_from_source(source_path)
    save_products(products, products_path)
    generate_autonomous_html(products, html_path)
    return products


if __name__ == "__main__":
    products = build_catalog()
    print(f"Оброблено {len(products)} товарів. Файли products.json і index.html оновлено.")
