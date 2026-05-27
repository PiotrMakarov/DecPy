"""
Тесты для декларативных запросов к контейнерным типам стандартного
модуля `collections` (defaultdict, OrderedDict, Counter, deque).

Этот файл служит исполняемой спецификацией для соответствующей
функциональности. Тесты покрывают все сценарии разделов 2.3.2 - 2.3.8
отчёта применительно к новым типам, а также специфику каждого типа.
"""

from collections import Counter, OrderedDict, defaultdict, deque

import pytest

from decpy import app, flat, lazyset, merge, queryclass, var


# Фабрики для параметризации тестов подклассов dict.
# Каждая фабрика принимает обычный dict и возвращает экземпляр
# соответствующего подкласса с теми же парами.
DICT_SUBCLASS_FACTORIES = [
    pytest.param(lambda d: defaultdict(int, d), id="defaultdict"),
    pytest.param(lambda d: OrderedDict(d), id="OrderedDict"),
    pytest.param(lambda d: Counter(d), id="Counter"),
]


# ============================================================
# 2.3.2 / 2.3.3 / 2.3.4 / 2.3.5 / 2.3.6 / 2.3.7 / 2.3.8 для подклассов dict
# ============================================================


@pytest.mark.parametrize("make", DICT_SUBCLASS_FACTORIES)
def test_dict_subclass_lazy_access_by_key(make):
    """2.3.2: ленивый доступ к элементу по ключу."""
    d = var(make({"alice": 85, "bob": 92}))
    assert d["alice"] == 85
    assert d["bob"] == 92


@pytest.mark.parametrize("make", DICT_SUBCLASS_FACTORIES)
def test_dict_subclass_keys_values_items(make):
    """2.3.2: доступ к представлениям keys/values/items."""
    d = var(make({"a": 1, "b": 2, "c": 3}))
    assert set(d.keys()) == {"a", "b", "c"}
    assert set(d.values()) == {1, 2, 3}
    assert set(d.items()) == {("a", 1), ("b", 2), ("c", 3)}


@pytest.mark.parametrize("make", DICT_SUBCLASS_FACTORIES)
def test_dict_subclass_filter_by_value_preserves_type(make):
    """2.3.3: фильтрация по значению, результат — того же типа."""
    d = make({"alice": 85, "bob": 92, "carol": 78, "dave": 55})
    a = var()
    passed = var(d)[a >= 60]()
    assert type(passed) is type(d)
    assert dict(passed) == {"alice": 85, "bob": 92, "carol": 78}


@pytest.mark.parametrize("make", DICT_SUBCLASS_FACTORIES)
def test_dict_subclass_filter_by_key_preserves_type(make):
    """2.3.3: фильтрация по ключу через исчисление на доменах."""
    d = make({"alice": 85, "bob": 92, "carol": 78})
    k, v = var(2)
    short = var(d)[k, v, k < "carol"]()
    assert type(short) is type(d)
    assert dict(short) == {"alice": 85, "bob": 92}


@pytest.mark.parametrize("make", DICT_SUBCLASS_FACTORIES)
def test_dict_subclass_transform_values_preserves_type(make):
    """2.3.4: преобразование значений, результат — того же типа."""
    d = make({"a": 3, "b": 5})
    a = var()
    doubled = var(d)[a * 2]()
    assert type(doubled) is type(d)
    assert dict(doubled) == {"a": 6, "b": 10}


@pytest.mark.parametrize("make", DICT_SUBCLASS_FACTORIES)
def test_dict_subclass_domain_calculus_preserves_type(make):
    """2.3.5: исчисление на доменах через пары (key, value)."""
    d = make({"яблоко": 80, "банан": 120, "вишня": 250, "груша": 95})
    k, v = var(2)
    expensive = var(d)[k, v, v > 100]()
    assert type(expensive) is type(d)
    assert dict(expensive) == {"банан": 120, "вишня": 250}


@pytest.mark.parametrize("make", DICT_SUBCLASS_FACTORIES)
def test_dict_subclass_slice_syntax_preserves_type(make):
    """2.3.6: slice-синтаксис, результат — того же типа."""
    d = make({"яблоко": 80, "банан": 120, "вишня": 250})
    k, v = var(2)
    result = var(d)[k:v, v > 100]()
    assert type(result) is type(d)
    assert dict(result) == {"банан": 120, "вишня": 250}


@pytest.mark.parametrize("make", DICT_SUBCLASS_FACTORIES)
def test_dict_subclass_slice_inline_value_predicate(make):
    """2.3.6: inline-предикат в позиции значения."""
    d = make({"яблоко": 80, "банан": 120, "вишня": 250})
    k, v = var(2)
    result = var(d)[k : v > 100]()
    assert type(result) is type(d)
    assert dict(result) == {"банан": 120, "вишня": 250}


