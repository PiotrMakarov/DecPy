# Новые возможности DecPy

Этот документ описывает возможности, добавленные в DecPy в рамках веток `dict-queries` и `collections-queries`: декларативные запросы к словарям `dict`, slice-синтаксис для словарей и поддержку четырёх типов из стандартного модуля `collections` (`defaultdict`, `OrderedDict`, `Counter`, `deque`).

Если Вы не знакомы с базовыми механизмами библиотеки (классы `var`, `expr`, исчисление на кортежах и доменах), ознакомьтесь с туториалом «DecPy Tutorial».

## Оглавление

- [Запросы к словарям dict](#запросы-к-словарям-dict)
  - [Ленивый доступ к элементам и представлениям](#ленивый-доступ-к-элементам-и-представлениям)
  - [Фильтрация по значению](#фильтрация-по-значению)
  - [Преобразование значений](#преобразование-значений)
  - [Исчисление на доменах через пары (ключ, значение)](#исчисление-на-доменах-через-пары-ключ-значение)
  - [Slice-синтаксис](#slice-синтаксис)
  - [Агрегатные функции](#агрегатные-функции)
  - [Декартово произведение](#декартово-произведение)
  - [Вспомогательные функции merge, app, flat](#вспомогательные-функции-merge-app-flat)
- [Поддержка типов из модуля collections](#поддержка-типов-из-модуля-collections)
  - [Общий принцип](#общий-принцип)
  - [Запросы к подклассам dict](#запросы-к-подклассам-dict)
    - [Ленивый доступ по ключу](#ленивый-доступ-по-ключу)
    - [Доступ к представлениям keys, values, items](#доступ-к-представлениям-keys-values-items)
    - [Фильтрация по значению](#фильтрация-по-значению-1)
    - [Преобразование значений](#преобразование-значений-1)
    - [Исчисление на доменах через пары (ключ, значение)](#исчисление-на-доменах-через-пары-ключ-значение-1)
    - [Slice-синтаксис](#slice-синтаксис-1)
    - [Проекции на ключи и значения](#проекции-на-ключи-и-значения)
    - [Агрегатные функции](#агрегатные-функции-1)
    - [Декартово произведение](#декартово-произведение-1)
  - [Специфика defaultdict](#специфика-defaultdict)
  - [Специфика OrderedDict](#специфика-ordereddict)
  - [Специфика Counter](#специфика-counter)
  - [Запросы к двусторонней очереди deque](#запросы-к-двусторонней-очереди-deque)
    - [Ленивый доступ по индексу](#ленивый-доступ-по-индексу)
    - [Фильтрация](#фильтрация)
    - [Преобразование элементов](#преобразование-элементов)
    - [Проекции](#проекции)
    - [Агрегатные функции](#агрегатные-функции-2)
    - [Декартово произведение](#декартово-произведение-2)
  - [Специфика deque (maxlen)](#специфика-deque-maxlen)
  - [Расширение merge, app, flat для подклассов dict](#расширение-merge-app-flat-для-подклассов-dict)

---

## Запросы к словарям dict

### Ленивый доступ к элементам и представлениям

Переменная `var(d)`, обёрнутая вокруг словаря, поддерживает обычный доступ по ключу и доступ к представлениям `keys()`, `values()`, `items()`:

```python
from decpy import var

grades = var({"alice": 85, "bob": 92, "carol": 78})
print(grades["alice"])          # 85
print(set(grades.keys()))       # {'alice', 'bob', 'carol'}
print(set(grades.values()))     # {85, 92, 78}
print(set(grades.items()))      # {('alice', 85), ('bob', 92), ('carol', 78)}
```

### Фильтрация по значению

Если внутри квадратных скобок передать ленивое выражение со сравнением, словарь фильтруется по значениям. Результатом является словарь только с теми парами, для которых условие истинно:

```python
from decpy import var

grades = var({"alice": 85, "bob": 92, "carol": 78, "dave": 55})
a = var()
passed = grades[a >= 60]
print(passed)
# {'alice': 85, 'bob': 92, 'carol': 78}
```

### Преобразование значений

Ленивое выражение без сравнения интерпретируется как трансформация — оно применяется к каждому значению, ключи сохраняются:

```python
a = var()
doubled = grades[a * 2]
print(doubled)
# {'alice': 170, 'bob': 184, 'carol': 156, 'dave': 110}
```

### Исчисление на доменах через пары (ключ, значение)

При передаче кортежа из двух переменных словарь рассматривается как множество пар (ключ, значение). Дополнительные элементы кортежа играют роль условий или вычисляемых столбцов:

```python
from decpy import var

prices = var({"яблоко": 80, "банан": 120, "вишня": 250, "груша": 95})
k, v = var(2)
expensive = prices[k, v, v > 100]
print(expensive)
# {'банан': 120, 'вишня': 250}

# Фильтрация по ключу
short_names = prices[k, v, k < "г"]
print(short_names)
# {'банан': 120, 'вишня': 250}

# Проекция: None в позиции исключает её из результата
names = prices[k, v, v > 100][k, None]
print(names)
# {'банан', 'вишня'}
```

### Slice-синтаксис

Slice-синтаксис явно разделяет позицию ключа и позицию значения двоеточием, как в dict comprehension `{k: v for ...}`. Эквивалентен старому tuple-синтаксису, но более выразителен:

```python
from decpy import var

prices = var({"яблоко": 80, "банан": 120, "вишня": 250, "груша": 95})
k, v = var(2)

# D[k : v, conds...] — пары с условиями
print(prices[k : v, v > 100])
# {'банан': 120, 'вишня': 250}

# Inline-предикат в позиции значения
print(prices[k : v > 100])
# {'банан': 120, 'вишня': 250}

# Inline-предикаты с обеих сторон
print(prices[k < "г" : v >= 90])
# {'банан': 120, 'вишня': 250}

# Односторонние срезы — проекции
print(set(prices[k :]))          # {'яблоко', 'банан', 'вишня', 'груша'}  — только ключи
print(set(prices[: v]))          # {80, 120, 250, 95}                      — только значения
print(set(prices[: v > 100]))    # {120, 250}                              — проекция с фильтром
```

Старый tuple-синтаксис `D[k, v, cond]` продолжает работать параллельно — для проектов, использующих его исторически.

### Агрегатные функции

К представлению `values()` словаря применимы стандартные агрегаты `calculus`:

```python
grades = var({"alice": 85, "bob": 92, "carol": 78, "dave": 55})
print(grades.values().sum())   # 310
print(grades.values().avg())   # 77.5
print(grades.values().len())   # 4
print(grades.values().min())   # 55
print(grades.values().max())   # 92
```

### Декартово произведение

Словарь, обёрнутый в `var(...)`, можно комбинировать с другими коллекциями через оператор `**`. Словарь при этом автоматически рассматривается как множество пар:

```python
from decpy import var, lazyset

prices = {"яблоко": 80, "банан": 120}
orders = lazyset({("яблоко", 3), ("банан", 5)})

name, price, product, qty = var(4)
total = (var(prices) ** orders)[
    name, price, product, qty,
    name == product,
    price * qty,
]
print(total)
# {('яблоко', 80, 'яблоко', 3, 240), ('банан', 120, 'банан', 5, 600)}
```

### Вспомогательные функции merge, app, flat

```python
from decpy import merge, app, flat

# merge: объединение, при конфликте — значение из второго
print(merge({"a": 1, "b": 2}, {"b": 3, "c": 4}))
# {'a': 1, 'b': 3, 'c': 4}

# app: добавление пары
print(app({"x": 10}, ("y", 20)))
# {'x': 10, 'y': 20}

# flat: линеаризация вложенных словарей
print(flat({"user": {"name": "Alice", "age": 30}, "role": "admin"}))
# {('user', 'name'): 'Alice', ('user', 'age'): 30, 'role': 'admin'}
```

---

## Поддержка типов из модуля collections

### Общий принцип

Все механизмы декларативных запросов, описанные выше для `dict`, работают для подклассов `dict`:

- `collections.defaultdict`
- `collections.OrderedDict`
- `collections.Counter`

Поддержка двусторонней очереди `collections.deque` обеспечивает работу всех запросов, применимых к спискам.

Во всех случаях **результирующая коллекция имеет тот же тип, что и исходная**, и сохраняет специфичные атрибуты типа: `default_factory` у `defaultdict`, порядок ключей у `OrderedDict`, доступность `most_common` и арифметики счётчиков у `Counter`, ограничение `maxlen` у `deque`.

### Запросы к подклассам dict

Все механизмы из раздела «[Запросы к словарям dict](#запросы-к-словарям-dict)» применимы к `defaultdict`, `OrderedDict`, `Counter` без дополнительной адаптации. Ниже — по одному примеру на каждый из ключевых видов запроса. Примеры используют разные типы, чтобы показать единообразие поведения.

#### Ленивый доступ по ключу

```python
from collections import Counter
from decpy import var

c = var(Counter({"яблоко": 3, "банан": 5}))
print(c["яблоко"])   # 3
print(c["банан"])    # 5
```

#### Доступ к представлениям keys, values, items

```python
from collections import OrderedDict
from decpy import var

od = var(OrderedDict([("a", 1), ("b", 2), ("c", 3)]))
print(set(od.keys()))     # {'a', 'b', 'c'}
print(set(od.values()))   # {1, 2, 3}
print(set(od.items()))    # {('a', 1), ('b', 2), ('c', 3)}
```

#### Фильтрация по значению

```python
from collections import defaultdict
from decpy import var

dd = defaultdict(int, {"alice": 85, "bob": 92, "carol": 78, "dave": 55})
a = var()
passed = var(dd)[a >= 60]
print(type(passed))   # <class 'collections.defaultdict'>
print(passed)         # defaultdict(<class 'int'>, {'alice': 85, 'bob': 92, 'carol': 78})
```

#### Преобразование значений

```python
from collections import Counter
from decpy import var

c = Counter({"a": 3, "b": 5, "c": 2})
a = var()
doubled = var(c)[a * 2]
print(type(doubled))  # <class 'collections.Counter'>
print(doubled)        # Counter({'b': 10, 'a': 6, 'c': 4})
```

#### Исчисление на доменах через пары (ключ, значение)

```python
from collections import OrderedDict
from decpy import var

od = OrderedDict([("яблоко", 80), ("банан", 120), ("вишня", 250), ("груша", 95)])
k, v = var(2)
expensive = var(od)[k, v, v > 100]
print(type(expensive))   # <class 'collections.OrderedDict'>
print(expensive)         # OrderedDict([('банан', 120), ('вишня', 250)])
```

#### Slice-синтаксис

```python
from collections import defaultdict, Counter
from decpy import var

dd = defaultdict(int, {"alice": 85, "bob": 92, "carol": 78})
k, v = var(2)
print(var(dd)[k : v, v >= 80])
# defaultdict(<class 'int'>, {'alice': 85, 'bob': 92})

c = Counter({"the": 3, "quick": 2, "brown": 1, "fox": 2})
print(var(c)[k : v > 1])
# Counter({'the': 3, 'quick': 2, 'fox': 2})
```

#### Проекции на ключи и значения

```python
from collections import OrderedDict
from decpy import var

od = OrderedDict([("яблоко", 80), ("банан", 120), ("вишня", 250)])
k, v = var(2)

# Только ключи, удовлетворяющие условию
print(set(var(od)[k : v, v > 100]))           # {'банан', 'вишня'}
# Только значения
print(set(var(od)[: v, v > 100]))             # {120, 250}
```

#### Агрегатные функции

```python
from collections import Counter
from decpy import var

c = Counter({"a": 3, "b": 5, "c": 2, "d": 1})
print(var(c).values().sum())   # 11
print(var(c).values().avg())   # 2.75
print(var(c).values().max())   # 5
print(var(c).values().len())   # 4
```

#### Декартово произведение

```python
from collections import defaultdict
from decpy import var, lazyset

prices = defaultdict(int, {"яблоко": 80, "банан": 120})
orders = lazyset({("яблоко", 3), ("банан", 5)})

name, price, product, qty = var(4)
total = (var(prices) ** orders)[
    name, price, product, qty,
    name == product,
    price * qty,
]
print(total)
# {('яблоко', 80, 'яблоко', 3, 240), ('банан', 120, 'банан', 5, 600)}
```

### Специфика defaultdict

Фабрика значений по умолчанию (`default_factory`) сохраняется в результате запроса — обращение к несуществующему ключу продолжает возвращать значение фабрики:

```python
from collections import defaultdict
from decpy import var

dd = defaultdict(int, {"alice": 85, "bob": 92, "carol": 78})
a = var()
top = var(dd)[a >= 80]
print(top.default_factory)   # <class 'int'>
print(top["unknown_key"])    # 0  (фабрика сработала)
```

### Специфика OrderedDict

Порядок ключей сохраняется: элементы в результате расположены в том же относительном порядке, в котором они были в исходной коллекции:

```python
from collections import OrderedDict
from decpy import var

od = OrderedDict([("first", 1), ("second", 2), ("third", 3), ("fourth", 4)])
v = var()
filtered = var(od)[v >= 2]
print(list(filtered))   # ['second', 'third', 'fourth']  — порядок сохранён
```

### Специфика Counter

Тип `Counter` сохраняется, поэтому к результату применимы специфичные методы — `most_common` и арифметика счётчиков (`+`, `-`, `&`, `|`):

```python
from collections import Counter
from decpy import var

text = "the quick brown fox jumps over the lazy dog the".split()
c = Counter(text)
v = var()
frequent = var(c)[v >= 2]
print(frequent.most_common(1))     # [('the', 3)]

# Результат остаётся пригоден для арифметики счётчиков
print(frequent + Counter({"the": 1, "new": 1}))
# Counter({'the': 4, 'new': 1})
```

### Запросы к двусторонней очереди deque

`deque` поведенчески эквивалентен списку: к нему применимы все запросы, описанные в разделе «Запросы к словарям dict» применительно к последовательностям. Результаты сохраняют тип `deque`.

#### Ленивый доступ по индексу

```python
from collections import deque
from decpy import var

q = var(deque([10, 20, 30, 40, 50]))
print(q[0])    # 10
print(q[-1])   # 50
```

#### Фильтрация

```python
from collections import deque
from decpy import var

q = deque([10, 20, 30, 40, 50])
a = var()
big = var(q)[a > 25]
print(type(big))   # <class 'collections.deque'>
print(big)         # deque([30, 40, 50])
```

#### Преобразование элементов

```python
a = var()
squared = var(q)[a * a]
print(type(squared))   # <class 'collections.deque'>
print(squared)         # deque([100, 400, 900, 1600, 2500])
```

#### Проекции

`deque` может содержать составные элементы (кортежи), к которым применима проекция через исчисление на доменах:

```python
from collections import deque
from decpy import var

points = deque([(1, 2), (3, 4), (5, 6), (7, 8)])
x, y = var(2)
ys = var(points)[None, y]
print(type(ys))   # <class 'collections.deque'>
print(ys)         # deque([2, 4, 6, 8])
```

#### Агрегатные функции

```python
q = deque([10, 20, 30, 40, 50])
print(var(q).sum())   # 150
print(var(q).avg())   # 30.0
print(var(q).min())   # 10
print(var(q).max())   # 50
print(var(q).len())   # 5
```

#### Декартово произведение

```python
from collections import deque
from decpy import var, lazyset

q = deque([1, 2, 3])
s = lazyset({"a", "b"})
print(set(var(q) ** s))
# {(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b'), (3, 'a'), (3, 'b')}
```

### Специфика deque (maxlen)

Ограничение длины `maxlen` сохраняется в результате запроса:

```python
from collections import deque
from decpy import var

q = deque([10, 20, 30, 40, 50], maxlen=5)
a = var()
big = var(q)[a > 25]
print(big.maxlen)   # 5
```

### Расширение merge, app, flat для подклассов dict

Функции `merge`, `app`, `flat` сохраняют тип внешней коллекции при работе с подклассами `dict`:

```python
from collections import defaultdict, Counter, OrderedDict
from decpy import merge, app, flat

# merge: тип первого аргумента сохраняется
print(merge(Counter({"a": 1, "b": 2}), {"b": 3, "c": 4}))
# Counter({'a': 1, 'b': 3, 'c': 4})

print(merge(defaultdict(int, {"a": 1}), {"b": 2}))
# defaultdict(<class 'int'>, {'a': 1, 'b': 2})

# app: добавление пары с сохранением типа
print(app(OrderedDict([("a", 1)]), ("b", 2)))
# OrderedDict([('a', 1), ('b', 2)])

# flat: линеаризация вложенных подклассов dict
print(flat(OrderedDict([("user", OrderedDict([("name", "Alice"), ("age", 30)]))])))
# OrderedDict([(('user', 'name'), 'Alice'), (('user', 'age'), 30)])
```

Сохранение типа особенно важно для `Counter`: результат `merge` остаётся пригодным для арифметических операций над счётчиками и метода `most_common`.

Поведение функций по отношению к обычному `dict` не изменено.
