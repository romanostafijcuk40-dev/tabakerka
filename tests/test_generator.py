import os
from parser import generate_autonomous_html


def test_generate_writes_index(tmp_path, monkeypatch):
    # prepare a minimal template in tmp_path
    tpl = tmp_path / 'index.template.html'
    tpl.write_text("<html><script>const products = JSON.parse(decodeURIComponent('__PRODUCTS_DATA_JSON__'));</script></html>", encoding='utf-8')

    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        products = [{"title": "X", "price": 10}]
        res = generate_autonomous_html(products)
        assert res is True
        assert (tmp_path / 'index.html').exists()
        content = (tmp_path / 'index.html').read_text(encoding='utf-8')
        assert 'decodeURIComponent' in content
    finally:
        os.chdir(cwd)
