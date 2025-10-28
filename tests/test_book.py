"""
Tests for DecPy
Author: Andrey Kvichansky, github.com/kvichans
"""

import math
from math import sqrt

import pytest

from decpy import var,lazyfun,queryclass,table

# Тесты для примеров из книги 
#   БИБЛИОТЕКА DECPY
#   Декларативное программирование на Python

NEED_CHAPS=(
    'book_1'
    'book_2'
    'book_3'
    'book_4'
#   'book_5'
#   'book_6'
)

@pytest.mark.skipif('book_1' not in NEED_CHAPS, reason='')
def test_book_1_2():
    a,b = var(2)

    pithagor=(a**2+b**2)**0.5
    a(3);b(4)
    assert pithagor==5.0
    a(5);b(12)
    assert pithagor==13.0

    assert pithagor(3,4)==5.0
    assert pithagor(5,12)==13.0

    f=a**2+a*b+a+1
    assert f(2,3)==13

@pytest.mark.skipif('book_1' not in NEED_CHAPS, reason='')
def test_book_1_3():
    a,b,c=var(3)

    f=a+b
    a(1);b(2);c(3)
    g=c+f
    assert g==6
    a(4)
    assert g==9
    
    a(1);b(2);c(3)
    g=c+f()     # See ()
    assert g==6
    a(4)
    assert g==6

@pytest.mark.skipif('book_1' not in NEED_CHAPS, reason='')
def test_book_1_4():
    def sqrt(x):
        return x**0.5
    a,b = var(2)
    pithagor=sqrt(a**2+b**2)
    assert pithagor(3,4)==5.0

    sqrt=lazyfun(math.sqrt)
    a,b = var(2)
    pithagor=sqrt(a**2+b**2)
    assert pithagor(3,4)==5.0
    
    @lazyfun
    def sqrt(x):
        return math.sqrt(x)
    a,b = var(2)
    pithagor=sqrt(a**2+b**2)
    assert pithagor(3,4)==5.0

    @lazyfun
    def exp(n):
        return 2**n
    x = var()
    f = x + exp(x)
    assert f(3)==11
    
    x = var()
    f = x + lazyfun(lambda x: 2**x)(x)
    assert f(3)==11

@pytest.mark.skipif('book_1' not in NEED_CHAPS, reason='')
def test_book_1_5_ex1_dist():
    class point:
        def __init__(self,x=0,y=0):
            self.x=x;self.y=y
    A,B=var(2)
    dist=((A.x-B.x)**2+(A.y-B.y)**2)**0.5
    
    p1=point(0,0);p2=point(3,4);p3=point(5,12)
    assert dist(p1,p2)==5.0
    assert dist(p1,p3)==13.0
    
    A(point(0,0));B(point(3,4))
    assert dist==5.0
    B(point(5,12))
    assert dist==13.0
    
    A(point(0,0))
    p=point(3,4)
    B(p)
    assert dist==5.0
    p.x=5;p.y=12
    assert dist==13.0

@pytest.mark.skipif('book_1' not in NEED_CHAPS, reason='')
def test_book_1_6_ex1_dist():
    v=var()
    mod=(v[0]**2+v[1]**2+v[2]**2)**0.5
    assert mod([2,3,6])==7.0
    assert mod([1,4,8])==9.0

@pytest.mark.skipif('book_1' not in NEED_CHAPS, reason='')
def test_book_1_7_ex1_prm():
    class point:
        def __init__(self,x=0,y=0):
            self.x=x;self.y=y
    ABC = var()
    perimeter = (((ABC[0].x-ABC[1].x)**2+(ABC[0].y-ABC[1].y)**2)**0.5+
                 ((ABC[1].x-ABC[2].x)**2+(ABC[1].y-ABC[2].y)**2)**0.5+
                 ((ABC[2].x-ABC[0].x)**2+(ABC[2].y-ABC[0].y)**2)**0.5)
    assert perimeter([point(0,0),point(0,4),point(3,0)])==12
    
    def dist(A,B):
        return ((A.x-B.x)**2+(A.y-B.y)**2)**0.5
    ABC = var()
    perimeter = dist(ABC[0],ABC[1]) + dist(ABC[1],ABC[2]) + dist(ABC[2],ABC[0])
    assert perimeter([point(0,0),point(0,4),point(3,0)])==12

@pytest.mark.skipif('book_2' not in NEED_CHAPS, reason='')
def test_book_2_1_ex1_lazy_cond():
    # Фильтрация списков и множеств
    el=var()
    L=[10,20,30,40,50]
    M=var(L)[el>15]
    assert M==[20,30,40,50]
    L.append(60)
    assert M==[20,30,40,50,60]

@pytest.mark.skipif('book_2' not in NEED_CHAPS, reason='')
def test_book_2_1_ex2_y2000():
    curr_year=2025
    class person:
        def __init__(self,name,year):
            self.name=name;self.year=year
#       def __str__(self):
#           return f"{self.name} {curr_year-self.year}"
        def __repr__(self):
           #return self.name+" "+str(curr_year-self.year)
            return f"'{self.name} {curr_year-self.year}'"
    p1=person("Василий",1990)
    p2=person("Иван",2000)
    p3=person("Мария",2001)
    people=[p1,p2,p3]
    el=var()
    youth=var(people)[el.year>=2000]
    pass;                      #print()
    pass;                      #print(f'{people =}')
    pass;                      #people_=["Василий 35","Иван 25","Мария 24"]
    pass;                      #print(f'{people_=}')
    pass;                      #assert repr(people)==repr(["Василий 35","Иван 25","Мария 24"])
    pass;                      #return 
    pass;                       assert str(people)==str(["Василий 35","Иван 25","Мария 24"])
#   assert people==["Василий 35","Иван 25","Мария 24"]  # Fail! Why?
    pass;                       assert str(youth)==str(["Иван 25","Мария 24"])
#   assert youth==["Иван 25","Мария 24"]                # Fail! Why?
    p4=person("Андрей",2024)
    people.append(p4)
    pass;                       assert str(people)==str(["Василий 35","Иван 25","Мария 24","Андрей 1"])
#   assert people==["Василий 35","Иван 25","Мария 24","Андрей 1"]
    pass;                       assert str(youth)==str(["Иван 25","Мария 24","Андрей 1"])
#   assert youth==["Иван 25","Мария 24","Андрей 1"]

