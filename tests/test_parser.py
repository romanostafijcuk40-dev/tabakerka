from parser import extract_products_from_html


def test_extract_products_from_html_reads_titles_prices_and_images():
    html = """
    <html><body>
      <div class="js-product" data-product-url="https://example.com/p1" data-product-img="https://img.example/p1.jpg">
        <div class="js-store-prod-name">Kent KS 8 turbo</div>
        <div class="js-product-price">750</div>
        <div class="js-store-prod-descr">Nice product</div>
      </div>
      <div class="js-product" data-product-url="https://example.com/p2" data-product-img="https://img.example/p2.jpg">
        <div class="js-store-prod-name">Parliament Aqua Blue</div>
        <div class="js-product-price">800</div>
        <div class="js-store-prod-descr">Another one</div>
      </div>
    </body></html>
    """

    products = extract_products_from_html(html, markup=50)

    assert len(products) == 2
    assert products[0]["title"] == "Kent KS 8 turbo"
    assert products[0]["price"] == 800
    assert products[0]["base_price"] == 750
    assert products[0]["image"] == "https://img.example/p1.jpg"
    assert products[1]["description"] == "Another one"
