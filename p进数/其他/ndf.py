from p进数.p进数重构 import 多进制有理数 as dy

def 使用1():
    def f(x):
        return x - (x*x+1)/(2*x)
    a=dy(2,进制=5)
    for i in range(6):
        a=f(a)
        print(repr(a))
        print(a.padic表示())
        print((a**2).padic表示())
使用1()

a = dy.有理数重构("(1)2")
b = dy.有理数重构("(3204)4")
print((a*b).padic表示()) # 输出 (7292)8

print(repr(a)) #十进制: 8/9, 当前进制为: 10, 表示: 8/9
print(repr(b)) #十进制: 884/1111, 当前进制为: 10, 表示: 884/1111
print(repr(a*b)) #十进制: 7072/9999, 当前进制为: 10, 表示: 7072/9999
print(dy.有理数重构((a*b).padic表示()) == a*b) #True

w1 = dy.有理数逼近("3.14159...")
w2 = dy.有理数逼近("1.4142...")
w3 = dy.有理数逼近("2.71828...")
print(repr(w1))
print(repr(w2**2))
print(repr(w3))
print("-------------")
w3 = dy(3, 进制=7)
for i in range(5):
    w3 = (w3 ** 2 + 2)/ (2 * w3)
    print(w3.padic表示())

    print(repr(w3))
    print(float(w3))
    a=dy.有理数重构(w3.padic表示(),7)
    print(repr(a))
    print(float(a))

print(repr(dy(314,100).padic表示()))