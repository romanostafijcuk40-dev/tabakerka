# Коротка інструкція для власника

## Що потрібно робити

### Якщо потрібно оновити каталог товарів
1. Замініть або оновіть файл [source.html](source.html).
2. Запустіть команду:

```bash
python parser.py
```

3. Після цього сайт автоматично оновиться:
   - [products.json](products.json)
   - [index.html](index.html)

### Якщо потрібно змінити ціну або націнку
1. Відкрийте [parser.py](parser.py).
2. Змініть значення:

```python
NATSINKA = 50
```

3. Знову запустіть:

```bash
python parser.py
```

### Якщо потрібно змінити зовнішній вигляд сайту
1. Відкрийте [index.template.html](index.template.html).
2. Змініть дизайн за потреби.
3. Запустіть:

```bash
python parser.py
```

## Що перевірити перед публікацією
- товари відображаються на сайті;
- зображення підвантажуються;
- ціни виглядають правильно;
- сторінка відкривається у браузері.

## Коли потрібен доступ до GitHub
Якщо потрібно відправити зміни в інтернет, виконайте:

```bash
git add .
git commit -m "Оновлення сайту"
git push origin main
```

## Основні файли
- [source.html](source.html) — джерело товарів
- [products.json](products.json) — каталог товарів
- [index.html](index.html) — готова сторінка сайту
- [parser.py](parser.py) — обробка даних
- [index.template.html](index.template.html) — дизайн сайту
