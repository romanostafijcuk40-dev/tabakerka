import os
from parser import generate_autonomous_html


def test_generate_writes_index(tmp_path, monkeypatch):
    # prepare a minimal template in tmp_path
    tpl = tmp_path / 'index.template.html'
    tpl.write_text(
        '<html><script type="application/json" id="products-data">'
        '__PRODUCTS_DATA_JSON__</script><script src="./catalog.js" defer></script></html>',
        encoding='utf-8',
    )

    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        products = [{"title": "X", "price": 10}]
        res = generate_autonomous_html(products)
        assert res is True
        assert (tmp_path / 'index.html').exists()
        content = (tmp_path / 'index.html').read_text(encoding='utf-8')
        assert '__PRODUCTS_DATA_JSON__' not in content
        assert 'src="./catalog.js" defer' in content
        assert '%22title%22%3A%20%22X%22' in content
    finally:
        os.chdir(cwd)
