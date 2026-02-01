class PBN:
    def __init__(self, value, base=10, jbiao="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        self.base = base
        self.jbiao = jbiao
        if len(jbiao) != len(set(jbiao)):
            raise ValueError("jbiao中标志不唯一")

        if isinstance(value, int):
            self.decimal_value = value
            self.fuhao = 1 if value >= 0 else -1
            abs_value = abs(value)
            self.p_base_value = self._decimal_to_p_base(abs_value, base)
        elif isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("空字符串")

            # 处理符号
            if stripped[0] == '-':
                self.fuhao = -1
                num_str = stripped[1:]
            else:
                self.fuhao = 1
                num_str = stripped

            # 验证数值部分
            if not num_str:
                raise ValueError("数值部分不能为空")
            if '-' in num_str or '+' in num_str:
                raise ValueError("无效符号")
            if not self.jiace(num_str, self.jbiao[:base]):
                raise ValueError("与基底不符")

            # 转换并规范化p_base_value
            abs_decimal = self._p_base_to_decimal(num_str, base)
            self.decimal_value = self.fuhao * abs_decimal
            self.p_base_value = self._decimal_to_p_base(abs_decimal, base)
            if self.fuhao == -1:
                self.p_base_value = '-' + self.p_base_value
        else:
            raise ValueError("必须是整数或者字符串")

    def _decimal_to_p_base(self, decimal_value, base):
        """将十进制数转换为p进制字符串"""
        if base < 2 or base > len(self.jbiao):
            raise ValueError("与基底不符")
        if decimal_value == 0:
            return '0'
        digits = []
        while decimal_value > 0:
            digits.append(decimal_value % base)
            decimal_value = decimal_value // base
        return ''.join(self.jbiao[i] for i in reversed(digits))

    def _p_base_to_decimal(self, p_base_str, base):
        """将p进制字符串转换为十进制数"""
        decimal_value = 0
        reversed_str = p_base_str[::-1]
        for i, char in enumerate(reversed_str):
            digit = self.jbiao.index(char)
            decimal_value += digit * (base ** i)
        return decimal_value

    @classmethod
    def jiace(cls, num_str, allowed_chars):
        """检查字符串是否仅包含允许的字符"""
        return all(c in allowed_chars for c in num_str)

    def to_base(self, new_base):
        """转换为新基数的PBN对象"""
        return PBN(self.decimal_value, new_base, self.jbiao)

    def __str__(self):
        return self.p_base_value

    def __add__(self, other):
        if not isinstance(other, (int, PBN)):
            return NotImplemented
        if isinstance(other, int):
            other = PBN(other)
        new_decimal_value = self.decimal_value + other.decimal_value
        return PBN(new_decimal_value, self.base, self.jbiao)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if not isinstance(other, (int, PBN)):
            return NotImplemented
        if isinstance(other, int):
            other = PBN(other)
        new_decimal_value = self.decimal_value - other.decimal_value
        return PBN(new_decimal_value, self.base, self.jbiao)

    def __rsub__(self, other):
        if not isinstance(other, (int, PBN)):
            return NotImplemented
        if isinstance(other, int):
            other = PBN(other)
        new_decimal_value = -self.decimal_value + other.decimal_value
        return PBN(new_decimal_value, self.base, self.jbiao)

    def __mul__(self, other):
        if not isinstance(other, (int, PBN)):
            return NotImplemented
        if isinstance(other, int):
            other = PBN(other)
        new_decimal_value = self.decimal_value * other.decimal_value
        return PBN(new_decimal_value, self.base, self.jbiao)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __mod__(self, other):
        if not isinstance(other, (int, PBN)):
            return NotImplemented
        if isinstance(other, int):
            other = PBN(other)
        new_decimal_value = self.decimal_value % other.decimal_value
        return PBN(new_decimal_value, self.base, self.jbiao)

    def __rmod__(self, other):
        if not isinstance(other, (int, PBN)):
            return NotImplemented
        if isinstance(other, int):
            other = PBN(other)
        new_decimal_value = other.decimal_value % self.decimal_value
        return PBN(new_decimal_value, self.base, self.jbiao)

    def __pow__(self, other):
        if not isinstance(other, (int, PBN)):
            return NotImplemented
        if isinstance(other, int):
            other = PBN(other)
        if other.decimal_value < 0:
            raise ValueError("指数不可以为负")
        new_decimal_value = pow(self.decimal_value, other.decimal_value)
        return PBN(new_decimal_value, self.base, self.jbiao)

    def __rpow__(self, other):
        if not isinstance(other, (int, PBN)):
            return NotImplemented
        if isinstance(other, int):
            other = PBN(other)
        if self.decimal_value < 0:
            raise ValueError("指数不可以为负")
        new_decimal_value = pow(other.decimal_value, self.decimal_value)
        return PBN(new_decimal_value, self.base, self.jbiao)

    def mod_pow(self, jishu, zhishu):
        if not isinstance(jishu, PBN):
            jishu = PBN(jishu, self.base)
        if not isinstance(zhishu, PBN):
            zhishu = PBN(zhishu, self.base)
        if zhishu.decimal_value < 0:
            raise ValueError("指数不可以为负")
        new_decimal_value = pow(jishu.decimal_value, zhishu.decimal_value, self.decimal_value)
        return PBN(new_decimal_value, self.base, self.jbiao)

    def __floordiv__(self, other):
        if not isinstance(other, (int, PBN)):
            return NotImplemented
        if isinstance(other, int):
            other = PBN(other)
        new_decimal_value = self.decimal_value // other.decimal_value
        return PBN(new_decimal_value, self.base, self.jbiao)

    def __rfloordiv__(self, other):
        if not isinstance(other, (int, PBN)):
            return NotImplemented
        if isinstance(other, int):
            other = PBN(other)
        new_decimal_value = other.decimal_value // self.decimal_value
        return PBN(new_decimal_value, self.base, self.jbiao)

    def __neg__(self):
        return PBN(-self.decimal_value, self.base,self.jbiao)

    def __eq__(self, other):
        if not isinstance(other, (int, PBN)):
            return NotImplemented
        if isinstance(other, int):
            other = PBN(other)
        return self.decimal_value == other.decimal_value

    def __ne__(self, other):
        if not isinstance(other, (int, PBN)):
            return NotImplemented
        if isinstance(other, int):
            other = PBN(other)
        return not self.decimal_value == other.decimal_value

    def __gt__(self, other):
        if not isinstance(other, (int, PBN)):
            return NotImplemented
        if isinstance(other, int):
            other = PBN(other)
        return self.decimal_value > other.decimal_value

    def __lt__(self, other):
        if not isinstance(other, (int, PBN)):
            return NotImplemented
        if isinstance(other, int):
            other = PBN(other)
        return self.decimal_value < other.decimal_value

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return self < other or self == other


# noinspection PyUnboundLocalVariable,PyTypeChecker
class PBNF:
    def __init__(self, fenzi, fenmu=1, base=10, jbiao="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        self.base = base
        self.jbiao = jbiao
        self.fenzi, self.fenmu = self._biaozhuih(fenzi, fenmu)

    def _biaozhuih(self, fenzi, fenmu):
        a, b = PBNF._zuijian(PBN(fenzi, self.base, self.jbiao), PBN(fenmu, self.base, self.jbiao))
        if b == 0:
            raise ValueError("分母不能为0")

        return a, b

    @staticmethod
    def _gcd(m, n):
        while n != 0:
            m, n = n, m % n
        return m

    @staticmethod
    def _zuijian(m, n):
        m, n = m // PBNF._gcd(m, n), n // PBNF._gcd(m, n)
        return m, n

    def __str__(self):
        return f"{self.fenzi}/{self.fenmu}"

    def __add__(self, other):
        if not isinstance(other, PBNF):
            if isinstance(other, PBN):
                other = other.decimal_value
            other = PBNF(other)
        m = (self.fenzi * other.fenmu + self.fenmu * other.fenzi).decimal_value
        n = (self.fenmu * other.fenmu).decimal_value
        return PBNF(*PBNF._zuijian(m, n), self.base, self.jbiao)

    def __radd__(self, other):
        if not isinstance(other, PBNF):
            if isinstance(other, PBN):
                base = other.base
                jbiao = other.jbiao
                other = other.decimal_value
            else:
                return self.__add__(other)
        m = (self.fenzi * other.fenmu + self.fenmu * other.fenzi).decimal_value
        n = (self.fenmu * other.fenmu).decimal_value
        return PBNF(*PBNF._zuijian(m, n), base, jbiao)

    def __sub__(self, other):
        if not isinstance(other, PBNF):
            if isinstance(other, PBN):
                other = other.decimal_value
            other = PBNF(other)
        m = (self.fenzi * other.fenmu - self.fenmu * other.fenzi).decimal_value
        n = (self.fenmu * other.fenmu).decimal_value
        return PBNF(*PBNF._zuijian(m, n), self.base, self.jbiao)

    def __neg__(self):
        return 0-self

    def __rsub__(self, other):
        if not isinstance(other, PBNF):
            if isinstance(other, PBN):
                base = other.base
                jbiao = other.jbiao
                other = other.decimal_value
            else:
                base = self.base
                jbiao = self.jbiao
                other = PBNF(other)
        m = (-self.fenzi * other.fenmu + self.fenmu * other.fenzi).decimal_value
        n = (self.fenmu * other.fenmu).decimal_value
        return PBNF(*PBNF._zuijian(m, n), base, jbiao)

    def __mul__(self, other):
        if not isinstance(other, PBNF):
            if isinstance(other, PBN):
                other = other.decimal_value
            other = PBNF(other)
        m = (self.fenzi * other.fenzi).decimal_value
        n = (self.fenmu * other.fenmu).decimal_value
        return PBNF(*PBNF._zuijian(m, n), self.base, self.jbiao)

    def __rmul__(self, other):
        if not isinstance(other, PBNF):
            if isinstance(other, PBN):
                base = other.base
                jbiao = other.jbiao
                other = other.decimal_value
            else:
                return self.__mul__(other)
        m = (self.fenzi * other.fenzi).decimal_value
        n = (self.fenmu * other.fenmu).decimal_value
        return PBNF(*PBNF._zuijian(m, n), base, jbiao)

    def __truediv__(self, other):
        if not isinstance(other, PBNF):
            if isinstance(other, PBN):
                other = other.decimal_value
            other = PBNF(other)
        m = (self.fenzi * other.fenmu).decimal_value
        n = (self.fenmu * other.fenzi).decimal_value
        return PBNF(*PBNF._zuijian(m, n), self.base, self.jbiao)

    def __rtruediv__(self, other):
        if not isinstance(other, PBNF):
            if isinstance(other, PBN):
                base = other.base
                jbiao = other.jbiao
                other = other.decimal_value
            else:
                base = self.base
                jbiao = self.jbiao
                other = PBNF(other)
        m = (self.fenmu * other.fenzi).decimal_value
        n = (self.fenzi * other.fenmu).decimal_value
        return PBNF(*PBNF._zuijian(m, n), base, jbiao)
