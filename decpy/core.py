from collections import deque
from functools import reduce
from copy import deepcopy

from .utils import flat, monaddistinct, monadreduce, monadreplace


# Множественный конструктор
def multiconstr(cls):
    def wrapper(*n):
        if len(n) == 0:
            return cls()
        elif len(n) == 1 and type(n[0]) == int:
            return (cls() for i in range(n[0]))
        else:
            return cls(*n)

    return wrapper


# ленивое выражение
class expr:
    def __init__(self, arg1, op, arg2):
        self.arg1 = arg1
        self.op = op
        self.arg2 = arg2
        self.recstart = False

    def __call__(self, *args):
        # вычисления с рекурсиями
        if self.recstart:
            from .sets import lazyset

            n = 0
            buf = self.recparam[0].value
            self.recparam[0].value = lazyset()
            # reclim=10
            # while reclim>0:
            while True:
                R = self.callmain(*args)
                if len(R) == n:
                    break
                n = len(R)
                self.recparam[0].value = lazyset(R)
                # reclim=reclim-1
            self.recparam[0].value = buf
            return lazyset(R)
        else:
            return self.callmain(*args)

    def __iter__(self):
        return self().__iter__()

    def __next__(self):
        return self().__next__()

    # вычисления или выполнение запросов без рекурсий
    def callmain(self, *args):
        from .queries import lazyindex as _lazyindex
        from .sets import multset

        if len(args) > 0:
            sign = self.createsign()
            for i in range(len(sign)):
                sign[i](args[i])
        arg1 = self.arg1
        # проверка на цепочку умножений
        manymult = False
        if type(arg1) == expr and arg1.op == "*" and self.op == "*":
            manymult = True
        elif (
            type(arg1) == _lazyindex
            and type(arg1.obj) == expr
            and arg1.obj.op == "*"
            and self.op == "*"
        ):
            manymult = True
        # получение выборок, вычислений; прерывание вызовов, если аргумент - класс.
        while callable(arg1):
            if (
                hasattr(arg1, "__dict__")
                and ("qrcls" in arg1.__dict__)
                and (arg1.__dict__["qrcls"] == True)
            ):
                break
            arg1 = arg1()
        arg2 = self.arg2
        while callable(arg2):
            if (
                hasattr(arg2, "__dict__")
                and ("qrcls" in arg2.__dict__)
                and (arg2.__dict__["qrcls"] == True)
            ):
                break
            arg2 = arg2()
        if self.op == "+":
            return arg1 + arg2
        elif self.op == "*":
            if isinstance(arg1, dict):
                arg1 = multset(arg1.items())
            if isinstance(arg2, dict):
                arg2 = multset(arg2.items())
            if manymult and type(arg1) is multset and type(arg2) is multset:
                return arg1.specialmult(arg2)
            if type(arg1) == set or type(arg2) == set:
                return multset(arg1) * multset(arg2)
            return arg1 * arg2
        elif self.op == "**":
            if isinstance(arg1, dict):
                arg1 = multset(arg1.items())
            if isinstance(arg2, dict):
                arg2 = multset(arg2.items())
            if isinstance(arg1, deque):
                arg1 = multset(arg1)
            if isinstance(arg2, deque):
                arg2 = multset(arg2)
            if type(arg1) == set or type(arg2) == set:
                return multset(arg1) ** multset(arg2)
            return arg1**arg2
        elif self.op == "<":
            return arg1 < arg2
        elif self.op == "<=":
            return arg1 <= arg2
        elif self.op == "==":
            return arg1 == arg2
        elif self.op == ">=":
            return arg1 >= arg2
        elif self.op == ">":
            return arg1 > arg2
        elif self.op == "!=":
            return arg1 != arg2
        elif self.op == "&":
            return arg1 & arg2
        elif self.op == "|":
            return arg1 | arg2
        elif self.op == "|=":
            return arg2
        elif self.op == "/":
            return arg1 / arg2
        elif self.op == "//":
            return arg1 // arg2
        elif self.op == "%":
            return arg1 % arg2
        elif self.op == "-":
            return arg1 - arg2
        elif self.op == "^":
            return arg1 ^ arg2
        elif self.op == "neg":
            return -arg1

    def __str__(self):
        return str(self())

    def __repr__(self):
        return str(self)

    def __add__(self, other):
        return expr(self, "+", other)

    def __mul__(self, other):
        return expr(self, "*", other)

    def __pow__(self, other):
        return expr(self, "**", other)

    def __or__(self, other):
        return expr(self, "|", other)

    def __sub__(self, other):
        return expr(self, "-", other)

    def __xor__(self, other):
        return expr(self, "^", other)

    def __lt__(self, other):
        return expr(self, "<", other)

    def __le__(self, other):
        return expr(self, "<=", other)

    def __eq__(self, other):
        return expr(self, "==", other)

    def __ge__(self, other):
        return expr(self, ">=", other)

    def __gt__(self, other):
        return expr(self, ">", other)

    def __ne__(self, other):
        return expr(self, "!=", other)

    def __and__(self, other):
        return expr(self, "&", other)

    def __truediv__(self, other):
        return expr(self, "/", other)

    def __floordiv__(self, other):
        return expr(self, "//", other)

    def __neg__(self):
        return expr(self, "neg", None)

    def __mod__(self, other):
        return expr(self, "%", other)

    def __radd__(self, other):
        return expr(other, "+", self)

    def __rmul__(self, other):
        return expr(other, "*", self)

    def __rpow__(self, other):
        return expr(other, "**", self)

    def __rsub__(self, other):
        return expr(other, "-", self)

    def __rtruediv__(self, other):
        return expr(other, "/", self)

    def __rfloordiv__(self, other):
        return expr(other, "//", self)

    def __rmod__(self, other):
        return expr(other, "%", self)

    # определение новых понятий в стиле пролога
    def __ior__(self, other):
        from .queries import reccheck, lazyindex as _lazyindex, indpropagation

        L = reccheck(self, other)
        if len(L) > 0:
            # проталкивание индекса внутрь выражения:
            if type(other) == _lazyindex:
                A = var()[other.arg]
                other = other.obj
                R = indpropagation(A, other)
                other.recstart = True
                other.recparam = L
                return R
            else:
                other.recstart = True
                other.recparam = L
                return other
        return other

    # создание сигнатуры для превращения ленивого выражения в функцию
    def createsign(self, L=None):
        if L == None:
            L = []
        if callable(self.arg1):
            self.arg1.createsign(L)
        if callable(self.arg2):
            self.arg2.createsign(L)
        return L

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            from .queries import lazyattr

            return lazyattr(self, attr)

    def __getitem__(self, ind):
        from .queries import lazyindex

        return lazyindex(self, ind)

    def __deepcopy__(self, memo):
        arg1 = deepcopy(self.arg1, memo)
        op = deepcopy(self.op, memo)
        arg2 = deepcopy(self.arg2, memo)
        my_copy = type(self)(arg1, op, arg2)
        my_copy.recstart = self.recstart
        memo[id(self)] = my_copy
        return my_copy


