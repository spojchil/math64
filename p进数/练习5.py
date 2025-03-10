from p进制运算 import PBN  # 假设已实现优化后的PBN类
from typing import Tuple, List, Optional
P = 10
p = P
jindu = 30


def gcd(m, n):
    while n != 0:
        m, n = n, m % n
    return m


def zuijian(m, n):
    m, n = m // gcd(m, n), n // gcd(m, n)
    return m, n


def xsd(m, k):
    m_str = str(m)
    k = int(str(k))
    if k >= 0:
        return m_str + '0' * int(str(k))
    else:
        char_list = [char for char in m_str]
        if len(char_list) > (-k):
            char_list.insert(k, '.')
            return ''.join(char_list)
        else:
            char_list = ['0'] * (-len(char_list) + 1 - k) + char_list
            char_list.insert(1, '.')
            return ''.join(char_list)


def fuhzhenfs(m, n):
    f = 0
    if m * n < 0:
        f = 1
        if m < 0:
            m = -m
        else:
            n = -n
    elif m < 0:
        m, n = -m, -n
    return m, n, f
def mod_inverse(a, m):
    gcd, x, y = qzo(a, m)
    if gcd != 1:
        return None
    else:
        return x % m


def fs2(m, n):
    if m * n == 0:
        return 0
    k, f = 0, fuhzhenfs(m, n)[2]
    m, n = zuijian(*fuhzhenfs(m, n)[0:2])
    while gcd(p, n) != 1:
        k -= 1
        m, n = zuijian(p * m, n)
    if n == 1:
        return xsd(m // n, k)
    while m % p == 0:
        m = m // p
        k += 1
    nn = mod_inverse(n, p ** (jindu + 2))
    jg = (nn * m) % (p ** jindu)
    if f == 1:
        jg = p ** jindu - jg
    return xsd(jg, k)


kxs = 20


# p = 10
# 该代码通过避免使用浮点数的运算所造成的误差
def lfszk(a: float, k=kxs):
    a = str(a)
    char_list = [char for char in a]
    xsdwz = char_list.index('.')
    zhengs = int(''.join(char_list[:xsdwz]))
    xszf = char_list[xsdwz + 1:]
    n = int(''.join(xszf))
    m = 10 ** len(xszf)
    lfs, i = [zhengs], 1
    while n != 0 and i <= k:
        lfs.append(m // n)
        m, n = n, m % n
        i += 1
    return lfs


def biaoslb(a: list, k=kxs):
    lfs = []
    for i in range(2, min(len(a) + 1, k)):
        lfs.append(bslfs(a[:i]))
    return lfs


def bslfs(a: list):
    m, n = 1, a[-1]
    if len(a) == 2:
        na = 1 + a[1] * a[0]
        return f"{na}/{a[-1]}"
    for i in range(2, len(a)):
        m, n = n, m + n * a[-i]
    mm = m + a[0] * n
    return f"{mm}/{n}"


def find_zjfraction(fractions):
    for i in range(len(fractions) - 1):
        numerator_current, denominator_current = map(int, fractions[i].split('/'))
        numerator_next, denominator_next = map(int, fractions[i + 1].split('/'))

        # 检查条件
        if denominator_current < denominator_next:
            quotient = denominator_next // denominator_current  # 使用整除来得到商
            if quotient > 10 ** 2:
                return fractions[i]



def qzo(m:int,n:int):
    if m<n:
        m,n=n,m
        a=True
    else:
        a=False
    shang=[]
    while m%n != 0:
        shang.append(m//n)
        m,n=n,m%n
    m,n,t=1,0,n
    for i in range(1,len(shang)+1):
        m,n=n-m*shang[-i],m
    if a:
        n,m=m,n
    return t,n,m