from copy import deepcopy

from .core import (
    expr,
    calculus,
    lazyfunc,
    var,
    vartype,
    vargrouptype,
    simpletypes,
    agrfunctypes,
    funcanytype,
    funcalltype,
    calcfunclist,
)
from .sets import multset, lazyset


# абстрактный класс-предок для ленивого индекса и атрибута
class lazyabc(expr, calculus):
    def __init__(self, obj, arg):
        self.obj = obj
        self.arg = arg

    def __call__(self, *args):
        obj = self.obj
        if callable(obj):
            if not (
                hasattr(obj, "__dict__")
                and ("qrcls" in obj.__dict__)
                and (obj.__dict__["qrcls"] == True)
            ):
                obj = obj(*args)
            else:
                obj = obj.value
        else:
            obj = obj.value
        return obj

    def createsign(self, L=None):
        return self.obj.createsign(L)

    def __deepcopy__(self, memo):
        obj = deepcopy(self.obj, memo)
        arg = deepcopy(self.arg, memo)
        my_copy = type(self)(obj, arg)
        memo[id(self)] = my_copy
        return my_copy


# Ленивый атрибут
class lazyattr(lazyabc):
    def __call__(self, *args):
        obj = super().__call__(*args)
        if isinstance(obj, dict) and self.arg in ("keys", "values", "items"):
            return lazyset(getattr(obj, self.arg)())
        if self.arg in obj.__dict__:
            return obj.__dict__[self.arg]
        # Потенциально опасно, но устраняет необходимость писать код типа F=flight.L
        elif self.arg == "L":
            return set(obj.__dict__.values())


# вспомогательная функция для заполнения пользовательской коллекции результатом - сохранения её типа и настроек. Несколько стратегий:
def createcoll(obj, coll):
    coll = list(coll)
    # создается копия исходной коллекции и из нее удаляются элементы, не входящие в ответ
    if (
        type(obj) not in [multset, set, list]
        and hasattr(obj, "remove")
        and all(el in obj for el in coll)
    ):
        R = deepcopy(obj)
        for el in zip(obj, R):
            if el[0] not in coll:
                R.remove(el[1])
        return R
    # создание копии коллекции, её очистка и повторное заполнение отобранными значениями (попытка сохранить все настройки):
    elif (
        type(obj) not in [multset, set, list]
        and (hasattr(obj, "clear") or hasattr(obj, "remove"))
        and (hasattr(obj, "append") or hasattr(obj, "add"))
    ):
        R = deepcopy(obj)
        if hasattr(obj, "clear"):
            R.clear()
        else:
            for el in R:
                R.remove(el)
        if hasattr(obj, "append"):
            f = True
        else:
            f = False
        for el in coll:
            if f:
                R.append(el)
            else:
                R.add(el)
        return R
    # создаем коллекцию с ключом, добавляем элементы
    elif type(obj) not in [multset, set, list] and hasattr(obj, "key"):
        return type(obj)([el for el in coll], obj.key)
    # заполнение коллекции отобранными значениями - свойства-установки коллекции теряются.
    else:
        return type(obj)([el for el in coll])


# вспомогательная функция - определяет, состоит ли коллекция только из истин и лжи
def isbool(arg):
    if isinstance(arg, str) or not (hasattr(arg, "__iter__")):
        if arg in [True, False]:
            return True
        else:
            return False
    else:
        for a in arg:
            if not (isbool(a)):
                return False
    return True


# Формирование выборки на основе истин и лжи
def selection(obj, arg):
    R = []
    for el in zip(obj, arg):
        if hasattr(el[1], "__iter__"):
            r = selection(el[0], el[1])
            if len(r) == 1:
                R.append(*r)
            elif len(r) > 0:
                R.append(r)
        elif el[1]:
            R.append(el[0])
    return type(obj)(R)
    # return type(obj)(el[0] for el in zip(obj,arg) if el[1])