@pytest.mark.skipif('book_2' not in NEED_CHAPS, reason='')
def test_book_2_1_ex3_notlazy_cond():
    el=var()
    L=[10,20,30,40,50]
    M=var(L)[el>15]()   # see ()
    assert M==[20,30,40,50]
    L.append(60)
    assert M==[20,30,40,50]

@pytest.mark.skipif('book_2' not in NEED_CHAPS, reason='')
def test_book_2_1_ex4_lazy_set_cond():
    el=var()
    L={10,20,30,40,50}
    M=var(L)[el>15]
    assert M=={20,30,40,50}
    L.add(60)
    assert M=={20,30,40,50,60}

@pytest.mark.skipif('book_2' not in NEED_CHAPS, reason='')
def test_book_2_2():
    # Запросы к запросам, множественные условия
    el=var()
    L=[10,20,30,40,50]
    M=var(L)[el>15]
    pass;                      #print(M)
    pass;                      #print(f'{M=}')
    P=M[el<45]
    assert L==[10,20,30,40,50]
    assert M==[20,30,40,50]
    pass;                      #assert M==[10,20,30,40,50]
    pass;                      #print(P)
    pass;                      #print(f'{P=}')
    pass;                      #print(P==[10,20,30,40])
    pass;                      #print(P==[20,30,40])
    pass;                      #assert P==[20,30,40]
    pass;                      #P=[20,30,40]
    pass;                      #assert P==[10,20,30,40]     # Success! Why?
    assert P==[20,30,40]
    
    L.append(35)
    assert L==[10,20,30,40,50,35]
    assert M==[20,30,40,50,35]
    assert P==[20,30,40,35]
    
    L=[10,20,30,40,50]
    el=var()
    P=var(L)[el>15][el<45]
    assert P==[20,30,40]
    L.append(35)
    assert P==[20,30,40,35]

    el=var()
    P=var(L)[el>15,el<45]
    assert P==[20,30,40]

    el=var()
    P=var(L)[(el>15) & (el<45)]
    assert P==[20,30,40]

    el=var()
    P=var(L)[(el<15) | (el>45)]
    assert P==[10,50]

@pytest.mark.skipif('book_2' not in NEED_CHAPS, reason='')
def test_book_2_3():
    # Групповые операции
    L=var([30,20,50,10,40,20])
    assert L==[30,20,50,10,40,20]
    assert L.min()==10
    assert L.max()==50
    assert L.avg()==28.333333333333332
    assert L.sum()==170
    assert L.len()==6
    assert L.sorted()==[10, 20, 20, 30, 40, 50]
    pass;                       assert L.distinct()==[10, 20, 30, 40, 50]
    assert L.distinct()==[40, 10, 50, 20, 30]

    L=var([30,20,50,10,40,20])
    a=L.min()
    b=L.max()
    c=L.avg()
    d=L.sum()
    e=L.len()
    f=L.sorted()
    g=L.distinct()
    assert L==[30,20,50,10,40,20]
    assert a==10
    assert b==50
    assert c==28.333333333333332
    assert d==170
    assert e==6
    assert f==[10,20,20,30,40,50]
    assert g==[40,10,50,20,30]
    L.append(5)
    L.append(60)
    assert L==[30,20,50,10,40,20,5,60]
    assert a==5
    assert b==60
    assert c==29.375
    assert d==235
    assert e==8
    assert f==[5,10,20,20,30,40,50,60]
    assert g==[5,40,10,50,20,60,30]
    
    L=var([1,2,3,4,5])
    assert L.sum()==15
    x,y=var(2)
    assert L.reduce(x*y)==120
    L.append(6)
    assert L==[1,2,3,4,5,6]
    assert L.sum()==21
    assert L.reduce(x*y)==720

@pytest.mark.skipif('book_2' not in NEED_CHAPS, reason='')
def test_book_2_4():
    # Новый список на основе вычислений над элементами исходного
    L=[1,2,3,4,5]
    el=var()
    M=var(L)[el**2]
    assert M==[1,4,9,16,25]

@pytest.mark.skipif('book_2' not in NEED_CHAPS, reason='')
def test_book_2_5():
    # Выборки из составной коллекции
    L=var([(6,0),(1,7),(0,4),(4,4),(1,3),(6,6),(3,4)])
    assert L==[(6,0), (1,7), (0,4), (4,4), (1,3), (6,6), (3,4)]
    el=var()
    M=L[(el[0]<=5) & (el[1]<=5)]
    assert M==[(0,4), (4,4), (1,3), (3,4)]
    P=L[(el[0]<=5) | (el[1]<=5)]
    assert P==[(6,0), (1,7), (0,4), (4,4), (1,3), (3,4)]
    R=L[el[0]**2+el[1]**2<=25]
    assert R==[(0,4), (1,3), (3,4)]
    
    class point:
        def __init__(self,x=0,y=0):
            self.x=x;self.y=y
        def __repr__(self):
            return f"({self.x},{self.y})"
        def abs(self):
            return (self.x**2+self.y**2)**0.5
    L=var([point(6,0),point(1,7),point(0,4),point(4,4),point(1,3),point(6,6),point(3,4)])
    pass;                      #print(L)
    assert L==[(6,0), (1,7), (0,4), (4,4), (1,3), (6,6), (3,4)]
    el=var()
    M=L[(el.x<=5) & (el.y<=5)]
    pass;                      #print(M)
    assert M==[(0,4), (4,4), (1,3), (3,4)]
    P=L[(el.x<=5) | (el.y<=5)]
    pass;                      #print(P)
    assert P==[(6,0), (1,7), (0,4), (4,4), (1,3), (3,4)]
    R=L[el.x**2+el.y**2<=25]
    pass;                      #print(R)
    assert R==[(0,4), (1,3), (3,4)]

    el=var()
    R=L[lazyfun(point.abs)(el)<=5]
    assert R==[(0,4), (1,3), (3,4)]

    A=point(6,0);B=point(1,7);C=point(0,4);D=point(4,4);E=point(1,3);F=point(6,6);G=point(3,4)
    L=var([A,B,C,D,E,F,G])
    assert L==[(6,0), (1,7), (0,4), (4,4), (1,3), (6,6), (3,4)]
    el=var()
    M=L[(el.x<=5) & (el.y<=5)]
    assert M==[(0,4), (4,4), (1,3), (3,4)]
    P=L[(el.x<=5) | (el.y<=5)]
    assert P==[(6,0), (1,7), (0,4), (4,4), (1,3), (3,4)]
    R=L[el.x**2+el.y**2<=25]
    assert R==[(0,4), (1,3), (3,4)]

