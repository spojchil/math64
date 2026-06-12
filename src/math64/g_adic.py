"""g 进数有理数模块。

支持任意进制（2 到符号表长度）的精确有理数运算，含四则运算、比较、
进制转换、浮点展开、g-adic 展开与重构、连分数逼近。
"""

from __future__ import annotations

from math import gcd
from typing import ClassVar


class g进数:
    """任意进制下的精确有理数，内部以最简分数存储。

    支持整数与字符串混合输入，自动约分。分子/分母的字符串表示按当前进制解析。
    实例不可变：所有运算返回新实例。
    """

    _默认进制: ClassVar[int] = 10
    _默认符号表: ClassVar[str] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    __slots__ = (
        "_进制",
        "_符号表",
        "_分子值",
        "_分子表示",
        "_分母值",
        "_分母表示",
        "_映射字典",
    )

    def __init__(
        self,
        分子: int | str,
        分母: int | str = 1,
        进制: int | None = None,
        符号表: str | None = None,
    ) -> None:
        """根据分子/分母创建最简分数。

        分子、分母可为十进制整数或当前进制下的字符串（允许前导负号）。
        自动以 gcd 约分到最简；分母为 0 时抛出 ZeroDivisionError。
        """
        self._进制 = 进制 if 进制 is not None else g进数._默认进制
        self._符号表 = 符号表 if 符号表 is not None else g进数._默认符号表
        g进数._验证进制和符号表(self._进制, self._符号表)
        self._分子表示: str | None = None
        self._分母表示: str | None = None
        self._映射字典: dict[str, int] | None = None
        分母, 分母符号 = self._处理输入(分母)
        分子, 分子符号 = self._处理输入(分子)
        公因子 = gcd(分母, 分子)
        分母 //= 公因子
        分子 //= 公因子
        self._分母值: int = 分母
        self._分子值: int = 分子 * 分母符号 * 分子符号
        if self._分母值 == 0:
            raise ZeroDivisionError("分母不能为0")

    # -- 只读属性 ----------------------------------------------------------

    @property
    def 进制(self) -> int:
        """当前实例的进制。"""
        return self._进制

    @property
    def 符号表(self) -> str:
        """当前实例的符号表字符串。"""
        return self._符号表

    @property
    def 分子值(self) -> int:
        """最简分数的分子（十进制整数，可负）。"""
        return self._分子值

    @property
    def 分母值(self) -> int:
        """最简分数的分母（十进制正整数）。"""
        return self._分母值

    @property
    def 分子表示(self) -> str:
        """分子在当前进制下的字符串表示（含符号）。"""
        if self._分子表示 is None:
            self._分子表示 = "-" if self._分子值 < 0 else ""
            self._分子表示 += self._十进转n(abs(self._分子值))
        return self._分子表示

    @property
    def 分母表示(self) -> str:
        """分母在当前进制下的字符串表示（恒正）。"""
        if self._分母表示 is None:
            self._分母表示 = self._十进转n(abs(self._分母值))
        return self._分母表示

    # -- 基础表示 ----------------------------------------------------------

    def __str__(self) -> str:
        """当前进制下的 "分子/分母" 字符串，分母为 1 时省略分母。"""
        return f"{self.分子表示}/{self.分母表示}" if self._分母值 != 1 else self.分子表示

    def __repr__(self) -> str:
        """含十进制数值的调试表示。"""
        return (
            f"十进制: {self._分子值}/{self._分母值}, "
            f"当前进制为: {self._进制}, 表示: {self.分子表示}/{self.分母表示}"
        )

    # -- 静态 / 私有工具方法 ------------------------------------------------

    @staticmethod
    def _验证进制和符号表(进制: int, 符号表: str) -> None:
        """校验进制与符号表合法性，不合法时抛出 TypeError 或 ValueError。

        规则：进制为 2 到 len(符号表) 的整数，符号表不含 . / \\ 空格 - 且无重复。
        使用默认符号表时跳过长度检查（默认表足够长，仅要求 2 <= 进制 <= 36 即可）。
        """
        if not isinstance(进制, int):
            raise TypeError("进制必须是int类型")
        if not isinstance(符号表, str):
            raise TypeError("符号表必须是str")
        if 符号表 is g进数._默认符号表 and 2 <= 进制 <= len(符号表):
            return
        if any(char in r"./ \-" for char in 符号表):
            raise ValueError("符号表中不允许有点，空格，斜杠，反斜杠和减号")
        if len(set(符号表)) != len(符号表):
            raise ValueError("符号表重复")
        if not (2 <= 进制 <= len(符号表)):
            raise ValueError(
                f"进制{进制}不合法！"
                f"符号表长度为{len(符号表)}，"
                f"进制需在2到该长度之间"
            )

    def _处理输入(self, 值: int | str) -> tuple[int, int]:
        """将分子或分母输入统一解析为 (绝对值, 符号±1)。

        int 直接取绝对值和符号；str 先做合法性校验再通过 _n进转十 解析。
        """
        if isinstance(值, int):
            return abs(值), 1 if 值 >= 0 else -1
        if isinstance(值, str):
            self._验证输入字符串(值)
            符号 = 1
            if 值.startswith("-"):
                符号 = -1
                值 = 值[1:]
            return self._n进转十(值), 符号
        raise TypeError("分子和分母必须是整数或者字符串")

    def _验证输入字符串(self, 字符串: str) -> None:
        """校验输入字符串：不可仅含负号、负号只能在首位、所有字符必须在当前进制合法集合内。"""
        if 字符串 == "":
            raise ValueError("输入字符串不能为空")

        if 字符串 == "-":
            raise ValueError("输入字符串不能仅包含负号")

        if "-" in 字符串[1:]:
            raise ValueError("负号仅允许出现在字符串开头")

        字符集合 = set(self._符号表[: self._进制])
        清理后字符 = 字符串.lstrip("-")
        if not all(字符 in 字符集合 for 字符 in 清理后字符):
            raise ValueError(
                f"输入字符串{字符串}包含非法字符！"
                f"当前进制{self._进制}的合法集合为：{''.join(字符集合)}"
            )

    def _读取映射(self) -> dict[str, int]:
        """返回 {符号字符: 数值} 的映射字典，惰性构建并缓存。"""
        if self._映射字典 is None:
            self._映射字典 = {c: idx for idx, c in enumerate(self._符号表)}
        return self._映射字典

    def _十进转n(self, 值: int) -> str:
        """十进制非负整数 → 当前进制字符串（短除法）。"""
        if 值 == 0:
            return self._符号表[0]
        进制 = self._进制
        符号表 = self._符号表

        字符表: list[str] = []
        while 值 > 0:
            字符表.append(符号表[值 % 进制])
            值 = 值 // 进制

        return "".join(reversed(字符表))

    def _n进转十(self, 字符串: str) -> int:
        """当前进制字符串（无符号） → 十进制非负整数（秦九韶算法）。"""
        字典映射 = self._读取映射()
        进制 = self._进制

        十进值 = 0
        当前基 = 1
        for char in reversed(字符串):
            十进值 += 字典映射[char] * 当前基
            当前基 *= 进制
        return 十进值

    @classmethod
    def _快速创建(
        cls, 分子值: int, 分母值: int, 进制: int, 符号表: str
    ) -> g进数:
        """绕过 __init__ 的输入解析与符号表校验，直接用整数分子/分母构建实例。

        性能敏感路径（算术运算内部）使用此方法，避免重复校验与字符串转换。
        调用方保证分母非零、进制与符号表合法。
        """
        if 分母值 == 0:
            raise ZeroDivisionError("分母不能为0")
        if 分母值 < 0:
            分母值, 分子值 = -分母值, -分子值

        公因子 = gcd(分母值, abs(分子值))
        分母值 //= 公因子
        分子值 //= 公因子
        实例 = cls.__new__(cls)
        实例._进制 = 进制
        实例._符号表 = 符号表
        实例._分子值 = 分子值
        实例._分母值 = 分母值
        实例._分子表示 = None
        实例._分母表示 = None
        实例._映射字典 = None
        return 实例

    @staticmethod
    def 修改类默认属性(
        进制: int | None = None, 符号表: str | None = None
    ) -> None:
        """修改类的全局默认进制与符号表，影响此后所有未显式指定进制/符号表的实例。

        注意：仅影响新创建的实例，已有实例不受影响。
        """
        进制 = 进制 if 进制 is not None else g进数._默认进制
        符号表 = 符号表 if 符号表 is not None else g进数._默认符号表
        g进数._验证进制和符号表(进制, 符号表)
        g进数._默认进制 = 进制
        g进数._默认符号表 = 符号表

    def 进制转换(
        self, 进制: int | None = None, 符号表: str | None = None
    ) -> g进数:
        """返回当前有理数在目标进制/符号表下的新实例，数值不变。"""
        return g进数(self._分子值, self._分母值, 进制, 符号表)

    # -- 数值类型转换 -------------------------------------------------------

    def __float__(self) -> float:
        return self._分子值 / self._分母值

    def __bool__(self) -> bool:
        return bool(self._分子值)

    def __hash__(self) -> int:
        if self._分母值 == 1:
            return hash(self._分子值)
        else:
            return hash((self._分子值, self._分母值))

    def __int__(self) -> int:
        if self._分子值 >= 0:
            return self._分子值 // self._分母值
        return -((-self._分子值) // self._分母值)

    def __abs__(self) -> g进数:
        return g进数(abs(self._分子值), self._分母值, self._进制, self._符号表)

    # -- 算术运算 ----------------------------------------------------------

    def __add__(self, other: int | g进数) -> g进数:
        if not isinstance(other, (int, g进数)):
            return NotImplemented

        if isinstance(other, int):
            新分子 = self._分子值 + self._分母值 * other
            新分母 = self._分母值
        else:
            新分子 = self._分子值 * other._分母值 + self._分母值 * other._分子值
            新分母 = self._分母值 * other._分母值
        return g进数._快速创建(新分子, 新分母, self._进制, self._符号表)

    def __radd__(self, other: int) -> g进数:
        return self.__add__(other)

    def __neg__(self) -> g进数:
        return g进数._快速创建(
            -self._分子值, self._分母值, self._进制, self._符号表
        )

    def __sub__(self, other: int | g进数) -> g进数:
        if not isinstance(other, (int, g进数)):
            return NotImplemented

        if isinstance(other, int):
            新分子 = self._分子值 - self._分母值 * other
            新分母 = self._分母值
        else:
            新分子 = self._分子值 * other._分母值 - self._分母值 * other._分子值
            新分母 = self._分母值 * other._分母值
        return g进数._快速创建(新分子, 新分母, self._进制, self._符号表)

    def __rsub__(self, other: int) -> g进数:
        if not isinstance(other, int):
            return NotImplemented
        新分子 = self._分母值 * other - self._分子值
        新分母 = self._分母值
        return g进数._快速创建(新分子, 新分母, self._进制, self._符号表)

    def __mul__(self, other: int | g进数) -> g进数:
        if not isinstance(other, (int, g进数)):
            return NotImplemented

        if isinstance(other, int):
            新分子 = self._分子值 * other
            新分母 = self._分母值
        else:
            新分子 = self._分子值 * other._分子值
            新分母 = self._分母值 * other._分母值
        return g进数._快速创建(新分子, 新分母, self._进制, self._符号表)

    def __rmul__(self, other: int) -> g进数:
        return self.__mul__(other)

    def __truediv__(self, other: int | g进数) -> g进数:
        if not isinstance(other, (int, g进数)):
            return NotImplemented

        if isinstance(other, int):
            if other == 0:
                raise ZeroDivisionError("被除数不能为0")
            新分子 = self._分子值
            新分母 = self._分母值 * other
        else:
            if other._分子值 == 0:
                raise ZeroDivisionError("被除数不能为0")
            新分子 = self._分子值 * other._分母值
            新分母 = self._分母值 * other._分子值
        return g进数._快速创建(新分子, 新分母, self._进制, self._符号表)

    def __rtruediv__(self, other: int) -> g进数:
        if not isinstance(other, int):
            return NotImplemented

        if self._分子值 == 0:
            raise ZeroDivisionError("被除数不能为0")
        新分子 = self._分母值 * other
        新分母 = self._分子值
        return g进数._快速创建(新分子, 新分母, self._进制, self._符号表)

    # -- 幂运算 ------------------------------------------------------------

    @staticmethod
    def _整数根(m: int, n: int) -> int | None:
        """计算 m 的整数 n 次方根，即 k 满足 k^n = m。非完全次方返回 None。

        使用二分查找 + 乘法溢出保护，而非 ``int(m ** (1/n))`` 后验证，
        以避免大整数浮点转换的精度损失。
        负数仅允许奇数次方根。
        """
        if m == 0:
            return 0

        if m == 1:
            return m

        if m == -1:
            if n % 2 == 0:
                return None
            return m

        符号 = 1
        if m < 0:
            if n % 2 == 0:
                return None
            符号 = -1
            m = -m

        左, 右 = 0, m

        # 对较大 n 收紧右边界：k = m^(1/n) ≤ 2^(⌈bit_length / n⌉)
        if n > 1 and m > 1:
            右 = min(右, 1 << ((m.bit_length() + n - 1) // n))

        while 左 <= 右:
            中 = (左 + 右) // 2

            结果 = 1
            基 = 中
            指数 = n
            溢出 = False

            while 指数 > 0:
                if 指数 & 1:
                    if 结果 > m // 基:
                        溢出 = True
                        break
                    结果 *= 基
                    if 结果 > m:
                        溢出 = True
                        break

                指数 >>= 1
                if 指数 > 0:
                    if 基 > m // 基:
                        溢出 = True
                        break
                    基 *= 基

            if 溢出 or 结果 > m:
                右 = 中 - 1
            elif 结果 < m:
                左 = 中 + 1
            else:
                return 符号 * 中

        return None

    def __pow__(self, other: int | g进数) -> g进数:
        """幂运算 ``self ** other``。

        - 整数指数：直接对分子/分母分别乘方（负指数则先取倒）。
        - 有理指数：分子/分母各自开 other.分母 次方根后再乘方。
          非完全次方根会抛出 ValueError。
        """
        if not isinstance(other, (int, g进数)):
            return NotImplemented

        if isinstance(other, int):
            if other >= 0:
                新分子 = self._分子值 ** other
                新分母 = self._分母值 ** other
            else:
                新分母 = self._分子值 ** (-other)
                新分子 = self._分母值 ** (-other)
        else:
            新分子 = g进数._整数根(self._分子值, other._分母值)
            新分母 = g进数._整数根(self._分母值, other._分母值)
            if 新分子 is None or 新分母 is None:
                raise ValueError(f"无法在有理数中开{other._分母值}开方")
            if other._分子值 >= 0:
                新分子 = 新分子 ** other._分子值
                新分母 = 新分母 ** other._分子值
            else:
                新分母, 新分子 = (
                    新分子 ** (-other._分子值),
                    新分母 ** (-other._分子值),
                )
        return g进数._快速创建(新分子, 新分母, self._进制, self._符号表)

    def __rpow__(self, other: int) -> g进数:
        """``int ** self``：整数开分母次方后乘方。"""
        if not isinstance(other, int):
            return NotImplemented

        根 = g进数._整数根(other, self._分母值)
        if 根 is None:
            raise ValueError(f"无法在有理数中开{self._分母值}开方")
        if self._分子值 >= 0:
            新分子 = 根 ** self._分子值
            新分母 = 1
        else:
            新分子 = 1
            新分母 = 根 ** (-self._分子值)
        return g进数._快速创建(新分子, 新分母, self._进制, self._符号表)

    # -- 取模 & 整除（仅限分母为 1 的"整数"）-------------------------------

    def __mod__(self, other: int | g进数) -> g进数:
        if not isinstance(other, (int, g进数)):
            return NotImplemented

        if isinstance(other, int):
            if self._分母值 != 1:
                raise ValueError("取模只允许分母值为1")
            新分子 = self._分子值 % other
        else:
            if self._分母值 != 1 or other._分母值 != 1:
                raise ValueError("取模只允许分母值为1")
            新分子 = self._分子值 % other._分子值
        return g进数._快速创建(新分子, 1, self._进制, self._符号表)

    def __rmod__(self, other: int) -> g进数:
        if not isinstance(other, int):
            return NotImplemented

        if self._分母值 != 1:
            raise ValueError("取模只允许分母值为1")

        新分子 = other % self._分子值
        return g进数._快速创建(新分子, 1, self._进制, self._符号表)

    def __floordiv__(self, other: int | g进数) -> g进数:
        if not isinstance(other, (int, g进数)):
            return NotImplemented

        if isinstance(other, int):
            if self._分母值 != 1:
                raise ValueError("整除只允许分母值为1")
            新分子 = self._分子值 // other
        else:
            if self._分母值 != 1 or other._分母值 != 1:
                raise ValueError("整除只允许分母值为1")
            新分子 = self._分子值 // other._分子值
        return g进数._快速创建(新分子, 1, self._进制, self._符号表)

    def __rfloordiv__(self, other: int) -> g进数:
        if not isinstance(other, int):
            return NotImplemented

        if self._分母值 != 1:
            raise ValueError("整除只允许分母值为1")

        新分子 = other // self._分子值
        return g进数._快速创建(新分子, 1, self._进制, self._符号表)

    # -- 比较运算符 ---------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (int, g进数)):
            return False

        if isinstance(other, int):
            if self._分母值 != 1:
                return False
            return self._分子值 == other
        else:
            return self._分子值 == other._分子值 and self._分母值 == other._分母值

    def __lt__(self, other: int | g进数) -> bool:
        if not isinstance(other, (int, g进数)):
            return NotImplemented

        if isinstance(other, int):
            return self._分子值 < other * self._分母值
        else:
            return self._分子值 * other._分母值 < self._分母值 * other._分子值

    def __gt__(self, other: int | g进数) -> bool:
        if not isinstance(other, (int, g进数)):
            return NotImplemented
        return not self.__lt__(other) and not self.__eq__(other)

    def __le__(self, other: int | g进数) -> bool:
        if not isinstance(other, (int, g进数)):
            return NotImplemented
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other: int | g进数) -> bool:
        if not isinstance(other, (int, g进数)):
            return NotImplemented
        return not self.__lt__(other)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    # -- 浮点展开（当前进制下的小数表示）------------------------------------

    def 浮点数(self, 截断位数: int = 30) -> str:
        """返回当前进制下的小数表示，含循环节标记。

        有限小数直接展开如 ``"B.32"``；无限小数用括号标记循环节如 ``"0.1(6)"``；
        达到截断位数仍未发现循环则末尾加 ``"..."``。
        """
        符号 = "-" if self._分子值 < 0 else ""

        整数部分 = abs(self._分子值) // self._分母值
        整数部分表示 = self._十进转n(整数部分)

        余数 = abs(self._分子值) % self._分母值

        if 余数 == 0:
            return 符号 + 整数部分表示 + "." + self._符号表[0]

        余数位置: dict[int, int] = {}
        小数位列表: list[int] = []
        循环开始位置 = -1

        for 位置 in range(截断位数):
            if 余数 == 0:
                break

            if 余数 in 余数位置:
                循环开始位置 = 余数位置[余数]
                break

            余数位置[余数] = 位置

            余数 *= self._进制
            商 = 余数 // self._分母值
            小数位列表.append(商)
            余数 = 余数 % self._分母值

        小数位字符列表 = [self._符号表[数字] for 数字 in 小数位列表]

        if 循环开始位置 >= 0:
            非循环部分 = 小数位字符列表[:循环开始位置]
            循环部分 = 小数位字符列表[循环开始位置:]

            if 非循环部分:
                小数部分表示 = "".join(非循环部分) + "(" + "".join(循环部分) + ")"
            else:
                小数部分表示 = "(" + "".join(循环部分) + ")"
        else:
            小数部分表示 = "".join(小数位字符列表)
            if 余数 != 0 and len(小数位列表) >= 截断位数:
                小数部分表示 += "..."

        if 小数部分表示:
            return 符号 + 整数部分表示 + "." + 小数部分表示
        else:
            return 符号 + 整数部分表示

    # -- 连分数逼近（从进制小数串反推有理数）--------------------------------

    @staticmethod
    def 有理数逼近(
        字符串: str,
        进制: int | None = None,
        符号表: str | None = None,
    ) -> g进数:
        """从进制小数串（有限 / 循环 / 截断）反向重构最简有理数。

        支持三种格式：
        - ``"0.5"`` → 有限小数
        - ``"0.(3)"`` → 纯循环小数
        - ``"0.142857..."`` → 截断小数（连分数逼近）
        """
        进制 = 进制 if 进制 is not None else g进数._默认进制
        符号表 = 符号表 if 符号表 is not None else g进数._默认符号表

        def 连分数展开(p: int, q: int) -> list[int]:
            """p/q 的连分数展开系数 [a0, a1, a2, ...]（辗转相除）。"""
            结果: list[int] = []
            while q != 0:
                a = p // q
                结果.append(a)
                p, q = q, p - a * q
            return 结果

        def 连分数截断(列表: list[int]) -> list[int]:
            """在连分数系数的"最大跳跃"处截断以得到最佳有理逼近。

            找到第一个 a[i] 使得 a[i] / max(a[i-1], 1) 达到历史最大值，
            此处截断给出 π 等常数的经典有理逼近。
            """
            if len(列表) < 2:
                return 列表[:]

            历史最大比例, 对应的索引 = 1, 0
            for i in range(1, len(列表)):
                if 列表[i] >= 历史最大比例 * max(列表[i - 1], 1):
                    历史最大比例 = 列表[i] // max(列表[i - 1], 1)
                    对应的索引 = i
            return 列表[:对应的索引]

        def 连分数重建(列表: list[int]) -> tuple[int, int]:
            """从连分数系数恢复 (分子, 分母)。"""
            if not 列表:
                return 0, 1

            n = len(列表)
            分子 = 列表[-1]
            分母 = 1

            for i in range(n - 2, -1, -1):
                新分子 = 列表[i] * 分子 + 分母
                新分母 = 分子
                分子, 分母 = 新分子, 新分母

            return 分子, 分母

        def 解析可省略位串(位串: str) -> int:
            """解析整数/小数的可省略部分，空串按 0 处理。"""
            if 位串 == "":
                return 0
            return g进数(位串, 1, 进制, 符号表)._分子值

        符号 = 1
        if "-" in 字符串:
            if "-" in 字符串[1:]:
                raise ValueError("负号仅允许出现在字符串开头")
            字符串 = 字符串[1:]
            符号 = -1
        if 字符串 == "" or 字符串 == ".":
            raise ValueError("输入字符串不能为空")
        if 字符串.endswith("..."):
            字符串 = 字符串[:-3]
            if 字符串 == "" or 字符串 == ".":
                raise ValueError("输入字符串不能为空")
            整数部分, _, 小数部分 = 字符串.partition(".")
            if "." in 小数部分:
                raise ValueError("除尾部的省略号外，必须有且只有一个'.'")
            解析整数 = 解析可省略位串(整数部分)
            解析小数 = 解析可省略位串(小数部分)

            展开结果 = 连分数展开(
                解析小数 + 解析整数 * 进制 ** len(小数部分), 进制 ** len(小数部分)
            )
            分子值, 分母值 = 连分数重建(连分数截断(展开结果))
            return g进数(符号 * 分子值, 分母值, 进制, 符号表)
        else:
            if "(" in 字符串 and ")" in 字符串:
                左括号前, _, 左括号后 = 字符串.partition("(")
                循环节, _, 右括号后 = 左括号后.partition(")")
                if 右括号后:
                    raise ValueError("精确的表示必须以循环节结束")
                循环节值 = g进数(循环节, 1, 进制, 符号表)._分子值
                循环节系数 = 进制 ** len(循环节) - 1
            else:
                循环节值 = 0
                左括号前 = 字符串
                循环节系数 = 1

            整数部分, _, 不循环部分 = 左括号前.partition(".")
            整数值 = 解析可省略位串(整数部分)
            不循环值 = 解析可省略位串(不循环部分)
            分子值 = (
                整数值 * 进制 ** len(不循环部分) + 不循环值
            ) * 循环节系数 + 循环节值
            分母值 = 进制 ** len(不循环部分) * 循环节系数
            return g进数(符号 * 分子值, 分母值, 进制, 符号表)

    # -- g-adic 展开与重构 -------------------------------------------------

    def padic表示(self, 截断位数: int = 30) -> str:
        """返回当前有理数在当前进制下的 g-adic 展开字符串。

        g-adic 数向左无限延伸（"小数点"右侧为有限位）。
        循环节用括号标记，如 ``"(6).9"`` 对应 10-adic 下的 7/30；
        截断不足以发现循环时末尾加 ``"..."``。
        """
        负指数 = 0
        分子, 分母 = self._分子值, self._分母值
        进制, 符号表 = self._进制, self._符号表

        # 消去分母与进制的公因子，转化为负指数
        while (公因子 := gcd(分母, 进制)) != 1:
            分子 = (进制 // 公因子) * 分子
            分母 = ((进制 // 公因子) * 分母) // 进制
            负指数 += 1

        # 此时 gcd(分母, 进制) = 1，分母存在模逆元
        逆元 = pow(分母, -1, 进制)

        余数字典: dict[int, int] = {}
        商列表: list[int] = []
        索引 = 0
        while 索引 <= 截断位数 and 分子 not in 余数字典:
            余数字典[分子] = 索引
            商 = (逆元 * 分子) % 进制
            分子 = (分子 - 商 * 分母) // 进制
            商列表.append(商)
            索引 += 1

        字符列表 = [符号表[商值] for 商值 in 商列表]
        if 索引 <= 截断位数:
            循环部分 = 字符列表[余数字典[分子] :]
            if 负指数 != 0:
                if len(字符列表) < 负指数:
                    扩展次数 = (负指数 - len(字符列表)) // len(循环部分) + 1
                    字符列表.extend(循环部分 * 扩展次数)

                整数部分 = 字符列表[负指数:]

                # 调整循环节使表示规范化：如 (123)124.54 → (312)4.54
                while 整数部分 and 整数部分[-1] == 循环部分[-1]:
                    整数部分.pop()
                    循环部分 = 循环部分[-1:] + 循环部分[:-1]
                if len(循环部分) == 1 and 循环部分[0] == 符号表[0]:
                    if len(整数部分) == 0:
                        整数部分.append(符号表[0])
                    结果列表 = 字符列表[:负指数] + ["."] + 整数部分
                else:
                    结果列表 = (
                        字符列表[:负指数]
                        + ["."]
                        + 整数部分
                        + [")"]
                        + 循环部分
                        + ["("]
                    )

            else:
                if len(循环部分) == 1 and 循环部分[0] == 符号表[0]:
                    结果列表 = 字符列表[: 余数字典[分子]]
                else:
                    结果列表 = (
                        字符列表[: 余数字典[分子]] + [")"] + 循环部分 + ["("]
                    )
        elif 负指数 != 0:
            if 负指数 >= len(字符列表):
                raise ValueError("截断位数不足以计算完小数部分")
            结果列表 = 字符列表[:负指数] + ["."] + 字符列表[负指数:] + ["..."]
        else:
            结果列表 = 字符列表 + ["..."]

        反转列表 = 结果列表[::-1]
        return "".join(反转列表)

    @staticmethod
    def 有理数重构(
        字符串: str,
        进制: int | None = None,
        符号表: str | None = None,
    ) -> g进数:
        """从 g-adic 展开字符串反向重构有理数。

        支持循环节格式 ``"(6).9"`` 与截断格式 ``"...66.9"``。
        使用有理数重建算法（基于扩展欧几里得）。
        """
        进制 = 进制 if 进制 is not None else g进数._默认进制
        符号表 = 符号表 if 符号表 is not None else g进数._默认符号表

        def 有理数重建(t: int, M: int) -> tuple[int, int]:
            """给定 t 和 M，求 (r, u) 使得 r ≡ t * u (mod M) 且 |r|, |u| 尽可能小。

            用于从截断的 g-adic 表示中恢复原始有理数。
            """
            if t == 0:
                return 0, 1

            r_p, r = M, t
            u_p, u = 0, 1
            r_b, r_bp = 1, 1
            r_m, u_m = 0, 1

            while True:
                q = r_p // r
                r_p, r, r_b = r, r_p - q * r, r_p // r
                u_p, u = u, u_p - q * u
                if abs(r_b) >= abs(r_bp):
                    r_m, u_m = r_p, u_p
                    r_bp = r_b
                if r == 0:
                    break

            return r_m, u_m

        def 解析可省略位串(位串: str) -> int:
            """解析整数/小数的可省略部分，空串按 0 处理。"""
            if 位串 == "":
                return 0
            return g进数(位串, 1, 进制, 符号表)._分子值

        if "-" in 字符串:
            raise ValueError("标准的p-adic截断没有符号")

        if 字符串.startswith("..."):
            字符串 = 字符串[3:]
            if "." in 字符串:
                整数部分, _, 小数部分 = 字符串.partition(".")
            else:
                整数部分 = 字符串
                小数部分 = ""
            解析整数 = 解析可省略位串(整数部分)
            解析小数 = 解析可省略位串(小数部分)
            分子, 分母 = 有理数重建(
                解析整数 * 进制 ** len(小数部分) + 解析小数,
                进制 ** len(整数部分 + 小数部分),
            )
            return g进数(分子, 分母 * 进制 ** len(小数部分), 进制, 符号表)

        else:
            if "(" in 字符串 and ")" in 字符串:
                左括号前, _, 左括号后 = 字符串.partition("(")
                循环节, _, 右括号后 = 左括号后.partition(")")
                if 左括号前:
                    raise ValueError("精确表示必须以循环节开始")
                循环节值 = g进数(循环节, 1, 进制, 符号表)._分子值
                循环节系数 = 进制 ** len(循环节) - 1
            else:
                循环节值 = 0
                右括号后 = 字符串
                循环节系数 = 1

            整数部分, _, 小数部分 = 右括号后.partition(".")
            整数值 = 解析可省略位串(整数部分)
            小数值 = 解析可省略位串(小数部分)
            分子值 = -循环节值 * 进制 ** len(整数部分 + 小数部分) + 循环节系数 * (
                整数值 * 进制 ** len(小数部分) + 小数值
            )
            分母值 = 进制 ** len(小数部分) * 循环节系数
            return g进数(分子值, 分母值, 进制, 符号表)
