"""
Tests for declarative queries on Python dicts.
"""

import pytest

from decpy import var, merge, app, flat, lazyset, multset, queryclass


def test_lazy_access_by_key():
    d = var({"alice": 85, "bob": 92})
    assert d["alice"] == 85
    assert d["bob"] == 92


def test_keys_values_items_views():
    grades = var({"alice": 85, "bob": 92, "carol": 78})
    assert set(grades.keys()) == {"alice", "bob", "carol"}
    assert set(grades.values()) == {85, 92, 78}
    assert set(grades.items()) == {
        ("alice", 85),
        ("bob", 92),
        ("carol", 78),
    }


def test_filter_by_value_condition():
    grades = var({"alice": 85, "bob": 92, "carol": 78, "dave": 55})
    a = var()
    passed = grades[a >= 60]()
    assert passed == {"alice": 85, "bob": 92, "carol": 78}


def test_transform_values():
    grades = var({"alice": 85, "bob": 92})
    a = var()
    doubled = grades[a * 2]()
    assert doubled == {"alice": 170, "bob": 184}


def test_domain_calculus_two_vars():
    prices = var({"яблоко": 80, "банан": 120, "вишня": 250, "груша": 95})
    k, v = var(2)
    expensive = prices[k, v, v > 100]()
    assert expensive == {"банан": 120, "вишня": 250}


def test_domain_calculus_filter_by_key():
    grades = var({"alice": 85, "bob": 92, "carol": 78, "dave": 55})
    k, v = var(2)
    short_names = grades[k, v, k < "carol"]()
    assert short_names == {"alice": 85, "bob": 92}


def test_domain_calculus_projection_chain():
    prices = var({"яблоко": 80, "банан": 120, "вишня": 250})
    k, v = var(2)
    names = prices[k, v, v > 100][k, None]()
    assert set(names) == {"банан", "вишня"}


def test_aggregates_on_values():
    grades = var({"alice": 85, "bob": 92, "carol": 78, "dave": 55})
    assert grades.values().sum() == 310
    assert grades.values().avg() == 77.5
    assert grades.values().len() == 4
    assert grades.values().min() == 55
    assert grades.values().max() == 92


def test_cartesian_product_dict_and_set():
    prices = {"яблоко": 80, "банан": 120}
    orders = lazyset({("яблоко", 3), ("банан", 5)})
    prod = (var(prices) ** orders)()
    assert set(prod) == {
        ("яблоко", 80, "яблоко", 3),
        ("яблоко", 80, "банан", 5),
        ("банан", 120, "яблоко", 3),
        ("банан", 120, "банан", 5),
    }

    name, price, product, qty = var(4)
    total = (var(prices) ** orders)[
        name, price, product, qty, name == product, price * qty
    ]()
    assert set(total) == {
        ("яблоко", 80, "яблоко", 3, 240),
        ("банан", 120, "банан", 5, 600),
    }


def test_queryclass_with_dict_attribute():
    @queryclass
    class Product:
        def __init__(self, name, props):
            self.name = name
            self.props = props

        def __repr__(self):
            return self.name

    Product("яблоко", {"цвет": "красный", "вес": 150})
    Product("банан", {"цвет": "жёлтый", "вес": 120})
    Product("вишня", {"цвет": "красный", "вес": 5})

    el = var()
    red = Product[el.props["цвет"] == "красный"]()
    names = {p.name for p in red}
    assert names == {"яблоко", "вишня"}


def test_merge_dicts():
    assert merge({"a": 1, "b": 2}, {"b": 3, "c": 4}) == {"a": 1, "b": 3, "c": 4}


def test_app_dict():
    assert app({"x": 10}, ("y", 20)) == {"x": 10, "y": 20}


def test_flat_nested_dict():
    result = flat({"user": {"name": "Alice", "age": 30}, "role": "admin"})
    assert result == {
        ("user", "name"): "Alice",
        ("user", "age"): 30,
        "role": "admin",
    }


def test_var_dict_python_semantics():
    d = {"a": 1, "b": 2}
    vd = var(d)
    assert set(iter(vd())) == {"a", "b"}
    assert str(vd()) == str(d)


def test_slice_full_pair():
    prices = var({"яблоко": 80, "банан": 120, "вишня": 250})
    k, v = var(2)
    assert prices[k:v]() == {"яблоко": 80, "банан": 120, "вишня": 250}


def test_slice_filter_by_value():
    prices = var({"яблоко": 80, "банан": 120, "вишня": 250, "груша": 95})
    k, v = var(2)
    assert prices[k:v, v > 100]() == {"банан": 120, "вишня": 250}


def test_slice_filter_by_key_and_value():
    grades = var({"alice": 85, "bob": 92, "carol": 78, "dave": 55})
    k, v = var(2)
    assert grades[k:v, k < "carol", v >= 60]() == {"alice": 85, "bob": 92}


def test_slice_inline_value_predicate():
    prices = var({"яблоко": 80, "банан": 120, "вишня": 250})
    k, v = var(2)
    assert prices[k : v > 100]() == {"банан": 120, "вишня": 250}


def test_slice_inline_both_predicates():
    grades = var({"alice": 85, "bob": 92, "carol": 78, "dave": 55})
    k, v = var(2)
    assert grades[k < "carol" : v >= 60]() == {"alice": 85, "bob": 92}


def test_slice_project_keys():
    prices = var({"яблоко": 80, "банан": 120, "вишня": 250})
    k = var()
    assert set(prices[k:]()) == {"яблоко", "банан", "вишня"}


def test_slice_project_values():
    prices = var({"яблоко": 80, "банан": 120, "вишня": 250})
    v = var()
    assert set(prices[:v]()) == {80, 120, 250}


def test_slice_project_values_with_inline_predicate():
    prices = var({"яблоко": 80, "банан": 120, "вишня": 250})
    v = var()
    assert set(prices[: v > 100]()) == {120, 250}


def test_slice_projection_chain():
    prices = var({"яблоко": 80, "банан": 120, "вишня": 250})
    k, v = var(2)
    names = prices[k : v > 100][k, None]()
    assert set(names) == {"банан", "вишня"}
