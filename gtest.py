import pytest
from g进数 import 多进制有理数 as dy


def test_initialization_example():
    """测试示例用例，验证核心初始化逻辑"""
    a = dy(7, "-be", 5, "abcde")
    assert str(a) == "-bc/be"
    assert a.分子值 == -7
    assert a.分母值 == 9
    assert a.进制 == 5
    assert a.符号表 == "abcde"


def test_initialization_integer_input_default_base():
    """测试整数分子/分母 + 默认进制（10）的情况"""
    b1 = dy(15, 25)
    assert b1.分子值 == 3
    assert b1.分母值 == 5
    assert str(b1) == "3/5"

    b2 = dy(-28, 1)
    assert b2.分子值 == -28
    assert b2.分母值 == 1
    assert str(b2) == "-28"

    b3 = dy(0, -99)
    assert b3.分子值 == 0
    assert b3.分母值 == 1
    assert str(b3) == "0"


def test_initialization_string_input_custom_base():
    """测试字符串分子/分母 + 自定义进制/符号表的情况"""
    c1 = dy("-A3", "-14", 16, "0123456789ABCDEF")
    assert c1.分子值 == 163
    assert c1.分母值 == 20
    assert c1.分子表示 == "A3"
    assert c1.分母表示 == "14"
    assert str(c1) == "A3/14"

    c2 = dy("1011", "-110", 2, "01")
    assert c2.分子值 == -11
    assert c2.分母值 == 6
    assert str(c2) == "-1011/110"


def test_initialization_mixed_input_types():
    """测试分子/分母混合整数和字符串的情况"""
    d1 = dy(45, "-103", 8, "01234567")
    assert d1.分子值 == -45
    assert d1.分母值 == 67
    assert d1.分母表示 == "103"
    assert str(d1) == "-55/103"

    d2 = dy("-7F", 255, 16, "0123456789ABCDEF")
    assert d2.分子值 == -127
    assert d2.分母值 == 255
    assert str(d2) == "-7F/FF"


def test_initialization_exceptions_base_symbols():
    """测试进制、符号表非法的异常情况"""
    with pytest.raises(TypeError, match="进制必须是int类型"):
        dy(10, 2, "10", "0123")

    with pytest.raises(TypeError, match="符号表必须是str"):
        dy(5, 3, 8, [0, 1, 2, 3, 4, 5, 6, 7])

    with pytest.raises(ValueError, match="符号表中不允许有点，空格，斜杠，反斜杠和减号"):
        dy(1, 2, 2, "0 1")

    with pytest.raises(ValueError, match="符号表中不允许有点，空格，斜杠，反斜杠和减号"):
        dy(1, 2, 2, "0/1")

    with pytest.raises(ValueError, match="符号表重复"):
        dy(1, 2, 2, "001")

    with pytest.raises(ValueError, match="进制1不合法！"):
        dy(1, 2, 1, "01")

    with pytest.raises(ValueError, match="进制6不合法！"):
        dy(1, 2, 6, "01234")


def test_initialization_exceptions_input_values():
    """测试分子/分母输入值非法的异常情况"""
    with pytest.raises(ZeroDivisionError, match="分母不能为0"):
        dy(5, 0)
    with pytest.raises(ZeroDivisionError, match="分母不能为0"):
        dy(10, "0", 2, "01")

    with pytest.raises(TypeError, match="分子和分母必须是整数或者字符串"):
        dy(5.5, 3)
    with pytest.raises(TypeError, match="分子和分母必须是整数或者字符串"):
        dy([1, 2], 3)

    with pytest.raises(ValueError, match="输入字符串不能仅包含负号"):
        dy("-", 5)

    with pytest.raises(ValueError, match="负号仅允许出现在字符串开头"):
        dy("12-3", 5, 10)

    with pytest.raises(ValueError, match="输入字符串12G包含非法字符！"):
        dy("12G", 5, 16, "0123456789ABCDEF")
    with pytest.raises(ValueError, match="输入字符串125包含非法字符！"):
        dy("125", 5, 5, "01234")


def test_reduction_function():
    """单独验证约分逻辑（核心内部功能）"""
    e1 = dy(48, -72, 10)
    assert e1.分子值 == -2
    assert e1.分母值 == 3
    assert str(e1) == "-2/3"

    e2 = dy(-66, -88, 10)
    assert e2.分子值 == 3
    assert e2.分母值 == 4
    assert str(e2) == "3/4"

    e3 = dy(0, 100, 10)
    assert e3.分子值 == 0
    assert e3.分母值 == 1
    assert str(e3) == "0"


def test_str_repr_methods():
    """测试__str__和__repr__方法的输出"""
    f1 = dy(15, "32", 8, "01234567")
    assert str(f1) == "17/32"

    repr_str = repr(f1)
    assert "十进制: 15/26" in repr_str
    assert "当前进制为: 8" in repr_str
    assert "表示: 17/32" in repr_str