@pytest.mark.skipif('book_2' not in NEED_CHAPS, reason='')
def test_book_2_6():
    # Запросы к классам
    @queryclass
    class point:
        def __init__(self,x=0,y=0):
            self.x=x;self.y=y
        def __repr__(self):
            return f"({self.x},{self.y})"
        def abs(self):
            return (self.x**2+self.y**2)**0.5
    A=point(6,0);B=point(1,7);C=point(0,4);D=point(4,4);E=point(1,3);F=point(6,6);G=point(3,4)
    pass;                      #print(point)#{(6,0), (1,7), (0,4), (4,4), (1,3), (6,6), (3,4)}
#?  assert point=={(6,0), (1,7), (0,4), (4,4), (1,3), (6,6), (3,4)} #?? Как узнать какое значение у point?
    el=var()
    M=point[(el.x<=5) & (el.y<=5)]
    assert M=={(0,4), (4,4), (1,3), (3,4)}
    P=point[(el.x<=5) | (el.y<=5)]
    assert P=={(6,0), (1,7), (0,4), (4,4), (1,3), (3,4)}
    R=point[lazyfun(point.abs)(el)<=5]
    assert R=={(0,4), (1,3), (3,4)}

    el=var()
    M=point[(el.x<=5) & (el.y<=5)]
    assert M=={(0,4), (4,4), (1,3), (3,4)}
    P=point[(el.x<=5) | (el.y<=5)]
    assert P=={(6,0), (1,7), (0,4), (4,4), (1,3), (3,4)}
    R=point[lazyfun(point.abs)(el)<=5]
    assert R=={(0,4), (1,3), (3,4)}
    
    curr_year=2025
    @queryclass
    class person:
        def __init__(self,name,year):
            self.name=name;self.year=year
        def __repr__(self):
            return f"'{self.name} {curr_year-self.year}'"
           #return self.name+" "+str(curr_year-self.year)
    
    person("Василий",1990)
    person("Иван",2000)
    person("Мария",2001)
    el=var()
    youth= person[el.year>=2000]
    pass;                      #print(person)   #?! Загадочный набор person
    pass;                      #print(set(person))
#?  assert set(person)=={'Василий 35', 'Мария 24', 'Иван 25'}
    pass;                      #print(youth)
#?  assert set(youth)=={'Иван 25', 'Мария 24'}
    p4=person("Андрей",2024)
    pass;                      #print(person)
    pass;                      #print(youth)
#?  assert set(youth)=={'Андрей 1', 'Иван 25', 'Мария 24'}

    point=table("x","y")
    point(6,0);point(1,7);point(0,4);point(4,4);point(1,3);point(6,6);point(3,4)
    pass;                      #print(point)
#?  assert point==?
    el=var()
    M=point[(el.x<=5) & (el.y<=5)]
    pass;                      #print(M)
#?  assert M==?
    P=point[(el.x<=5) | (el.y<=5)]
    pass;                      #print(P)
    R=point[el.x**2+el.y**2<=25]
    pass;                      #print(R)
#?  assert R==?

@pytest.mark.skipif('book_2' not in NEED_CHAPS, reason='')
def test_book_2_7():
    # Проекции и вычисления
    point=table("x","y")
    point(6,0);point(1,7);point(0,4);point(4,4);point(1,3);point(6,6);point(3,4)
    el=var()
    M=point[el.x]
    pass;                      #print(M)#{0, 1, 3, 4, 6}
    assert M=={0, 1, 3, 4, 6}
    P=point[el.y]
    pass;                      #print(P)#{0, 3, 4, 6, 7}
    assert P=={0, 3, 4, 6, 7}
    R=point[el.x**2+el.y**2]
    pass;                      #print(R)#{32, 36, 72, 10, 16, 50, 25}
    assert R=={32, 36, 72, 10, 16, 50, 25}

@pytest.mark.skipif('book_2' not in NEED_CHAPS, reason='')
def test_book_2_8():
    # Групповые операции над составной коллекцией
    point=table("x","y")
    point(6,0);point(1,7);point(0,4);point(4,4);point(1,3);point(6,6);point(3,4)
    pass;                      #print(point)
    el=var()
    Q=point[el].max((el.x**2+el.y**2)**0.5)
    pass;                      #print(Q)#(6,6)
    assert Q==(6,6)
    S=point[el].sorted((el.x**2+el.y**2)**0.5)
    pass;                      #print(S)#[(1, 3), (0, 4), (3, 4), (4, 4), (6, 0), (1, 7), (6, 6)]
    assert S==[(1, 3), (0, 4), (3, 4), (4, 4), (6, 0), (1, 7), (6, 6)]

@pytest.mark.skipif('book_3' not in NEED_CHAPS, reason='')
def test_book_3_1():
    # Альтернатива исчислению на кортежах
    L=var([(6,0),(1,7),(0,4),(4,4),(1,3),(6,6),(3,4)])
    pass;                      #print(L)
    assert L==[(6, 0), (1, 7), (0, 4), (4, 4), (1, 3), (6, 6), (3, 4)]
    x,y,d=var(3)
    pass;                      #print(L[x, None])
    assert L[x, None]=={0, 1, 3, 4, 6}
    pass;                      #print(L[None, y])
    assert L[None, y]=={0, 3, 4, 6, 7}
    pass;                      #print(L[x<=5, y<=5])
    assert L[x<=5, y<=5]=={(4, 4), (1, 3), (3, 4), (0, 4)}
    pass;                      #print(L[x, y, (x<=5) | (y<=5)])
    assert L[x, y, (x<=5) | (y<=5)]=={(4, 4), (0, 4), (3, 4), (1, 7), (6, 0), (1, 3)}
    pass;                      #print(L[x, y, x**2+y**2<=25])
    assert L[x, y, x**2+y**2<=25]=={(1, 3), (3, 4), (0, 4)}

    point=table("x","y")
    point(6,0);point(1,7);point(0,4);point(4,4);point(1,3);point(6,6);point(3,4)
    pass;                      #print(point)