# ленивая функция (в том числе - метод) для внутреннего использования
def lazyfunc(f):
    class wrapper(expr):
        def __init__(self, *args):
            self.args = args

        def __call__(self, *args):
            if len(args) > 0:
                sign = self.createsign()
                for i in range(len(sign)):
                    sign[i](args[i])
            return f(*self.args)

        def createsign(self, L=None):
            if L == None:
                L = []
            for arg in self.args:
                if callable(arg):
                    arg.createsign(L)
            return L

    def res(*args):
        return wrapper(*args)

    def __repr__(self):
        return str(self())

    res.lzfnc = True
    return res


# ленивая функция, например, для встраивания в формулу функций библиотеки math
def lazyfun(f):
    @lazyfunc
    def wrapper(*args):
        return f(*[a() for a in args])

    return wrapper


# абстрактный класс c ленивыми вычислительными методами
class calculus:
    def __len__(self):
        return len(self())

    @lazyfunc
    def flat(self, n=0):
        return flat(self(), n)

    @lazyfunc
    def len(self):
        return len(self())
        # return len(flat(self()))

    @lazyfunc
    def monadlen(self):
        # return len(self())
        return len(flat(self()))

    @lazyfunc
    def sum(self):
        return sum(self())
        # return sum(flat(self()))

    @lazyfunc
    def monadsum(self):
        # sum(self())
        return sum(flat(self()))

    @lazyfunc
    def min(self, arg=lambda x: x):
        return min(self(), key=arg)
        # return min(flat(self()),key=arg)

    @lazyfunc
    def monadmin(self, arg=lambda x: x):
        # return min(self(),key=arg)
        return min(flat(self()), key=arg)

    @lazyfunc
    def max(self, arg=lambda x: x):
        return max(self(), key=arg)
        # return max(flat(self()),key=arg)

    @lazyfunc
    def monadmax(self, arg=lambda x: x):
        # return max(self(),key=arg)
        return max(flat(self()), key=arg)

    @lazyfunc
    def avg(self):
        return sum(self()) / len(self())
        # return sum(flat(self()))/len(flat(self()))

    @lazyfunc
    def monadavg(self):
        # return sum(self())/len(self())
        return sum(flat(self())) / len(flat(self()))

    @lazyfunc
    def sorted(self, arg=lambda x: x):
        return sorted(self(), key=arg)
        # return sorted(flat(self()),key=arg)

    @lazyfunc
    def monadsorted(self, arg=lambda x: x):
        # return sorted(self(),key=arg)
        # return sorted(flat(self()),key=arg)
        L = sorted(flat(self()), key=arg)
        R = deepcopy(self())
        monadreplace(R, L)
        return R

    @lazyfunc
    def group(self):
        return self()

    @lazyfunc
    def distinct(self):
        S = self()
        R = type(S)()
        if hasattr(R, "append"):
            for el in S:
                if el not in R:
                    R.append(el)
            return R
        elif hasattr(R, "add"):
            for el in S:
                if el not in R:
                    R.add(el)
            return R
        elif type(R) == tuple:
            for el in S:
                if el not in R:
                    R = R + (el,)
            return R
        else:
            return type(self())(set(self()))

    @lazyfunc
    def monaddistinct(self):
        return monaddistinct(self())

    @lazyfunc
    def reduce(self, arg):
        return reduce(arg, self())
        # return sorted(flat(self()),key=arg)

    @lazyfunc
    def monadreduce(self, arg):
        return monadreduce(arg, self())
        # return sorted(flat(self()),key=arg)

    def All(self, arg):
        if type(arg) in [int, float, str]:
            a = var()
            arg = a == arg

        @lazyfunc
        def f(self):
            return all(arg(el) for el in self)
            # return all(arg(el) for el in flat(self))

        return f(self)

    def Any(self, arg):
        if type(arg) in [int, float, str]:
            a = var()
            arg = a == arg

        @lazyfunc
        def f(self):
            return any(arg(el) for el in self)
            # return any(arg(el) for el in flat(self))

        return f(self)

    def monadall(self, arg):
        if type(arg) in [int, float, str]:
            a = var()
            arg = a == arg

        @lazyfunc
        def f(self):
            return all(arg(el) for el in flat(self))

        return f(self)

    def monadany(self, arg):
        if type(arg) in [int, float, str]:
            a = var()
            arg = a == arg

        @lazyfunc
        def f(self):
            return any(arg(el) for el in flat(self))

        return f(self)