# Запросы к графам
def patternmatch(obj, arg):
    if type(arg) != tuple:
        return False
    if type(arg[0]) != tuple:
        return False
    f = True
    for a in arg[0]:
        if type(a) != vartype and a != Ellipsis:
            f = False
            break
    if f:
        # Шаблон (A,A,...) Пути в дереве
        if (
            len(arg[0]) == 3
            and type(arg[0][0]) == vartype
            and type(arg[0][1]) == vartype
            and arg[0][2] == Ellipsis
        ):
            # print("(A,A,...)")
            R = packelements(var(obj))
            M = var(obj)
            n = len(obj)
            while True:
                P = lazyset()
                for m in M * R:
                    S = lazyset({(m[0], m[1])})[arg[0][:-1] + arg[1:]]()
                    if len(S) > 0:
                        P.append(m)
                R = R | P
                k = len(R())
                if k == n:
                    break
                else:
                    n = k
            return R()
        # Шаблон (A,A,...,A) Пути в графе без циклов
        elif (
            len(arg[0]) == 4
            and type(arg[0][0]) == vartype
            and type(arg[0][1]) == vartype
            and arg[0][2] == Ellipsis
            and type(arg[0][3]) == vartype
        ):
            R = packelements(var(obj))
            M = var(obj)
            n = len(obj)
            # print("(A,A,...,A)")
            while True:
                P = lazyset()
                for m in M * R:
                    S = lazyset({(m[0], m[1], m[-1])})[
                        arg[0][:2] + (arg[0][3],) + arg[1:]
                    ]()
                    if len(S) > 0:
                        P.append(m)
                R = R | P
                k = len(R())
                if k == n:
                    break
                else:
                    n = k
            return R()
        # Шаблон (A,A,...,A,...) Пути в  графе
        elif (
            len(arg[0]) == 5
            and type(arg[0][0]) == vartype
            and type(arg[0][1]) == vartype
            and arg[0][2] is Ellipsis
            and type(arg[0][3]) == vartype
            and arg[0][4] is Ellipsis
        ):
            R = packelements(var(obj))
            M = var(obj)
            n = len(obj)
            # print("(A,A,...,A,...)")
            while True:
                P = lazyset()
                for m in M * R:
                    fl = True
                    for i in range(1, len(m)):
                        S = lazyset({(m[0], m[1], m[i])})[
                            arg[0][:2] + (arg[0][3],) + arg[1:]
                        ]()
                        if len(S) == 0:
                            fl = False
                            break
                    if fl:
                        P.append(m)
                R = R | P
                k = len(R())
                if k == n:
                    break
                else:
                    n = k
            return R()
        # Шаблон (A,...,A,...,A) циклы, воcьмерки тоже выводятся
        elif (
            len(arg[0]) == 5
            and type(arg[0][0]) == vartype
            and arg[0][1] is Ellipsis
            and type(arg[0][2]) == vartype
            and arg[0][3] is Ellipsis
            and type(arg[0][4]) == vartype
        ):
            M = var(obj)
            C = set()
            P = var(obj)
            # print("(A,...,A,...,A)")
            while True:
                newP = lazyset()
                for m in M * P:
                    S = lazyset({(m[0], m[1])})[(arg[0][0], arg[0][2]) + arg[1:]]()
                    if len(S) > 0:
                        if m[0] == m[-1]:
                            C.add(m[:-1])
                        elif m[0] not in m[1:]:
                            newP.append(m)
                if len(newP()) == 0:
                    break
                else:
                    P = newP
            # Убираем одинаковые циклы
            D = set()
            for c in C:
                f = True
                d = c
                for i in range(len(c)):
                    d = d[1:] + (d[0],)
                    if d in D:
                        f = False
                        break
                if f:
                    D.add(d)
            return D
        # Шаблон (A,...,A) циклы, удаление восьмерок
        elif (
            len(arg[0]) == 3
            and type(arg[0][0]) == vartype
            and arg[0][1] is Ellipsis
            and type(arg[0][2]) == vartype
        ):
            M = var(obj)
            C = set()
            P = var(obj)
            # print("(A,...,A)")
            while True:
                newP = lazyset()
                for m in M * P:
                    S = lazyset({(m[0], m[1])})[(arg[0][0], arg[0][2]) + arg[1:]]()
                    if len(S) > 0:
                        if m[0] == m[-1]:
                            C.add(m[:-1])
                        elif m[0] not in m[1:]:
                            newP.append(m)
                if len(newP()) == 0:
                    break
                else:
                    P = newP
            # Убираем одинаковые циклы
            D = set()
            for c in C:
                f = True
                d = c
                for i in range(len(c)):
                    d = d[1:] + (d[0],)
                    if d in D:
                        f = False
                        break
                if f:
                    D.add(d)
            # Убираем "восьмерки" - рекурсивно ищем циклы в уже найденном цикле
            E = set()
            for d in D:
                dc = lazyset(d)[(arg[0][0], ..., arg[0][2], ..., arg[0][2]), *arg[1:]]()
                if len(dc) == 1:
                    E.add(d)
            return E
        # декартово произведение множества само на себя несколько раз
        # Шаблон (A,B,C,D,E)
        else:
            M = lazyset(obj)
            for i in range(len(arg[0]) - 1):
                M = M * lazyset(obj)
            if len(arg) > 1:
                R = M[arg[0] + arg[1:]]
            else:
                R = M()
            return R
    return f