#?  assert L=={(3, 4), (4, 4), (0, 4), (6, 6), (6, 0), (1, 7), (1, 3)}
    el=var()
    pass;                      #print(point[el.x])
    assert point[el.x]=={0, 1, 3, 4, 6}
    pass;                      #print(point[el.y])
    assert point[el.y]=={0, 3, 4, 6, 7}
    pass;                      #print(point[(el.x<=5) & (el.y<=5)])
    assert point[(el.x<=5) & (el.y<=5)]=={(4, 4), (1, 3), (3, 4), (0, 4)}
    pass;                      #print(point[(el.x<=5) | (el.y<=5)])
    assert point[(el.x<=5) | (el.y<=5)]=={(4, 4), (0, 4), (3, 4), (1, 7), (6, 0), (1, 3)}
    pass;                      #print(point[el.x**2+el.y**2<=25])
    assert point[el.x**2+el.y**2<=25]=={(1, 3), (3, 4), (0, 4)}

@pytest.mark.skipif('book_3' not in NEED_CHAPS, reason='')
def test_book_3_2():
    # Запросы с группировками
    sales=table("salesman","buyer","good","price","amount")
    sales("Тысяча мелочей","Петров","Шило",10,5)
    sales("Тысяча мелочей","Петров","Мыло",15,10)
    sales("Тысяча мелочей","Сидоров","Веревка",50,1)
    sales("Хозтовары","Сидоров","Мыло",20,30)
    sales("Хозтовары","Петров","Мыло",12,10)

    # Запрос №1. Вывести покупателей и покупаемые ими товары.
    el=var()
    S=sales[el.buyer,el.good]
    pass;                      #print(S)#{('Сидоров', 'Мыло'), ('Петров', 'Мыло'), ('Петров', 'Шило'), ('Сидоров', 'Веревка')}
    assert S=={('Сидоров', 'Мыло'), 
               ('Петров', 'Мыло'), 
               ('Петров', 'Шило'), 
               ('Сидоров', 'Веревка')}
    buyer,good=var(2)
    S=sales[None,buyer,good,None,None]
    assert S=={('Сидоров', 'Мыло'), 
               ('Петров', 'Мыло'), 
               ('Петров', 'Шило'), 
               ('Сидоров', 'Веревка')}

    # Запрос №2. Для каждой пары «покупатель / товар» составить списки магазинов, в которых были совершены эти покупки.
    salesman,buyer,good=var(3)
    S=sales[salesman,buyer.group(),good.group(),None,None]
    pass;                      #print(S)#{(('Хозтовары',), 'Сидоров', 'Мыло'), (('Тысяча мелочей',), 'Сидоров', 'Веревка'), (('Тысяча мелочей', 'Хозтовары'), 'Петров', 'Мыло'), (('Тысяча мелочей',), 'Петров', 'Шило')}
    assert S=={(('Хозтовары',), 'Сидоров', 'Мыло'), 
               (('Тысяча мелочей',), 'Сидоров', 'Веревка'), 
               (('Тысяча мелочей', 'Хозтовары'), 'Петров', 'Мыло'), 
               (('Тысяча мелочей',), 'Петров', 'Шило')}
    
    # Запрос №3. В каких магазинах покупатели делали свои покупки?
    salesman,buyer=var(2)
    S=sales[salesman,buyer.group(),None,None,None]
    pass;                      #print(S)#{(('Тысяча мелочей', 'Хозтовары'), 'Сидоров'), (('Тысяча мелочей', 'Тысяча мелочей', 'Хозтовары'), 'Петров')}
    assert S=={(('Тысяча мелочей', 'Хозтовары'), 'Сидоров'), 
               (('Тысяча мелочей', 'Тысяча мелочей', 'Хозтовары'), 'Петров')}

    # Запрос №4. Убрать дубликаты из предыдущего запроса.
    salesman,buyer=var(2)
    S=sales[salesman.distinct(),buyer.group(),None,None,None]
    pass;                      #print(S)#{(('Тысяча мелочей', 'Хозтовары'), 'Петров'), (('Тысяча мелочей', 'Хозтовары'), 'Сидоров')}
    assert S=={(('Тысяча мелочей', 'Хозтовары'), 'Петров'), 
               (('Тысяча мелочей', 'Хозтовары'), 'Сидоров')}
    
    # Запрос №5. Посчитать количество покупок, сделанных каждым покупателем.
    salesman,buyer=var(2)
    S=sales[salesman.len(),buyer.group(),None,None,None]
    pass;                      #print(S)#{(2, 'Сидоров'), (3, 'Петров')}
    assert S=={(2, 'Сидоров'), (3, 'Петров')}
    salesman,buyer=var(2)
    S=sales[salesman.len(),buyer.group(),None,None,None]
    T,X,Y=var(3)
    T[X,Y]|=S[Y,X]
    pass;                      #print(T)#{(2, 'Сидоров'), (3, 'Петров')}
    assert T=={(2, 'Сидоров'), (3, 'Петров')}
    
    # Запрос №6. Добавить колонку «Стоимость», которая расчитывается как произведение цены на количество
    salesman,buyer,good,price,amount=var(5)
    S=sales[salesman,buyer,good,price,amount,price*amount]
    pass;                      #print(S)#{('Хозтовары', 'Сидоров', 'Мыло', 20, 30, 600), ('Хозтовары', 'Петров', 'Мыло', 12, 10, 120), ('Тысяча мелочей', 'Петров', 'Шило', 10, 5, 50), ('Тысяча мелочей', 'Сидоров', 'Веревка', 50, 1, 50), ('Тысяча мелочей', 'Петров', 'Мыло', 15, 10, 150)}
    assert S=={('Хозтовары', 'Сидоров', 'Мыло', 20, 30, 600), 
               ('Хозтовары', 'Петров', 'Мыло', 12, 10, 120), 
               ('Тысяча мелочей', 'Петров', 'Шило', 10, 5, 50), 
               ('Тысяча мелочей', 'Сидоров', 'Веревка', 50, 1, 50), 
               ('Тысяча мелочей', 'Петров', 'Мыло', 15, 10, 150)}
    
    # Запрос №7. Для каждого продавца посчитать общую стоимость сделок.
    salesman,buyer,good,price,amount,cost=var(6)
    S=sales[salesman,buyer,good,price,amount,price*amount][None,buyer.group(),None,None,None,cost.sum()]
    pass;                      #print(S)#{('Петров', 320), ('Сидоров', 650)}
    assert S=={('Петров', 320), ('Сидоров', 650)}
    
