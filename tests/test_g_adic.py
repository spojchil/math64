"""g进数 测试套件。

覆盖：初始化 / 属性 / 表示 / 进制转换 / 类型转换 / 算术 / 幂取模整除 /
比较 / 浮点展开 / 有理数逼近 / g-adic 展开与重构 / 类默认属性。
"""

import pytest

from math64 import g进数 as G


# ======================================================================
# 共享 fixtures
# ======================================================================

@pytest.fixture
def 五进() -> G:
    """7 / -be(5) = -7/9，5进制，符号表 abcde。"""
    return G(7, "-be", 5, "abcde")


@pytest.fixture
def 半() -> G:
    """1/2，默认10进制。"""
    return G(1, 2)


@pytest.fixture
def 三之一() -> G:
    """1/3，默认10进制。"""
    return G(1, 3)


# ======================================================================
# 初始化
# ======================================================================

class Test初始化:
    """构造函数：正常输入 / 异常输入 / 边界值。"""

    # -- 正常路径 --------------------------------------------------------

    def test_整数输入_默认进制(self):
        assert G(15, 25).分子值 == 3
        assert G(15, 25).分母值 == 5
        assert str(G(15, 25)) == "3/5"

    def test_负分子_分母为1_省略分母(self):
        v = G(-28, 1)
        assert v.分子值 == -28
        assert v.分母值 == 1
        assert str(v) == "-28"

    def test_分子为零_约分后分母为1(self):
        v = G(0, -99)
        assert v.分子值 == 0
        assert v.分母值 == 1
        assert str(v) == "0"

    @pytest.mark.parametrize(
        ("分子", "分母", "进制", "符号表", "期望分子值", "期望分母值", "期望str"),
        [
            (7, "-be", 5, "abcde", -7, 9, "-bc/be"),
            ("-A3", "-14", 16, "0123456789ABCDEF", 163, 20, "A3/14"),
            ("1011", "-110", 2, "01", -11, 6, "-1011/110"),
        ],
    )
    def test_字符串输入_自定义进制(self, 分子, 分母, 进制, 符号表, 期望分子值, 期望分母值, 期望str):
        v = G(分子, 分母, 进制, 符号表)
        assert v.分子值 == 期望分子值
        assert v.分母值 == 期望分母值
        assert str(v) == 期望str

    @pytest.mark.parametrize(
        ("分子", "分母", "进制", "符号表", "期望分子值", "期望分母值", "期望str"),
        [
            (45, "-103", 8, "01234567", -45, 67, "-55/103"),
            ("-7F", 255, 16, "0123456789ABCDEF", -127, 255, "-7F/FF"),
        ],
    )
    def test_混合输入_整数与字符串(self, 分子, 分母, 进制, 符号表, 期望分子值, 期望分母值, 期望str):
        v = G(分子, 分母, 进制, 符号表)
        assert v.分子值 == 期望分子值
        assert v.分母值 == 期望分母值
        assert str(v) == 期望str

    # -- 约分 ------------------------------------------------------------

    @pytest.mark.parametrize(
        ("分子", "分母", "期望分子值", "期望分母值", "期望str"),
        [
            (48, -72, -2, 3, "-2/3"),
            (-66, -88, 3, 4, "3/4"),
            (0, 100, 0, 1, "0"),
        ],
    )
    def test_自动约分(self, 分子, 分母, 期望分子值, 期望分母值, 期望str):
        v = G(分子, 分母)
        assert v.分子值 == 期望分子值
        assert v.分母值 == 期望分母值
        assert str(v) == 期望str

    # -- 异常 ------------------------------------------------------------

    def test_分母为零_抛出ZeroDivisionError(self):
        with pytest.raises(ZeroDivisionError, match="分母不能为0"):
            G(5, 0)
        with pytest.raises(ZeroDivisionError, match="分母不能为0"):
            G(10, "0", 2, "01")

    def test_输入类型非法_抛出TypeError(self):
        with pytest.raises(TypeError, match="分子和分母必须是整数或者字符串"):
            G(5.5, 3)
        with pytest.raises(TypeError, match="分子和分母必须是整数或者字符串"):
            G([1, 2], 3)

    def test_字符串仅含负号_抛出ValueError(self):
        with pytest.raises(ValueError, match="输入字符串不能仅包含负号"):
            G("-", 5)

    def test_空字符串_抛出ValueError(self):
        with pytest.raises(ValueError, match="输入字符串不能为空"):
            G("", 5)

    def test_负号出现在中间_抛出ValueError(self):
        with pytest.raises(ValueError, match="负号仅允许出现在字符串开头"):
            G("12-3", 5, 10)

    @pytest.mark.parametrize(
        ("分子", "分母", "进制", "符号表", "match"),
        [
            ("12G", 5, 16, "0123456789ABCDEF", "输入字符串12G包含非法字符"),
            ("125", 5, 5, "01234", "输入字符串125包含非法字符"),
        ],
    )
    def test_字符超出进制范围_抛出ValueError(self, 分子, 分母, 进制, 符号表, match):
        with pytest.raises(ValueError, match=match):
            G(分子, 分母, 进制, 符号表)

    @pytest.mark.parametrize(
        ("进制", "符号表", "异常类", "match"),
        [
            ("10", "0123", TypeError, "进制必须是int类型"),
            (8, ["0"], TypeError, "符号表必须是str"),
            (2, "0 1", ValueError, "符号表中不允许有点"),
            (2, "0/1", ValueError, "符号表中不允许有点"),
            (2, "001", ValueError, "符号表重复"),
            (1, "01", ValueError, "进制1不合法"),
            (6, "01234", ValueError, "进制6不合法"),
        ],
    )
    def test_进制或符号表非法(self, 进制, 符号表, 异常类, match):
        with pytest.raises(异常类, match=match):
            G(1, 2, 进制, 符号表)

    def test_默认符号表下进制类型非法_抛出TypeError(self):
        with pytest.raises(TypeError, match="进制必须是int类型"):
            G(1, 2, "10")


