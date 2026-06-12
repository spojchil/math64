from p进数.p进数重构 import 多进制有理数
from p进数重构 import 多进制有理数 as dy

a = dy(1,进制=5)
assert str(6 * a) == "11"

a =  6 * a /7

assert str(a) == "11/12"

assert a.分子值 == 6
assert a.分母值 == 7
assert a.分子表示 == "11"
assert a.分母表示 == "12"

b = dy("11",7,5)
assert str(b) == "11/12"

a = dy(7,"-be",5,"abcde")
print(repr(a))
d = dy(4, 9)
d_pow_neg_rat = d ** dy(-1, 2)  # 负平方根 → 9/4
print(repr(d_pow_neg_rat))
dd = dy(1,7,3)
print(dd.浮点数(7))
print(repr(dy.有理数逼近(dd.浮点数(6),3)))

print("---------------")
ad = dy(1,4,2)
print(ad.padic表示(12))
print(ad.padic表示(40))
print(repr(dy.有理数重构(ad.padic表示(12),2)))
