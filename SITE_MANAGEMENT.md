# Інструкція керування сайтом Tabakerka

## 1. Що треба оновлювати

- [source.html](source.html) — вихідний HTML з асортиментом постачальника.
- [parser.py](parser.py) — логіка парсингу, націнка та генерація сторінки.
- [products.json](products.json) — згенерований каталог товарів.
- [index.html](index.html) — статична сторінка вітрини для Telegram WebApp.
- [index.template.html](index.template.html) — шаблон сторінки, якщо потрібно змінити зовнішній вигляд.

## 2. Як оновити каталог товарів

1. Відкрийте [source.html](source.html) або замініть його новим HTML з сайту постачальника.
2. Запустіть парсер:

```bash
python parser.py
```

3. Після виконання скрипта будуть оновлені:
   - [products.json](products.json)
   - [index.html](index.html)

## 3. Як змінити націнку

Відкрийте [parser.py](parser.py) і змініть значення:

```python
NATSINKA = 50
```

Після цього знову запустіть:

```bash
python parser.py
```

## 4. Як перевірити, що сайт працює

- Відкрийте [index.html](index.html) у браузері.
- Переконайтеся, що товари відображаються, а зображення підвантажуються.
- Якщо фото не видно, перевірте:
  - чи є правильні URL у [source.html](source.html)
  - чи не змінився HTML-структурний шаблон постачальника
  - чи правильно працює парсер у [parser.py](parser.py)

## 5. Як опублікувати зміни

1. Переконайтеся, що всі зміни збережені.
2. Додайте файли до Git:

```bash
git add .
git commit -m "Оновлення каталогу та сайту"
git push origin main
```

## 6. Коли потрібні зміни у шаблоні

Якщо треба змінити зовнішній вигляд вітрини, правте [index.template.html](index.template.html). Після цього знову запустіть:

```bash
python parser.py
```

## 7. Корисні команди

```bash
python -m pytest
python parser.py
```
