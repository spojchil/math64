import sympy
import eulerlib

e = eulerlib.numtheory.Divisors(10000)

def fenshu(m: int, n: int):
    if m * n == 0:
        return 0
    k, f = 0, fuhzhenfs(m, n)[2]
    m, n = zuijian(*fuhzhenfs(m, n)[0:2])

    while gcd(10, n) != 1:
        k -= 1
        m, n = zuijian(10 * m, n)
    if n == 1:
        return Decimal(str((10 ** k))) * Decimal((str(m / n)))
    while m % 10 == 0:
        m = int(m / 10)
        k += 1
    x0 = (m // n) + 1
    m = n - m % n

    def f10m(n1):
        phi = int(e.phi(n1))
        for i in sympy.divisors(phi):
            if pow(10, i, n1) == 1:
                return i

    v = f10m(n)
    ce = (jindu + 5) // v + 1
    i = 0
    jg = 0
    while i <= ce:
        jg += m * ((10 ** v - 1) // n) * (10 ** (i * v))
        i += 1
    if f == 0:
        jg = (jg + x0) % (10 ** jindu)
    else:
        jg = 10 ** jindu - (jg + x0) % (10 ** jindu)
    jg = Decimal(jg)
    k = Decimal(str(10 ** k))
    jg = jg * k
    return Decimal(jg)
def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return gcd, x, y