@pytest.mark.parametrize("make", DICT_SUBCLASS_FACTORIES)
def test_dict_subclass_slice_inline_both_predicates(make):
    """2.3.6: inline-предикаты с обеих сторон D[k>x : v>y]."""
    d = make({"alice": 85, "bob": 92, "carol": 78, "dave": 55})
    k, v = var(2)
    result = var(d)[k < "carol" : v >= 60]()
    assert type(result) is type(d)
    assert dict(result) == {"alice": 85, "bob": 92}


@pytest.mark.parametrize("make", DICT_SUBCLASS_FACTORIES)
def test_dict_subclass_slice_multiple_conditions(make):
    """2.3.6: slice-синтаксис с несколькими дополнительными условиями."""
    d = make({"alice": 85, "bob": 92, "carol": 78, "dave": 55})
    k, v = var(2)
    result = var(d)[k:v, k < "carol", v >= 60]()
    assert type(result) is type(d)
    assert dict(result) == {"alice": 85, "bob": 92}


@pytest.mark.parametrize("make", DICT_SUBCLASS_FACTORIES)
def test_dict_subclass_slice_project_keys(make):
    """2.3.6: односторонний срез D[k:] — проекция на ключи."""
    d = make({"яблоко": 80, "банан": 120, "вишня": 250})
    k = var()
    keys = var(d)[k:]()
    assert set(keys) == {"яблоко", "банан", "вишня"}


@pytest.mark.parametrize("make", DICT_SUBCLASS_FACTORIES)
def test_dict_subclass_slice_project_values(make):
    """2.3.6: односторонний срез D[:v] — проекция на значения."""
    d = make({"яблоко": 80, "банан": 120, "вишня": 250})
    v = var()
    values = var(d)[:v]()
    assert set(values) == {80, 120, 250}


@pytest.mark.parametrize("make", DICT_SUBCLASS_FACTORIES)
def test_dict_subclass_project_keys(make):
    """2.3.5: проекция на ключи через [k, None]."""
    d = make({"яблоко": 80, "банан": 120, "вишня": 250})
    k, v = var(2)
    names = var(d)[k, v, v > 100][k, None]()
    assert set(names) == {"банан", "вишня"}


@pytest.mark.parametrize("make", DICT_SUBCLASS_FACTORIES)
def test_dict_subclass_aggregates(make):
    """2.3.7: агрегатные функции над values()."""
    d = make({"a": 3, "b": 5, "c": 2, "d": 1})
    assert var(d).values().sum() == 11
    assert var(d).values().min() == 1
    assert var(d).values().max() == 5
    assert var(d).values().len() == 4


@pytest.mark.parametrize("make", DICT_SUBCLASS_FACTORIES)
def test_dict_subclass_cartesian_product(make):
    """2.3.8: декартово произведение с другой коллекцией."""
    d = make({"яблоко": 80, "банан": 120})
    orders = lazyset({("яблоко", 3), ("банан", 5)})
    name_v, price, product, qty = var(4)
    total = (var(d) ** orders)[
        name_v, price, product, qty,
        name_v == product,
        price * qty,
    ]()
    assert set(total) == {
        ("яблоко", 80, "яблоко", 3, 240),
        ("банан", 120, "банан", 5, 600),
    }


# ============================================================
# Специфика defaultdict
# ============================================================


def test_defaultdict_factory_preserved_after_filter():
    """default_factory сохраняется в результате фильтрации."""
    dd = defaultdict(int, {"alice": 85, "bob": 92, "carol": 78})
    a = var()
    passed = var(dd)[a >= 80]()
    assert type(passed) is defaultdict
    assert passed.default_factory is int
    assert passed["unknown_key"] == 0


def test_defaultdict_factory_preserved_after_slice():
    """default_factory сохраняется в результате slice-запроса."""
    dd = defaultdict(int, {"a": 10, "b": 20, "c": 30})
    k, v = var(2)
    result = var(dd)[k:v, k != "c"]()
    assert type(result) is defaultdict
    assert result.default_factory is int
    assert dict(result) == {"a": 10, "b": 20}
    assert result["new_key"] == 0


# ============================================================
# Специфика OrderedDict
# ============================================================


def test_ordereddict_order_preserved_after_filter():
    """Порядок ключей сохраняется при фильтрации."""
    od = OrderedDict([("first", 1), ("second", 2), ("third", 3), ("fourth", 4)])
    v = var()
    filtered = var(od)[v >= 2]()
    assert type(filtered) is OrderedDict
    assert list(filtered) == ["second", "third", "fourth"]