@pytest.mark.skipif('book_3' not in NEED_CHAPS, reason='')
def test_book_3_3():
    # Запросы с кванторами
    sales=table("salesman","buyer","good","price","amount")
    sales("Рога и копыта","Иванов","Рога",10,1)
    sales("Рога и копыта","Иванов","Рога",15,2)
    sales("Рога и копыта","Петров","Рога",10,1)
    sales("Рога и копыта","Петров","Копыта",5,4)
    sales("Охотник","Сидоров","Патроны",10,20)
    
    # Запрос №1. Для каждого покупателя составить список покупок.
    buyer,good=var(2)
    S=sales[None,buyer.group(),good,None,None]
    pass;                      #print(S)#{('Петров', ('Рога', 'Копыта')), ('Сидоров', ('Патроны',)), ('Иванов', ('Рога', 'Рога'))}
    assert S=={('Петров', ('Рога', 'Копыта')), 
               ('Сидоров', ('Патроны',)), 
               ('Иванов', ('Рога', 'Рога'))}
    
    # Запрос №2. Вывести покупателей, которые покупали только рога
    buyer,good,el=var(3)
    S=sales[None,buyer.group(),good.All(el=="Рога"),None,None]
    pass;                      #print(S)#{('Иванов', ('Рога', 'Рога'))}
    assert S=={('Иванов', ('Рога', 'Рога'))}
    S=sales[None,buyer.group(),good.All("Рога"),None,None]
    assert S=={('Иванов', ('Рога', 'Рога'))}
    buyer,good=var(2)
    S=sales[None,buyer.group(),good.All("Рога"),None,None][buyer,None]
    pass;                      #print(S)#{'Иванов'}
    assert S=={'Иванов'}
    
    # Запрос №2. Вывести покупателей, которые хотя бы раз купили рога.
    buyer,good=var(2)
    S=sales[None,buyer.group(),good.Any("Рога"),None,None][buyer,None]
    pass;                      #print(S)#{'Иванов','Петров'}
    assert S=={'Иванов','Петров'}
    buyer,good=var(2)
    S=sales[None,buyer,good,None,None,good=="Рога"]
    pass;                      #print(S)#{('Иванов', 'Рога'), ('Петров', 'Рога')}
    assert S=={('Иванов', 'Рога'), ('Петров', 'Рога')}
    S=sales[None,buyer,good=="Рога",None,None]
    assert S=={('Иванов', 'Рога'), ('Петров', 'Рога')}
    S=sales[None,buyer,"Рога",None,None]
    assert S=={('Иванов', 'Рога'), ('Петров', 'Рога')}

@pytest.mark.skipif('book_3' not in NEED_CHAPS, reason='')
def test_book_3_4():
    # Объединение однотипных запросов
    salesA=table("salesman","buyer","good","price","amount")
    salesA("Тысяча мелочей","Петров","Шило",10,5)
    salesA("Тысяча мелочей","Петров","Мыло",15,10)
    salesA("Тысяча мелочей","Сидоров","Веревка",50,1)
    salesA("Хозтовары","Сидоров","Мыло",20,30)
    salesA("Хозтовары","Петров","Мыло",12,10)
    salesA("Охотник","Смирнов","Рогатка",10,20)
    salesB=table("salesman","buyer","good","price","amount")
    salesB("Рога и копыта","Иванов","Рога",10,1)
    salesB("Рога и копыта","Иванов","Рога",15,2)
    salesB("Рога и копыта","Петров","Рога",10,1)
    salesB("Рога и копыта","Петров","Копыта",5,4)
    salesB("Охотник","Сидоров","Патроны",10,20)

    buyer=var()
    A=salesA[None,buyer,None,None,None]
    pass;                      #print(A)#{'Смирнов', 'Сидоров', 'Петров'}
    assert A=={'Смирнов', 'Сидоров', 'Петров'}
    B=salesB[None,buyer,None,None,None]
    pass;                      #print(B)#{'Сидоров', 'Петров', 'Иванов'}
    assert B=={'Сидоров', 'Петров', 'Иванов'}
    pass;                      #print(A | B)#{'Иванов', 'Смирнов', 'Сидоров', 'Петров'}
    assert (A | B)=={'Иванов', 'Смирнов', 'Сидоров', 'Петров'}
    pass;                      #print(A & B)#{'Сидоров', 'Петров'}
    assert (A & B)=={'Сидоров', 'Петров'}
    pass;                      #print(A - B)#{'Смирнов'}
    assert (A - B)=={'Смирнов'}
    pass;                      #print(B - A)#{'Иванов'}
    assert (B - A)=={'Иванов'}
    pass;                      #print(B ^ A)#{'Смирнов', 'Иванов'}
    assert (A ^ B)=={'Смирнов', 'Иванов'}

    salesA=var({("salesman","buyer","good","price","amount"),
                ("Тысяча мелочей","Петров","Шило",10,5),
                ("Тысяча мелочей","Петров","Мыло",15,10),
                ("Тысяча мелочей","Сидоров","Веревка",50,1),
                ("Хозтовары","Сидоров","Мыло",20,30),
                ("Хозтовары","Петров","Мыло",12,10),
                ("Охотник","Смирнов","Рогатка",10,20)})
    
    salesB=var({("salesman","buyer","good","price","amount"),
                ("Рога и копыта","Иванов","Рога",10,1),
                ("Рога и копыта","Иванов","Рога",15,2),
                ("Рога и копыта","Петров","Рога",10,1),
                ("Рога и копыта","Петров","Копыта",5,4),
                ("Охотник","Сидоров","Патроны",10,20)})
    buyer=var()
    A=salesA[None,buyer,None,None,None]
    pass;                      #print(A)
    B=salesB[None,buyer,None,None,None]
    pass;                      #print(B)
    pass;                      #print(A | B)
    assert (A | B)=={'Иванов', 'Смирнов', 'Сидоров', 'Петров', 'buyer'}

