from .core import var, simpletypes


# множество с операциями декартова произведения
class multset(set):
    def __mul__(self, other):
        R = set()
        # попытка присоединения кортежей справа
        for el in self:
            exL = el
            if type(exL) == tuple:
                exa = exL[0]
                for el in other:
                    exb = el
                    break
                if type(exa) == type(exb):
                    return self.specialmult(other)
                else:
                    break
        # попытка присоединения кортежей слева
        for el in other:
            exL = el
            if type(exL) == tuple:
                exb = exL[0]
                for el in self:
                    exa = el
                    break
                if type(exa) == type(exb):
                    return self.specialmultleft(other)
                else:
                    break
        # декартово произведение
        for a in self:
            for b in other:
                R.add((a, b))
        return multset(R)

    def specialmult(self, other):
        R = set()
        for a in self:
            for b in other:
                R.add((a + (b,)))
        return multset(R)

    def specialmultleft(self, other):
        R = set()
        for a in self:
            for b in other:
                R.add(((a,) + b))
        return multset(R)

    def __pow__(self, other):
        R = set()
        for a in self:
            for b in other:
                if type(a) in simpletypes:
                    a1 = (a,)
                elif type(a) in [tuple, list]:
                    a1 = a
                else:
                    a1 = tuple(el for el in a)
                    # a1=tuple(a.__dict__.values())
                if type(b) in simpletypes:
                    b1 = (b,)
                elif type(b) in [tuple, list]:
                    b1 = b
                else:
                    b1 = tuple(el for el in b)
                    # b1=tuple(b.__dict__.values())
                R.add(a1 + b1)
        return multset(R)

    def __str__(self):
        f = True
        for el in self:
            if not (type(el) == tuple and len(el) == 1):
                f = False
                break
        if f:
            return str({el[0] for el in self})  # вывод кортежа из одного элемента
        else:
            return str({el for el in self})


# создание ленивого множества с умножением (упаковка множества с умножением в ленивую переменную)
def lazyset(L=None):
    if L == None:
        L = set()
    M = multset(L)
    v = var()
    v(M)
    return v