def test_ordereddict_order_preserved_after_slice():
    """Порядок ключей сохраняется при slice-запросе."""
    od = OrderedDict([("first", 1), ("second", 2), ("third", 3), ("fourth", 4)])
    k, v = var(2)
    result = var(od)[k:v, v > 1]()
    assert type(result) is OrderedDict
    assert list(result) == ["second", "third", "fourth"]


def test_ordereddict_order_preserved_after_transform():
    """Порядок ключей сохраняется при преобразовании значений."""
    od = OrderedDict([("a", 1), ("b", 2), ("c", 3)])
    a = var()
    doubled = var(od)[a * 2]()
    assert type(doubled) is OrderedDict
    assert list(doubled) == ["a", "b", "c"]
    assert list(doubled.values()) == [2, 4, 6]


# ============================================================
# Специфика Counter
# ============================================================


def test_counter_most_common_after_filter():
    """Counter.most_common доступен после фильтрации."""
    text = "the quick brown fox jumps over the lazy dog the".split()
    c = Counter(text)
    v = var()
    frequent = var(c)[v >= 2]()
    assert type(frequent) is Counter
    assert frequent.most_common(1) == [("the", 3)]


def test_counter_arithmetic_after_filter():
    """Арифметика счётчиков работает над результатом запроса."""
    c = Counter({"a": 3, "b": 5, "c": 2, "d": 1})
    v = var()
    frequent = var(c)[v >= 2]()
    combined = frequent + Counter({"a": 1, "e": 1})
    assert combined == Counter({"a": 4, "b": 5, "c": 2, "e": 1})


# ============================================================
# Запросы к deque (2.3.2 - 2.3.8 для последовательностей)
# ============================================================


def test_deque_lazy_access_by_index():
    """2.3.2: доступ по индексу."""
    q = var(deque([10, 20, 30, 40, 50]))
    assert q[0] == 10
    assert q[-1] == 50


def test_deque_filter_preserves_type():
    """2.3.3: фильтрация, результат — deque."""
    q = deque([10, 20, 30, 40, 50])
    a = var()
    big = var(q)[a > 25]()
    assert type(big) is deque
    assert list(big) == [30, 40, 50]


def test_deque_transform_preserves_type():
    """2.3.4: преобразование элементов, результат — deque."""
    q = deque([1, 2, 3, 4, 5])
    a = var()
    squared = var(q)[a * a]()
    assert type(squared) is deque
    assert list(squared) == [1, 4, 9, 16, 25]


def test_deque_project_from_tuples():
    """2.3.5: проекция элементов deque, содержащего кортежи.

    Тип результата — deque (сохраняется как у исходной коллекции). Порядок
    при проекции через _tuple_query не гарантирован: внутри используется
    multset (set-семантика), как и для list/set.
    """
    points = deque([(1, 2), (3, 4), (5, 6), (7, 8)])
    x, y = var(2)
    ys = var(points)[None, y]()
    assert type(ys) is deque
    assert set(ys) == {2, 4, 6, 8}


def test_deque_domain_calculus_with_tuples():
    """2.3.5: исчисление на доменах для deque с tuple-элементами."""
    data = deque([(1, 2), (3, 4), (5, 1), (7, 8)])
    a, b = var(2)
    filtered = var(data)[a, b, a < b]()
    assert type(filtered) is deque
    assert set(filtered) == {(1, 2), (3, 4), (7, 8)}


def test_deque_aggregates():
    """2.3.7: агрегатные функции над deque."""
    q = deque([10, 20, 30, 40, 50])
    assert var(q).sum() == 150
    assert var(q).avg() == 30.0
    assert var(q).min() == 10
    assert var(q).max() == 50
    assert var(q).len() == 5


def test_deque_cartesian_product():
    """2.3.8: декартово произведение deque с другим множеством."""
    q = deque([1, 2, 3])
    s = lazyset({"a", "b"})
    prod = (var(q) ** s)()
    assert set(prod) == {
        (1, "a"), (1, "b"),
        (2, "a"), (2, "b"),
        (3, "a"), (3, "b"),
    }


# ============================================================
# Специфика deque (maxlen)
# ============================================================


def test_deque_maxlen_preserved_after_filter():
    """maxlen сохраняется после фильтрации."""
    q = deque([10, 20, 30, 40, 50], maxlen=5)
    a = var()
    big = var(q)[a > 25]()
    assert type(big) is deque
    assert big.maxlen == 5
    assert list(big) == [30, 40, 50]


def test_deque_maxlen_preserved_after_transform():
    """maxlen сохраняется после преобразования элементов."""
    q = deque([1, 2, 3], maxlen=10)
    a = var()
    doubled = var(q)[a * 2]()
    assert type(doubled) is deque
    assert doubled.maxlen == 10


# ============================================================
# Расширение merge, app, flat для подклассов dict
# ============================================================