# calcfunclist=[calculus.len,calculus.max,calculus.min,calculus.sum]
calcfunclist = [
    calculus.len,
    calculus.max,
    calculus.min,
    calculus.sum,
    calculus.avg,
    calculus.monadlen,
    calculus.monadmax,
    calculus.monadmin,
    calculus.monadsum,
    calculus.monadavg,
]


# Ленивая переменная
@multiconstr
class var(expr, calculus):
    def __init__(self, value=None):
        self.value = value
        # self.addgetitem()

    def __call__(self, *args):
        if len(args) == 0:
            return self.value
        else:
            self.value = args[0]
            # self.addgetitem()
            return self.value

    # Функция - попытка добавить итератор к обычной коллекции - перебор её атрибутов.
    def addgetitem(self):
        if (
            not (hasattr(self.value, "__iter__"))
            and not (hasattr(self.value, "__getitem__"))
            and hasattr(self.value, "__dict__")
        ):
            K = list(self.value.__dict__.keys())
            setattr(
                type(self.value),
                "__iter__",
                lambda self: iter(list(self.__dict__[k] for k in K)),
            )
            setattr(
                type(self.value),
                "__next__",
                lambda self: next(list(self.__dict__[k] for k in K)),
            )

    # добавление переменной в сигнатуру функции из ленивого выражения
    def createsign(self, L=None):
        if L == None:
            L = []
        f = True
        for el in L:
            if self is el:
                f = False
        if f:
            L.append(self)
        return L

    def add(self, value):
        if hasattr(self.value, "add"):
            self.value.add(value)
        else:
            self.value.append(value)

    def append(self, value):
        if hasattr(self.value, "append"):
            self.value.append(value)
        else:
            self.value.add(value)

    def __setitem__(self, ind, value):
        self(value)

    def __deepcopy__(self, memo):
        my_copy = type(self)()
        memo[id(self)] = my_copy
        my_copy.value = deepcopy(self.value, memo)
        return my_copy

    def __iter__(self):
        if hasattr(self.value, "__iter__"):
            return iter(self.value)
        elif hasattr(self.value, "__dict__"):
            return iter(list(self.value.__dict__[k] for k in self.value.__dict__))


