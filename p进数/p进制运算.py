class PBN:
    def __init__(self, value, base=10, digits="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        self.base = base
        self.digits = digits
        if len(digits) != len(set(digits)):
            raise ValueError("Digits must be unique")
        if isinstance(value, int):
            self.decimal_value = value
            self.sign = 1 if value >= 0 else -1
            abs_value = abs(value)
            self.p_base_str = self._decimal_to_p_base(abs_value, base)
        elif isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("Empty string invalid")
            self.sign, num_part = self._parse_sign(value)
            self._validate_num_part(num_part, base)
            self.p_base_str = ('-' if self.sign == -1 else '') + num_part
            self.decimal_value = self._p_base_to_decimal(num_part, base) * self.sign
        else:
            raise ValueError("Value must be int or str")

    def _parse_sign(self, value_str):
        sign = 1
        if value_str[0] == '-':
            sign = -1
            num_part = value_str[1:].lstrip()
        elif value_str[0] == '+':
            num_part = value_str[1:].lstrip()
        else:
            num_part = value_str
        if not num_part:
            raise ValueError("Missing numeric part")
        return sign, num_part

    def _validate_num_part(self, num_part, base):
        valid_chars = self.digits[:base]
        for c in num_part:
            if c not in valid_chars:
                raise ValueError(f"Character '{c}' not in base {base} digits")

    def _decimal_to_p_base(self, decimal_value, base):
        if base < 2 or base > len(self.digits):
            raise ValueError("Invalid base")
        if decimal_value == 0:
            return '0'
        digits = []
        while decimal_value > 0:
            digits.append(decimal_value % base)
            decimal_value //= base
        return ''.join(self.digits[i] for i in reversed(digits))

    def _p_base_to_decimal(self, num_str, base):
        decimal = 0
        for i, char in enumerate(reversed(num_str)):
            decimal += self.digits.index(char) * (base ​** i)
        return decimal

    def to_base(self, new_base):
        return PBN(self.decimal_value, new_base, self.digits)

    def __str__(self):
        return self.p_base_str

    def _convert_other(self, other):
        if isinstance(other, int):
            return PBN(other, self.base, self.digits)
        elif isinstance(other, PBN):
            return other.to_base(self.base)
        return NotImplemented

    def __add__(self, other):
        other = self._convert_other(other)
        if other is NotImplemented:
            return NotImplemented
        new_decimal = self.decimal_value + other.decimal_value
        return PBN(new_decimal, self.base, self.digits)

    __radd__ = __add__

    def __sub__(self, other):
        other = self._convert_other(other)
        if other is NotImplemented:
            return NotImplemented
        new_decimal = self.decimal_value - other.decimal_value
        return PBN(new_decimal, self.base, self.digits)

    def __rsub__(self, other):
        other = self._convert_other(other)
        if other is NotImplemented:
            return NotImplemented
        return PBN(other.decimal_value - self.decimal_value, self.base, self.digits)

    def __mul__(self, other):
        other = self._convert_other(other)
        if other is NotImplemented:
            return NotImplemented
        new_decimal = self.decimal_value * other.decimal_value
        return PBN(new_decimal, self.base, self.digits)

    __rmul__ = __mul__

    def __mod__(self, other):
        other = self._convert_other(other)
        if other is NotImplemented:
            return NotImplemented
        new_decimal = self.decimal_value % other.decimal_value
        return PBN(new_decimal, self.base, self.digits)

    def __rmod__(self, other):
        other = self._convert_other(other)
        if other is NotImplemented:
            return NotImplemented
        return PBN(other.decimal_value % self.decimal_value, self.base, self.digits)

    def __pow__(self, exponent):
        exponent = self._convert_other(exponent)
        if exponent is NotImplemented or exponent.decimal_value < 0:
            return NotImplemented
        new_decimal = self.decimal_value ​** exponent.decimal_value
        return PBN(new_decimal, self.base, self.digits)

    def __rpow__(self, base):
        base = self._convert_other(base)
        if base is NotImplemented or self.decimal_value < 0:
            return NotImplemented
        new_decimal = base.decimal_value ​** self.decimal_value
        return PBN(new_decimal, self.base, self.digits)

    def mod_pow(self, base, exponent):
        base = self._convert_other(base)
        exponent = self._convert_other(exponent)
        if exponent.decimal_value < 0:
            raise ValueError("Negative exponent not allowed")
        result = pow(base.decimal_value, exponent.decimal_value, self.decimal_value)
        return PBN(result, self.base, self.digits)

    def __floordiv__(self, other):
        other = self._convert_other(other)
        if other is NotImplemented:
            return NotImplemented
        new_decimal = self.decimal_value // other.decimal_value
        return PBN(new_decimal, self.base, self.digits)

    def __rfloordiv__(self, other):
        other = self._convert_other(other)
        if other is NotImplemented:
            return NotImplemented
        return PBN(other.decimal_value // self.decimal_value, self.base, self.digits)

    def __neg__(self):
        return PBN(-self.decimal_value, self.base, self.digits)

    def __eq__(self, other):
        other = self._convert_other(other)
        return other is not NotImplemented and self.decimal_value == other.decimal_value

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        other = self._convert_other(other)
        return other is not NotImplemented and self.decimal_value > other.decimal_value

    def __lt__(self, other):
        other = self._convert_other(other)
        return other is not NotImplemented and self.decimal_value < other.decimal_value

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return self < other or self == other


class PBNF:
    def __init__(self, numerator, denominator=1, base=10, digits="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        self.base = base
        self.digits = digits
        self.numerator, self.denominator = self._normalize(numerator, denominator)

    def _normalize(self, num, den):
        num_pbn = self._to_pbn(num)
        den_pbn = self._to_pbn(den)
        if den_pbn.decimal_value == 0:
            raise ValueError("Denominator cannot be zero")
        gcd = self._gcd(num_pbn.decimal_value, den_pbn.decimal_value)
        simplified_num = num_pbn.decimal_value // gcd
        simplified_den = den_pbn.decimal_value // gcd
        if simplified_den < 0:
            simplified_num = -simplified_num
            simplified_den = -simplified_den
        return (PBN(simplified_num, self.base, self.digits),
                PBN(simplified_den, self.base, self.digits))

    def _to_pbn(self, value):
        if isinstance(value, PBN):
            return value.to_base(self.base)
        return PBN(value, self.base, self.digits)

    @staticmethod
    def _gcd(a, b):
        while b != 0:
            a, b = b, a % b
        return a

    def __str__(self):
        return f"{self.numerator}/{self.denominator}"

    def _convert_other(self, other):
        if isinstance(other, (int, PBN)):
            return PBNF(other, 1, self.base, self.digits)
        elif isinstance(other, PBNF):
            return other
        return NotImplemented

    def __add__(self, other):
        other = self._convert_other(other)
        if other is NotImplemented:
            return NotImplemented
        new_num = (self.numerator.decimal_value * other.denominator.decimal_value +
                   self.denominator.decimal_value * other.numerator.decimal_value)
        new_den = self.denominator.decimal_value * other.denominator.decimal_value
        return PBNF(new_num, new_den, self.base, self.digits)

    __radd__ = __add__

    def __sub__(self, other):
        other = self._convert_other(other)
        if other is NotImplemented:
            return NotImplemented
        new_num = (self.numerator.decimal_value * other.denominator.decimal_value -
                   self.denominator.decimal_value * other.numerator.decimal_value)
        new_den = self.denominator.decimal_value * other.denominator.decimal_value
        return PBNF(new_num, new_den, self.base, self.digits)

    def __rsub__(self, other):
        return -self + other

    def __neg__(self):
        return PBNF(-self.numerator.decimal_value, self.denominator.decimal_value, self.base, self.digits)

    def __mul__(self, other):
        other = self._convert_other(other)
        if other is NotImplemented:
            return NotImplemented
        new_num = self.numerator.decimal_value * other.numerator.decimal_value
        new_den = self.denominator.decimal_value * other.denominator.decimal_value
        return PBNF(new_num, new_den, self.base, self.digits)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self._convert_other(other)
        if other is NotImplemented:
            return NotImplemented
        new_num = self.numerator.decimal_value * other.denominator.decimal_value
        new_den = self.denominator.decimal_value * other.numerator.decimal_value
        return PBNF(new_num, new_den, self.base, self.digits)

    def __rtruediv__(self, other):
        other = self._convert_other(other)
        if other is NotImplemented:
            return NotImplemented
        return other / self

    def __eq__(self, other):
        other = self._convert_other(other)
        return (other is not NotImplemented and
                self.numerator.decimal_value * other.denominator.decimal_value ==
                self.denominator.decimal_value * other.numerator.decimal_value)

    def __bool__(self):
        return self.numerator.decimal_value != 0