@pytest.mark.skipif('book_3' not in NEED_CHAPS, reason='')
def test_book_3_5():
    # Запросы к нескольким таблицам
    person=table("name","year")
    person("Иванов",2000)
    person("Петров",2005)
    person("Сидоров",2010)
    pass;                      #print(person)
    dog=table("name","year","owner")
    dog("Шарик",2010,"Иванов")
    dog("Жучка",2015,"Петров")
    dog("Бобик",2020,"Иванов")
    pass;                      #print(dog)

    L=person*dog
    pass;                      #print(L)
    assert L=={(('Петров', 2005), ('Бобик', 2020, 'Иванов')), 
               (('Иванов', 2000), ('Бобик', 2020, 'Иванов')), 
               (('Сидоров', 2010), ('Шарик', 2010, 'Иванов')), 
               (('Сидоров', 2010), ('Жучка', 2015, 'Петров')), 
               (('Петров', 2005), ('Жучка', 2015, 'Петров')), 
               (('Петров', 2005), ('Шарик', 2010, 'Иванов')), 
               (('Иванов', 2000), ('Жучка', 2015, 'Петров')), 
               (('Иванов', 2000), ('Шарик', 2010, 'Иванов')), 
               (('Сидоров', 2010), ('Бобик', 2020, 'Иванов'))}
    el=var()
    L=(person*dog)[el[0].name==el[1].owner]
    pass;                      #print(L)
    assert L=={(('Иванов', 2000), ('Бобик', 2020, 'Иванов')), 
               (('Иванов', 2000), ('Шарик', 2010, 'Иванов')), 
               (('Петров', 2005), ('Жучка', 2015, 'Петров'))}
    p,d=var(2)
    L=(person*dog)[p,d,p.name==d.owner]
    assert L=={(('Иванов', 2000), ('Бобик', 2020, 'Иванов')), 
               (('Иванов', 2000), ('Шарик', 2010, 'Иванов')), 
               (('Петров', 2005), ('Жучка', 2015, 'Петров'))}

    L=person**dog
    pass;                      #print(L)
    assert L=={('Сидоров', 2010, 'Шарик', 2010, 'Иванов'), 
               ('Иванов', 2000, 'Жучка', 2015, 'Петров'), 
               ('Иванов', 2000, 'Бобик', 2020, 'Иванов'), 
               ('Петров', 2005, 'Шарик', 2010, 'Иванов'), 
               ('Петров', 2005, 'Жучка', 2015, 'Петров'), 
               ('Сидоров', 2010, 'Жучка', 2015, 'Петров'), 
               ('Иванов', 2000, 'Шарик', 2010, 'Иванов'), 
               ('Петров', 2005, 'Бобик', 2020, 'Иванов'), 
               ('Сидоров', 2010, 'Бобик', 2020, 'Иванов')}
    name1,name2,year1,year2,owner=var(5)
    L=(person**dog)[name1,year1,name2,year2,owner,name1==owner]
    pass;                      #print(L)
    assert L=={('Иванов', 2000, 'Шарик', 2010, 'Иванов'), 
               ('Петров', 2005, 'Жучка', 2015, 'Петров'), 
               ('Иванов', 2000, 'Бобик', 2020, 'Иванов')}
    L=(person**dog)[name1,year1,name2,year2,name1]
    pass;                      #print(L)
    assert L=={('Иванов', 2000, 'Бобик', 2020), 
               ('Петров', 2005, 'Жучка', 2015), 
               ('Иванов', 2000, 'Шарик', 2010)}

@pytest.mark.skipif('book_3' not in NEED_CHAPS, reason='')
def test_book_3_6():
    # Гибридный вариант запроса исчислений на кортежах и доменах
    @queryclass
    class point:
        def __init__(self,x=0,y=0):
            self.x=x;self.y=y
        def __repr__(self):
            return "("+str(self.x)+","+str(self.y)+")"
    
    def dist(A,B):
        return ((A.x-B.x)**2+(A.y-B.y)**2)**0.5
    
    A=point(6,0);B=point(1,7);C=point(0,4);D=point(4,4);F=point(1,3);G=point(6,6);H=point(3,4)
    pass;                      #print(point)
    a,b,d,el=var(4)
    L=(point*point)[a,b,dist(a,b)][a.group(),None,d.sum()]
    pass;                      #print(L)
    assert L=={((6,0), 37.116515667815484), 
               ((1,3), 22.474462989731865), 
               ((3,4), 18.44717052842777), 
               ((0,4), 25.112149093806213), 
               ((1,7), 28.711814403387066), 
               ((6,6), 29.688505128985025), 
               ((4,4), 19.705481427033433)}
    L=(point*point)[a,b,dist(a,b)][a.group(),None,d.sum()].min(el[1])
    pass;                      #print(L)
    assert L==((3,4), 18.44717052842777)
    L=(point*point)[a,b,dist(a,b)][a.group(),None,d.sum()].min(el[1])[0]    #? ToDo timeit!
    assert L==H#(3,4)
    
    L=[A,B,C,D,F,G,H]
    R=min((sum(dist(a,b) for b in L),a) for a in L)[1]                      #? ToDo timeit!
    pass;                      #print(R)
    assert R==H#(3,4)

@pytest.mark.skipif('book_4' not in NEED_CHAPS, reason='')
def test_book_4_2():
    # Родословное древо – постановка задачи
    @queryclass
    class person:
        def __init__(self,name,age,mother=None,father=None):
            self.name=name;self.age=age;self.mother=mother;self.father=father
        def __repr__(self):
            return f"{self.name} {self.age}"
    m31=person("Ману",1931)             # p0
    a50=person("Адам",1950,None,m31)    # p1
    e51=person("Ева",1951)              # p2
    t52=person("Татьяна",1952)          # p3
    g70=person("Глеб",1970,e51,a50)     # p4
    o70=person("Ольга",1970,t52)        # p5
    i90=person("Иван",1990,o70,g70)     # p6
    m91=person("Мария",1991)            # p7
    v00=person("Василий",2000,m91,i90)  # p8
    s12=person("Cветлана",2012,m91,i90) # p9
    e12=person("Елена",2012,o70,g70)    # p10
    r24=person("Роман",2024,e12)        # p11
    k12=person("Кирилл",2012)           # p12
    v24=person("Виталий",2024,m91,k12)  # p13
    k24=person("Ксения",2024)           # p14

    X,Y,el=var(3)
    mother = (person*person)[X,Y,X.mother==Y]
    pass;                      #print(mother)#{(Василий 2000, Мария 1991), (Роман 2024, Елена 2012), (Виталий 2024, Мария 1991), (Елена 2012, Ольга 1970), (Иван 1990, Ольга 1970), (Cветлана 2012, Мария 1991), (Глеб 1970, Ева 1951), (Ольга 1970, Татьяна 1952)}
    assert mother=={(v00, m91), 
                    (r24, e12), 
                    (v24, m91), 
                    (e12, o70), 
                    (i90, o70), 
                    (s12, m91), 
                    (g70, e51), 
                    (o70, t52)}

    # Понятие 1. Мать
    X,Y,el=var(3)
    mother = (person*person)[X,Y,X.mother==Y]
    pass;                      #print(mother[X,m91])#{(Cветлана 2012, Мария 1991), (Виталий 2024, Мария 1991), (Василий 2000, Мария 1991)}
    assert mother[X,m91]=={(v00, m91), 
                           (v24, m91), 
                           (s12, m91)}
    assert mother[X,m91][X,None]=={v00,v24,s12}
    
    father = (person*person)[X,Y,X.father==Y]
    # Понятие 2. Родитель
    parent = mother | father
    pass;                      #print(parent)#{(Cветлана 2012, Мария 1991), (Глеб 1970, Адам 1950), (Ольга 1970, Татьяна 1952), (Василий 2000, Иван 1990), (Адам 1950, Ману 1931), (Василий 2000, Мария 1991), (Елена 2012, Ольга 1970), (Cветлана 2012, Иван 1990), (Виталий 2024, Кирилл 2012), (Виталий 2024, Мария 1991), (Роман 2024, Елена 2012), (Иван 1990, Ольга 1970), (Глеб 1970, Ева 1951), (Елена 2012, Глеб 1970), (Иван 1990, Глеб 1970)}
    assert parent=={(s12, m91), 
                    (g70, a50), 
                    (o70, t52), 
                    (v00, i90), 
                    (a50, m31), 
                    (v00, m91), 
                    (e12, o70), 
                    (s12, i90), 
                    (v24, k12), 
                    (v24, m91), 
                    (r24, e12), 
                    (i90, o70), 
                    (g70, e51), 
                    (e12, g70), 
                    (i90, g70)}

