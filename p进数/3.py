def zhp(decimal_value,base):
    digits = []
    while decimal_value > 0:
        digits.append(int(decimal_value % base))
        decimal_value //= base
    return ''.join(str(digit) for digit in digits[::-1])
print(-496//7,-496%7)
print(-71//7,-71%7)
print(-11//7,-11%7)
print(-2//7,-2%7)
print(-1//7,-1%7)