def _tuple_query(obj, arg):
    """Domain calculus / projection для кортежа-индекса.

    Вынесено из `lazyindex.__call__`, чтобы можно было переиспользовать
    при обработке `dict[tuple]` через `multset(obj.items())`.
    """
    sign = []
    func = []
    example = None
    for el in obj:
        example = el
        break
    if example == None:
        return multset()
    if type(example) in simpletypes:
        lenexample = 1
    else:
        lenexample = len(example)
    if lenexample > len(arg):
        A = set()
        for el in obj:
            f = True
            for i in range(len(arg)):
                if type(arg[i]) is expr:
                    if not (arg[i](el)):
                        f = False
                        break
            if f:
                a = []
                for i in range(len(arg)):
                    if type(arg[i]) in [lazyindex, lazyattr, expr]:
                        xx = arg[i](el)
                        if type(xx) != bool:
                            a.append(xx)
                        else:
                            a.append(el)
                if len(a) == 1:
                    A.add(a[0])
                else:
                    A.add(tuple(a))
        return multset(A)
    else:
        g = False
        lg = 0
        arggroup = [None] * min(len(arg), lenexample)
        for i in range(min(len(arg), lenexample)):
            if type(arg[i]) == vargrouptype:
                g = True
                lg = lg + 1
                arggroup[i] = var()
        if g:
            grp = lazyset(obj)[*arggroup]
            res = lazyset()
            for el in grp:
                k = 0
                arggroup1 = [var() for a in range(len(arggroup))]
                for i in range(len(arggroup)):
                    if type(arggroup[i]) == vartype:
                        if lg > 1:
                            arggroup1[i] = el[k]
                        else:
                            arggroup1[i] = el
                        k = k + 1
                grp1 = lazyset(obj)[*arggroup1]
                b = []
                for i in range(len(arggroup1)):
                    if type(arggroup1[i]) == vartype:
                        b.append([])
                    else:
                        b.append(arggroup1[i])
                for a in grp1:
                    for i in range(len(a)):
                        if type(arggroup[i]) != vartype:
                            b[i].append(a[i])
                for i in range(len(b)):
                    if type(b[i]) == list:
                        b[i] = tuple(b[i])
                b = tuple(b)
                res.add(b)
            obj = res
        for i in range(min(len(arg), lenexample)):
            if arg[i] != None:
                sign.append(i)
        for i in range(len(arg)):
            if arg[i] != None:
                if callable(arg[i]):
                    func.append(arg[i])
                else:
                    if i < lenexample:
                        v = var()
                        func.append(v == arg[i])
        if lenexample == 1:
            A = {(el,) for el in obj}
        else:
            A = {tuple(el[i] for i in sign) for el in obj}
        B = multset()
        for el in A:
            f = True
            for i in range(min(len(func), len(sign))):
                if type(func[i]) == funcanytype or type(func[i]) == funcalltype:
                    if not (func[i](el[i])()):
                        f = False
                        break
                elif (
                    type(func[i]) not in [vartype, lazyindex, lazyattr]
                    and type(func[i]) not in agrfunctypes
                    and not (func[i](el[i]))
                ):
                    f = False
                    break
            if f:
                argname = []
                for i in range(lenexample):
                    if arg[i] != None:
                        argname.append(arg[i])
                mask = [True] * len(argname)
                for i in range(len(argname)):
                    for j in range(i + 1, len(argname)):
                        if argname[i] is argname[j]:
                            mask[j] = False
                            if el[i] != el[j]:
                                f = False
                                break
                    if not (f):
                        break
            if f:
                for i in range(len(sign), len(func)):
                    S = func[i].createsign()
                    for j in range(len(S)):
                        for k in range(len(sign)):
                            if S[j] is arg[sign[k]]:
                                S[j](el[k])
                    if not (func[i]()):
                        f = False
                        break
            if f:
                el = list(el)
                for i in range(len(sign)):
                    if (
                        type(arg[sign[i]]) in [lazyindex, lazyattr]
                        or arg[sign[i]] in calcfunclist
                    ):
                        xx = arg[sign[i]](el[i])
                        if type(xx) != bool:
                            el[i] = xx
                el = tuple(el)
            if f:
                ex = tuple(el[i] for i in range(len(el)) if mask[i])
            if f:
                ex = list(ex)
                for i in range(lenexample, len(arg)):
                    if (
                        type(arg[i])
                        not in [expr, lazyindex, lazyattr, vartype]
                        and arg[i] not in calcfunclist
                    ):
                        ex.append(arg[i])
                    elif type(arg[i]) == vartype:
                        for j in range(len(sign)):
                            if arg[i] is arg[sign[j]]:
                                ex.append(el[j])
                    elif (
                        type(arg[i]) == expr
                        and arg[i].op
                        not in ["<", "<=", "==", ">=", ">", "!="]
                        or type(arg[i]) in [lazyindex, lazyattr]
                        or arg[i] in calcfunclist
                    ):
                        S = arg[i].createsign()
                        for j in range(len(S)):
                            for k in range(len(sign)):
                                if S[j] is arg[sign[k]]:
                                    S[j](el[k])
                        aa = arg[i]()
                        if type(aa) is not bool:
                            ex.append(aa)
                ex = tuple(ex)
            if f:
                if len(ex) == 1:
                    ex = ex[0]
                B.add(ex)

        f = False
        if len(B) > 0 and not (g):
            for b in B:
                exampleres = b
                break
            if exampleres in obj:
                f = True
            elif (
                hasattr(exampleres, "__iter__")
                and hasattr(example, "__iter__")
                and hasattr(exampleres, "__len__")
                and hasattr(example, "__len__")
                and len(exampleres) == len(example)
                and not (hasattr(example, "qrcls"))
            ):
                f = all(
                    type(el[0]) == type(el[1])
                    for el in zip(exampleres, example)
                )
                if type(example)(exampleres) in obj:
                    f = True
                    B = (type(example)(b) for b in B)
        if f and not (g):
            return createcoll(obj, B)
        else:
            return multset(B)