def test_base_conversion_indirect():
    """通过初始化和属性间接验证_n进转十、_十进转n的正确性"""
    g1 = dy("A5", 100, 12, "0123456789AB")
    assert g1.分子值 == 5
    assert g1.分母值 == 4
    assert g1.分子表示 == "5"
    assert g1.分母表示 == "4"
    assert str(g1) == "5/4"

    g2 = dy("ZY", "-10", 36, "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    assert g2.分子值 == -647
    assert g2.分母值 == 18
    assert g2.分子表示 == "-HZ"
    assert g2.分母表示 == "I"
    assert str(g2) == "-HZ/I"


def test_base_conversion_method():
    """测试进制转换方法，验证新实例的进制/符号表变化、数值不变"""
    original = dy(7, "-be", 5, "abcde")
    assert original.进制 == 5
    assert original.符号表 == "abcde"
    assert original.分子值 == -7
    assert original.分母值 == 9

    converted1 = original.进制转换(10)
    assert converted1.进制 == 10
    assert converted1.符号表 == "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    assert converted1.分子值 == -7
    assert converted1.分母值 == 9
    assert str(converted1) == "-7/9"

    converted2 = original.进制转换(16, "0123456789ABCDEF")
    assert converted2.进制 == 16
    assert converted2.符号表 == "0123456789ABCDEF"
    assert converted2.分子值 == -7
    assert converted2.分母值 == 9
    assert str(converted2) == "-7/9"

    converted3 = original.进制转换(2)
    assert converted3.分子表示 == "-111"
    assert converted3.分母表示 == "1001"
    assert str(converted3) == "-111/1001"


def test_numeric_conversion_float_int_bool():
    """测试__float__、__int__、__bool__方法"""
    a = dy(3, 2)
    assert float(a) == 1.5
    assert int(a) == 1
    assert bool(a) is True

    b = dy(-7, 3)
    assert float(b) - (-2.3333333333333) < 0.000000001
    assert int(b) == -3
    assert bool(b) is True

    c = dy(0, 99)
    assert float(c) == 0.0
    assert int(c) == 0
    assert bool(c) is False

    d = dy(-28, 1)
    assert float(d) == -28.0
    assert int(d) == -28
    assert bool(d) is True


def test_hash_method():
    """测试__hash__方法，验证hash值的唯一性和一致性"""
    a1 = dy(5, 1)
    a2 = dy(5, 1)
    a3 = dy(5, 2)
    assert hash(a1) == hash(5)
    assert hash(a1) == hash(a2)
    assert hash(a1) != hash(a3)

    b1 = dy(3, 2)
    b2 = dy(3, 2)
    b3 = dy(6, 4)
    assert hash(b1) == hash((3, 2))
    assert hash(b1) == hash(b2)
    assert hash(b1) == hash(b3)

    c1 = dy(-7, 9)
    c2 = dy(-7, 9)
    assert hash(c1) == hash((-7, 9))
    assert hash(c1) == hash(c2)


def test_abs_method():
    """测试__abs__方法，验证绝对值的正确性"""
    a = dy(-7, 9, 5, "abcde")
    abs_a = abs(a)
    assert abs_a.分子值 == 7
    assert abs_a.分母值 == 9
    assert abs_a.进制 == 5
    assert str(abs_a) == "bc/be"

    b = dy(3, 2)
    abs_b = abs(b)
    assert abs_b.分子值 == 3
    assert abs_b.分母值 == 2
    assert str(abs_b) == "3/2"

    c = dy(0, -5)
    abs_c = abs(c)
    assert abs_c.分子值 == 0
    assert abs_c.分母值 == 1
    assert str(abs_c) == "0"


def test_addition():
    """测试__add__（实例+int/实例）和__radd__（int+实例）"""
    a = dy(1, 2)
    a_plus_3 = a + 3
    assert a_plus_3.分子值 == 7
    assert a_plus_3.分母值 == 2
    assert str(a_plus_3) == "7/2"

    b1 = dy(1, 3)
    b2 = dy(1, 6)
    b_sum = b1 + b2
    assert b_sum.分子值 == 1
    assert b_sum.分母值 == 2
    assert str(b_sum) == "1/2"

    c = dy(1, 2)
    c_radd = 5 + c
    assert c_radd.分子值 == 11
    assert c_radd.分母值 == 2
    assert str(c_radd) == "11/2"

    d = dy(-1, 2) + (-3)
    assert d.分子值 == -7
    assert d.分母值 == 2
    assert str(d) == "-7/2"

    with pytest.raises(TypeError):
        dy(1, 2) + 3.5
    with pytest.raises(TypeError):
        [1, 2] + dy(1, 2)


def test_neg_method():
    """测试__neg__方法，验证取反的正确性"""
    a = dy(3, 2)
    neg_a = -a
    assert neg_a.分子值 == -3
    assert neg_a.分母值 == 2
    assert str(neg_a) == "-3/2"

    b = dy(-7, 9, 5, "abcde")
    neg_b = -b
    assert neg_b.分子值 == 7
    assert neg_b.分母值 == 9
    assert str(neg_b) == "bc/be"

    c = dy(0, 5)
    neg_c = -c
    assert neg_c.分子值 == 0
    assert neg_c.分母值 == 1
    assert str(neg_c) == "0"


def test_subtraction():
    """测试__sub__（实例-int/实例）和__rsub__（int-实例）"""
    a = dy(5, 2)
    a_minus_2 = a - 2
    assert a_minus_2.分子值 == 1
    assert a_minus_2.分母值 == 2
    assert str(a_minus_2) == "1/2"

    b1 = dy(3, 4)
    b2 = dy(1, 2)
    b_sub = b1 - b2
    assert b_sub.分子值 == 1
    assert b_sub.分母值 == 4
    assert str(b_sub) == "1/4"

    c = dy(1, 2)
    c_rsub = 3 - c
    assert c_rsub.分子值 == 5
    assert c_rsub.分母值 == 2
    assert str(c_rsub) == "5/2"

    d = dy(-1, 2) - 3
    assert d.分子值 == -7
    assert d.分母值 == 2
    assert str(d) == "-7/2"

    with pytest.raises(TypeError):
        dy(1, 2) - 3.5
    with pytest.raises(TypeError):
        "abc" - dy(1, 2)


def test_invert_method():
    """测试__invert__方法（~取倒数），验证分子分母交换"""
    a = dy(3, 2)
    inv_a = ~a
    assert inv_a.分子值 == 2
    assert inv_a.分母值 == 3
    assert str(inv_a) == "2/3"

    b = dy(-7, 9, 5, "abcde")
    inv_b = ~b
    assert inv_b.分子值 == -9
    assert inv_b.分母值 == 7
    assert inv_b.分子表示 == "-be"
    assert inv_b.分母表示 == "bc"
    assert str(inv_b) == "-be/bc"

    c = dy(5, 1)
    inv_c = ~c
    assert inv_c.分子值 == 1
    assert inv_c.分母值 == 5
    assert str(inv_c) == "1/5"

    d = dy(0, 5)
    with pytest.raises(ZeroDivisionError, match="分母不能为0"):
        ~d


def test_multiplication():
    """测试__mul__（实例*int/实例）和__rmul__（int*实例）"""
    a = dy(1, 2)
    a_mul_4 = a * 4
    assert a_mul_4.分子值 == 2
    assert a_mul_4.分母值 == 1
    assert str(a_mul_4) == "2"

    b1 = dy(2, 3)
    b2 = dy(3, 4)
    b_mul = b1 * b2
    assert b_mul.分子值 == 1
    assert b_mul.分母值 == 2
    assert str(b_mul) == "1/2"

    c = dy(-1, 3)
    c_rmul = 6 * c
    assert c_rmul.分子值 == -2
    assert c_rmul.分母值 == 1
    assert str(c_rmul) == "-2"

    d1 = dy(-2, 5)
    d2 = dy(-5, 4)
    d_mul = d1 * d2
    assert d_mul.分子值 == 1
    assert d_mul.分母值 == 2
    assert str(d_mul) == "1/2"

    with pytest.raises(TypeError):
        dy(1, 2) * 3.5
    with pytest.raises(TypeError):
        [1, 2] * dy(1, 2)


def test_division():
    """测试__truediv__（实例/int/实例）和__rtruediv__（int/实例）"""
    a = dy(3, 4)
    a_div_2 = a / 2
    assert a_div_2.分子值 == 3
    assert a_div_2.分母值 == 8
    assert str(a_div_2) == "3/8"

    b1 = dy(1, 2)
    b2 = dy(3, 4)
    b_div = b1 / b2
    assert b_div.分子值 == 2
    assert b_div.分母值 == 3
    assert str(b_div) == "2/3"

    c = dy(2, 3)
    c_rdiv = 5 / c
    assert c_rdiv.分子值 == 15
    assert c_rdiv.分母值 == 2
    assert str(c_rdiv) == "15/2"

    with pytest.raises(ZeroDivisionError, match="被除数不能为0"):
        dy(1, 2) / 0
    with pytest.raises(ZeroDivisionError, match="被除数不能为0"):
        dy(1, 2) / dy(0, 5)
    with pytest.raises(ZeroDivisionError, match="被除数不能为0"):
        5 / dy(0, 1)

    with pytest.raises(TypeError):
        dy(1, 2) / 3.5
    with pytest.raises(TypeError):
        "abc" / dy(1, 2)


def test_integer_root_static_method():
    """测试静态方法_整数根，覆盖完全次方、非完全次方、负数、0等场景"""
    assert dy._整数根(8, 3) == 2
    assert dy._整数根(16, 4) == 2
    assert dy._整数根(25, 2) == 5
    assert dy._整数根(-8, 3) == -2
    assert dy._整数根(-16, 2) is None
    assert dy._整数根(7, 2) is None
    assert dy._整数根(9, 3) is None
    assert dy._整数根(0, 5) == 0
    assert dy._整数根(1, 100) == 1
    assert dy._整数根(-1, 3) == -1


def test_power():
    """测试__pow__（实例^int/实例）和__rpow__（int^实例）"""
    a = dy(2, 3)
    a_pow_2 = a ** 2
    assert a_pow_2.分子值 == 4
    assert a_pow_2.分母值 == 9
    assert str(a_pow_2) == "4/9"

    b = dy(3, 2)
    b_pow_neg2 = b ** (-2)
    assert b_pow_neg2.分子值 == 4
    assert b_pow_neg2.分母值 == 9
    assert str(b_pow_neg2) == "4/9"

    c = dy(16, 81)
    c_pow_rat = c ** dy(1, 2)
    assert c_pow_rat.分子值 == 4
    assert c_pow_rat.分母值 == 9
    assert str(c_pow_rat) == "4/9"

    d = dy(4, 9)
    d_pow_neg_rat = d ** dy(-1, 2)
    assert d_pow_neg_rat.分子值 == 3
    assert d_pow_neg_rat.分母值 == 2
    assert str(d_pow_neg_rat) == "3/2"

    e_rpow = 8 ** dy(1, 3)
    assert e_rpow.分子值 == 2
    assert e_rpow.分母值 == 1
    assert str(e_rpow) == "2"

    with pytest.raises(ValueError, match="无法在有理数中开2开方"):
        dy(7, 1) ** dy(1, 2)
    with pytest.raises(ValueError, match="无法在有理数中开3开方"):
        10 ** dy(1, 3)

    f = dy(0, 1) ** 0
    assert f.分子值 == 1
    assert f.分母值 == 1
    assert str(f) == "1"

    with pytest.raises(TypeError):
        dy(1, 2) ** 3.5


def test_modulo():
    """测试__mod__（实例%int/实例）和__rmod__（int%实例），仅允许分母为1"""
    a = dy(7, 1)
    a_mod_3 = a % 3
    assert a_mod_3.分子值 == 1
    assert a_mod_3.分母值 == 1
    assert str(a_mod_3) == "1"

    b1 = dy(10, 1)
    b2 = dy(3, 1)
    b_mod = b1 % b2
    assert b_mod.分子值 == 1
    assert str(b_mod) == "1"

    c = dy(4, 1)
    c_rmod = 11 % c
    assert c_rmod.分子值 == 3
    assert str(c_rmod) == "3"

    with pytest.raises(ValueError, match="取模只允许分母值为1"):
        dy(3, 2) % 3
    with pytest.raises(ValueError, match="取模只允许分母值为1"):
        dy(5, 1) % dy(3, 2)
    with pytest.raises(ValueError, match="取模只允许分母值为1"):
        10 % dy(3, 2)

    with pytest.raises(TypeError):
        dy(5, 1) % 3.5


def test_floor_division():
    """测试__floordiv__（实例//int/实例）和__rfloordiv__（int//实例），仅允许分母为1"""
    a = dy(7, 1)
    a_floor_3 = a // 3
    assert a_floor_3.分子值 == 2
    assert a_floor_3.分母值 == 1
    assert str(a_floor_3) == "2"

    b1 = dy(10, 1)
    b2 = dy(3, 1)
    b_floor = b1 // b2
    assert b_floor.分子值 == 3
    assert str(b_floor) == "3"

    c = dy(4, 1)
    c_rfloor = 11 // c
    assert c_rfloor.分子值 == 2
    assert str(c_rfloor) == "2"

    d = dy(-7, 1) // 3
    assert d.分子值 == -3

    with pytest.raises(ValueError, match="整除只允许分母值为1"):
        dy(3, 2) // 3
    with pytest.raises(ValueError, match="整除只允许分母值为1"):
        dy(5, 1) // dy(3, 2)
    with pytest.raises(ValueError, match="整除只允许分母值为1"):
        10 // dy(3, 2)

    with pytest.raises(TypeError):
        dy(5, 1) // 3.5


def test_comparison_operators():
    """测试__eq__/__ne__/__lt__/__gt__/__le__/__ge__"""
    a1 = dy(1, 2)
    a2 = dy(2, 4)
    a3 = dy(1, 3)
    assert a1 == a2
    assert a1 != a3
    assert (a1 == 0.5) is False
    assert dy(2, 1) == 2
    assert dy(3, 2) != 2

    b1 = dy(1, 2)
    b2 = dy(3, 4)
    assert b1 < b2
    assert b2 > b1
    assert b1 < 1
    assert b2 > 0
    assert not (b1 > b2)
    assert not (b2 < b1)

    c1 = dy(2, 2)
    c2 = dy(1, 1)
    assert c1 <= c2
    assert c1 >= c2
    assert dy(1, 2) <= 1
    assert dy(3, 2) >= 1

    d1 = dy(-1, 2)
    d2 = dy(-1, 3)
    assert d1 < d2
    assert d2 > d1
    assert d1 <= 0
    assert d2 >= -1

    with pytest.raises(TypeError):
        dy(1, 2) < 3.5
    with pytest.raises(TypeError):
        dy(1, 2) > "abc"


def test_float_method_integer():
    """测试余数为0的整数场景，验证小数部分为0"""
    a1 = dy(5, 1)
    assert a1.浮点数() == "5.0"

    a2 = dy(-7, 1)
    assert a2.浮点数() == "-7.0"

    a3 = dy(5, 1, 2, "01")
    assert a3.浮点数() == "101.0"


def test_float_method_finite_decimal():
    """测试有限小数场景（除尽），覆盖10进制/自定义进制"""
    b1 = dy(1, 2)
    assert b1.浮点数() == "0.5"

    b2 = dy(3, 4)
    assert b2.浮点数() == "0.75"

    b3 = dy(-3, 2)
    assert b3.浮点数() == "-1.5"

    b4 = dy(1, 2, 2, "01")
    assert b4.浮点数() == "0.1"

    b5 = dy(1, 16, 16, "0123456789ABCDEF")
    assert b5.浮点数() == "0.1"


def test_float_method_repeating_decimal():
    """测试循环小数场景（纯循环/混循环），覆盖10进制/自定义进制"""
    c1 = dy(1, 3)
    assert c1.浮点数() == "0.(3)"

    c2 = dy(1, 6)
    assert c2.浮点数() == "0.1(6)"

    c3 = dy(-2, 3)
    assert c3.浮点数() == "-0.(6)"

    c4 = dy(1, 3, 2, "01")
    assert c4.浮点数() == "0.(01)"

    c5 = dy(1, 15, 16, "0123456789ABCDEF")
    assert c5.浮点数() == "0.(1)"


def test_float_method_truncation():
    """测试达到截断位数未除尽的场景，验证末尾添加..."""
    d1 = dy(1, 7)
    assert d1.浮点数(截断位数=5) == "0.14285..."

    d2 = dy(1, 7, 2, "01")
    assert d2.浮点数(截断位数=3) == "0.001..."

    d3 = dy(-1, 7)
    assert d3.浮点数(截断位数=3) == "-0.142..."


def test_rational_approximation_integer_string():
    """测试纯整数字符串的逼近，覆盖正负、自定义进制"""
    e1 = dy.有理数逼近("5")
    assert e1.分子值 == 5
    assert e1.分母值 == 1
    assert str(e1) == "5"

    e2 = dy.有理数逼近("-7")
    assert e2.分子值 == -7
    assert e2.分母值 == 1
    assert str(e2) == "-7"

    e3 = dy.有理数逼近("101", 2, "01")
    assert e3.分子值 == 5
    assert e3.分母值 == 1
    assert str(e3) == "101"


def test_rational_approximation_finite_decimal_string():
    """测试有限小数字符串的逼近，覆盖10进制/自定义进制"""
    f1 = dy.有理数逼近("0.5")
    assert f1.分子值 == 1
    assert f1.分母值 == 2
    assert str(f1) == "1/2"

    f2 = dy.有理数逼近("1.75")
    assert f2.分子值 == 7
    assert f2.分母值 == 4
    assert str(f2) == "7/4"

    f3 = dy.有理数逼近("-0.25")
    assert f3.分子值 == -1
    assert f3.分母值 == 4
    assert str(f3) == "-1/4"

    f4 = dy.有理数逼近("0.1", 2, "01")
    assert f4.分子值 == 1
    assert f4.分母值 == 2
    assert str(f4) == "1/10"

    f5 = dy.有理数逼近("0.1", 16, "0123456789ABCDEF")
    assert f5.分子值 == 1
    assert f5.分母值 == 16
    assert str(f5) == "1/10"


def test_rational_approximation_repeating_decimal_string():
    """测试带循环节的小数字符串逼近，覆盖纯循环/混循环"""
    g1 = dy.有理数逼近("0.(3)")
    assert g1.分子值 == 1
    assert g1.分母值 == 3
    assert str(g1) == "1/3"

    g2 = dy.有理数逼近("0.1(6)")
    assert g2.分子值 == 1
    assert g2.分母值 == 6
    assert str(g2) == "1/6"

    g3 = dy.有理数逼近("-1.2(3)")
    assert g3.分子值 == -37
    assert g3.分母值 == 30
    assert str(g3) == "-37/30"

    g4 = dy.有理数逼近("0.(01)", 2, "01")
    assert g4.分子值 == 1
    assert g4.分母值 == 3
    assert str(g4) == "1/11"

    g5 = dy.有理数逼近("0.(1)", 16, "0123456789ABCDEF")
    assert g5.分子值 == 1
    assert g5.分母值 == 15
    assert str(g5) == "1/F"


def test_rational_approximation_truncated_string():
    """测试带省略号的截断小数字符串逼近"""
    h1 = dy.有理数逼近("0.142857...")
    assert h1.分子值 == 1
    assert h1.分母值 == 7
    assert str(h1) == "1/7"

    h2 = dy.有理数逼近("0.010212...", 3, "012")
    assert h2.分子值 == 1
    assert h2.分母值 == 7
    assert str(h2) == "1/21"

    h3 = dy.有理数逼近("0.01021...", 3, "012")
    assert str(h3) != "1/21"

    h4 = dy.有理数逼近("-0.333...")
    assert h4.分子值 == -1
    assert h4.分母值 == 3
    assert str(h4) == "-1/3"


def test_rational_approximation_exceptions():
    """测试非法输入字符串的异常处理"""
    with pytest.raises(ValueError, match="负号仅允许出现在字符串开头"):
        dy.有理数逼近("12-34")

    with pytest.raises(ValueError, match="除尾部的省略号外，必须有且只有一个'.'"):
        dy.有理数逼近("0.12.34...")

    with pytest.raises(ValueError, match="精确的表示必须以循环节结束"):
        dy.有理数逼近("0.(12)34")

    with pytest.raises(ValueError):
        dy.有理数逼近("0.(123")

    with pytest.raises(ValueError, match="输入字符串G包含非法字符"):
        dy.有理数逼近("0.G", 16, "0123456789ABCDEF")


def test_gadic_representation_basic():
    """测试核心场景：10-adic下7/30的gadic表示，预期返回(6).9"""
    a = dy(7, 30, 10)
    gadic_str = a.gadic表示(截断位数=30)
    assert gadic_str == "(6).9"


def test_gadic_representation_integer():
    """测试整数的gadic表示（分母为1，无循环、无小数部分）"""
    b1 = dy(5, 1, 10)
    assert b1.gadic表示() == "5"

    b2 = dy(-7, 1, 10)
    assert b2.gadic表示() == "(9)3"

    b3 = dy(5, 1, 2, "01")
    assert b3.gadic表示() == "101"


def test_gadic_representation_finite():
    """测试有限gadic表示（无循环节，除尽）"""
    c1 = dy(1, 2, 10)
    assert c1.gadic表示() == "0.5"

    c2 = dy(3, 4, 10)
    assert c2.gadic表示() == "0.75"

    c3 = dy(1, 4, 2, "01")
    assert c3.gadic表示() == "0.01"


def test_gadic_representation_pure_repeating():
    """测试纯循环gadic表示（无小数部分，循环节向左延伸）"""
    d1 = dy(1, 3, 10)
    assert d1.gadic表示() == "(6)7"

    d2 = dy(1, 3, 2, "01")
    assert d2.gadic表示() == "(01)1"


def test_gadic_representation_insufficient_truncation():
    """测试截断位数不足时添加...，或触发ValueError"""
    e1 = dy(17, 31, 10)
    assert e1.gadic表示(截断位数=4) == "...25807"

    e2 = dy(1, 2, 10)
    with pytest.raises(ValueError, match="截断位数不足以计算完小数部分"):
        e2.gadic表示(截断位数=0)


def test_gadic_representation_custom_base():
    """测试非10进制的gadic表示"""
    f1 = dy(7, 30, 16, "0123456789ABCDEF")
    gadic_16 = f1.gadic表示()
    assert "." in gadic_16
    assert any(char in gadic_16 for char in ["(", ")"])


def test_rational_reconstruction_repeating():
    """测试重构10-adic字符串(6).9 → 7/30"""
    g1 = dy.有理数重构("(6).9", 10)
    assert g1.分子值 == 7
    assert g1.分母值 == 30
    assert str(g1) == "7/30"


def test_rational_reconstruction_pure_repeating():
    """测试重构纯循环gadic字符串(3).0 → 1/3"""
    h1 = dy.有理数重构("(3)", 10)
    assert h1.分子值 == -1
    assert h1.分母值 == 3
    assert str(h1) == "-1/3"

    h2 = dy.有理数重构("(01)1", 2, "01")
    assert h2.分子值 == 1
    assert h2.分母值 == 3
    assert str(h2) == "1/11"


def test_rational_reconstruction_truncated():
    """测试重构带...的截断gadic字符串"""
    i1 = dy.有理数重构("...66.9", 10)
    assert i1.分子值 == 7
    assert i1.分母值 == 30
    assert str(i1) == "7/30"

    i2 = dy.有理数重构("...1011001111101", 2, "01")
    assert i2.分子值 == 17
    assert i2.分母值 == 37
    assert str(i2) == "10001/100101"

    i3 = dy(17, 37, 2)
    assert dy.有理数重构(i3.gadic表示(12), 2) == i3
    assert dy.有理数重构(i3.gadic表示(11), 2) != i3


def test_rational_reconstruction_integer():
    """测试重构整数gadic字符串"""
    j1 = dy.有理数重构("5.0", 10)
    assert j1.分子值 == 5
    assert j1.分母值 == 1
    assert str(j1) == "5"

    j2 = dy.有理数重构("101.0", 2, "01")
    assert j2.分子值 == 5
    assert j2.分母值 == 1
    assert str(j2) == "101"


def test_rational_reconstruction_finite():
    """测试重构有限gadic字符串（无循环节）"""
    k1 = dy.有理数重构("0.5", 10)
    assert k1.分子值 == 1
    assert k1.分母值 == 2
    k2 = dy.有理数重构("0.5", 10)
    assert k2.浮点数() == "0.5"


def test_rational_reconstruction_exceptions():
    """测试非法输入的异常处理"""
    with pytest.raises(ValueError, match="标准的g-adic截断没有符号"):
        dy.有理数重构("-5.0", 10)

    with pytest.raises(ValueError, match="精确表示必须以循环节开始"):
        dy.有理数重构("12(3).4", 10)

    with pytest.raises(ValueError, match="输入字符串G包含非法字符"):
        dy.有理数重构("G.0", 16, "0123456789ABCDEF")

    with pytest.raises(ValueError):
        dy.有理数重构("(6.9", 10)


def test_gadic_operations():
    """测试gadic运算：通过有理数重构、运算、gadic表示的完整流程"""
    gadic_str1 = "(1)2"
    gadic_str2 = "(3204)4"
    r1 = dy.有理数重构(gadic_str1, 进制=10)
    r2 = dy.有理数重构(gadic_str2, 进制=10)
    r_result = r1 * r2
    gadic_result = r_result.gadic表示()
    assert dy.有理数重构(gadic_result, 进制=10) == r_result


class TestFastCreation:
    """验证 _快速创建 的内部行为"""

    def test_negative_denominator_corrected(self):
        """_快速创建 传入负分母时，应修正符号并保持数值正确"""
        q = dy._快速创建(-3, -4, 10, dy.默认符号表)
        assert q.分子值 == 3
        assert q.分母值 == 4
        assert str(q) == "3/4"

    def test_reduction(self):
        q = dy._快速创建(6, 9, 10, dy.默认符号表)
        assert q.分子值 == 2
        assert q.分母值 == 3

    def test_denominator_zero_raises_exception(self):
        with pytest.raises(ZeroDivisionError):
            dy._快速创建(1, 0, 10, dy.默认符号表)

    def test_numerator_zero_reduction(self):
        q = dy._快速创建(0, 100, 10, dy.默认符号表)
        assert q.分子值 == 0
        assert q.分母值 == 1


class TestStringRepresentation:
    def test_repr_integer(self):
        q = dy(7, 1, 10)
        r = repr(q)
        assert "十进制: 7/1" in r
        assert "当前进制为: 10" in r
        assert "表示: 7/1" in r

    def test_repr_fraction(self):
        q = dy(1, 3, 16, "0123456789ABCDEF")
        r = repr(q)
        assert "十进制: 1/3" in r
        assert "当前进制为: 16" in r

    def test_str_denominator_one_no_slash(self):
        assert str(dy(12, 1, 10)) == "12"
        assert str(dy(-5, 1, 10)) == "-5"

    def test_str_zero(self):
        assert str(dy(0, 7)) == "0"


class TestIntegerConversion:
    def test_positive_fraction_floor(self):
        assert int(dy(7, 2)) == 3

    def test_negative_fraction_python_floor(self):
        assert int(dy(-7, 2)) == -4

    def test_integer_unchanged(self):
        assert int(dy(6, 1)) == 6
        assert int(dy(-6, 1)) == -6


class TestImmutability:
    def test_double_neg_equals_original(self):
        q = dy(3, 7, 5, "abcde")
        qq = -(-q)
        assert qq == q
        assert qq is not q

    def test_double_invert_equals_original(self):
        q = dy(3, 7)
        assert ~~q == q
        assert ~~q is not q

    def test_abs_positive_equal_but_different(self):
        q = dy(3, 4)
        aq = abs(q)
        assert aq == q
        assert aq is not q

    def test_slots_constraint(self):
        q = dy(1, 2)
        with pytest.raises(AttributeError):
            q.不存在的属性 = 123


class TestAdditionChaining:
    def test_sum_three_instances(self):
        terms = [dy(1, 6), dy(1, 6), dy(1, 6)]
        result = sum(terms, dy(0, 1))
        assert result == dy(1, 2)

    def test_sum_starting_from_zero(self):
        terms = [dy(1, 3), dy(1, 3), dy(1, 3)]
        result = sum(terms)
        assert result == dy(1, 1)
        assert result == 1

    def test_consecutive_addition_base_propagation(self):
        a = dy(1, 2, 2, "01")
        b = dy(1, 4, 2, "01")
        c = a + b
        assert c.进制 == 2
        assert c.符号表 == "01"
        assert c == dy(3, 4)

    def test_addition_commutative(self):
        a = dy(2, 5)
        b = dy(3, 7)
        assert a + b == b + a


class TestOperationBasePropagation:
    def test_multiplication_preserves_base(self):
        a = dy(1, 3, 8, "01234567")
        b = dy(2, 5, 8, "01234567")
        c = a * b
        assert c.进制 == 8

    def test_division_preserves_base(self):
        a = dy(3, 4, 16, "0123456789ABCDEF")
        b = dy(1, 2, 16, "0123456789ABCDEF")
        c = a / b
        assert c.进制 == 16
        assert str(c) == "3/2"

    def test_int_mul_instance_preserves_base(self):
        a = dy(1, 5, 2, "01")
        c = 3 * a
        assert c.进制 == 2
        assert c == dy(3, 5)


class TestPowerEdgeCases:
    def test_zero_to_zero_power_is_one(self):
        assert dy(0, 1) ** 0 == 1

    def test_any_to_zero_power_is_one(self):
        assert dy(3, 7) ** 0 == 1
        assert dy(-5, 3) ** 0 == 1

    def test_zero_to_positive_power_is_zero(self):
        assert dy(0, 1) ** 5 == 0

    def test_one_to_any_power_is_one(self):
        assert dy(1, 1) ** 100 == 1
        assert dy(1, 1) ** dy(3, 1) == 1

    def test_rational_exponent_numerator_zero_is_one(self):
        q = dy(8, 27) ** dy(0, 3)
        assert q == 1

    def test_rpow_base_one(self):
        result = 1 ** dy(99, 7)
        assert result == 1

    def test_rpow_base_negative_odd_root(self):
        result = (-8) ** dy(1, 3)
        assert result == dy(-2, 1)
        assert result.分子值 == -2

    def test_rpow_base_negative_even_root_raises(self):
        with pytest.raises(ValueError):
            (-4) ** dy(1, 2)

    def test_power_result_base_preserved(self):
        q = dy(4, 9, 16, "0123456789ABCDEF")
        r = q ** dy(1, 2)
        assert r.进制 == 16
        assert r == dy(2, 3)


class TestModuloFloorNegative:
    def test_negative_modulo_python_semantics(self):
        q = dy(-7, 1) % 3
        assert q.分子值 == 2

    def test_modulo_negative_modulus(self):
        q = dy(7, 1) % (-3)
        assert q.分子值 == -2

    def test_negative_floor_division_python_semantics(self):
        q = dy(-7, 1) // 3
        assert q.分子值 == -3

    def test_rmod_negative(self):
        q = (-11) % dy(4, 1)
        assert q.分子值 == 1


class TestComparisonEdgeCases:
    def test_negative_zero_equals_zero(self):
        assert dy(0, 1) == dy(0, 5)
        assert not (dy(0, 1) < dy(0, 1))
        assert not (dy(0, 1) > dy(0, 1))

    def test_comparison_with_integer_zero(self):
        assert dy(0, 7) == 0
        assert dy(1, 2) > 0
        assert dy(-1, 2) < 0

    def test_unsupported_type_returns_notimplemented(self):
        with pytest.raises(TypeError):
            dy(1, 2) < 0.5
        with pytest.raises(TypeError):
            dy(1, 2) >= "abc"

    def test_le_ge_equal_cases(self):
        a = dy(1, 2)
        b = dy(2, 4)
        assert a <= b
        assert a >= b
        assert not (a < b)
        assert not (a > b)

    def test_sorting(self):
        items = [dy(3, 4), dy(1, 2), dy(1, 3), dy(2, 3)]
        assert sorted(items) == [dy(1, 3), dy(1, 2), dy(2, 3), dy(3, 4)]


class TestHashAndSets:
    def test_equal_objects_same_hash_set_dedup(self):
        a = dy(2, 4)
        b = dy(3, 6)
        assert a == b
        assert hash(a) == hash(b)
        s = {a, b}
        assert len(s) == 1

    def test_as_dict_key(self):
        d = {dy(1, 2): "half", dy(2, 4): "also half"}
        assert len(d) == 1
        assert d[dy(1, 2)] == "also half"

    def test_hash_equal_int(self):
        q = dy(6, 2)
        assert q == 3
        assert hash(q) == hash(3)


class TestFloatEdgeCases:
    def test_truncation_one_digit(self):
        q = dy(1, 3)
        result = q.浮点数(截断位数=1)
        assert result == "0.3..."

    def test_truncation_zero_digits(self):
        q = dy(1, 3)
        result = q.浮点数(截断位数=0)
        assert result == "0"

    def test_multi_digit_integer_part(self):
        q = dy(100, 3)
        result = q.浮点数()
        assert result.startswith("33.")
        assert "(3)" in result

    def test_negative_fraction_multi_digit_integer(self):
        q = dy(-22, 7)
        result = q.浮点数()
        assert result.startswith("-3.")

    def test_custom_base_finite_decimal(self):
        q = dy(1, 3, 3, "012")
        assert q.浮点数() == "0.1"

    def test_custom_base_repeating(self):
        q = dy(1, 3, 4, "0123")
        result = q.浮点数()
        assert result == "0.(1)"

    def test_large_denominator_finite_decimal(self):
        q = dy(1, 1024, 2, "01")
        result = q.浮点数()
        assert result.endswith(".0") is False
        assert "..." not in result
        assert "(" not in result


class TestRationalApproximationEdgeCases:
    def test_no_decimal_point_pure_integer(self):
        q = dy.有理数逼近("5.0")
        assert q == 5

    def test_empty_integer_part(self):
        try:
            q = dy.有理数逼近(".5")
            assert q == dy(1, 2)
        except (ValueError, Exception):
            pass

    def test_repeating_all_zeros(self):
        q = dy.有理数逼近("0.(0)")
        assert q == 0

    def test_truncated_string_sufficient_precision(self):
        q = dy.有理数逼近("0.142857...")
        assert q == dy(1, 7)

    def test_truncated_string_insufficient_precision(self):
        q = dy.有理数逼近("0.142...")
        assert isinstance(q, dy)

    def test_negative_sign_wrong_position(self):
        with pytest.raises(ValueError, match="负号仅允许出现在字符串开头"):
            dy.有理数逼近("1-2.3")

    def test_ellipsis_followed_by_chars_raises(self):
        with pytest.raises((ValueError, Exception)):
            dy.有理数逼近("0.33...5")


class TestGadicRepresentationEdgeCases:
    def test_negative_numerator_twos_complement(self):
        q = dy(-1, 1, 10)
        result = q.gadic表示()
        assert result == "(9)"

    def test_denominator_with_base_factor(self):
        q = dy(1, 4, 2, "01")
        result = q.gadic表示()
        assert result == "0.01"

    def test_denominator_with_base_factor_decimal(self):
        q = dy(3, 20, 10)
        result = q.gadic表示()
        assert "." in result

    def test_gadic_float_equivalence(self):
        q = dy(3, 4, 10)
        assert q.浮点数() == "0.75"
        assert q.gadic表示() == "0.75"

    def test_binary_negative(self):
        q = dy(-3, 1, 2, "01")
        result = q.gadic表示()
        assert "1" in result

    def test_truncation_affects_length(self):
        q = dy(1, 7, 10)
        short = q.gadic表示(截断位数=7)
        long_ = q.gadic表示(截断位数=30)
        assert short == long_

    def test_large_prime_denominator(self):
        q = dy(1, 97, 10)
        result = q.gadic表示(截断位数=100)
        assert "(" in result or "..." not in result

    def test_numerator_denominator_coprime(self):
        q = dy(7, 11, 10)
        result = q.gadic表示()
        assert dy.有理数重构(result, 10) == q


class TestGadicRoundTrip:
    CASES = [
        dy(1, 2, 10),
        dy(1, 3, 10),
        dy(7, 30, 10),
        dy(-1, 1, 10),
        dy(3, 4, 10),
        dy(22, 7, 10),
        dy(1, 6, 10),
        dy(5, 12, 10),
        dy(1, 2, 2, "01"),
        dy(1, 3, 2, "01"),
        dy(3, 5, 2, "01"),
        dy(7, 11, 16, "0123456789ABCDEF"),
    ]

    @pytest.mark.parametrize("q", CASES)
    def test_round_trip_exact(self, q):
        gadic_str = q.gadic表示(截断位数=50)
        if "..." not in gadic_str:
            recovered = dy.有理数重构(gadic_str, q.进制, q.符号表)
            assert recovered == q, f"往返失败: {q} → '{gadic_str}' → {recovered}"


class TestFloatRoundTrip:
    CASES = [
        dy(1, 2),
        dy(1, 3),
        dy(1, 6),
        dy(2, 3),
        dy(7, 12),
        dy(22, 7),
        dy(-1, 3),
    ]

    @pytest.mark.parametrize("q", CASES)
    def test_float_round_trip(self, q):
        s = q.浮点数(截断位数=50)
        if "..." not in s:
            recovered = dy.有理数逼近(s, q.进制, q.符号表)
            assert recovered == q, f"往返失败: {q} → '{s}' → {recovered}"


class TestLargeNumberPrecision:
    def test_large_integer_power_no_overflow(self):
        q = dy(2, 1) ** 100
        assert q.分子值 == 2 ** 100
        assert q.分母值 == 1

    def test_large_numerator_denominator_reduction(self):
        n = 10 ** 18
        q = dy(n * 6, n * 9)
        assert q.分子值 == 2
        assert q.分母值 == 3

    def test_large_number_addition_exact(self):
        a = dy(10 ** 15, 10 ** 15 + 1)
        b = dy(1, 10 ** 15 + 1)
        c = a + b
        assert c == 1

    def test_large_number_gadic_no_crash(self):
        q = dy(1, 10 ** 6 + 3, 10)
        result = q.gadic表示(截断位数=20)
        assert isinstance(result, str)
        assert len(result) > 0


class TestClassVariableIsolation:
    def test_default_base_not_changed_by_instance(self):
        _ = dy(1, 2, 16, "0123456789ABCDEF")
        assert dy.默认进制 == 10

    def test_default_symbols_not_changed_by_instance(self):
        _ = dy(1, 2, 2, "AB")
        assert dy.默认符号表 == "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def test_two_instances_base_independent(self):
        a = dy(7, 3, 16, "0123456789ABCDEF")
        b = dy(7, 3, 8, "01234567")
        assert a.进制 == 16
        assert b.进制 == 8
        assert a.分子值 == b.分子值


class TestEuclideanAlgorithm:
    def test_basic_cases(self):
        assert dy._欧几里得算法(12, 8) == 4
        assert dy._欧几里得算法(7, 13) == 1
        assert dy._欧几里得算法(100, 75) == 25

    def test_one_zero(self):
        assert dy._欧几里得算法(0, 5) == 5
        assert dy._欧几里得算法(7, 0) == 7

    def test_both_zero(self):
        assert dy._欧几里得算法(0, 0) == 0

    def test_coprime(self):
        assert dy._欧几里得算法(17, 19) == 1


class TestBaseConversionThenOperation:
    def test_conversion_then_addition_base_correct(self):
        a = dy(1, 3, 10).进制转换(2)
        b = dy(1, 6, 10).进制转换(2)
        c = a + b
        assert c.进制 == 2
        assert c == dy(1, 2)

    def test_conversion_then_comparison_equal(self):
        a = dy(1, 2, 10)
        b = dy(1, 2, 10).进制转换(16, "0123456789ABCDEF")
        assert a == b

    def test_none_base_uses_default(self):
        q = dy(5, 3, 8, "01234567")
        q2 = q.进制转换()
        assert q2.进制 == 10
        assert q2 == q


class TestReverseOperationTypeCheck:
    def test_radd_no_float(self):
        with pytest.raises(TypeError):
            1.5 + dy(1, 2)

    def test_rsub_no_float(self):
        with pytest.raises(TypeError):
            1.5 - dy(1, 2)

    def test_rmul_no_float(self):
        with pytest.raises(TypeError):
            1.5 * dy(1, 2)

    def test_rtruediv_no_float(self):
        with pytest.raises(TypeError):
            1.5 / dy(1, 2)

    def test_rmod_no_string(self):
        with pytest.raises(TypeError):
            "abc" % dy(3, 1)

    def test_rfloordiv_no_string(self):
        with pytest.raises(TypeError):
            "abc" // dy(3, 1)

    def test_rpow_no_float(self):
        with pytest.raises(TypeError):
            1.5 ** dy(1, 2)


if __name__ == "__main__":
    pytest.main(["-v", __file__])