@pytest.mark.skipif('book_4' not in NEED_CHAPS, reason='')
def test_book_4_3():
    # Ограничения и хороший стиль
    @queryclass
    class person:
        def __init__(self,name,age,mother=None,father=None):
            self.name=name;self.age=age;self.mother=mother;self.father=father
        def __repr__(self):
            return f"{self.name} {self.age}"
    m31=person("Ману",1931)             # p0
    a50=person("Адам",1950,None,m31)    # p1
    e51=person("Ева",1951)              # p2
    t52=person("Татьяна",1952)          # p3
    g70=person("Глеб",1970,e51,a50)     # p4
    o70=person("Ольга",1970,t52)        # p5
    i90=person("Иван",1990,o70,g70)     # p6
    m91=person("Мария",1991)            # p7
    v00=person("Василий",2000,m91,i90)  # p8
    s12=person("Cветлана",2012,m91,i90) # p9
    e12=person("Елена",2012,o70,g70)    # p10
    r24=person("Роман",2024,e12)        # p11
    k12=person("Кирилл",2012)           # p12
    v24=person("Виталий",2024,m91,k12)  # p13
    k24=person("Ксения",2024)           # p14
    
    # Понятие 3. Ребенок
    # |= «равно по определению» для var
    # |= «доп-определение» для table
    X,Y=var(2)
    mother,father,parent,child=table(4)
    mother |= (person*person)[X,Y,X.mother==Y]
    father |= (person*person)[X,Y,X.father==Y]
    parent |= mother
    parent |= father
    child[X,Y] |= parent[Y,X]
    pass;                      #print(child)#{(Елена 2012, Роман 2024), (Ману 1931, Адам 1950), (Кирилл 2012, Виталий 2024), (Татьяна 1952, Ольга 1970), (Глеб 1970, Иван 1990), (Ольга 1970, Елена 2012), (Ольга 1970, Иван 1990), (Мария 1991, Виталий 2024), (Иван 1990, Cветлана 2012), (Иван 1990, Василий 2000), (Мария 1991, Василий 2000), (Мария 1991, Cветлана 2012), (Адам 1950, Глеб 1970), (Ева 1951, Глеб 1970), (Глеб 1970, Елена 2012)}
    assert set(child)=={(e12, r24), #? set()?
                        (m31, a50), 
                        (k12, v24), 
                        (t52, o70), 
                        (g70, i90), 
                        (o70, e12), 
                        (o70, i90), 
                        (m91, v24), 
                        (i90, s12), 
                        (i90, v00), 
                        (m91, v00), 
                        (m91, s12), 
                        (a50, g70), 
                        (e51, g70), 
                        (g70, e12)}
    
    # Понятие 4. Ближайший родственник – родитель или ребенок.
    near=table()
    near |= parent | child
    pass;                      #print(near[i90,X][None,X])
    assert near[i90,X][None,X]=={o70, g70, s12, v00}
    
@pytest.mark.skipif('book_4' not in NEED_CHAPS, reason='')
def test_book_4_4():
    @queryclass
    class person:
        def __init__(self,name,age,mother=None,father=None):
            self.name=name;self.age=age;self.mother=mother;self.father=father
        def __repr__(self):
            return f"{self.name} {self.age}"
    X,Y=var(2)
    mother,father,parent,child,near=table(5)
    mother |= (person*person)[X,Y,X.mother==Y]
    father |= (person*person)[X,Y,X.father==Y]
    parent |= mother | father
    child[X,Y] |= parent[Y,X]
    near |= parent | child
            
    m31=person("Ману",1931)             # p0
    a50=person("Адам",1950,None,m31)    # p1
    e51=person("Ева",1951)              # p2
    t52=person("Татьяна",1952)          # p3
    g70=person("Глеб",1970,e51,a50)     # p4
    o70=person("Ольга",1970,t52)        # p5
    i90=person("Иван",1990,o70,g70)     # p6
    m91=person("Мария",1991)            # p7
    v00=person("Василий",2000,m91,i90)  # p8
    s12=person("Cветлана",2012,m91,i90) # p9
    e12=person("Елена",2012,o70,g70)    # p10
    r24=person("Роман",2024,e12)        # p11
    k12=person("Кирилл",2012)           # p12
    v24=person("Виталий",2024,m91,k12)  # p13
    k24=person("Ксения",2024)           # p14
    # Понятие 5. Бабушка и дедушка
    X,Y,Z=var(3)
    grandparent = table()