def _handle_dict_query(obj, arg):
    """Обработка запросов к dict: фильтрация/преобразование значений
    и domain calculus через пары (ключ, значение)."""
    if type(arg) is tuple:
        result = _tuple_query(multset(obj.items()), arg)
        if (
            isinstance(result, multset)
            and len(result) > 0
            and all(type(el) is tuple and len(el) == 2 for el in result)
        ):
            return dict(result)
        return result
    if type(arg) is expr:
        if arg.op in ("<", "<=", "==", ">=", ">", "!=", "&", "|", "^"):
            return {k: v for k, v in obj.items() if arg(v)}
        return {k: arg(v) for k, v in obj.items()}
    return obj


# Ленивый индекс
class lazyindex(lazyabc):
    # проверка и расчет декларативных цепочек
    def chainmatch(self, *args):
        # шаблон A*A*...*A*...
        if (
            type(self.obj) == expr
            and hasattr(self.obj, "op")
            and self.obj.arg2 is Ellipsis
            and type(self.obj.arg1.arg1) == expr
            and hasattr(self.obj.arg1.arg1, "op")
            and self.obj.arg1.arg1.arg2 is Ellipsis
        ):
            return var(self.obj.arg1.arg2())[
                ((self.arg[0], self.arg[1], ..., self.arg[2], ...),) + self.arg[3:]
            ](*args)
        # шаблон A*A*...
        elif (
            type(self.obj) == expr
            and hasattr(self.obj, "op")
            and self.obj.arg2 is Ellipsis
        ):
            return var(self.obj.arg1.arg2())[
                ((self.arg[0], self.arg[1], ...),) + self.arg[2:]
            ](*args)
        # шаблон A*...*A*...*A - цикл с сохранением восьмерок
        elif (
            type(self.obj) == expr
            and hasattr(self.obj, "op")
            and type(self.obj.arg1) == expr
            and hasattr(self.obj.arg1, "op")
            and self.obj.arg1.arg2 is Ellipsis
            and type(self.obj.arg1.arg1) == expr
            and hasattr(self.obj.arg1.arg1, "op")
            and type(self.obj.arg1.arg1.arg1) == expr
            and hasattr(self.obj.arg1.arg1.arg1, "op")
            and self.obj.arg1.arg1.arg1.arg2 is Ellipsis
        ):
            return var(self.obj.arg2())[
                ((self.arg[0], ..., self.arg[1], ..., self.arg[1]), self.arg[1])
                + self.arg[2:]
            ](*args)
        # шаблон A*A*...*A
        elif (
            type(self.obj) == expr
            and hasattr(self.obj, "op")
            and type(self.obj.arg1) == expr
            and hasattr(self.obj.arg1, "op")
            and self.obj.arg1.arg2 is Ellipsis
            and type(self.obj.arg1.arg1) == expr
            and hasattr(self.obj.arg1.arg1, "op")
        ):
            return var(self.obj.arg2())[
                ((self.arg[0], self.arg[1], ..., self.arg[2]),) + self.arg[3:]
            ](*args)
        # шаблон A*...*A - цикл c удалением восьмерок
        elif (
            type(self.obj) == expr
            and hasattr(self.obj, "op")
            and type(self.obj.arg1) == expr
            and hasattr(self.obj.arg1, "op")
            and self.obj.arg1.arg2 is Ellipsis
        ):
            return var(self.obj.arg2())[
                ((self.arg[0], ..., self.arg[1]),) + self.arg[2:]
            ](*args)
        return False

    def __call__(self, *args):
        # проверка декларативной цепочки, возвращение результата поиска
        P = self.chainmatch(*args)
        if P:
            return P
        obj = super().__call__(*args)
        while callable(obj):
            if (
                hasattr(obj, "__dict__")
                and ("qrcls" in obj.__dict__)
                and (obj.__dict__["qrcls"] == True)
            ):
                break
            obj = obj()
        # проверка соответствия шаблону, возвращение результата поиска
        P = patternmatch(obj, self.arg)
        if P:
            return P
        # монадическая выборка
        from .functional import monad

        if type(self.arg) == monad:
            R = self.arg(obj)()()
            if isbool(R):
                return var(obj)[R]()
            else:
                return R
            # return var(obj)[self.arg(obj)()()]()
        # Декларативные запросы к dict: фильтрация/преобразование значений
        # и domain calculus через пары (key, value)
        if isinstance(obj, dict) and (
            (callable(self.arg) and type(self.arg) is expr)
            or type(self.arg) is tuple
        ):
            return _handle_dict_query(obj, self.arg)
        # Одно условие - исчисление на кортежах
        if callable(self.arg):
            if type(self.arg) is expr and self.arg.op not in [
                "<",
                "<=",
                "==",
                ">=",
                ">",
                "!=",
                "&",
                "|",
                "^",
            ]:
                return createcoll(obj, (self.arg(el) for el in obj))
                # return type(obj)(self.arg(el) for el in obj)
                # return type(obj)(*(self.arg(el) for el in obj))
            elif type(self.arg) in [
                expr,
                var,
            ]:  # вероятно, ошибка - вместо var - vartype
                return createcoll(obj, (el for el in obj if self.arg(el)))
                # return type(obj)(el for el in obj if self.arg(el))
            else:
                if type(self.arg) is expr and self.arg.op in [
                    "<",
                    "<=",
                    "==",
                    ">=",
                    ">",
                    "!=",
                    "&",
                    "|",
                    "^",
                ]:
                    return createcoll(obj, (self.arg(el) for el in obj if self.arg(el)))
                    # return type(obj)(self.arg(el) for el in obj if self.arg(el))
                else:
                    return createcoll(obj, (self.arg(el) for el in obj))
                    return type(obj)(self.arg(el) for el in obj)

        # Несколько условий - исчисление на доменах или проекция
        elif type(self.arg) == tuple:
            return _tuple_query(obj, self.arg)
        # Числовой индекс или срез
        else:
            # индекс из истин и лжи
            if type(self.arg) != int and isbool(self.arg):
                return selection(obj, self.arg)
            # Числовой индекс или срез
            else:
                if hasattr(obj, "__getitem__"):
                    return obj.__getitem__(self.arg)
                elif hasattr(obj, "__dict__"):
                    return list(obj.__dict__.values())[self.arg]
                return obj.__getitem__(self.arg)

    # общий индекс из индексов аргументов при декартовом произведении
    def __pow__(self, other):
        if type(other) == lazyindex:
            return (self.obj**other.obj)[self.arg + other.arg]
        else:
            return super().__pow__(other)

    def __ior__(self, other):
        L = reccheck(self.obj, other)
        if len(L) > 0:
            other.recstart = True
            other.recparam = L
        R = indpropagation(self, other)
        return R


