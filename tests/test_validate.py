from parser import validate_products


def test_validate_products_filters_and_normalizes():
    products = [
        123,
        {"title": "Good", "price": "100", "image": "http://img"},
        {"title": None, "price": 50},
        {"title": "BadPrice", "price": "abc"},
        {"title": "NoImage", "price": 75, "image": 999},
    ]

    out = validate_products(products)
    assert isinstance(out, list)
    # Only two valid entries: Good and NoImage
    assert len(out) == 2
    assert out[0]['title'] == 'Good'
    assert isinstance(out[0]['price'], (int, float))
    assert out[1]['title'] == 'NoImage'
    assert out[1]['image'] == ''  # non-string image normalized to empty string