#   grandparent |= (parent**parent)[X,Z,Z,Y][X,None,Y]  #? Печатает set()
    grandparent[X,Z] |= parent[X,Y]**parent[Y,Z]
    pass;                      #print(grandparent)#{(Елена 2012, Татьяна 1952), (Василий 2000, Глеб 1970), (Иван 1990, Адам 1950), (Cветлана 2012, Ольга 1970), (Иван 1990, Татьяна 1952), (Роман 2024, Ольга 1970), (Иван 1990, Ева 1951), (Елена 2012, Ева 1951), (Василий 2000, Ольга 1970), (Глеб 1970, Ману 1931), (Роман 2024, Глеб 1970), (Елена 2012, Адам 1950), (Cветлана 2012, Глеб 1970)}
    assert set(grandparent)=={(e12, t52), 
                              (v00, g70), 
                              (i90, a50), 
                              (s12, o70), 
                              (i90, t52), 
                              (r24, o70), 
                              (i90, e51), 
                              (e12, e51), 
                              (v00, o70), 
                              (g70, m31), 
                              (r24, g70), 
                              (e12, a50), 
                              (s12, g70)}

    X,Y,Z,U=var(4)
    mother,father,parent,child,near,grandparent=table(6)
    mother[X,Y] |= (person*person)[X,Y,X.mother==Y]
    father[X,Y] |= (person*person)[X,Y,X.father==Y]
    parent[X,Y] |= mother[X,Y] | father[X,Y]
    near[X,Y] |= parent[X,Y] | parent[Y,X]
    grandparent[X,Y] |= parent[X,Z]**parent[Z,Y]
    pass;                      #print(near[i90,X][None,X])
    assert near[i90,X][None,X]=={s12,v00,g70,o70}
    pass;                      #print(grandparent[i90,X][None,X])
    assert grandparent[i90,X][None,X]=={a50,t52,e51}
    
    # Понятие 6. Брат и сестра
    brother = table()
    brother[X,Y] |= parent[X,Z]**parent[Y,Z]
    pass;                      #print(brother[v00,X][None,X])
    assert brother[v00,X][None,X]=={s12,v00,v24}
    brother = table()
    brother[X,Y,X!=Y] |= parent[X,Z]**parent[Y,Z]
    assert brother[v00,X][None,X]=={s12,v24}
    brother = table()
    brother[X,Y] |= parent[X,Z]**parent[Y,Z,X!=Y]
    assert brother[v00,X][None,X]=={s12,v24}
    rodbrat = table()
    rodbrat[X,Y,X!=Y] |= mother[X,Z]**mother[Y,Z]**father[X,U]**father[Y,U]
    assert rodbrat[v00,X][None,X]=={s12}

@pytest.mark.skipif('book_4' not in NEED_CHAPS, reason='')
def test_book_4_5():
    # Рекурсивные определения
    @queryclass
    class person:
        def __init__(self,name,age,mother=None,father=None):
            self.name=name;self.age=age;self.mother=mother;self.father=father
        def __repr__(self):
            return f"{self.name} {self.age}"
    X,Y,Z,U=var(4)
    mother,father,parent,child,near,grandparent=table(6)
    mother[X,Y] |= (person*person)[X,Y,X.mother==Y]
    father[X,Y] |= (person*person)[X,Y,X.father==Y]
    parent[X,Y] |= mother[X,Y] | father[X,Y]
    near[X,Y] |= parent[X,Y] | parent[Y,X]
    grandparent[X,Y] |= parent[X,Z]**parent[Z,Y]
            
    m31=person("Ману",1931)             # p0
    a50=person("Адам",1950,None,m31)    # p1
    e51=person("Ева",1951)              # p2
    t52=person("Татьяна",1952)          # p3
    g70=person("Глеб",1970,e51,a50)     # p4
    o70=person("Ольга",1970,t52)        # p5
    i90=person("Иван",1990,o70,g70)     # p6
    m91=person("Мария",1991)            # p7
    v00=person("Василий",2000,m91,i90)  # p8
    s12=person("Cветлана",2012,m91,i90) # p9
    e12=person("Елена",2012,o70,g70)    # p10
    r24=person("Роман",2024,e12)        # p11
    k12=person("Кирилл",2012)           # p12
    v24=person("Виталий",2024,m91,k12)  # p13
    k24=person("Ксения",2024)           # p14
    
    # Понятие 7. Предок.
    ancestor = table()
    ancestor[X,Y] |= parent[X,Y] | parent[X,Z]**ancestor[Z,Y]
    pass;                      #print(ancestor[v00,X][None,X])#{Ману 1931, Мария 1991, Глеб 1970, Ева 1951, Адам 1950, Ольга 1970, Иван 1990, Татьяна 1952}
    assert ancestor[v00,X][None,X]=={m31, m91, g70, e51, a50, o70, i90, t52}
    
    # Понятие 8. Кровные родственники.
    rod = table()
    rod[X,Y,X!=Y] |= ancestor[X,Y] | ancestor[Y,X] | ancestor[X,Z]**ancestor[Y,Z]
    pass;                      #print(rod[i90,X][None,X])#{Ману 1931, Татьяна 1952, Роман 2024, Адам 1950, Ольга 1970, Глеб 1970, Cветлана 2012, Василий 2000, Ева 1951, Елена 2012}
    assert rod[i90,X][None,X]=={m31, t52, r24, a50, o70, g70, s12, v00, e51, e12}
    
    # Понятие 9. Свояк
    svoy = table()
    svoy[X,Y,X!=Y] |= rod[X,Y] | rod[X,Z]**svoy[Z,Y]
    pass;                      #print(svoy[r24,X][None,X]-rod[r24,X][None,X])#{Кирилл 2012, Мария 1991, Виталий 2024}
    assert svoy[r24,X][None,X]-rod[r24,X][None,X]=={k12, m91, v24}
    
    # Понятие 10. Поколение.
    generation = table()
    generation[X,Y] |= (parent[X,Z]**parent[Y,Z] | 
                        parent[Z,X]**parent[Z,Y] | 
                        parent[X,Z]**parent[Y,U]**generation[Z,U] | 
                        parent[Z,X]**parent[U,Y]**generation[Z,U])
    pass;                      #print(generation[e12,X][None,X])#{Кирилл 2012, Мария 1991, Елена 2012, Иван 1990}
    assert generation[e12,X][None,X]=={k12, m91, e12, i90}
    assert generation[r24,X][None,X]=={r24, v00, v24, s12}

###########
# Run as 
#   py13 -m pytest -q tests/test_book.py
#   uv run  pytest -q tests/test_book.py