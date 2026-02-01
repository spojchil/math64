import pytest
from p进数重构 import 多进制有理数 as dy


def test_初始化_示例用例():
    """测试示例用例，验证核心初始化逻辑"""
    a = dy(7, "-be", 5, "abcde")
    # 验证字符串表示
    assert str(a) == "-bc/be"
    # 验证数值属性
    assert a.分子值 == -7
    assert a.分母值 == 9
    # 验证进制和符号表
    assert a.进制 == 5
    assert a.符号表 == "abcde"


def test_初始化_整数输入_默认进制():
    """测试整数分子/分母 + 默认进制（10）的情况"""
    # 正分子正分母
    b1 = dy(15, 25)
    assert b1.分子值 == 3
    assert b1.分母值 == 5
    assert str(b1) == "3/5"

    # 负分子、分母为1（简化显示）
    b2 = dy(-28, 1)
    assert b2.分子值 == -28
    assert b2.分母值 == 1
    assert str(b2) == "-28"

    # 分子为0（约分后分母为1，正负为1）
    b3 = dy(0, -99)
    assert b3.分子值 == 0
    assert b3.分母值 == 1
    assert str(b3) == "0"
    assert b3._正负 == 1  # 验证内部正负号


def test_初始化_字符串输入_自定义进制():
    """测试字符串分子/分母 + 自定义进制/符号表的情况"""
    # 16进制，符号表自定义（0-9A-F）
    c1 = dy("A3", "14", 16, "0123456789ABCDEF")
    # A3(16) = 10*16 +3 = 163；14(16)=1*16+4=20 → 163/20（不可约分）
    assert c1.分子值 == 163
    assert c1.分母值 == 20
    assert c1.分子表示 == "A3"
    assert c1.分母表示 == "14"
    assert str(c1) == "A3/14"

    # 2进制，带负号的字符串分母
    c2 = dy("1011", "-110", 2, "01")
    # 1011(2)=11；-110(2)=-6 → 约分后 -11/6
    assert c2.分子值 == -11
    assert c2.分母值 == 6
    assert str(c2) == "-1011/110"


def test_初始化_混合输入类型():
    """测试分子/分母混合整数和字符串的情况"""
    # 分子整数，分母字符串（8进制）
    d1 = dy(45, "-103", 8, "01234567")
    # -103(8) = -(1*64 +0*8 +3) = -67 → 45/-67 → 约分后 -45/67
    assert d1.分子值 == -45
    assert d1.分母值 == 67
    assert d1.分母表示 == "103"
    assert str(d1) == "-55/103"  # 45转8进制是55

    # 分子字符串，分母整数（16进制）
    d2 = dy("-7F", 255, 16, "0123456789ABCDEF")
    # -7F(16) = -127；255=FF(16) → -127/255（不可约分）
    assert d2.分子值 == -127
    assert d2.分母值 == 255
    assert str(d2) == "-7F/FF"


def test_初始化_异常场景_进制和符号表():
    """测试进制、符号表非法的异常情况"""
    # 进制非整数
    with pytest.raises(TypeError, match="进制必须是int类型"):
        dy(10, 2, "10", "0123")

    # 符号表非字符串
    with pytest.raises(TypeError, match="符号表必须是str"):
        dy(5, 3, 8, [0, 1, 2, 3, 4, 5, 6, 7])

    # 符号表含非法字符（点、空格、斜杠等）
    with pytest.raises(ValueError, match="符号表中不允许有点，空格，斜杠，反斜杠和减号"):
        dy(1, 2, 2, "0 1")  # 含空格
    with pytest.raises(ValueError, match="符号表中不允许有点，空格，斜杠，反斜杠和减号"):
        dy(1, 2, 2, "0/1")  # 含斜杠

    # 符号表有重复字符
    with pytest.raises(ValueError, match="符号表重复"):
        dy(1, 2, 2, "001")

    # 进制小于2
    with pytest.raises(ValueError, match="进制1不合法！"):
        dy(1, 2, 1, "01")

    # 进制大于符号表长度
    with pytest.raises(ValueError, match="进制6不合法！"):
        dy(1, 2, 6, "01234")  # 符号表长度5，进制6


def test_初始化_异常场景_输入值():
    """测试分子/分母输入值非法的异常情况"""
    # 分母为0
    with pytest.raises(ZeroDivisionError, match="分母不能为0"):
        dy(5, 0)
    with pytest.raises(ZeroDivisionError, match="分母不能为0"):
        dy(10, "0", 2, "01")

    # 输入类型非int/str
    with pytest.raises(TypeError, match="分子和分母必须是整数或者字符串"):
        dy(5.5, 3)  # 浮点数分子
    with pytest.raises(TypeError, match="分子和分母必须是整数或者字符串"):
        dy([1, 2], 3)  # 列表分子

    # 字符串仅含负号
    with pytest.raises(ValueError, match="输入字符串不能仅包含负号"):
        dy("-", 5)

    # 负号出现在字符串中间
    with pytest.raises(ValueError, match="负号仅允许出现在字符串开头"):
        dy("12-3", 5, 10)

    # 字符串含非法字符（超出当前进制的符号）
    with pytest.raises(ValueError, match="输入字符串12G包含非法字符！"):
        dy("12G", 5, 16, "0123456789ABCDEF")  # 16进制合法字符到F，G非法
    with pytest.raises(ValueError, match="输入字符串125包含非法字符！"):
        dy("125", 5, 5, "01234")  # 5进制合法字符0-4，5非法


