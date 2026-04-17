# ИНСТРУМЕНТЫ ФУНКЦИОНАЛЬНОГО ПРОГРАММИРОВАНИЯ

from inspect import signature

from .core import expr, lazyfunc, var


# Карринг
def curry(f):
    def curry(f):
        return lambda *y: functor(lambda x: f(*y, x))

    if type(f) == expr:
        length = len(f.createsign())
    else:
        length = len(signature(f).parameters)
    for i in range(length - 1):
        f = curry(f)
    return f


# Аппликативный функтор
class applicative:
    def __init__(self, coll):
        self.coll = coll

    def __call__(self, arg):
        # R=type(self.coll)(f(arg) for f in self.coll)
        if type(self.coll) != set:
            R = type(self.coll)(f(arg) for f in self.coll)
        else:
            R = tuple(f(arg) for f in self.coll)
        app = False
        for el in R:
            if callable(el):
                app = True
                break
        if app:
            return applicative(R)
        else:
            return R
        # return type(self.coll)(f(arg) for f in self.coll)

    def __iter__(self):
        return iter(self.coll)


# Функтор, также работает как монада
class functor:
    def __init__(self, f):
        self.f = curry(f)

    def __call__(self, arg):
        while callable(arg):
            arg = arg()
        if not (hasattr(arg, "__iter__")):
            return self.f(arg)
        else:
            # R=(type(arg)(self(el) for el in arg))
            if type(arg) != set:
                R = type(arg)(self(el) for el in arg)
            else:
                R = tuple(self(el) for el in arg)
            app = False
            for el in R:
                if callable(el):
                    app = True
                    break
            if app:
                return applicative(R)
            else:
                return R

    def __matmul__(self, other):
        return functor(lambda *args: self(other(*args)))


# Монада. Работает как f(x,y) -> f([...],[...])
class monad:
    def __init__(self, f):
        self.f = functor(f)

    @lazyfunc
    def __call__(self, *args):
        R = self.f(args[0])
        for i in range(1, len(args)):
            R = R(args[i])
        res = var()
        res(R)
        return res
