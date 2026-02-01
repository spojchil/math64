from random import randint
def gcd(m, n):
    while n != 0:
        m, n = n, m % n
    return m
m=0
#N = int(input("请输入一个正整数"))
N =59
#g= randint(3,int((N+9)**0.5))
g=3
n=g
if gcd(N,g)!=1:
    print(f"N的一个因数是{g}")
else:
    while N%n-1!=0:
        n*=g
        m+=1
    print()
    p=gcd(n**(2*m),N)
    print(f"N的一个因数是{p}")