# ======================================================================
# 属性 & 表示
# ======================================================================

class Test属性:
    """只读属性。"""

    def test_进制与符号表(self, 五进):
        assert 五进.进制 == 5
        assert 五进.符号表 == "abcde"

    def test_分子值与分母值(self, 五进):
        assert 五进.分子值 == -7
        assert 五进.分母值 == 9

    def test_分子表示与分母表示(self, 五进):
        assert 五进.分子表示 == "-bc"
        assert 五进.分母表示 == "be"


class Test表示:
    """__str__ / __repr__。"""

    def test_str_分母为1_省略分母(self):
        assert str(G(5, 1)) == "5"
        assert str(G(-3, 1)) == "-3"

    def test_str_分母非1(self):
        assert str(G(1, 2)) == "1/2"

    def test_repr_包含十进制与当前进制(self):
        r = repr(G(15, "32", 8, "01234567"))
        assert "十进制: 15/26" in r
        assert "当前进制为: 8" in r
        assert "表示: 17/32" in r


# ======================================================================
# 进制转换
# ======================================================================

class Test进制转换:
    """进制转换方法 与 内部转换正确性。"""

    def test_内部进制转换_十二进制(self):
        v = G("A5", 100, 12, "0123456789AB")
        assert v.分子值 == 5
        assert v.分母值 == 4
        assert v.分子表示 == "5"
        assert v.分母表示 == "4"

    def test_内部进制转换_三十六进制(self):
        v = G("ZY", "-10", 36, "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        assert v.分子值 == -647
        assert v.分母值 == 18
        assert v.分子表示 == "-HZ"
        assert v.分母表示 == "I"

    def test_进制转换_数值不变(self, 五进):
        c = 五进.进制转换(10)
        assert c.进制 == 10
        assert c.分子值 == -7
        assert c.分母值 == 9
        assert str(c) == "-7/9"

    def test_进制转换_自定义符号表(self, 五进):
        c = 五进.进制转换(16, "0123456789ABCDEF")
        assert c.进制 == 16
        assert c.符号表 == "0123456789ABCDEF"
        assert str(c) == "-7/9"

    def test_进制转换_二进制(self, 五进):
        c = 五进.进制转换(2)
        assert c.分子表示 == "-111"
        assert c.分母表示 == "1001"
        assert str(c) == "-111/1001"


# ======================================================================
# 类型转换
# ======================================================================

class Test类型转换:
    """float / int / bool / hash / abs。"""

    def test_float(self):
        assert float(G(3, 2)) == 1.5
        assert float(G(-7, 3)) == pytest.approx(-2.3333333333333)
        assert float(G(0, 99)) == 0.0

    def test_int(self):
        assert int(G(3, 2)) == 1
        assert int(G(-7, 3)) == -2
        assert int(G(-28, 1)) == -28

    def test_bool(self):
        assert bool(G(3, 2)) is True
        assert bool(G(0, 99)) is False

    def test_hash_分母为1_等于分子的hash(self):
        assert hash(G(5, 1)) == hash(5)

    def test_hash_分母非1_等于元组的hash(self):
        assert hash(G(3, 2)) == hash((3, 2))

    def test_hash_约分后相同_值相同(self):
        assert hash(G(3, 2)) == hash(G(6, 4))

    def test_abs_正数(self, 半):
        assert abs(半).分子值 == 1
        assert abs(半).分母值 == 2

    def test_abs_负数(self, 五进):
        a = abs(五进)
        assert a.分子值 == 7
        assert a.分母值 == 9
        assert a.进制 == 5
        assert str(a) == "bc/be"

    def test_abs_零(self):
        a = abs(G(0, -5))
        assert a.分子值 == 0
        assert a.分母值 == 1


# ======================================================================
# 算术运算
# ======================================================================

class Test加法:
    def test_实例加整数(self, 半):
        v = 半 + 3
        assert v.分子值 == 7
        assert v.分母值 == 2
        assert str(v) == "7/2"

    def test_实例加实例(self):
        v = G(1, 3) + G(1, 6)
        assert v.分子值 == 1
        assert v.分母值 == 2

    def test_整数加实例(self, 半):
        v = 5 + 半
        assert v.分子值 == 11
        assert v.分母值 == 2

    def test_负数(self):
        v = G(-1, 2) + (-3)
        assert v.分子值 == -7
        assert v.分母值 == 2
        assert str(v) == "-7/2"

    def test_进制保持(self, 半):
        assert (半 + 1).进制 == 10

    def test_不支持的类型抛TypeError(self):
        with pytest.raises(TypeError):
            G(1, 2) + 3.5


class Test减法:
    def test_实例减整数(self):
        v = G(5, 2) - 2
        assert v.分子值 == 1
        assert v.分母值 == 2

    def test_实例减实例(self):
        v = G(3, 4) - G(1, 2)
        assert v.分子值 == 1
        assert v.分母值 == 4

    def test_整数减实例(self, 半):
        v = 3 - 半
        assert v.分子值 == 5
        assert v.分母值 == 2

    def test_负数(self):
        v = G(-1, 2) - 3
        assert v.分子值 == -7
        assert v.分母值 == 2

    def test_不支持的类型抛TypeError(self):
        with pytest.raises(TypeError):
            G(1, 2) - 3.5


class Test取反:
    def test_正数(self, 半):
        v = -半
        assert v.分子值 == -1
        assert v.分母值 == 2

    def test_负数(self, 五进):
        v = -五进
        assert v.分子值 == 7
        assert v.分母值 == 9
        assert str(v) == "bc/be"

    def test_零(self):
        v = -G(0, 5)
        assert v.分子值 == 0
        assert v.分母值 == 1


class Test乘法:
    def test_实例乘整数(self, 半):
        v = 半 * 4
        assert v.分子值 == 2
        assert v.分母值 == 1
        assert str(v) == "2"

    def test_实例乘实例(self):
        v = G(2, 3) * G(3, 4)
        assert v.分子值 == 1
        assert v.分母值 == 2

    def test_整数乘实例(self):
        v = 6 * G(-1, 3)
        assert v.分子值 == -2
        assert v.分母值 == 1

    def test_负负得正(self):
        v = G(-2, 5) * G(-5, 4)
        assert v.分子值 == 1
        assert v.分母值 == 2

    def test_不支持的类型抛TypeError(self):
        with pytest.raises(TypeError):
            G(1, 2) * 3.5


class Test除法:
    def test_实例除整数(self):
        v = G(3, 4) / 2
        assert v.分子值 == 3
        assert v.分母值 == 8

    def test_实例除实例(self):
        v = G(1, 2) / G(3, 4)
        assert v.分子值 == 2
        assert v.分母值 == 3

    def test_整数除实例(self):
        v = 5 / G(2, 3)
        assert v.分子值 == 15
        assert v.分母值 == 2

    @pytest.mark.parametrize("表达式", [
        lambda: G(1, 2) / 0,
        lambda: G(1, 2) / G(0, 5),
        lambda: 5 / G(0, 1),
    ])
    def test_除数为零_抛ZeroDivisionError(self, 表达式):
        with pytest.raises(ZeroDivisionError, match="被除数不能为0"):
            表达式()

    def test_不支持的类型抛TypeError(self):
        with pytest.raises(TypeError):
            G(1, 2) / 3.5


# ======================================================================
# 幂 / 取模 / 整除
# ======================================================================

class Test幂运算:
    def test_正整数指数(self):
        v = G(2, 3) ** 2
        assert v.分子值 == 4
        assert v.分母值 == 9

    def test_负整数指数(self):
        v = G(3, 2) ** (-2)
        assert v.分子值 == 4
        assert v.分母值 == 9

    def test_有理指数_平方根(self):
        v = G(16, 81) ** G(1, 2)
        assert v.分子值 == 4
        assert v.分母值 == 9

    def test_有理指数_负指数(self):
        v = G(4, 9) ** G(-1, 2)
        assert v.分子值 == 3
        assert v.分母值 == 2

    def test_整数底_实例指数(self):
        v = 8 ** G(1, 3)
        assert v.分子值 == 2
        assert v.分母值 == 1

    def test_整数底_实例负指数(self):
        v = 8 ** G(-1, 3)
        assert v.分子值 == 1
        assert v.分母值 == 2

    def test_零的零次方为1(self):
        v = G(0, 1) ** 0
        assert v.分子值 == 1
        assert v.分母值 == 1

    def test_非完全次方_抛ValueError(self):
        with pytest.raises(ValueError, match="无法在有理数中开2开方"):
            G(7, 1) ** G(1, 2)

    def test_不支持的类型抛TypeError(self):
        with pytest.raises(TypeError):
            G(1, 2) ** 3.5


class Test整数根:
    """静态方法 _整数根。"""

    @pytest.mark.parametrize(
        ("m", "n", "期望"),
        [
            (8, 3, 2),
            (16, 4, 2),
            (25, 2, 5),
            (-8, 3, -2),
            (0, 5, 0),
            (1, 100, 1),
            (-1, 3, -1),
        ],
    )
    def test_完全次方(self, m, n, 期望):
        assert G._整数根(m, n) == 期望

    @pytest.mark.parametrize(
        ("m", "n"),
        [
            (-16, 2),  # 负数偶次方
            (7, 2),    # 非完全平方
            (9, 3),    # 非完全立方
        ],
    )
    def test_无整数根返回None(self, m, n):
        assert G._整数根(m, n) is None


class Test取模:
    def test_实例模整数(self):
        assert str(G(7, 1) % 3) == "1"

    def test_实例模实例(self):
        assert str(G(10, 1) % G(3, 1)) == "1"

    def test_整数模实例(self):
        assert str(11 % G(4, 1)) == "3"

    def test_分母非1_抛ValueError(self):
        with pytest.raises(ValueError, match="取模只允许分母值为1"):
            G(3, 2) % 3


class Test整除:
    def test_实例整除数(self):
        assert str(G(7, 1) // 3) == "2"

    def test_实例整除实例(self):
        assert str(G(10, 1) // G(3, 1)) == "3"

    def test_整数整除实例(self):
        assert str(11 // G(4, 1)) == "2"

    def test_负数整除(self):
        assert G(-7, 1) // 3 == G(-3, 1)

    def test_分母非1_抛ValueError(self):
        with pytest.raises(ValueError, match="整除只允许分母值为1"):
            G(3, 2) // 3


# ======================================================================
# 比较
# ======================================================================

class Test比较:
    def test_相等_约分后一致(self):
        assert G(1, 2) == G(2, 4)

    def test_相等_与整数(self):
        assert G(2, 1) == 2
        assert G(3, 2) != 2

    def test_不等(self):
        assert G(1, 2) != G(1, 3)

    def test_与非支持类型_不等(self):
        assert G(1, 2) != 0.5

    def test_小于(self):
        assert G(1, 2) < G(3, 4)
        assert G(1, 2) < 1
        assert not (G(3, 4) < G(1, 2))

    def test_大于(self):
        assert G(3, 4) > G(1, 2)
        assert G(3, 4) > 0

    def test_小于等于(self):
        assert G(2, 2) <= G(1, 1)
        assert G(1, 2) <= 1

    def test_大于等于(self):
        assert G(2, 2) >= G(1, 1)
        assert G(3, 2) >= 1

    def test_负数比较(self):
        assert G(-1, 2) < G(-1, 3)  # -0.5 < -0.333...

    @pytest.mark.parametrize("表达式", [
        lambda: G(1, 2) < 3.5,
        lambda: G(1, 2) > "abc",
    ])
    def test_不支持的类型抛TypeError(self, 表达式):
        with pytest.raises(TypeError):
            表达式()


# ======================================================================
# 浮点展开
# ======================================================================

class Test浮点数:
    def test_整数_显示点零(self):
        assert G(5, 1).浮点数() == "5.0"
        assert G(-7, 1).浮点数() == "-7.0"
        assert G(5, 1, 2, "01").浮点数() == "101.0"

    @pytest.mark.parametrize(
        ("分子", "分母", "进制", "符号表", "期望"),
        [
            (1, 2, 10, None, "0.5"),
            (3, 4, 10, None, "0.75"),
            (-3, 2, 10, None, "-1.5"),
            (1, 2, 2, "01", "0.1"),
            (1, 16, 16, "0123456789ABCDEF", "0.1"),
        ],
    )
    def test_有限小数(self, 分子, 分母, 进制, 符号表, 期望):
        v = G(分子, 分母, 进制, 符号表) if 符号表 else G(分子, 分母, 进制)
        assert v.浮点数() == 期望

    @pytest.mark.parametrize(
        ("分子", "分母", "进制", "符号表", "期望"),
        [
            (1, 3, 10, None, "0.(3)"),
            (1, 6, 10, None, "0.1(6)"),
            (-2, 3, 10, None, "-0.(6)"),
            (1, 3, 2, "01", "0.(01)"),
            (1, 15, 16, "0123456789ABCDEF", "0.(1)"),
        ],
    )
    def test_循环小数(self, 分子, 分母, 进制, 符号表, 期望):
        v = G(分子, 分母, 进制, 符号表) if 符号表 else G(分子, 分母, 进制)
        assert v.浮点数() == 期望

    def test_截断(self):
        assert G(1, 7).浮点数(截断位数=5) == "0.14285..."
        assert G(1, 7, 2, "01").浮点数(截断位数=3) == "0.001..."
        assert G(-1, 7).浮点数(截断位数=3) == "-0.142..."


# ======================================================================
# 有理数逼近
# ======================================================================

class Test有理数逼近:
    @pytest.mark.parametrize(
        ("字符串", "进制", "符号表", "期望分子", "期望分母", "期望str"),
        [
            ("5", 10, None, 5, 1, "5"),
            ("-7", 10, None, -7, 1, "-7"),
            ("101", 2, "01", 5, 1, "101"),
            ("0.5", 10, None, 1, 2, "1/2"),
            ("1.75", 10, None, 7, 4, "7/4"),
            ("-0.25", 10, None, -1, 4, "-1/4"),
            ("0.1", 2, "01", 1, 2, "1/10"),
            ("0.1", 16, "0123456789ABCDEF", 1, 16, "1/10"),
            ("0.(3)", 10, None, 1, 3, "1/3"),
            ("0.1(6)", 10, None, 1, 6, "1/6"),
            ("-1.2(3)", 10, None, -37, 30, "-37/30"),
            ("0.(01)", 2, "01", 1, 3, "1/11"),
            ("0.(1)", 16, "0123456789ABCDEF", 1, 15, "1/F"),
            ("0.142857...", 10, None, 1, 7, "1/7"),
            ("0.010212...", 3, "012", 1, 7, "1/21"),
            ("-0.333...", 10, None, -1, 3, "-1/3"),
        ],
    )
    def test_各种格式(self, 字符串, 进制, 符号表, 期望分子, 期望分母, 期望str):
        args = (字符串, 进制, 符号表) if 符号表 else (字符串, 进制)
        v = G.有理数逼近(*args)
        assert v.分子值 == 期望分子
        assert v.分母值 == 期望分母
        assert str(v) == 期望str

    def test_截断信息不足_结果不同(self):
        assert str(G.有理数逼近("0.01021...", 3, "012")) != "1/21"

    @pytest.mark.parametrize(
        ("字符串", "进制", "符号表", "match"),
        [
            ("12-34", 10, None, "负号仅允许出现在字符串开头"),
            ("0.12.34...", 10, None, "必须有且只有一个'.'"),
            ("0.(12)34", 10, None, "精确的表示必须以循环节结束"),
            ("0.G", 16, "0123456789ABCDEF", "输入字符串G包含非法字符"),
            ("", 10, None, "输入字符串不能为空"),
            (".", 10, None, "输入字符串不能为空"),
        ],
    )
    def test_异常(self, 字符串, 进制, 符号表, match):
        args = (字符串, 进制, 符号表) if 符号表 else (字符串, 进制)
        with pytest.raises(ValueError, match=match):
            G.有理数逼近(*args)


# ======================================================================
# g-adic 展开
# ======================================================================

class TestPadic表示:
    def test_核心场景_7除30_十进制(self):
        assert G(7, 30, 10).padic表示() == "(6).9"

    @pytest.mark.parametrize(
        ("分子", "分母", "进制", "符号表", "期望"),
        [
            (5, 1, 10, None, "5"),
            (-7, 1, 10, None, "(9)3"),
            (5, 1, 2, "01", "101"),
        ],
    )
    def test_整数(self, 分子, 分母, 进制, 符号表, 期望):
        v = G(分子, 分母, 进制, 符号表) if 符号表 else G(分子, 分母, 进制)
        assert v.padic表示() == 期望

    @pytest.mark.parametrize(
        ("分子", "分母", "进制", "符号表", "期望"),
        [
            (1, 2, 10, None, "0.5"),
            (3, 4, 10, None, "0.75"),
            (1, 4, 2, "01", "0.01"),
        ],
    )
    def test_有限(self, 分子, 分母, 进制, 符号表, 期望):
        v = G(分子, 分母, 进制, 符号表) if 符号表 else G(分子, 分母, 进制)
        assert v.padic表示() == 期望

    @pytest.mark.parametrize(
        ("分子", "分母", "进制", "符号表", "期望"),
        [
            (1, 3, 10, None, "(6)7"),
            (1, 3, 2, "01", "(01)1"),
        ],
    )
    def test_纯循环(self, 分子, 分母, 进制, 符号表, 期望):
        v = G(分子, 分母, 进制, 符号表) if 符号表 else G(分子, 分母, 进制)
        assert v.padic表示() == 期望

    def test_截断位数不足(self):
        assert G(17, 31, 10).padic表示(截断位数=4) == "...25807"

    def test_截断位数不足以完成小数部分_抛ValueError(self):
        with pytest.raises(ValueError, match="截断位数不足以计算完小数部分"):
            G(1, 2, 10).padic表示(截断位数=0)

    def test_自定义进制_格式含循环节和小数点(self):
        s = G(7, 30, 16, "0123456789ABCDEF").padic表示()
        assert "." in s
        assert "(" in s or ")" in s


# ======================================================================
# g-adic 重构
# ======================================================================

class Test有理数重构:
    def test_循环节_7除30(self):
        v = G.有理数重构("(6).9", 10)
        assert v.分子值 == 7
        assert v.分母值 == 30

    @pytest.mark.parametrize(
        ("字符串", "进制", "符号表", "期望分子", "期望分母", "期望str"),
        [
            ("(3)", 10, None, -1, 3, "-1/3"),
            ("(01)1", 2, "01", 1, 3, "1/11"),
            ("...66.9", 10, None, 7, 30, "7/30"),
            ("...1011001111101", 2, "01", 17, 37, "10001/100101"),
            ("5.0", 10, None, 5, 1, "5"),
            ("101.0", 2, "01", 5, 1, "101"),
            ("0.5", 10, None, 1, 2, "1/2"),
        ],
    )
    def test_各种格式(self, 字符串, 进制, 符号表, 期望分子, 期望分母, 期望str):
        args = (字符串, 进制, 符号表) if 符号表 else (字符串, 进制)
        v = G.有理数重构(*args)
        assert v.分子值 == 期望分子
        assert v.分母值 == 期望分母
        assert str(v) == 期望str

    def test_截断位数决定精度(self):
        v = G(17, 37, 2)
        assert G.有理数重构(v.padic表示(12), 2) == v
        assert G.有理数重构(v.padic表示(11), 2) != v

    @pytest.mark.parametrize(
        ("字符串", "进制", "match"),
        [
            ("-5.0", 10, "标准的p-adic截断没有符号"),
            ("12(3).4", 10, "精确表示必须以循环节开始"),
            ("G.0", 16, "输入字符串G包含非法字符"),
        ],
    )
    def test_异常(self, 字符串, 进制, match):
        with pytest.raises(ValueError, match=match):
            G.有理数重构(字符串, 进制)


# ======================================================================
# 类默认属性（旧测试未覆盖）
# ======================================================================

class Test类默认属性:
    """修改类默认属性 静态方法。"""

    def test_修改默认进制(self):
        old = G._默认进制
        try:
            G.修改类默认属性(进制=8)
            assert G._默认进制 == 8
            v = G(10, 3)  # 不传进制，使用新默认
            assert v.进制 == 8
        finally:
            G.修改类默认属性(进制=old)

    def test_修改默认符号表(self):
        old_进制, old_表 = G._默认进制, G._默认符号表
        try:
            G.修改类默认属性(进制=3, 符号表="abc")
            assert G._默认进制 == 3
            assert G._默认符号表 == "abc"
            v = G(2, 1)
            assert v.进制 == 3
            assert v.符号表 == "abc"
        finally:
            G.修改类默认属性(进制=old_进制, 符号表=old_表)

    def test_修改后不影响已有实例(self, 五进):
        old = G._默认进制
        try:
            G.修改类默认属性(进制=2)
            assert 五进.进制 == 5  # 不受影响
        finally:
            G.修改类默认属性(进制=old)

    def test_非法参数抛异常_不修改状态(self):
        old_进制 = G._默认进制
        try:
            G.修改类默认属性(进制=1, 符号表="01")
        except ValueError:
            pass
        assert G._默认进制 == old_进制  # 回滚


# ======================================================================
# 综合 / 往返
# ======================================================================

class Test综合:
    """跨方法集成测试。"""

    def test_padic往返_循环节格式(self):
        for 值 in [(7, 30), (1, 3), (-1, 3), (17, 31)]:
            v = G(*值, 10)
            assert G.有理数重构(v.padic表示(), 10) == v

    def test_padic运算_重构后运算再展开(self):
        r1 = G.有理数重构("(1)2", 进制=10)
        r2 = G.有理数重构("(3204)4", 进制=10)
        result = r1 * r2
        assert G.有理数重构(result.padic表示(), 进制=10) == result

    def test_浮点往返_有限小数(self):
        for 分子, 分母 in [(1, 2), (3, 4), (1, 8), (7, 5)]:
            v = G(分子, 分母)
            restored = G.有理数逼近(v.浮点数())
            assert restored == v

    def test_连分数逼近_pi近似(self):
        """12 位截断 π 的连分数逼近应在 1e-6 以内。"""
        pi_approx = G.有理数逼近("3.141592653589...")
        assert abs(float(pi_approx) - 3.141592653589) < 1e-6

    def test_多次运算后精确性(self, 半, 三之一):
        r = (半 + 三之一) * G(6, 1) - G(1, 1)
        assert r == G(4, 1)
