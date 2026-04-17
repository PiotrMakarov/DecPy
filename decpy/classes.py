from itertools import product

from .core import multiconstr, expr, var, vartype
from .sets import lazyset
from .queries import lazyindex


# декоратор, добавляющий к классу экстент - ленивое множество
# (экземпляры автоматически помещаются в ленивое множество)
def queryclass(cls):
    class metaset(type):
        def __init__(self, *args):
            self.L = lazyset()
            self.qrcls = True

        def __repr__(self):
            return self.L.__repr__

        def __getitem__(self, i):
            return self.L[i]

        def __str__(self):
            return self.L.__str__()

        def __or__(self, other):
            if type(other) == vartype:
                return self.L | other()
            else:
                return self.L | other.L

        def __and__(self, other):
            return self.L & other.L

        def __mul__(self, other):
            return self.L * other.L

        def __sub__(self, other):
            return self.L - other.L

        def __xor__(self, other):
            return self.L ^ other.L

        def __pow__(self, other):
            if type(other) == expr:
                return self.L**other
            else:
                return self.L**other.L

        def __iter__(self):
            return self.L().__iter__()

        def __next__(self):
            return self.L().__next__()

    class newclass(cls, metaclass=metaset):
        def __init__(self, *args):
            super().__init__(*args)
            self.__class__.L.add(self)
            self.__class__.L.L.name = cls.__name__

        def __getattr__(self, attr):
            if attr in self.__dict__:
                return self.__dict__[attr]
            elif attr == "L":
                return tuple(self.__dict__.values())

        def __getitem__(self, ind):
            return list(self.__dict__.values())[ind]

        def __len__(self):
            return len(list(self.__dict__.values()))

    return newclass


# декоратор, добавляющий к классу экстент - любую коллекцию
def querycoll(coll=None, key=None):
    def queryclass(cls):
        class metaset(type):
            def __init__(self, *args):
                if coll == None:
                    self.L = lazyset()
                elif key == None:
                    self.L = var(coll())
                else:
                    self.L = var(coll([], key))
                self.qrcls = True

            def __repr__(self):
                return self.L.__repr__

            def __getitem__(self, i):
                return self.L[i]

            def __str__(self):
                return self.L.__str__()

            def __or__(self, other):
                if type(other) == vartype:
                    return self.L | other()
                else:
                    return self.L | other.L

            def __and__(self, other):
                return self.L & other.L

            def __mul__(self, other):
                return self.L * other.L

            def __sub__(self, other):
                return self.L - other.L

            def __xor__(self, other):
                return self.L ^ other.L

            def __pow__(self, other):
                if type(other) == expr:
                    return self.L**other
                else:
                    return self.L**other.L

            def __iter__(self):
                return self.L().__iter__()

            def __next__(self):
                return self.L().__next__()

        class newclass(cls, metaclass=metaset):
            def __init__(self, *args):
                super().__init__(*args)
                self.__class__.L.add(self)
                self.__class__.L.L.name = cls.__name__

            def __getattr__(self, attr):
                if attr in self.__dict__:
                    return self.__dict__[attr]
                elif attr == "L":
                    return tuple(self.__dict__.values())

            def __getitem__(self, ind):
                return list(self.__dict__.values())[ind]

            def __len__(self):
                return len(list(self.__dict__.values()))

        return newclass

    return queryclass


# превращение функции в предикат
class queryfun:
    def __init__(self, f):
        self.f = f
        self.L = lazyset()

    def __call__(self, *args):
        r = self.f(*args)
        self.L.add((*args, r))
        return r

    def __str__(self):
        return str(self.L)

    def __getitem__(self, ind):
        F = True
        for i in range(len(ind) - 1):
            if type(ind[i]) in [expr, lazyindex, lazyset, vartype]:
                F = False
                break
        if F:
            r = self(*ind[:-1])
            if ind[-1] not in [expr, lazyindex, lazyset, vartype]:
                return r == ind[-1]
            else:
                return lazyset({*(list(ind)[:-1]), r})
        else:
            return self.L.__getitem__(ind)

    def init(self, *args):
        for arg in product(*args):
            self(*arg)


# строка таблицы - предиката
def tablerow(header):
    class newclass:
        def __init__(self, lst):
            self.header = header
            self.L = lst
            self.qrcls = True
            # потенциально опасно, если будут изменяться значения атрибутов
            for i in range(len(header)):
                self.__dict__[header[i]] = self.L[i]

        def __getitem__(self, ind):
            return self.L[ind]

        def __getattr__(self, attr):
            if attr in self.__dict__:
                return self.__dict__[attr]
            elif attr in self.header:
                i = self.header.index(attr)
                return self.L[i]

        def __str__(self):
            return str(self.L)

        def __repr__(self):
            return str(self.L)

        def __len__(self):
            return len(list(self.L))

    return newclass


# таблица - предикат
@multiconstr
class table:
    def __init__(self, *args):
        self.L = lazyset()
        self.header = args
        self.rowclass = tablerow(self.header)
        self.allowfact = True
        self.terms = []
        self.recstart = False

    def __call__(self, *args):
        if self.allowfact:
            if len(self.header) == 0:
                if len(args) == 0:
                    return self.L
                if len(args) == 1:
                    self.L.add(args[0])
                else:
                    self.L.add(args)
                return args
            else:
                if len(args) != 0:
                    # el = tablerow(self.header,args)
                    el = self.rowclass(args)
                    self.L.add(el)
                    return el
                else:
                    return self.L
        else:
            n = len(self.L)
            while True:
                for el in self.realobj()():
                    self.L.add(el)
                if len(self.L) > n:
                    n = len(self.L)
                else:
                    break
            return self.L

    # подмена исходного множества на все добавленные и вычисленные
    def realobj(self):
        if self.allowfact:
            return self.L
        else:
            res = self.L
            for t in self.terms:
                res = res | t
            return res

    def __str__(self):
        if self.allowfact:
            return str(self.L)
        else:
            return str(self())

    def __getitem__(self, ind):
        return self.realobj()[ind]

    def __mul__(self, other):
        # if type(other)!=table:
        if type(other) != type(table()):
            return self.realobj() * other
        else:
            return self.realobj() * other.realobj()

    def __pow__(self, other):
        # if type(other)!=table:
        if type(other) != type(table()):
            return self.realobj() ** other
        else:
            return self.realobj() ** other.realobj()

    def __or__(self, other):
        # if type(other)!=table:
        if type(other) != type(table()):
            return self.realobj() | other
        else:
            return self.realobj() | other.realobj()

    def __sub__(self, other):
        return self.realobj() - other

    def __xor__(self, other):
        return self.realobj() ^ other

    def __setitem__(self, ind, value):
        self.allowfact = False
        self.terms.append(value[ind])
        return self

    def __ior__(self, other):
        self.allowfact = False
        self.terms.append(other)
        return self

    def __iter__(self):
        return self.realobj()().__iter__()

    def __next__(self):
        return self.realobj()().__next__()