def test_merge_preserves_counter_type():
    """merge сохраняет Counter как тип первого аргумента."""
    result = merge(Counter({"a": 1, "b": 2}), {"b": 3, "c": 4})
    assert type(result) is Counter
    assert result == Counter({"a": 1, "b": 3, "c": 4})


def test_merge_preserves_defaultdict_with_factory():
    """merge сохраняет defaultdict и его default_factory."""
    result = merge(defaultdict(int, {"a": 1}), {"b": 2})
    assert type(result) is defaultdict
    assert result.default_factory is int
    assert dict(result) == {"a": 1, "b": 2}
    assert result["unknown"] == 0


def test_merge_preserves_ordereddict_order():
    """merge сохраняет OrderedDict и порядок ключей."""
    a = OrderedDict([("a", 1), ("b", 2)])
    b = OrderedDict([("c", 3), ("b", 99)])
    result = merge(a, b)
    assert type(result) is OrderedDict
    assert list(result) == ["a", "b", "c"]
    assert result["b"] == 99


def test_app_preserves_ordereddict_order():
    """app добавляет пару с сохранением OrderedDict и порядка."""
    od = OrderedDict([("a", 1)])
    result = app(od, ("b", 2))
    assert type(result) is OrderedDict
    assert list(result) == ["a", "b"]


def test_app_preserves_counter_type():
    """app для Counter сохраняет тип."""
    c = Counter({"a": 1})
    result = app(c, ("b", 2))
    assert type(result) is Counter


def test_app_preserves_defaultdict_factory():
    """app для defaultdict сохраняет default_factory."""
    dd = defaultdict(int, {"a": 1})
    result = app(dd, ("b", 2))
    assert type(result) is defaultdict
    assert result.default_factory is int
    assert result["unknown"] == 0


def test_flat_preserves_ordereddict():
    """flat линеаризует вложенные OrderedDict, сохраняя тип."""
    src = OrderedDict([
        ("user", OrderedDict([("name", "Alice"), ("age", 30)])),
        ("role", "admin"),
    ])
    result = flat(src)
    assert type(result) is OrderedDict
    assert dict(result) == {
        ("user", "name"): "Alice",
        ("user", "age"): 30,
        "role": "admin",
    }


def test_flat_preserves_defaultdict_with_factory():
    """flat сохраняет defaultdict и его default_factory."""
    src = defaultdict(int, {"user": {"name": "Alice", "age": 30}, "role": "admin"})
    result = flat(src)
    assert type(result) is defaultdict
    assert result.default_factory is int
    assert dict(result) == {
        ("user", "name"): "Alice",
        ("user", "age"): 30,
        "role": "admin",
    }
    assert result["unknown"] == 0


def test_flat_preserves_counter_type():
    """flat сохраняет Counter (на простом случае без вложений)."""
    src = Counter({"a": 5, "b": 3})
    result = flat(src)
    assert type(result) is Counter
    assert dict(result) == {"a": 5, "b": 3}


# ============================================================
# Интеграция с @queryclass: подкласс dict как атрибут
# ============================================================


def test_queryclass_with_counter_attribute():
    """@queryclass работает с атрибутом-Counter без специальной адаптации."""
    @queryclass
    class Article:
        def __init__(self, name, words):
            self.name = name
            self.cnt = Counter(words)

        def __repr__(self):
            return self.name

    Article("a", "the quick fox the dog".split())
    Article("b", "the brown fox brown".split())
    Article("c", "lazy".split())

    el = var()
    has_the = Article[el.cnt["the"] >= 1]()
    names = {p.name for p in has_the}
    assert names == {"a", "b"}


def test_queryclass_with_defaultdict_attribute():
    """@queryclass работает с атрибутом-defaultdict."""
    @queryclass
    class Doc:
        def __init__(self, name, props):
            self.name = name
            self.props = defaultdict(str, props)

        def __repr__(self):
            return self.name

    Doc("a", {"type": "report", "year": "2024"})
    Doc("b", {"type": "memo", "year": "2025"})
    Doc("c", {"type": "report", "year": "2025"})

    el = var()
    reports = Doc[el.props["type"] == "report"]()
    names = {p.name for p in reports}
    assert names == {"a", "c"}


def test_queryclass_with_ordereddict_attribute():
    """@queryclass работает с атрибутом-OrderedDict."""
    @queryclass
    class Paper:
        def __init__(self, name, props):
            self.name = name
            self.props = OrderedDict(props)

        def __repr__(self):
            return self.name

    Paper("a", [("year", 2024), ("type", "report")])
    Paper("b", [("year", 2025), ("type", "memo")])
    Paper("c", [("year", 2025), ("type", "report")])

    el = var()
    reports = Paper[el.props["type"] == "report"]()
    names = {p.name for p in reports}
    assert names == {"a", "c"}