def test_约分功能():
    """单独验证约分逻辑（核心内部功能）"""
    # 分子分母有公约数
    e1 = dy(48, -72, 10)
    assert e1.分子值 == -2  # 48/-72 → 约分后 -2/3
    assert e1.分母值 == 3
    assert str(e1) == "-2/3"

    # 负负得正，且约分
    e2 = dy(-66, -88, 10)
    assert e2.分子值 == 3  # -66/-88 → 3/4
    assert e2.分母值 == 4
    assert str(e2) == "3/4"

    # 分子为0，约分后分母为1
    e3 = dy(0, 100, 10)
    assert e3.分子值 == 0
    assert e3.分母值 == 1
    assert str(e3) == "0"


def test_str_repr():
    """测试__str__和__repr__方法的输出"""
    f1 = dy(15, "32", 8, "01234567")
    # 15(10)=17(8)，18(8)=16(10) → 15/16（不可约分）
    assert str(f1) == "17/32"
    # 验证repr的格式和内容
    repr_str = repr(f1)
    assert "十进制: 15/26" in repr_str
    assert "当前进制为: 8" in repr_str
    assert "表示: 17/32" in repr_str


def test_进制转换_间接验证():
    """通过初始化和属性间接验证_n进转十、_十进转n的正确性"""
    # 验证12进制转换：符号表0-9AB
    g1 = dy("A5", 100, 12, "0123456789AB")
    # A5(12) = 10*12 +5 = 125；100(10)=84(12) → 125/100 = 5/4
    assert g1.分子值 == 5
    assert g1.分母值 == 4
    # 5转12进制是5，4转12进制是4 → 分子表示5，分母表示4
    assert g1.分子表示 == "5"
    assert g1.分母表示 == "4"
    assert str(g1) == "5/4"

    # 验证36进制转换：符号表0-9A-Z
    g2 = dy("ZY", "-10", 36, "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    # Z=35, Y=34 → ZY=35*36 +34=1294；-10(36)=-36 → 1294/-36 = -647/18
    assert g2.分子值 == -647
    assert g2.分母值 == 18
    # 647转36进制：36*17=612，647-612=35 → 17是H，35是Z → HZ
    assert g2.分子表示 == "-HZ"
    # 18转36进制是18 → I
    assert g2.分母表示 == "I"
    assert str(g2) == "-HZ/I"

def test_进制转换():
    """测试进制转换方法，验证新实例的进制/符号表变化、数值不变"""
    # 初始实例：10进制，7/-9（对应示例中的-7/9）
    original = dy(7, "-be", 5, "abcde")  # 分子值-7，分母值9，5进制，符号表abcde
    assert original.进制 == 5
    assert original.符号表 == "abcde"
    assert original.分子值 == -7
    assert original.分母值 == 9

    # 转换为10进制，默认符号表
    converted1 = original.进制转换(10)
    assert converted1.进制 == 10
    assert converted1.符号表 == "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    assert converted1.分子值 == -7  # 数值不变
    assert converted1.分母值 == 9
    assert str(converted1) == "-7/9"  # 10进制表示

    # 转换为16进制，自定义符号表
    converted2 = original.进制转换(16, "0123456789ABCDEF")
    assert converted2.进制 == 16
    assert converted2.符号表 == "0123456789ABCDEF"
    assert converted2.分子值 == -7
    assert converted2.分母值 == 9
    assert str(converted2) == "-7/9"  # 7和9在16进制中还是7、9

    # 转换为2进制，验证字符串表示
    converted3 = original.进制转换(2)
    assert converted3.分子表示 == "-111"  # -7的2进制是-111
    assert converted3.分母表示 == "1001"  # 9的2进制是1001
    assert str(converted3) == "-111/1001"

# ------------------------------ 测试 数值类型转换 方法 ------------------------------
def test_数值类型转换_float_int_bool():
    """测试__float__、__int__、__bool__方法"""
    # 基础用例：3/2（10进制）
    a = dy(3, 2)
    assert float(a) == 1.5  # __float__
    assert int(a) == 1      # __int__：整除 3//2=1
    assert bool(a) is True  # __bool__：分子非零为True

    # 负数用例：-7/3
    b = dy(-7, 3)
    assert float(b) - (-2.3333333333333) < 0.000000001  # 浮点近似值
    assert int(b) == -3                     # -7//3=-3（Python整除规则）
    assert bool(b) is True

    # 分子为0的边界用例
    c = dy(0, 99)
    assert float(c) == 0.0
    assert int(c) == 0
    assert bool(c) is False  # 分子为0，bool为False

    # 分母为1的用例：-28/1
    d = dy(-28, 1)
    assert float(d) == -28.0
    assert int(d) == -28
    assert bool(d) is True

# ------------------------------ 测试 __hash__ 方法 ------------------------------
def test_hash方法():
    """测试__hash__方法，验证hash值的唯一性和一致性"""
    # 分母为1时，hash(分子值)
    a1 = dy(5, 1)
    a2 = dy(5, 1)
    a3 = dy(5, 2)
    assert hash(a1) == hash(5)          # 分母为1，hash等于分子的hash
    assert hash(a1) == hash(a2)         # 相同值的实例hash相同
    assert hash(a1) != hash(a3)         # 不同值的实例hash不同

    # 分母不为1时，hash((分子值, 分母值))
    b1 = dy(3, 2)
    b2 = dy(3, 2)
    b3 = dy(6, 4)  # 约分后也是3/2，hash应相同
    assert hash(b1) == hash((3, 2))
    assert hash(b1) == hash(b2)
    assert hash(b1) == hash(b3)  # 约分后值相同，hash相同

    # 负数用例
    c1 = dy(-7, 9)
    c2 = dy(-7, 9)
    assert hash(c1) == hash((-7, 9))
    assert hash(c1) == hash(c2)

# ------------------------------ 测试 __abs__ 方法 ------------------------------
def test_abs方法():
    """测试__abs__方法，验证绝对值的正确性"""
    # 负数实例
    a = dy(-7, 9, 5, "abcde")
    abs_a = abs(a)
    assert abs_a.分子值 == 7    # 分子取绝对值
    assert abs_a.分母值 == 9    # 分母不变
    assert abs_a.进制 == 5      # 进制不变
    assert str(abs_a) == "bc/be"  # 7的5进制是bc，9的5进制是be

    # 正数实例（绝对值等于自身）
    b = dy(3, 2)
    abs_b = abs(b)
    assert abs_b.分子值 == 3
    assert abs_b.分母值 == 2
    assert str(abs_b) == "3/2"

    # 分子为0（绝对值还是0）
    c = dy(0, -5)
    abs_c = abs(c)
    assert abs_c.分子值 == 0
    assert abs_c.分母值 == 1
    assert str(abs_c) == "0"

# ------------------------------ 测试 加法运算 __add__/__radd__ ------------------------------
def test_加法运算():
    """测试__add__（实例+int/实例）和__radd__（int+实例）"""
    # 实例 + int
    a = dy(1, 2)  # 1/2
    a_plus_3 = a + 3
    assert a_plus_3.分子值 == 7  # 1 + 2*3 =7，分母=2 → 7/2
    assert a_plus_3.分母值 == 2
    assert str(a_plus_3) == "7/2"
    assert a_plus_3.进制 == 10  # 保持原进制

    # 实例 + 实例（同进制）
    b1 = dy(1, 3)  # 1/3
    b2 = dy(1, 6)  # 1/6
    b_sum = b1 + b2
    assert b_sum.分子值 == 1  # (1*6 + 3*1)=9，分母=18 → 9/18=1/2
    assert b_sum.分母值 == 2
    assert str(b_sum) == "1/2"

    # int + 实例（__radd__）
    c = dy(1, 2)
    c_radd = 5 + c
    assert c_radd.分子值 == 11  # 1 + 2*5 =11，分母=2 → 11/2
    assert c_radd.分母值 == 2
    assert str(c_radd) == "11/2"

    # 负数加法
    d = dy(-1, 2) + (-3)
    assert d.分子值 == -7  # -1 + 2*(-3) =-7，分母=2 → -7/2
    assert d.分母值 == 2
    assert str(d) == "-7/2"

    # 不支持的类型（返回NotImplemented，触发TypeError）
    with pytest.raises(TypeError):
        dy(1,2) + 3.5  # 浮点数不支持
    with pytest.raises(TypeError):
        [1,2] + dy(1,2)  # 列表不支持

# ------------------------------ 测试 __neg__ 方法（取反） ------------------------------
def test_neg方法():
    """测试__neg__方法，验证取反的正确性"""
    # 正数取反
    a = dy(3, 2)
    neg_a = -a
    assert neg_a.分子值 == -3
    assert neg_a.分母值 == 2
    assert str(neg_a) == "-3/2"

    # 负数取反
    b = dy(-7, 9, 5, "abcde")
    neg_b = -b
    assert neg_b.分子值 == 7
    assert neg_b.分母值 == 9
    assert str(neg_b) == "bc/be"

    # 分子为0取反（还是0）
    c = dy(0, 5)
    neg_c = -c
    assert neg_c.分子值 == 0
    assert neg_c.分母值 == 1
    assert str(neg_c) == "0"

# ------------------------------ 测试 减法运算 __sub__/__rsub__ ------------------------------
def test_减法运算():
    """测试__sub__（实例-int/实例）和__rsub__（int-实例）"""
    # 实例 - int
    a = dy(5, 2)  # 5/2
    a_minus_2 = a - 2
    assert a_minus_2.分子值 == 1  # 5 - 2*2 =1，分母=2 → 1/2
    assert a_minus_2.分母值 == 2
    assert str(a_minus_2) == "1/2"

    # 实例 - 实例
    b1 = dy(3, 4)  # 3/4
    b2 = dy(1, 2)  # 1/2
    b_sub = b1 - b2
    assert b_sub.分子值 == 1  # (3*2 - 4*1)=2，分母=8 → 2/8=1/4
    assert b_sub.分母值 == 4
    assert str(b_sub) == "1/4"

    # int - 实例（__rsub__）
    c = dy(1, 2)
    c_rsub = 3 - c
    assert c_rsub.分子值 == 5  # 2*3 -1 =5，分母=2 →5/2
    assert c_rsub.分母值 == 2
    assert str(c_rsub) == "5/2"

    # 负数减法
    d = dy(-1, 2) - 3
    assert d.分子值 == -7  # -1 - 2*3 =-7，分母=2 →-7/2
    assert d.分母值 == 2
    assert str(d) == "-7/2"

    # 不支持的类型
    with pytest.raises(TypeError):
        dy(1,2) - 3.5  # 浮点数不支持
    with pytest.raises(TypeError):
        "abc" - dy(1,2)  # 字符串不支持

# ------------------------------ 测试 __invert__ 方法（取倒数 ~） ------------------------------
def test_invert方法():
    """测试__invert__方法（~取倒数），验证分子分母交换"""
    # 正常用例：3/2 → 2/3
    a = dy(3, 2)
    inv_a = ~a
    assert inv_a.分子值 == 2
    assert inv_a.分母值 == 3
    assert str(inv_a) == "2/3"

    # 负数用例：-7/9 → -9/7
    b = dy(-7, 9, 5, "abcde")
    inv_b = ~b
    assert inv_b.分子值 == -9  # 分母9取反后作为分子，保留负号
    assert inv_b.分母值 == 7
    assert inv_b.分子表示 == "-be"  # -9的5进制是-be
    assert inv_b.分母表示 == "bc"   # 7的5进制是bc
    assert str(inv_b) == "-be/bc"

    # 分母为1的用例：5/1 →1/5
    c = dy(5, 1)
    inv_c = ~c
    assert inv_c.分子值 == 1
    assert inv_c.分母值 == 5
    assert str(inv_c) == "1/5"

    # 分子为0（取倒数抛ZeroDivisionError）
    d = dy(0, 5)
    with pytest.raises(ZeroDivisionError, match="分母不能为0"):
        ~d

# ------------------------------ 测试 乘法 __mul__/__rmul__ ------------------------------
def test_乘法运算():
    """测试__mul__（实例*int/实例）和__rmul__（int*实例）"""
    # 实例 * int
    a = dy(1, 2)  # 1/2
    a_mul_4 = a * 4
    assert a_mul_4.分子值 == 2  # 1*4=4，分母=2 → 4/2=2/1
    assert a_mul_4.分母值 == 1
    assert str(a_mul_4) == "2"

    # 实例 * 实例（约分）
    b1 = dy(2, 3)  # 2/3
    b2 = dy(3, 4)  # 3/4
    b_mul = b1 * b2
    assert b_mul.分子值 == 1  # 2*3=6，分母=3*4=12 → 6/12=1/2
    assert b_mul.分母值 == 2
    assert str(b_mul) == "1/2"

    # int * 实例（__rmul__）
    c = dy(-1, 3)
    c_rmul = 6 * c
    assert c_rmul.分子值 == -2  # -1*6=-6，分母=3 → -6/3=-2/1
    assert c_rmul.分母值 == 1
    assert str(c_rmul) == "-2"

    # 负数乘法（负负得正）
    d1 = dy(-2, 5)
    d2 = dy(-5, 4)
    d_mul = d1 * d2
    assert d_mul.分子值 == 1  # (-2)*(-5)=10，分母=5*4=20 → 10/20=1/2
    assert d_mul.分母值 == 2
    assert str(d_mul) == "1/2"

    # 不支持的类型
    with pytest.raises(TypeError):
        dy(1,2) * 3.5  # 浮点数不支持
    with pytest.raises(TypeError):
        [1,2] * dy(1,2)  # 列表不支持

# ------------------------------ 测试 除法 __truediv__/__rtruediv__ ------------------------------
def test_除法运算():
    """测试__truediv__（实例/int/实例）和__rtruediv__（int/实例）"""
    # 实例 / int
    a = dy(3, 4)  # 3/4
    a_div_2 = a / 2
    assert a_div_2.分子值 == 3  # 3，分母=4*2=8 → 3/8
    assert a_div_2.分母值 == 8
    assert str(a_div_2) == "3/8"

    # 实例 / 实例
    b1 = dy(1, 2)  # 1/2
    b2 = dy(3, 4)  # 3/4
    b_div = b1 / b2
    assert b_div.分子值 == 2  # 1*4=4，分母=2*3=6 → 4/6=2/3
    assert b_div.分母值 == 3
    assert str(b_div) == "2/3"

    # int / 实例（__rtruediv__）
    c = dy(2, 3)
    c_rdiv = 5 / c
    assert c_rdiv.分子值 == 15  # 3*5=15，分母=2 → 15/2
    assert c_rdiv.分母值 == 2
    assert str(c_rdiv) == "15/2"

    # 除数为0的异常
    with pytest.raises(ZeroDivisionError, match="被除数不能为0"):
        dy(1,2) / 0  # int除数为0
    with pytest.raises(ZeroDivisionError, match="被除数不能为0"):
        dy(1,2) / dy(0, 5)  # 实例除数分子为0
    with pytest.raises(ZeroDivisionError, match="被除数不能为0"):
        5 / dy(0, 1)  # __rtruediv__除数分子为0

    # 不支持的类型
    with pytest.raises(TypeError):
        dy(1,2) / 3.5  # 浮点数不支持
    with pytest.raises(TypeError):
        "abc" / dy(1,2)  # 字符串不支持

# ------------------------------ 测试 静态方法 _整数根 ------------------------------
def test_整数根静态方法():
    """测试静态方法_整数根，覆盖完全次方、非完全次方、负数、0等场景"""
    # 完全次方：8的立方根=2
    assert dy._整数根(8, 3) == 2
    # 完全次方：16的4次方根=2
    assert dy._整数根(16, 4) == 2
    # 完全次方：25的平方根=5
    assert dy._整数根(25, 2) == 5

    # 负数奇次方根：-8的立方根=-2
    assert dy._整数根(-8, 3) == -2
    # 负数偶次方根：无实数解，返回None
    assert dy._整数根(-16, 2) is None

    # 非完全次方：7的平方根=None
    assert dy._整数根(7, 2) is None
    # 非完全次方：9的立方根=None
    assert dy._整数根(9, 3) is None

    # 0的任意次方根=0
    assert dy._整数根(0, 5) == 0
    # 1的任意次方根=1
    assert dy._整数根(1, 100) == 1
    # -1的立方根=-1
    assert dy._整数根(-1, 3) == -1

# ------------------------------ 测试 幂运算 __pow__/__rpow__ ------------------------------
def test_幂运算():
    """测试__pow__（实例^int/实例）和__rpow__（int^实例）"""
    # 实例 ^ 正整数
    a = dy(2, 3)  # 2/3
    a_pow_2 = a ** 2
    assert a_pow_2.分子值 == 4  # 2²=4，分母=3²=9 → 4/9
    assert a_pow_2.分母值 == 9
    assert str(a_pow_2) == "4/9"

    # 实例 ^ 负整数（取倒数后次方）
    b = dy(3, 2)
    b_pow_neg2 = b ** (-2)
    assert b_pow_neg2.分子值 == 4  # 分母2²=4，分子3²=9 → 4/9
    assert b_pow_neg2.分母值 == 9
    assert str(b_pow_neg2) == "4/9"

    # 实例 ^ 有理数（分子/分母为整数根）
    c = dy(16, 81)  # 16/81
    c_pow_rat = c ** dy(1, 2)  # 平方根 → 4/9
    assert c_pow_rat.分子值 == 4
    assert c_pow_rat.分母值 == 9
    assert str(c_pow_rat) == "4/9"

    # 实例 ^ 有理数（负分子，取倒数后次方）
    d = dy(4, 9)
    d_pow_neg_rat = d ** dy(-1, 2)  # 负平方根 → 3/2
    assert d_pow_neg_rat.分子值 == 3
    assert d_pow_neg_rat.分母值 == 2
    assert str(d_pow_neg_rat) == "3/2"

    # int ^ 实例（__rpow__）：8 ^ (1/3) = 2
    e_rpow = 8 ** dy(1, 3)
    assert e_rpow.分子值 == 2
    assert e_rpow.分母值 == 1
    assert str(e_rpow) == "2"

    # 无法开方的异常
    with pytest.raises(ValueError, match="无法在有理数中开2开方"):
        dy(7, 1) ** dy(1, 2)  # 7的平方根不是整数
    with pytest.raises(ValueError, match="无法在有理数中开3开方"):
        10 ** dy(1, 3)  # 10的立方根不是整数

    # 0^0 特殊情况（Python规则：0**0=1）
    f = dy(0, 1) ** 0
    assert f.分子值 == 1
    assert f.分母值 == 1
    assert str(f) == "1"

    # 不支持的类型
    with pytest.raises(TypeError):
        dy(1,2) ** 3.5  # 浮点数幂次不支持

# ------------------------------ 测试 取模 __mod__/__rmod__ ------------------------------
def test_取模运算():
    """测试__mod__（实例%int/实例）和__rmod__（int%实例），仅允许分母为1"""
    # 实例 % int（分母为1）
    a = dy(7, 1)  # 7/1
    a_mod_3 = a % 3
    assert a_mod_3.分子值 == 1  # 7%3=1
    assert a_mod_3.分母值 == 1
    assert str(a_mod_3) == "1"

    # 实例 % 实例（均分母为1）
    b1 = dy(10, 1)
    b2 = dy(3, 1)
    b_mod = b1 % b2
    assert b_mod.分子值 == 1  # 10%3=1
    assert str(b_mod) == "1"

    # int % 实例（__rmod__，实例分母为1）
    c = dy(4, 1)
    c_rmod = 11 % c
    assert c_rmod.分子值 == 3  # 11%4=3
    assert str(c_rmod) == "3"

    # 分母非1的异常
    with pytest.raises(ValueError, match="取模只允许分母值为1"):
        dy(3, 2) % 3  # 实例分母非1
    with pytest.raises(ValueError, match="取模只允许分母值为1"):
        dy(5, 1) % dy(3, 2)  # 另一个实例分母非1
    with pytest.raises(ValueError, match="取模只允许分母值为1"):
        10 % dy(3, 2)  # __rmod__实例分母非1

    # 不支持的类型
    with pytest.raises(TypeError):
        dy(5,1) % 3.5  # 浮点数不支持

# ------------------------------ 测试 整除 __floordiv__/__rfloordiv__ ------------------------------
def test_整除运算():
    """测试__floordiv__（实例//int/实例）和__rfloordiv__（int//实例），仅允许分母为1"""
    # 实例 // int（分母为1）
    a = dy(7, 1)
    a_floor_3 = a // 3
    assert a_floor_3.分子值 == 2  # 7//3=2
    assert a_floor_3.分母值 == 1
    assert str(a_floor_3) == "2"

    # 实例 // 实例（均分母为1）
    b1 = dy(10, 1)
    b2 = dy(3, 1)
    b_floor = b1 // b2
    assert b_floor.分子值 == 3  # 10//3=3
    assert str(b_floor) == "3"

    # int // 实例（__rfloordiv__，实例分母为1）
    c = dy(4, 1)
    c_rfloor = 11 // c
    assert c_rfloor.分子值 == 2  # 11//4=2
    assert str(c_rfloor) == "2"

    # 负数整除（Python规则）
    d = dy(-7, 1) // 3
    assert d.分子值 == -3  # -7//3=-3

    # 分母非1的异常
    with pytest.raises(ValueError, match="整除只允许分母值为1"):
        dy(3, 2) // 3  # 实例分母非1
    with pytest.raises(ValueError, match="整除只允许分母值为1"):
        dy(5, 1) // dy(3, 2)  # 另一个实例分母非1
    with pytest.raises(ValueError, match="整除只允许分母值为1"):
        10 // dy(3, 2)  # __rfloordiv__实例分母非1

    # 不支持的类型
    with pytest.raises(TypeError):
        dy(5,1) // 3.5  # 浮点数不支持

# ------------------------------ 测试 比较运算符 ------------------------------
def test_比较运算符():
    """测试__eq__/__ne__/__lt__/__gt__/__le__/__ge__"""
    # 等于（==）和不等于（!=）
    a1 = dy(1, 2)
    a2 = dy(2, 4)  # 约分后1/2，相等
    a3 = dy(1, 3)
    assert a1 == a2
    assert a1 != a3
    assert (a1 == 0.5) is False  # 非int/实例返回False
    assert dy(2, 1) == 2  # 和int相等
    assert dy(3, 2) != 2  # 和int不等

    # 小于（<）和大于（>）
    b1 = dy(1, 2)  # 0.5
    b2 = dy(3, 4)  # 0.75
    assert b1 < b2
    assert b2 > b1
    assert b1 < 1  # 0.5 < 1
    assert b2 > 0  # 0.75 > 0
    assert not (b1 > b2)
    assert not (b2 < b1)

    # 小于等于（<=）和大于等于（>=）
    c1 = dy(2, 2)  # 1
    c2 = dy(1, 1)  # 1
    assert c1 <= c2
    assert c1 >= c2
    assert dy(1, 2) <= 1
    assert dy(3, 2) >= 1

    # 负数比较
    d1 = dy(-1, 2)
    d2 = dy(-1, 3)
    assert d1 < d2  # -0.5 < -0.333...
    assert d2 > d1
    assert d1 <= -0  # -0.5 <= 0
    assert d2 >= -1  # -0.333... >= -1

    # 不支持的类型（返回NotImplemented，触发TypeError）
    with pytest.raises(TypeError):
        dy(1,2) < 3.5
    with pytest.raises(TypeError):
        dy(1,2) > "abc"


def test_浮点数方法_整数情况():
    """测试余数为0的整数场景，验证小数部分为0"""
    # 正整数（10进制）
    a1 = dy(5, 1)
    assert a1.浮点数() == "5.0"

    # 负整数（10进制）
    a2 = dy(-7, 1)
    assert a2.浮点数() == "-7.0"

    # 自定义进制（2进制，5=101）
    a3 = dy(5, 1, 2, "01")
    assert a3.浮点数() == "101.0"


def test_浮点数方法_有限小数():
    """测试有限小数场景（除尽），覆盖10进制/自定义进制"""
    # 10进制：1/2 = 0.5
    b1 = dy(1, 2)
    assert b1.浮点数() == "0.5"

    # 10进制：3/4 = 0.75
    b2 = dy(3, 4)
    assert b2.浮点数() == "0.75"

    # 10进制：负数 -3/2 = -1.5
    b3 = dy(-3, 2)
    assert b3.浮点数() == "-1.5"

    # 2进制：1/2 = 0.1（2进制）
    b4 = dy(1, 2, 2, "01")
    assert b4.浮点数() == "0.1"

    # 16进制：1/16 = 0.1（16进制）
    b5 = dy(1, 16, 16, "0123456789ABCDEF")
    assert b5.浮点数() == "0.1"


def test_浮点数方法_循环小数():
    """测试循环小数场景（纯循环/混循环），覆盖10进制/自定义进制"""
    # 10进制：纯循环 1/3 = 0.(3)
    c1 = dy(1, 3)
    assert c1.浮点数() == "0.(3)"

    # 10进制：混循环 1/6 = 0.1(6)
    c2 = dy(1, 6)
    assert c2.浮点数() == "0.1(6)"

    # 10进制：负数纯循环 -2/3 = -0.(6)
    c3 = dy(-2, 3)
    assert c3.浮点数() == "-0.(6)"

    # 2进制：纯循环 1/3 = 0.(01)（2进制，1/3=0.010101...）
    c4 = dy(1, 3, 2, "01")
    assert c4.浮点数() == "0.(01)"

    # 16进制：纯循环 1/15 = 0.(1)（16进制，1/15=0.111...）
    c5 = dy(1, 15, 16, "0123456789ABCDEF")
    assert c5.浮点数() == "0.(1)"


def test_浮点数方法_截断情况():
    """测试达到截断位数未除尽的场景，验证末尾添加..."""
    # 10进制：1/7 = 0.14285714285...，截断位数5 → 0.14285...
    d1 = dy(1, 7)
    assert d1.浮点数(截断位数=5) == "0.14285..."

    # 2进制：1/7 = 0.001001001...，截断位数4 → 0.0010...
    d2 = dy(1, 7, 2, "01")
    assert d2.浮点数(截断位数=3) == "0.001..."

    # 负数截断：-1/7，截断3位 → -0.142...
    d3 = dy(-1, 7)
    assert d3.浮点数(截断位数=3) == "-0.142..."


# ------------------------------ 测试 有理数逼近 静态方法 ------------------------------
def test_有理数逼近_整数字符串():
    """测试纯整数字符串的逼近，覆盖正负、自定义进制"""
    # 10进制：正整数 "5" → 5/1
    e1 = dy.有理数逼近("5")
    assert e1.分子值 == 5
    assert e1.分母值 == 1
    assert str(e1) == "5"

    # 10进制：负整数 "-7" → -7/1
    e2 = dy.有理数逼近("-7")
    assert e2.分子值 == -7
    assert e2.分母值 == 1
    assert str(e2) == "-7"

    # 2进制："101" → 5/1
    e3 = dy.有理数逼近("101", 2, "01")
    assert e3.分子值 == 5
    assert e3.分母值 == 1
    assert str(e3) == "101"


def test_有理数逼近_有限小数字符串():
    """测试有限小数字符串的逼近，覆盖10进制/自定义进制"""
    # 10进制："0.5" → 1/2
    f1 = dy.有理数逼近("0.5")
    assert f1.分子值 == 1
    assert f1.分母值 == 2
    assert str(f1) == "1/2"

    # 10进制："1.75" → 7/4
    f2 = dy.有理数逼近("1.75")
    assert f2.分子值 == 7
    assert f2.分母值 == 4
    assert str(f2) == "7/4"

    # 10进制："-0.25" → -1/4
    f3 = dy.有理数逼近("-0.25")
    assert f3.分子值 == -1
    assert f3.分母值 == 4
    assert str(f3) == "-1/4"

    # 2进制："0.1" → 1/10
    f4 = dy.有理数逼近("0.1", 2, "01")
    assert f4.分子值 == 1
    assert f4.分母值 == 2
    assert str(f4) == "1/10"

    # 16进制："0.1" → 1/10
    f5 = dy.有理数逼近("0.1", 16, "0123456789ABCDEF")
    assert f5.分子值 == 1
    assert f5.分母值 == 16
    assert str(f5) == "1/10"


def test_有理数逼近_循环小数字符串():
    """测试带循环节的小数字符串逼近，覆盖纯循环/混循环"""
    # 10进制：纯循环 "0.(3)" → 1/3
    g1 = dy.有理数逼近("0.(3)")
    assert g1.分子值 == 1
    assert g1.分母值 == 3
    assert str(g1) == "1/3"

    # 10进制：混循环 "0.1(6)" → 1/6
    g2 = dy.有理数逼近("0.1(6)")
    assert g2.分子值 == 1
    assert g2.分母值 == 6
    assert str(g2) == "1/6"

    # 10进制：负数混循环 "-1.2(3)" → -1又7/30 = -37/30
    g3 = dy.有理数逼近("-1.2(3)")
    assert g3.分子值 == -37
    assert g3.分母值 == 30
    assert str(g3) == "-37/30"

    # 2进制：纯循环 "0.(01)" → 1/11
    g4 = dy.有理数逼近("0.(01)", 2, "01")
    assert g4.分子值 == 1
    assert g4.分母值 == 3
    assert str(g4) == "1/11"

    # 16进制：纯循环 "0.(1)" → 1/F
    g5 = dy.有理数逼近("0.(1)", 16, "0123456789ABCDEF")
    assert g5.分子值 == 1
    assert g5.分母值 == 15
    assert str(g5) == "1/F"


def test_有理数逼近_截断小数字符串():
    """测试带省略号的截断小数字符串逼近"""
    # 10进制："0.142857..." → 1/7（1/7=0.14285714285...）
    h1 = dy.有理数逼近("0.142857...")
    assert h1.分子值 == 1
    assert h1.分母值 == 7
    assert str(h1) == "1/7"

    # 3进制："0.010212..." → 1/21（3进制1/7=0.010212010212...）
    h2 = dy.有理数逼近("0.010212...", 3, "012")
    assert h2.分子值 == 1
    assert h2.分母值 == 7
    assert str(h2) == "1/21"

    # 当位数过少时不足以逼近得到原来的有理数
    h3 = dy.有理数逼近("0.01021...", 3, "012")
    assert str(h3) != "1/21"

    # 10进制：负数截断 "-0.333..." → -1/3
    h4 = dy.有理数逼近("-0.333...")
    assert h4.分子值 == -1
    assert h4.分母值 == 3
    assert str(h4) == "-1/3"


def test_有理数逼近_异常场景():
    """测试非法输入字符串的异常处理"""
    # 负号出现在中间
    with pytest.raises(ValueError, match="负号仅允许出现在字符串开头"):
        dy.有理数逼近("12-34")

    # 多个小数点
    with pytest.raises(ValueError, match="除尾部的省略号外，必须有且只有一个'.'"):
        dy.有理数逼近("0.12.34...")

    # 循环节后有多余字符
    with pytest.raises(ValueError, match="精确的表示必须以循环节结束"):
        dy.有理数逼近("0.(12)34")

    # 循环节括号不匹配
    with pytest.raises(ValueError):  # 依赖内部解析逻辑，捕获通用ValueError
        dy.有理数逼近("0.(123")

    # 非法字符（超出进制范围）
    with pytest.raises(ValueError, match="输入字符串G包含非法字符"):
        dy.有理数逼近("0.G", 16, "0123456789ABCDEF")


def test_padic表示_基础场景_7_30_10进制():
    """测试核心场景：10-adic下7/30的padic表示，预期返回(6).9"""
    # 7/30的10-adic表示：...6666.9 → 循环节6，小数位9
    a = dy(7, 30, 10)
    padic_str = a.padic表示(截断位数=30)
    assert padic_str == "(6).9"


def test_padic表示_整数场景():
    """测试整数的padic表示（分母为1，无循环、无小数部分）"""
    # 整数5（5/1）的10-adic表示：5（无循环）
    b1 = dy(5, 1, 10)
    assert b1.padic表示() == "5"

    # 整数-7（-7/1）的10-adic表示：7（padic无符号，有补位的概念如...9999 = -1）
    b2 = dy(-7, 1, 10)
    assert b2.padic表示() == "(9)3"

    # 整数5的2-adic表示：101.0
    b3 = dy(5, 1, 2, "01")
    assert b3.padic表示() == "101"


def test_padic表示_有限padic场景():
    """测试有限padic表示（无循环节，除尽）"""
    # 1/2的10-adic表示：0.5（因为5*2=10 → 1/2=5*10^-1 → 0.5）
    c1 = dy(1, 2, 10)
    assert c1.padic表示() == "0.5"

    # 3/4的10-adic表示：0.75（0.75*4=3 → 3/4=25*10^-2 → 0.75）
    c2 = dy(3, 4, 10)
    assert c2.padic表示() == "0.75"

    # 1/4的2-adic表示：0.01（10(2)=2 → 2*4=8=2^3 → 1/4=2*2^-2=10(2)*2^-2 → 0.01）
    c3 = dy(1, 4, 2, "01")
    assert c3.padic表示() == "0.01"


def test_padic表示_纯循环场景():
    """测试纯循环padic表示（无小数部分，循环节向左延伸）"""
    # 1/3的10-adic表示：(6)7 （...6667 *3=1）
    d1 = dy(1, 3, 10)
    assert d1.padic表示() == "(6)7"

    # 1/3的2-adic表示：(01)1   （...0101(1) * 11=1）
    d2 = dy(1, 3, 2, "01")
    assert d2.padic表示() == "(01)1"


def test_padic表示_截断位数不足场景():
    """测试截断位数不足时添加...，或触发ValueError"""
    # 17/31的10-adic表示，截断位数=4 → 字符列表长度不足，返回...25807
    e1 = dy(17, 31, 10)
    assert e1.padic表示(截断位数=4) == "...25807"

    # 截断位数不足导致负指数>字符列表长度，触发ValueError
    e2 = dy(1, 2, 10)  # 负指数=1，字符列表长度=1（截断位数=0）
    with pytest.raises(ValueError, match="截断位数不足以计算完小数部分"):
        e2.padic表示(截断位数=0)


def test_padic表示_自定义进制场景():
    """测试非10进制的padic表示"""
    # 7/30的16-adic表示（进制=16，符号表0123456789ABCDEF）
    f1 = dy(7, 30, 16, "0123456789ABCDEF")
    padic_16 = f1.padic表示()
    # 验证核心逻辑：解同余方程结果正确，格式含循环节/小数点
    assert "." in padic_16  # 有小数部分
    assert any(char in padic_16 for char in ["(", ")"])  # 有循环节


# ------------------------------ 测试 有理数重构 静态方法 ------------------------------
def test_有理数重构_循环节场景_7_30():
    """测试重构10-adic字符串(6).9 → 7/30"""
    # 重构(6).9 → 7/30
    g1 = dy.有理数重构("(6).9", 10)
    assert g1.分子值 == 7
    assert g1.分母值 == 30
    assert str(g1) == "7/30"


def test_有理数重构_纯循环场景():
    """测试重构纯循环padic字符串(3).0 → 1/3"""
    # 重构(3) → -1/3
    h1 = dy.有理数重构("(3)", 10)
    assert h1.分子值 == -1
    assert h1.分母值 == 3
    assert str(h1) == "-1/3"

    # 重构2-adic的(01)1 → 1/11
    h2 = dy.有理数重构("(01)1", 2, "01")
    assert h2.分子值 == 1
    assert h2.分母值 == 3
    assert str(h2) == "1/11"


def test_有理数重构_截断场景():
    """测试重构带...的截断padic字符串"""
    # 重构10-adic的66.9... → 7/30
    i1 = dy.有理数重构("...66.9", 10)
    assert i1.分子值 == 7
    assert i1.分母值 == 30
    assert str(i1) == "7/30"

    # 重构2-adic的...1011001111101 → 17/37
    i2 = dy.有理数重构("...1011001111101", 2, "01")
    assert i2.分子值 == 17
    assert i2.分母值 == 37
    assert str(i2) == "10001/100101"

    # 对应17/37 少于12位的截断的信息不足以还原，本身循环节长36
    i3 = dy(17, 37, 2)
    assert dy.有理数重构(i3.padic表示(12), 2) == i3
    assert dy.有理数重构(i3.padic表示(11), 2) != i3

def test_有理数重构_整数场景():
    """测试重构整数padic字符串"""
    # 重构10-adic的5.0 → 5/1
    j1 = dy.有理数重构("5.0", 10)
    assert j1.分子值 == 5
    assert j1.分母值 == 1
    assert str(j1) == "5"

    # 重构2-adic的101.0 → 5/1
    j2 = dy.有理数重构("101.0", 2, "01")
    assert j2.分子值 == 5
    assert j2.分母值 == 1
    assert str(j2) == "101"


def test_有理数重构_有限padic场景():
    """测试重构有限padic字符串（无循环节）"""
    # 重构10-adic的0.5 → 1/2
    k1 = dy.有理数重构("0.5", 10)
    assert k1.分子值 == 1
    assert k1.分母值 == 2  # 注意：1/2的padic表示是0.5，重构后是1/5*10^-1=1/2
    k2 = dy.有理数重构("0.5", 10)
    assert k2.浮点数() == "0.5"  # 验证数值等价


def test_有理数重构_异常场景():
    """测试非法输入的异常处理"""
    # 含负号（padic无符号）
    with pytest.raises(ValueError, match="标准的p-adic截断没有符号"):
        dy.有理数重构("-5.0", 10)

    # 循环节不在开头（精确表示必须以循环节开始）
    with pytest.raises(ValueError, match="精确表示必须以循环节开始"):
        dy.有理数重构("12(3).4", 10)

    # 非法字符（超出进制范围）
    with pytest.raises(ValueError, match="输入字符串G包含非法字符"):
        dy.有理数重构("G.0", 16, "0123456789ABCDEF")

    # 循环节括号不匹配
    with pytest.raises(ValueError):
        dy.有理数重构("(6.9", 10)

if __name__ == "__main__":
    # 执行所有测试
    pytest.main(["-v", __file__])