# используемые для сравнения типы данных
funcanytype = type(calculus.Any(var(), var() == 5))
funcalltype = type(calculus.All(var(), var() == 5))
vartype = type(var())
vargrouptype = type(var().group())
simpletypes = [int, float, str]
# agrfunctypes = [type(var().sum()),type(var().len()),type(var().min()),type(var().max())]
agrfunctypes = [
    type(var().sum()),
    type(var().len()),
    type(var().min()),
    type(var().max()),
    type(var().avg()),
    type(var().monadsum()),
    type(var().monadlen()),
    type(var().monadmin()),
    type(var().monadmax()),
    type(var().monadavg()),
]


@lazyfunc
def lazyrange(*args):
    fin = 0
    if len(args) == 1:
        start = 0
        fin = args[0]
        cond = lambda x: x < fin
        func = lambda x: x + 1
    elif len(args) == 2:
        start = args[0]
        fin = args[1]
        if start < fin:
            cond = lambda x: x < fin
            func = lambda x: x + 1
        else:
            cond = lambda x: x > fin
            func = lambda x: x - 1
    elif len(args) == 3 and type(args[2]) in [int, float]:
        start = args[0]
        fin = args[1]
        if start < fin:
            cond = lambda x: x < fin
        else:
            cond = lambda x: x > fin
        func = lambda x: x + args[2]
    elif len(args) == 3:
        start = args[0]
        fin = args[1]
        if start < fin:
            cond = lambda x: x < fin
        else:
            cond = lambda x: x > fin
        func = args[2]
    else:
        # Для последовательностей типа чисел Фибоначчи
        L = list(args[:-2])
        fin = args[-2]
        if L[0] < fin:
            cond = lambda x: x < fin
        else:
            cond = lambda x: x > fin
        func = args[-1]
        n = len(args) - 2
        while cond(L[-1]):
            r = func(*L[-n:])
            if cond(r):
                L.append(r)
            else:
                break
        return L
    # для обычных прогрессий
    n = start
    L = []
    while cond(n):
        L.append(n)
        # yield n
        n = func(n)
    return L