# проверка на наличие рекурсии
def reccheck(A, B, L=None):
    if L == None:
        L = []
    if type(B) == expr:
        L = reccheck(A, B.__dict__["arg1"], L)
        L = reccheck(A, B.__dict__["arg2"], L)
    elif type(B) == lazyindex or type(B) == lazyattr:
        L = reccheck(A, B.__dict__["obj"], L)
    elif type(B) == vartype:
        if A is B:
            L.append(B)
    return L


# перестановка местами элементов кортежа
@lazyfunc
def subst(R, P):
    return {tuple(el[i] for i in P) for el in R()}


# проталкивание левого индекса внутрь правого выражения
def indpropagation(self, other):
    if (
        type(other) == lazyindex
        and (type(other.arg) is tuple)
        and (type(self.arg) is tuple)
    ):
        ind = []
        for i in range(len(other.arg)):
            f = True
            for j in range(i):
                if other.arg[i] is other.arg[j]:
                    f = False
                    break
            if f:
                ind.append(other.arg[i])
        for i in range(len(ind)):
            f = True
            for j in range(len(self.arg)):
                if ind[i] is self.arg[j]:
                    f = False
                    break
            if f:
                ind[i] = None
        R = other[*ind]
        # формирование подстановки
        ind1 = []
        for i in range(len(ind)):
            if ind[i] != None:
                ind1.append(ind[i])
        P = []
        for i in range(len(self.arg)):
            for j in range(len(ind1)):
                if self.arg[i] is ind1[j]:
                    P.append(j)
                    break
        # return R
        return subst(R, P)
    elif type(other) == expr and other.op == "|":
        other.arg1 = indpropagation(self, other.arg1)
        other.arg2 = indpropagation(self, other.arg2)
        return other
    elif type(other) == vartype:
        return other[self.arg]
    else:
        return other[self.arg]


@lazyfunc
def packelements(L):
    return lazyset({(el,) for el in L})
