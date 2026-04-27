from functools import reduce


# универсальный способ добавления элемента в коллекцию
def app(coll, el):
    if isinstance(coll, dict):
        coll[el[0]] = el[1]
        return coll
    elif type(coll) == tuple:
        R = coll + (el,)
        return R
    elif hasattr(coll, "append"):
        coll.append(el)
        return coll
    elif hasattr(coll, "add"):
        coll.add(el)
        return coll


# универсальный способ соединения коллекций:
def merge(coll1, coll2):
    if hasattr(coll1, "__add__") and hasattr(coll2, "__add__"):
        if type(coll1) == type(coll2):
            return coll1 + coll2
        else:
            return coll1 + type(coll1)(coll2)
    elif hasattr(coll1, "__or__") and hasattr(coll2, "__or__"):
        if type(coll1) == type(coll2):
            return coll1 | coll2
        else:
            return coll1 | type(coll1)(coll2)
    elif hasattr(coll1, "__add__") and hasattr(coll2, "__or__"):
        return coll1 + type(coll1)(coll2)
    elif hasattr(coll1, "__or__") and hasattr(coll2, "__add__"):
        return coll1 | type(coll1)(coll2)
    elif hasattr(coll1, "merge"):
        return coll1.merge(coll2)


# Линеаризация - превращение коллекции со множеством уровней вложенности в одномерную коллекцию
# Или уменьшение количества уровней
def flat(coll, n=0):
    # функция обычной линеаризации:
    def flat(coll):
        if isinstance(coll, dict):
            L = {}
            for k, v in coll.items():
                if isinstance(v, dict):
                    sub = flat(v)
                    for sk, sv in sub.items():
                        nk = (k,) + sk if isinstance(sk, tuple) else (k, sk)
                        L[nk] = sv
                else:
                    L[k] = v
            return L
        if type(coll) in [list, set, tuple]:
            L = type(coll)()
        else:
            L = ()
        for el in coll:
            if type(el) == str or not (hasattr(el, "__iter__")):
                L = app(L, el)
            else:
                L = merge(L, flat(el))
        return L

    def depth(coll, r=0):
        D = []
        r = r + 1
        for el in coll:
            if type(el) == str or not (hasattr(el, "__iter__")):
                D.append(r)
            else:
                D.append(depth(el, r))
        return max(D)

    if n == 0:
        return flat(coll)
    elif n > 0:
        from .core import var

        if type(coll) in [list, set, tuple]:
            L = type(coll)()
        else:
            L = ()
        for el in coll:
            if type(el) == str or not (hasattr(el, "__iter__")):
                L = app(L, el)
            else:
                L = merge(L, [var(el).flat(n - 1)])
        return L
    else:
        from .core import var

        n = depth(coll) + n - 1
        return var(coll).flat(n)


# Монадическое удаление дубликатов
def monaddistinct(coll, D=None):
    R = type(coll)()
    if D == None:
        D = []
    for el in coll:
        if not (hasattr(el, "__iter__")):
            if el not in D:
                if hasattr(R, "append"):
                    R.append(el)
                else:
                    R.add(el)
                D.append(el)
        else:
            n = monaddistinct(el, D)
            if len(n) == 1:
                if hasattr(R, "append"):
                    R.append(*n)
                else:
                    R.add(*n)
            elif len(n) > 1:
                if hasattr(R, "append"):
                    R.append(n)
                else:
                    R.add(n)
    return R


# монадическое стягивание:
def monadreduce(f, coll):
    L = []
    for el in coll:
        if not (hasattr(el, "__iter__")):
            L.append(el)
        else:
            L.append(monadreduce(f, el))
    return reduce(f, L)


# Замена элементов коллекции на элементы из списка
def monadreplace(coll, L, st=0):
    j = st
    for i in range(len(coll)):
        if not (hasattr(coll[i], "__iter__")):
            coll[i] = L[j]
            j = j + 1
        else:
            j = monadreplace(coll[i], L, j)
    return j
