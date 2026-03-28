"""
多进制有理数模块
================
提供在任意进制下表示和运算有理数的能力，支持：
- 任意进制（2 到符号表长度）下的有理数表示
- 自定义符号表
- 完整的有理数算术运算（加减乘除、幂、模、整除）
- 进制间转换
- 小数展开（含循环节检测）
- g-adic（g进数）表示与有理数重构
"""

from __future__ import annotations
from typing import Optional


class 多进制有理数:
    """
    在任意进制下表示有理数（分数）的类。

    该类将有理数存储为最简分数形式（分子、分母互质，分母为正），
    并支持在指定进制和符号表下进行字符串表示与解析。
    支持完整的算术运算符重载，以及 g-adic 展开与逼近。

    类属性
    ------
    默认进制 : int
        未指定进制时使用的进制，默认为 10（十进制）。
    默认符号表 : str
        未指定符号表时使用的字符集，包含 0-9 及 A-Z，
        共 36 个字符，支持最高 36 进制。

    实例属性（内部，通过 property 访问）
    ------------------------------------
    _进制 : int
        当前实例使用的进制。
    _符号表 : str
        当前实例使用的符号表字符串。
    _分子值 : int
        有理数分子的十进制整数值（可为负）。
    _分母值 : int
        有理数分母的十进制正整数值（始终 > 0）。
    _分子表示 : str | None
        分子在当前进制下的字符串表示，懒加载缓存。
    _分母表示 : str | None
        分母在当前进制下的字符串表示，懒加载缓存。
    _映射字典 : dict[str, int] | None
        符号表字符到数值的映射，懒加载缓存。

    示例
    ----
    >>> q = 多进制有理数(1, 3)          # 十进制下的 1/3
    >>> print(q)                         # "1/3"
    >>> q.浮点数()                       # "0.(3)"
    >>> q.gadic表示()                    # "(3).0"（10-adic 展开）

    >>> q2 = 多进制有理数("FF", "10", 16)  # 十六进制下的 255/16
    >>> print(q2)                          # "FF/10"

    注意
    ----
    - 分母为 0 时抛出 ZeroDivisionError。
    - 分子/分母可以是十进制整数，也可以是当前进制下的字符串。
    - 运算结果保持 self 的进制和符号表。
    - 该类对象为不可变语义（所有运算返回新对象）。
    """

    默认进制: int = 10
    默认符号表: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    __slots__ = (
        "_进制", "_符号表", "_分子值", "_分子表示",
        "_分母值", "_分母表示", "_映射字典"
    )

    def __init__(
        self,
        分子: int | str,
        分母: int | str = 1,
        进制: Optional[int] = None,
        符号表: Optional[str] = None,
    ) -> None:
        """
        初始化多进制有理数。

        将输入的分子和分母解析为最简分数，并验证进制与符号表的合法性。
        自动化简：计算最大公因子并约分，分母始终保持正数。

        参数
        ----
        分子 : int | str
            有理数的分子。
            - 若为 ``int``，直接使用其十进制值。
            - 若为 ``str``，按当前进制解析（允许前缀 ``-`` 表示负数）。
        分母 : int | str, 默认 1
            有理数的分母，规则同分子。
        进制 : int, 可选
            使用的进制（2 到符号表长度）。
            若为 ``None``，则使用 ``默认进制``（10）。
        符号表 : str, 可选
            自定义符号表字符串，第 i 个字符表示数值 i。
            若为 ``None``，则使用 ``默认符号表``。

        抛出
        ----
        ZeroDivisionError
            分母化简后为 0 时抛出。
        TypeError
            进制不是 int，或符号表不是 str，
            或分子/分母既非 int 也非 str 时抛出。
        ValueError
            符号表包含非法字符（``.`` ``/`` 空格 ``\\`` ``-``），
            符号表有重复字符，进制超出符号表长度范围，
            或输入字符串包含非法字符时抛出。

        示例
        ----
        >>> 多进制有理数(1, 2)            # 1/2，十进制
        >>> 多进制有理数("A", "5", 16)   # 十六进制下 10/5 = 2
        >>> 多进制有理数(6, 4)            # 自动约分为 3/2
        """
        self._进制: int = 进制 if 进制 is not None else self.默认进制
        self._符号表: str = 符号表 if 符号表 is not None else self.默认符号表
        self._验证进制和符号表()
        self._分子表示: Optional[str] = None
        self._分母表示: Optional[str] = None
        self._映射字典: Optional[dict[str, int]] = None

        分母整数, 分母符号 = self._处理输入(分母)
        分子整数, 分子符号 = self._处理输入(分子)
        公因子 = 多进制有理数._欧几里得算法(分母整数, 分子整数)
        分母整数 //= 公因子
        分子整数 //= 公因子
        self._分母值: int = 分母整数
        self._分子值: int = 分子整数 * 分母符号 * 分子符号
        if self._分母值 == 0:
            raise ZeroDivisionError("分母不能为0")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def 进制(self) -> int:
        """当前实例使用的进制（只读）。"""
        return self._进制

    @property
    def 符号表(self) -> str:
        """当前实例使用的符号表字符串（只读）。"""
        return self._符号表

    @property
    def 分子值(self) -> int:
        """有理数分子的十进制整数值，可为负（只读）。"""
        return self._分子值

    @property
    def 分母值(self) -> int:
        """有理数分母的十进制正整数值，始终 > 0（只读）。"""
        return self._分母值

    @property
    def 分子表示(self) -> str:
        """
        分子在当前进制下的字符串表示（只读，懒加载）。

        负数以 ``-`` 前缀开头，数值部分按当前进制编码。

        示例
        ----
        >>> 多进制有理数(-10, 1, 16).分子表示   # "-A"
        >>> 多进制有理数(255, 1, 16).分子表示   # "FF"
        """
        if self._分子表示 is None:
            self._分子表示 = "-" if self._分子值 < 0 else ""
            self._分子表示 += self._十进转n(abs(self._分子值))
        return self._分子表示

    @property
    def 分母表示(self) -> str:
        """
        分母在当前进制下的字符串表示（只读，懒加载）。

        分母始终为正，因此不含符号前缀。

        示例
        ----
        >>> 多进制有理数(1, 16, 16).分母表示   # "10"
        """
        if self._分母表示 is None:
            self._分母表示 = self._十进转n(abs(self._分母值))
        return self._分母表示

    # ------------------------------------------------------------------
    # 魔术方法：字符串表示
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        返回有理数的简洁字符串表示。

        - 整数（分母为 1）：仅返回分子表示，如 ``"FF"``。
        - 分数：返回 ``"分子/分母"`` 格式，如 ``"1/3"``。

        返回
        ----
        str
            当前进制下的有理数字符串。
        """
        return (
            f"{self.分子表示}/{self.分母表示}"
            if self._分母值 != 1
            else self.分子表示
        )

    def __repr__(self) -> str:
        """
        返回有理数的详细调试表示。

        同时包含十进制内部值和当前进制下的字符串表示。

        返回
        ----
        str
            格式：``"十进制: 分子/分母, 当前进制为: N, 表示: 分子表示/分母表示"``

        示例
        ----
        >>> repr(多进制有理数(1, 3))
        '十进制: 1/3, 当前进制为: 10, 表示: 1/3'
        """
        return (
            f"十进制: {self._分子值}/{self._分母值}, "
            f"当前进制为: {self._进制}, 表示: {self.分子表示}/{self.分母表示}"
        )

    # ------------------------------------------------------------------
    # 内部验证与解析方法
    # ------------------------------------------------------------------

    def _验证进制和符号表(self) -> None:
        """
        验证进制和符号表的合法性。

        检查项：
        - 进制必须为 ``int`` 类型。
        - 符号表必须为 ``str`` 类型。
        - 符号表中不允许出现 ``.`` ``/`` 空格 ``\\`` ``-``（保留分隔符）。
        - 符号表中不允许有重复字符。
        - 进制必须在 ``[2, len(符号表)]`` 范围内。

        抛出
        ----
        TypeError
            进制或符号表类型不符时抛出。
        ValueError
            符号表含非法/重复字符，或进制超出范围时抛出。
        """
        if not isinstance(self._进制, int):
            raise TypeError("进制必须是int类型")
        if not isinstance(self._符号表, str):
            raise TypeError("符号表必须是str")
        if any(char in r"./ \-" for char in self._符号表):
            raise ValueError("符号表中不允许有点，空格，斜杠，反斜杠和减号")
        if len(set(self._符号表)) != len(self._符号表):
            raise ValueError("符号表重复")
        if not (2 <= self._进制 <= len(self._符号表)):
            raise ValueError(
                f"进制{self._进制}不合法！"
                f"符号表长度为{len(self._符号表)}，"
                f"进制需在2到该长度之间"
            )

    def _处理输入(self, 值: int | str) -> tuple[int, int]:
        """
        将分子或分母的输入值统一解析为 ``(绝对值, 符号)`` 二元组。

        参数
        ----
        值 : int | str
            待解析的分子或分母。
            - ``int``：直接取绝对值，符号为 ±1。
            - ``str``：先验证字符合法性，再按当前进制解析为整数。

        返回
        ----
        tuple[int, int]
            ``(绝对值, 符号)``，其中符号为 ``1`` 或 ``-1``。

        抛出
        ----
        TypeError
            输入既非 ``int`` 也非 ``str`` 时抛出。
        ValueError
            字符串不合法（含非法字符、仅含负号等）时抛出。
        """
        if isinstance(值, int):
            return abs(值), (1 if 值 >= 0 else -1)
        if isinstance(值, str):
            self._验证输入字符串(值)
            符号 = 1
            if 值.startswith('-'):
                符号 = -1
                值 = 值[1:]
            return self._n进转十(值), 符号
        raise TypeError("分子和分母必须是整数或者字符串")

    def _验证输入字符串(self, 字符串: str) -> None:
        """
        验证输入字符串在当前进制下的合法性。

        检查项：
        - 不能仅为 ``"-"``。
        - ``-`` 只能出现在首位。
        - 去掉符号后，所有字符必须属于当前进制的合法字符集。

        参数
        ----
        字符串 : str
            待验证的字符串（允许前缀 ``-``）。

        抛出
        ----
        ValueError
            字符串格式不合法或包含当前进制外的字符时抛出。
        """
        if 字符串 == "-":
            raise ValueError("输入字符串不能仅包含负号")
        if '-' in 字符串[1:]:
            raise ValueError("负号仅允许出现在字符串开头")
        字符集合 = set(self._符号表[:self._进制])
        清理后字符 = 字符串.lstrip('-')
        if not all(字符 in 字符集合 for 字符 in 清理后字符):
            raise ValueError(
                f"输入字符串{字符串}包含非法字符！"
                f"当前进制{self._进制}的合法集合为：{''.join(字符集合)}"
            )

    def _读取映射(self) -> dict[str, int]:
        """
        获取符号表字符到整数值的映射字典（懒加载）。

        首次调用时构建并缓存 ``{字符: 索引}`` 映射，后续复用缓存。

        返回
        ----
        dict[str, int]
            字符到其在符号表中索引的映射。
        """
        if self._映射字典 is None:
            self._映射字典 = {c: idx for idx, c in enumerate(self._符号表)}
        return self._映射字典

    def _十进转n(self, 值: int) -> str:
        """
        将非负十进制整数转换为当前进制的字符串表示。

        参数
        ----
        值 : int
            待转换的非负整数（``值 >= 0``）。

        返回
        ----
        str
            当前进制下的字符串，如十六进制下 255 → ``"FF"``。
            若 ``值 == 0``，返回符号表第 0 个字符（通常为 ``"0"``）。
        """
        if 值 == 0:
            return self._符号表[0]
        进制 = self._进制
        符号表 = self._符号表
        字符表: list[str] = []
        while 值 > 0:
            字符表.append(符号表[值 % 进制])
            值 = 值 // 进制
        return ''.join(reversed(字符表))

    def _n进转十(self, 字符串: str) -> int:
        """
        将当前进制的字符串解析为十进制整数。

        使用 Horner 法（秦九韶算法的逆向累加）从低位到高位计算。

        参数
        ----
        字符串 : str
            当前进制下的非负整数字符串（不含符号）。

        返回
        ----
        int
            对应的非负十进制整数。

        示例
        ----
        >>> # 十六进制实例下：
        >>> self._n进转十("FF")   # 255
        """
        字典映射 = self._读取映射()
        进制 = self._进制
        十进值 = 0
        当前基 = 1
        for char in reversed(字符串):
            十进值 += 字典映射[char] * 当前基
            当前基 *= 进制
        return 十进值

    # ------------------------------------------------------------------
    # 类方法与静态方法
    # ------------------------------------------------------------------

    @classmethod
    def _快速创建(
        cls,
        分子值: int,
        分母值: int,
        进制: int,
        符号表: str,
    ) -> 多进制有理数:
        """
        快速创建实例，跳过进制和符号表的重复验证。

        仅用于内部运算（如加减乘除），此时进制和符号表已经过验证。
        会自动执行：分母符号修正、最大公因子约分。

        参数
        ----
        分子值 : int
            新实例的分子（带符号）。
        分母值 : int
            新实例的分母（允许为负，内部会修正为正）。
        进制 : int
            使用的进制（已验证合法）。
        符号表 : str
            使用的符号表（已验证合法）。

        返回
        ----
        多进制有理数
            化简后的新实例。

        抛出
        ----
        ZeroDivisionError
            分母值为 0 时抛出。
        """
        if 分母值 == 0:
            raise ZeroDivisionError("分母不能为0")
        if 分母值 < 0:
            分母值, 分子值 = -分母值, -分子值

        公因子 = 多进制有理数._欧几里得算法(分母值, abs(分子值))
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
    def _欧几里得算法(a: int, b: int) -> int:
        """
        用辗转相除法（欧几里得算法）计算两个非负整数的最大公因子。

        参数
        ----
        a : int
            第一个非负整数。
        b : int
            第二个非负整数。

        返回
        ----
        int
            ``gcd(a, b)``，若两者均为 0 则返回 0。
        """
        while b != 0:
            a, b = b, a % b
        return a

    @staticmethod
    def _整数根(m: int, n: int) -> Optional[int]:
        """
        尝试计算整数 m 的 n 次整数根，即求满足 ``k^n == m`` 的整数 k。

        采用二分查找，结合快速幂与溢出检测，效率高于暴力枚举。

        参数
        ----
        m : int
            被开方数（可为负整数，当 n 为奇数时有意义）。
        n : int
            根次数，正整数。

        返回
        ----
        int | None
            若存在整数 k 使得 ``k^n == m``，返回 k；否则返回 ``None``。

        特殊情况
        --------
        - ``m == 0`` → 返回 ``0``。
        - ``m == 1`` → 返回 ``1``。
        - ``m == -1`` 且 n 为奇数 → 返回 ``-1``；n 为偶数 → 返回 ``None``。
        - m < 0 且 n 为偶数 → 返回 ``None``（负数无实数偶次根）。

        示例
        ----
        >>> 多进制有理数._整数根(8, 3)   # 2
        >>> 多进制有理数._整数根(2, 2)   # None（√2 不是整数）
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
                    if 结果 > m // 基 if 基 != 0 else False:
                        溢出 = True
                        break
                    结果 *= 基
                    if 结果 > m:
                        溢出 = True
                        break
                指数 >>= 1
                if 指数 > 0:
                    if 基 > m // 基 if 基 != 0 else False:
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

    # ------------------------------------------------------------------
    # 进制转换
    # ------------------------------------------------------------------

    def 进制转换(
        self,
        进制: Optional[int] = None,
        符号表: Optional[str] = None,
    ) -> 多进制有理数:
        """
        将当前有理数转换为另一个进制或符号表下的表示。

        数值不变，仅改变进制和符号表。若参数为 ``None``，则使用类默认值。

        参数
        ----
        进制 : int, 可选
            目标进制。``None`` 则用 ``默认进制``。
        符号表 : str, 可选
            目标符号表。``None`` 则用 ``默认符号表``。

        返回
        ----
        多进制有理数
            与 self 数值相同、但使用新进制和符号表的新实例。

        示例
        ----
        >>> q = 多进制有理数(255, 1, 10)
        >>> q.进制转换(16)   # 十六进制下的 255，即 "FF"
        """
        return 多进制有理数(self._分子值, self._分母值, 进制, 符号表)

    # ------------------------------------------------------------------
    # 类型转换魔术方法
    # ------------------------------------------------------------------

    def __float__(self) -> float:
        """
        转换为浮点数。

        返回
        ----
        float
            ``分子 / 分母`` 的浮点数结果，可能有精度损失。
        """
        return self._分子值 / self._分母值

    def __bool__(self) -> bool:
        """
        布尔值转换。

        返回
        ----
        bool
            分子为 0 时返回 ``False``，否则返回 ``True``。
        """
        return bool(self._分子值)

    def __hash__(self) -> int:
        """
        计算哈希值，使对象可用于集合和字典键。

        - 整数（分母为 1）：哈希与对应 ``int`` 一致。
        - 分数：哈希为 ``(分子, 分母)`` 元组的哈希。

        返回
        ----
        int
            哈希值。
        """
        if self._分母值 == 1:
            return hash(self._分子值)
        return hash((self._分子值, self._分母值))

    def __int__(self) -> int:
        """
        截断取整（向零方向）。

        返回
        ----
        int
            ``分子 // 分母``（Python 整除，向下取整）。
        """
        return self._分子值 // self._分母值

    def __abs__(self) -> 多进制有理数:
        """
        取绝对值。

        返回
        ----
        多进制有理数
            与 self 进制和符号表相同，但分子取绝对值的新实例。
        """
        return 多进制有理数(abs(self._分子值), self._分母值, self._进制, self._符号表)

    # ------------------------------------------------------------------
    # 算术运算魔术方法
    # ------------------------------------------------------------------

    def __add__(self, other: int | 多进制有理数) -> 多进制有理数:
        """
        加法运算：``self + other``。

        支持与 ``int`` 和 ``多进制有理数`` 相加。
        结果使用 self 的进制和符号表。

        参数
        ----
        other : int | 多进制有理数
            加数。

        返回
        ----
        多进制有理数
            化简后的和。

        返回 NotImplemented
            当 other 类型不支持时。
        """
        if not isinstance(other, (int, 多进制有理数)):
            return NotImplemented
        if isinstance(other, int):
            新分子 = self._分子值 + self._分母值 * other
            新分母 = self._分母值
        else:
            新分子 = self._分子值 * other._分母值 + self._分母值 * other._分子值
            新分母 = self._分母值 * other._分母值
        return 多进制有理数._快速创建(新分子, 新分母, self._进制, self._符号表)

    def __radd__(self, other: int) -> 多进制有理数:
        """
        反向加法：``other + self``（当 other 不支持与 self 相加时触发）。

        由于加法有交换律，直接委托给 ``__add__``。
        注意：``int + 多进制有理数`` 的结果会保持 self 的进制和符号表。

        参数
        ----
        other : int
            左侧加数（仅支持 int）。

        返回
        ----
        多进制有理数
            化简后的和。
        """
        return self.__add__(other)

    def __neg__(self) -> 多进制有理数:
        """
        取反（一元负号）：``-self``。

        返回分子取负后的新实例，进制和符号表不变。
        由于属性不可变，创建新对象而非修改原对象。

        返回
        ----
        多进制有理数
            ``-self``。
        """
        return 多进制有理数._快速创建(
            -self._分子值, self._分母值, self._进制, self._符号表
        )

    def __sub__(self, other: int | 多进制有理数) -> 多进制有理数:
        """
        减法运算：``self - other``。

        直接计算而非通过 ``__neg__`` + ``__add__``，以减少中间对象开销。

        参数
        ----
        other : int | 多进制有理数
            减数。

        返回
        ----
        多进制有理数
            化简后的差。

        返回 NotImplemented
            当 other 类型不支持时。
        """
        if not isinstance(other, (int, 多进制有理数)):
            return NotImplemented
        if isinstance(other, int):
            新分子 = self._分子值 - self._分母值 * other
            新分母 = self._分母值
        else:
            新分子 = self._分子值 * other._分母值 - self._分母值 * other._分子值
            新分母 = self._分母值 * other._分母值
        return 多进制有理数._快速创建(新分子, 新分母, self._进制, self._符号表)

    def __rsub__(self, other: int) -> 多进制有理数:
        """
        反向减法：``other - self``。

        减法无交换律，不能直接复用 ``__sub__``。
        结果保持 self 的进制和符号表。

        参数
        ----
        other : int
            被减数（仅支持 int）。

        返回
        ----
        多进制有理数
            ``other - self`` 的化简结果。

        返回 NotImplemented
            当 other 不是 int 时。
        """
        if not isinstance(other, int):
            return NotImplemented
        新分子 = self._分母值 * other - self._分子值
        新分母 = self._分母值
        return 多进制有理数._快速创建(新分子, 新分母, self._进制, self._符号表)

    def __invert__(self) -> 多进制有理数:
        """
        取倒数（重载 ``~`` 运算符）：``~self`` 即 ``1/self``。

        交换分子和分母，进制和符号表不变。
        若 self 为 0，分子和分母互换后分母为 0 会在 ``_快速创建`` 中抛出异常。

        返回
        ----
        多进制有理数
            ``1 / self``。

        抛出
        ----
        ZeroDivisionError
            当 self 为 0 时。
        """
        return 多进制有理数._快速创建(
            self._分母值, self._分子值, self._进制, self._符号表
        )

    def __mul__(self, other: int | 多进制有理数) -> 多进制有理数:
        """
        乘法运算：``self * other``。

        参数
        ----
        other : int | 多进制有理数
            乘数。

        返回
        ----
        多进制有理数
            化简后的积。

        返回 NotImplemented
            当 other 类型不支持时。
        """
        if not isinstance(other, (int, 多进制有理数)):
            return NotImplemented
        if isinstance(other, int):
            新分子 = self._分子值 * other
            新分母 = self._分母值
        else:
            新分子 = self._分子值 * other._分子值
            新分母 = self._分母值 * other._分母值
        return 多进制有理数._快速创建(新分子, 新分母, self._进制, self._符号表)

    def __rmul__(self, other: int) -> 多进制有理数:
        """
        反向乘法：``other * self``。

        乘法有交换律，委托给 ``__mul__``。

        参数
        ----
        other : int
            左侧乘数。

        返回
        ----
        多进制有理数
            化简后的积。
        """
        return self.__mul__(other)

    def __truediv__(self, other: int | 多进制有理数) -> 多进制有理数:
        """
        真除法：``self / other``。

        直接计算而非通过 ``~other * self``，以提升效率。

        参数
        ----
        other : int | 多进制有理数
            除数，不能为 0。

        返回
        ----
        多进制有理数
            化简后的商。

        抛出
        ----
        ZeroDivisionError
            除数为 0 时抛出。

        返回 NotImplemented
            当 other 类型不支持时。
        """
        if not isinstance(other, (int, 多进制有理数)):
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
        return 多进制有理数._快速创建(新分子, 新分母, self._进制, self._符号表)

    def __rtruediv__(self, other: int) -> 多进制有理数:
        """
        反向真除法：``other / self``。

        参数
        ----
        other : int
            被除数（仅支持 int）。

        返回
        ----
        多进制有理数
            ``other / self`` 的化简结果。

        抛出
        ----
        ZeroDivisionError
            self 为 0 时抛出。

        返回 NotImplemented
            当 other 不是 int 时。
        """
        if not isinstance(other, int):
            return NotImplemented
        if self._分子值 == 0:
            raise ZeroDivisionError("被除数不能为0")
        新分子 = self._分母值 * other
        新分母 = self._分子值
        return 多进制有理数._快速创建(新分子, 新分母, self._进制, self._符号表)

    def __pow__(self, other: int | 多进制有理数) -> 多进制有理数:
        """
        幂运算：``self ** other``，要求结果在有理数范围内（封闭）。

        - ``other`` 为非负 ``int``：直接整数幂，结果始终为有理数。
        - ``other`` 为负 ``int``：先取倒数再幂。
        - ``other`` 为 ``多进制有理数``（即有理数次幂 p/q）：
          先对分子/分母求 q 次整数根，再取 p 次幂；
          若整数根不存在，则抛出 ValueError。

        参数
        ----
        other : int | 多进制有理数
            指数。

        返回
        ----
        多进制有理数
            化简后的幂结果。

        抛出
        ----
        ValueError
            有理数指数的分母次根不是整数时（结果无法在有理数中表示）。

        返回 NotImplemented
            当 other 类型不支持时。

        示例
        ----
        >>> 多进制有理数(4, 9) ** 多进制有理数(1, 2)   # (2/3)^1 = 2/3
        >>> 多进制有理数(2) ** -3                       # 1/8
        """
        if not isinstance(other, (int, 多进制有理数)):
            return NotImplemented
        if isinstance(other, int):
            if other >= 0:
                新分子 = self._分子值 ** other
                新分母 = self._分母值 ** other
            else:
                新分母 = self._分子值 ** (-other)
                新分子 = self._分母值 ** (-other)
        else:
            新分子 = 多进制有理数._整数根(self._分子值, other._分母值)
            新分母 = 多进制有理数._整数根(self._分母值, other._分母值)
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
        return 多进制有理数._快速创建(新分子, 新分母, self._进制, self._符号表)

    def __rpow__(self, other: int) -> 多进制有理数:
        """
        反向幂：``other ** self``，即整数的有理数次幂。

        计算 ``other^(分子/分母)``：先求 other 的分母次整数根，
        再取分子次幂。

        参数
        ----
        other : int
            底数（仅支持 int）。

        返回
        ----
        多进制有理数
            ``other ** self`` 的化简结果。

        抛出
        ----
        ValueError
            other 的 self.分母值 次整数根不存在时抛出。

        返回 NotImplemented
            当 other 不是 int 时。
        """
        if not isinstance(other, int):
            return NotImplemented
        新分子 = 多进制有理数._整数根(other, self._分母值)
        if 新分子 is None:
            raise ValueError(f"无法在有理数中开{self._分母值}开方")
        新分子 = 新分子 ** self._分子值
        return 多进制有理数._快速创建(新分子, 1, self._进制, self._符号表)

    def __mod__(self, other: int | 多进制有理数) -> 多进制有理数:
        """
        取模运算：``self % other``。

        仅允许分母为 1 的情况（即两侧均为整数）。

        参数
        ----
        other : int | 多进制有理数
            模数，分母必须为 1。

        返回
        ----
        多进制有理数
            ``self % other`` 的结果。

        抛出
        ----
        ValueError
            self 或 other 的分母不为 1 时抛出。

        返回 NotImplemented
            当 other 类型不支持时。
        """
        if not isinstance(other, (int, 多进制有理数)):
            return NotImplemented
        if isinstance(other, int):
            if self._分母值 != 1:
                raise ValueError("取模只允许分母值为1")
            新分子 = self._分子值 % other
        else:
            if self._分母值 != 1 or other._分母值 != 1:
                raise ValueError("取模只允许分母值为1")
            新分子 = self._分子值 % other._分子值
        return 多进制有理数._快速创建(新分子, 1, self._进制, self._符号表)

    def __rmod__(self, other: int) -> 多进制有理数:
        """
        反向取模：``other % self``。

        参数
        ----
        other : int
            被取模数（仅支持 int）。

        返回
        ----
        多进制有理数
            ``other % self`` 的结果。

        抛出
        ----
        ValueError
            self 的分母不为 1 时抛出。

        返回 NotImplemented
            当 other 不是 int 时。
        """
        if not isinstance(other, int):
            return NotImplemented
        if self._分母值 != 1:
            raise ValueError("取模只允许分母值为1")
        新分子 = other % self._分子值
        return 多进制有理数._快速创建(新分子, 1, self._进制, self._符号表)

    def __floordiv__(self, other: int | 多进制有理数) -> 多进制有理数:
        """
        整除运算：``self // other``。

        仅允许分母为 1 的情况（即两侧均为整数）。

        参数
        ----
        other : int | 多进制有理数
            除数，分母必须为 1。

        返回
        ----
        多进制有理数
            ``self // other`` 的结果（向下取整）。

        抛出
        ----
        ValueError
            self 或 other 的分母不为 1 时抛出。

        返回 NotImplemented
            当 other 类型不支持时。
        """
        if not isinstance(other, (int, 多进制有理数)):
            return NotImplemented
        if isinstance(other, int):
            if self._分母值 != 1:
                raise ValueError("整除只允许分母值为1")
            新分子 = self._分子值 // other
        else:
            if self._分母值 != 1 or other._分母值 != 1:
                raise ValueError("整除只允许分母值为1")
            新分子 = self._分子值 // other._分子值
        return 多进制有理数._快速创建(新分子, 1, self._进制, self._符号表)

    def __rfloordiv__(self, other: int) -> 多进制有理数:
        """
        反向整除：``other // self``。

        参数
        ----
        other : int
            被除数（仅支持 int）。

        返回
        ----
        多进制有理数
            ``other // self`` 的结果。

        抛出
        ----
        ValueError
            self 的分母不为 1 时抛出。

        返回 NotImplemented
            当 other 不是 int 时。
        """
        if not isinstance(other, int):
            return NotImplemented
        if self._分母值 != 1:
            raise ValueError("整除只允许分母值为1")
        新分子 = other // self._分子值
        return 多进制有理数._快速创建(新分子, 1, self._进制, self._符号表)

    # ------------------------------------------------------------------
    # 比较运算魔术方法
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """
        相等判断：``self == other``。

        - 与 ``int`` 比较：分母为 1 且分子相等时相等。
        - 与 ``多进制有理数`` 比较：分子和分母均相等（已最简化）。
        - 与其他类型比较：返回 ``False``。

        参数
        ----
        other : object
            比较对象。

        返回
        ----
        bool
        """
        if not isinstance(other, (int, 多进制有理数)):
            return False
        if isinstance(other, int):
            if self._分母值 != 1:
                return False
            return self._分子值 == other
        return self._分子值 == other._分子值 and self._分母值 == other._分母值

    def __lt__(self, other: int | 多进制有理数) -> bool:
        """
        小于比较：``self < other``。

        通过交叉相乘比较，避免浮点误差。

        参数
        ----
        other : int | 多进制有理数
            比较对象。

        返回
        ----
        bool

        返回 NotImplemented
            当 other 类型不支持时。
        """
        if not isinstance(other, (int, 多进制有理数)):
            return NotImplemented
        if isinstance(other, int):
            return self._分子值 < other * self._分母值
        return self._分子值 * other._分母值 < self._分母值 * other._分子值

    def __gt__(self, other: int | 多进制有理数) -> bool:
        """
        大于比较：``self > other``。

        通过 ``not (self < other or self == other)`` 实现。

        参数
        ----
        other : int | 多进制有理数
            比较对象。

        返回
        ----
        bool

        返回 NotImplemented
            当 other 类型不支持时。
        """
        if not isinstance(other, (int, 多进制有理数)):
            return NotImplemented
        return not self.__lt__(other) and not self.__eq__(other)

    def __le__(self, other: int | 多进制有理数) -> bool:
        """
        小于等于比较：``self <= other``。

        参数
        ----
        other : int | 多进制有理数
            比较对象。

        返回
        ----
        bool

        返回 NotImplemented
            当 other 类型不支持时。
        """
        if not isinstance(other, (int, 多进制有理数)):
            return NotImplemented
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other: int | 多进制有理数) -> bool:
        """
        大于等于比较：``self >= other``。

        参数
        ----
        other : int | 多进制有理数
            比较对象。

        返回
        ----
        bool

        返回 NotImplemented
            当 other 类型不支持时。
        """
        if not isinstance(other, (int, 多进制有理数)):
            return NotImplemented
        return not self.__lt__(other)

    def __ne__(self, other: object) -> bool:
        """
        不等判断：``self != other``。

        返回
        ----
        bool
        """
        return not self.__eq__(other)

    # ------------------------------------------------------------------
    # 小数展开
    # ------------------------------------------------------------------

    def 浮点数(self, 截断位数: int = 30) -> str:
        """
        将当前有理数转换为当前进制下的小数字符串表示。

        使用长除法逐位计算小数，并通过余数字典检测循环节。

        输出格式
        --------
        - 整数：``"整数部分.0"``，如 ``"A.0"``（十六进制下的 10）。
        - 有限小数：``"整数部分.小数部分"``，如 ``"0.5"``。
        - 循环小数：非循环部分 + ``(循环节)``，如 ``"3.1(4)"``
          表示 3.1444...（十进制下 7/15 的对应进制展开）。
        - 截断（超过 ``截断位数`` 未发现循环）：末尾加 ``"..."``，
          如 ``"3.A4..."``。
        - 负数：结果前加 ``"-"`` 符号。

        参数
        ----
        截断位数 : int, 默认 30
            最多计算的小数位数，超出后停止并添加 ``"..."``。

        返回
        ----
        str
            当前进制下带循环节标记的小数字符串。

        示例
        ----
        >>> 多进制有理数(1, 3).浮点数()        # "0.(3)"
        >>> 多进制有理数(1, 4).浮点数()        # "0.25"
        >>> 多进制有理数(7, 30, 16).浮点数()   # 十六进制下的展开
        """
        符号 = "-" if self._分子值 < 0 else ""
        整数部分 = abs(self._分子值) // self._分母值
        整数部分表示 = self._十进转n(整数部分)
        余数 = abs(self._分子值) % self._分母值
        if 截断位数 == 0:
            return 整数部分表示
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
        return 符号 + 整数部分表示

    # ------------------------------------------------------------------
    # 有理数逼近（静态方法）
    # ------------------------------------------------------------------

    @staticmethod
    def 有理数逼近(
        字符串: str,
        进制: Optional[int] = None,
        符号表: Optional[str] = None,
    ) -> 多进制有理数:
        """
        从小数字符串（含循环节或省略号）逼近还原有理数。

        支持两类输入格式：

        **精确格式**（含循环节括号）
            完整描述有理数的循环小数，如 ``"0.(3)"``（表示 1/3）、
            ``"0.1(6)"``（表示 1/6）。直接通过代数方法精确还原。

        **截断格式**（以 ``"..."`` 结尾）
            有限位截断，可能有精度损失，如 ``"0.333..."``。
            使用连分数展开 + 截断策略选择最优有理数逼近。

        参数
        ----
        字符串 : str
            小数字符串，支持：
            - 无循环节：``"1.5"``（有限小数）
            - 含循环节：``"0.(3)"``、``"1.1(6)"``
            - 截断：``"0.333..."``
        进制 : int, 可选
            使用的进制，``None`` 时用类默认值。
        符号表 : str, 可选
            使用的符号表，``None`` 时用类默认值。

        返回
        ----
        多进制有理数
            还原或逼近得到的有理数实例。

        抛出
        ----
        ValueError
            字符串格式不合法（如多个小数点、循环节后有余余字符等）时抛出。

        示例
        ----
        >>> 多进制有理数.有理数逼近("0.(3)")    # 1/3
        >>> 多进制有理数.有理数逼近("0.1(6)")   # 1/6
        >>> 多进制有理数.有理数逼近("0.333...")  # 逼近 1/3
        """
        进制 = 进制 if 进制 is not None else 多进制有理数.默认进制
        符号表 = 符号表 if 符号表 is not None else 多进制有理数.默认符号表

        def 连分数展开(p: int, q: int) -> list[int]:
            """
            计算正分数 p/q 的连分数展开系数列表 [a0, a1, a2, ...]。

            使用辗转相除法，直到余数为 0 为止。

            参数
            ----
            p : int
                分子（正整数）。
            q : int
                分母（正整数）。

            返回
            ----
            list[int]
                连分数展开系数列表。
            """
            结果: list[int] = []
            while q != 0:
                a = p // q
                结果.append(a)
                p, q = q, p - a * q
            return 结果

        def 连分数截断(列表: list[int]) -> list[int]:
            """
            截断连分数展开列表，保留到跳变最大的系数处。

            通过寻找相邻系数比例突变最大的位置来确定截断点，
            用于从截断小数中过滤掉由截断引入的噪声系数。

            参数
            ----
            列表 : list[int]
                连分数展开系数列表。

            返回
            ----
            list[int]
                截断后的系数列表（不含截断点及之后的系数）。
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
            """
            从连分数展开系数列表恢复分数 (分子, 分母)。

            从最后一个系数向前递推，逐步合并得到最终分数。

            参数
            ----
            列表 : list[int]
                连分数展开系数列表 [a0, a1, ...]。

            返回
            ----
            tuple[int, int]
                ``(分子, 分母)``。空列表返回 ``(0, 1)``。
            """
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

        符号 = 1
        if '-' in 字符串:
            if '-' in 字符串[1:]:
                raise ValueError("负号仅允许出现在字符串开头")
            字符串 = 字符串[1:]
            符号 = -1

        if 字符串.endswith("..."):
            字符串 = 字符串[:-3]
            整数部分, _, 小数部分 = 字符串.partition('.')
            if '.' in 小数部分:
                raise ValueError("除尾部的省略号外，必须有且只有一个'.'")
            解析整数 = 多进制有理数(整数部分, 1, 进制, 符号表)._分子值
            解析小数 = 多进制有理数(小数部分, 1, 进制, 符号表)._分子值
            展开结果 = 连分数展开(
                解析小数 + 解析整数 * 进制 ** len(小数部分),
                进制 ** len(小数部分),
            )
            分子值, 分母值 = 连分数重建(连分数截断(展开结果))
            return 多进制有理数(符号 * 分子值, 分母值, 进制, 符号表)
        else:
            if "(" in 字符串 and ")" in 字符串:
                左括号前, _, 左括号后 = 字符串.partition("(")
                循环节, _, 右括号后 = 左括号后.partition(")")
                if 右括号后:
                    raise ValueError("精确的表示必须以循环节结束")
                循环节值 = 多进制有理数(循环节, 1, 进制, 符号表)._分子值
                循环节系数 = 进制 ** len(循环节) - 1
            else:
                循环节值 = 0
                左括号前 = 字符串
                循环节系数 = 1

            整数部分, _, 不循环部分 = 左括号前.partition(".")
            整数值 = 多进制有理数(整数部分, 1, 进制, 符号表)._分子值
            不循环值 = 多进制有理数(不循环部分, 1, 进制, 符号表)._分子值
            分子值 = (
                (整数值 * 进制 ** len(不循环部分) + 不循环值) * 循环节系数
                + 循环节值
            )
            分母值 = 进制 ** len(不循环部分) * 循环节系数
            return 多进制有理数(符号 * 分子值, 分母值, 进制, 符号表)

    # ------------------------------------------------------------------
    # g-adic 表示
    # ------------------------------------------------------------------

    def gadic表示(self, 截断位数: int = 30) -> str:
        """
        计算当前有理数的 g-adic（g进）展开字符串表示。

        g-adic 数的展开方向与普通小数相反：整数部分向**左**无限延伸，
        而普通小数向右延伸。本方法同时支持带负指数（即小数）的情形。

        **格式说明**

        g-adic 表示中不含符号位（g-adic 数本身无正负之分），
        循环节标记在**左侧**（因展开方向向左）：

        - 有限展开（含循环终止于 0）：直接输出，如 ``"7"``。
        - 含循环节：``(循环节)非循环整数部分.小数部分``，
          如 ``"(6).9"`` 表示 ...66666.9（10-adic 下 7/30）。
        - 超出截断：``"...数字串"`` 或 ``"...数字串.小数串"``。

        **算法说明**

        1. 先将分母中含进制因子的部分提取为负指数（``负指数``），
           使分母与进制互质。
        2. 对互质分母求解同余方程 ``n·a ≡ m (mod g)``，
           逐位计算 g-adic 展开系数。
        3. 通过余数字典检测循环节。
        4. 反转后拼接循环节标记。

        参数
        ----
        截断位数 : int, 默认 30
            最多计算的展开位数（整数部分位数），超出后添加 ``"..."``。

        返回
        ----
        str
            g-adic 展开字符串，含循环节标记（若在截断内发现循环）。

        抛出
        ----
        ValueError
            截断位数不足以完整计算小数部分时抛出。

        示例
        ----
        >>> 多进制有理数(7, 30).gadic表示()     # "(6).9"（10-adic）
        >>> 多进制有理数(1, 3).gadic表示()      # "(6667)"... 等效于 -1/3 的 10-adic
        >>> 多进制有理数(1, 2).gadic表示()      # "0.5"（小数部分）

        注意
        ----
        - 本方法支持合数进制（不要求 g 为质数），即广义 g-adic。
        - 当分子为负时，结果仍无符号（g-adic 数的负数通过循环节表达）。
        """
        负指数 = 0
        分子, 分母 = self._分子值, self._分母值
        进制, 符号表 = self._进制, self._符号表

        def 扩展欧几里得(a: int, b: int) -> tuple[int, int, int]:
            """
            扩展欧几里得算法，求解 ``d = gcd(a, b) = a*x + b*y``。

            参数
            ----
            a : int
                第一个整数。
            b : int
                第二个整数。

            返回
            ----
            tuple[int, int, int]
                ``(gcd, x, y)`` 使得 ``gcd == a*x + b*y``。
            """
            x0, x1 = 1, 0
            y0, y1 = 0, 1
            while b != 0:
                q = a // b
                a, b = b, a % b
                x0, x1 = x1, x0 - q * x1
                y0, y1 = y1, y0 - q * y1
            return a, x0, y0

        def 解同余方程(m: int, n: int) -> tuple[int, int]:
            """
            求解同余方程 ``n·a ≡ m (mod g)``，返回最小非负解 a0
            及满足 ``n·a0 - g·b = m`` 的新余数 b（取负后作为下一步余数）。

            参数
            ----
            m : int
                当前余数（分子）。
            n : int
                分母（与进制互质）。

            返回
            ----
            tuple[int, int]
                ``(a0, -b)``，其中 a0 是当前 g-adic 位的数字，
                -b 是下一步递推的新余数。
            """
            g = 进制
            d, x, y = 扩展欧几里得(n, g)
            a0 = (x * (m // d)) % (g // d)
            b = (a0 * n - m) // g
            return a0, -b

        # 将分母中含进制因子的部分提取为负指数
        公因子, _, _ = 扩展欧几里得(分母, 进制)
        while 公因子 != 1:
            分子, 分母 = (进制 // 公因子) * 分子, ((进制 // 公因子) * 分母) // 进制
            负指数 += 1
            公因子, _, _ = 扩展欧几里得(分母, 进制)

        余数字典: dict[int, int] = {}
        商列表: list[int] = []
        索引 = 0
        while 索引 <= 截断位数 and 分子 not in 余数字典:
            余数字典[分子] = 索引
            商, 分子 = 解同余方程(分子, 分母)
            商列表.append(商)
            索引 += 1

        字符列表: list[str] = [符号表[商值] for 商值 in 商列表]

        if 索引 <= 截断位数:
            循环部分 = 字符列表[余数字典[分子]:]
            if 负指数 != 0:
                if len(字符列表) < 负指数:
                    扩展次数 = (负指数 - len(字符列表)) // len(循环部分) + 1
                    字符列表.extend(循环部分 * 扩展次数)

                整数部分 = 字符列表[负指数:]
                while 整数部分 and 整数部分[-1] == 循环部分[-1]:
                    整数部分.pop()
                    循环部分 = 循环部分[-1:] + 循环部分[:-1]

                if len(循环部分) == 1 and 循环部分[0] == 符号表[0]:
                    if len(整数部分) == 0:
                        整数部分.append(符号表[0])
                    结果列表 = 字符列表[:负指数] + ['.'] + 整数部分
                else:
                    结果列表 = (
                        字符列表[:负指数]
                        + ['.']
                        + 整数部分
                        + [')']
                        + 循环部分
                        + ['(']
                    )
            else:
                if len(循环部分) == 1 and 循环部分[0] == 符号表[0]:
                    结果列表 = 字符列表[:余数字典[分子]]
                else:
                    结果列表 = (
                        字符列表[:余数字典[分子]]
                        + [')']
                        + 循环部分
                        + ['(']
                    )
        elif 负指数 != 0:
            if 负指数 >= len(字符列表):
                raise ValueError("截断位数不足以计算完小数部分")
            结果列表 = 字符列表[:负指数] + ['.'] + 字符列表[负指数:] + ["..."]
        else:
            结果列表 = 字符列表 + ["..."]

        反转列表 = 结果列表[::-1]
        return ''.join(反转列表)

    # ------------------------------------------------------------------
    # 有理数重构（g-adic 逆变换）
    # ------------------------------------------------------------------

    @staticmethod
    def 有理数重构(
        字符串: str,
        进制: Optional[int] = None,
        符号表: Optional[str] = None,
    ) -> 多进制有理数:
        """
        从 g-adic 展开字符串还原有理数。

        与 ``gadic表示`` 互为逆操作，支持以下两种格式：

        **精确格式**（含循环节）
            以循环节开头的 g-adic 表示，如 ``"(6)9"``（10-adic 下 7/3 的整数部分）、
            ``"(6).9"``（10-adic 下 7/30）。通过代数方程精确还原。

        **截断格式**（以 ``"..."`` 开头）
            有限位截断的 g-adic 表示，如 ``"...3333"``（截断的 10-adic）。
            使用最优有理数重建算法（基于辗转相除法跳变检测）进行逼近。

        参数
        ----
        字符串 : str
            g-adic 展开字符串，不含符号（g-adic 无符号）：
            - 截断：``"...数字串"`` 或 ``"...数字串.小数串"``
            - 精确：``"(循环节)非循环.小数"`` 或 ``"(循环节)非循环"``
            - 无循环：``"整数.小数"`` 或 ``"整数"``
        进制 : int, 可选
            使用的进制，``None`` 时用类默认值。
        符号表 : str, 可选
            使用的符号表，``None`` 时用类默认值。

        返回
        ----
        多进制有理数
            还原或逼近得到的有理数实例。

        抛出
        ----
        ValueError
            字符串含符号（``-``），或格式不合法时抛出。

        示例
        ----
        >>> 多进制有理数.有理数重构("(6).9")      # 7/30（10-adic）
        >>> 多进制有理数.有理数重构("...3333")    # 逼近 1/3 的截断形式
        """
        进制 = 进制 if 进制 is not None else 多进制有理数.默认进制
        符号表 = 符号表 if 符号表 is not None else 多进制有理数.默认符号表

        def 有理数重建(t: int, M: int) -> tuple[int, int]:
            """
            从截断的 g-adic 整数 ``t``（模 ``M = g^n``）重建最优有理数逼近。

            算法基于辗转相除法，在迭代过程中监测商的跳变幅度，
            将跳变最大处的余数和系数作为最优逼近的分子/分母。

            参数
            ----
            t : int
                截断的 g-adic 值（非负整数，< M）。
            M : int
                模数，通常为 ``g^n``（n 为截断位数）。

            返回
            ----
            tuple[int, int]
                ``(分子, 分母)``，满足 ``分子/分母 ≡ t (mod M)``
                且分子/分母为最简最优逼近。
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

        if '-' in 字符串:
            raise ValueError("标准的g-adic截断没有符号")

        if 字符串.startswith("..."):
            字符串 = 字符串[3:]
            if '.' in 字符串:
                整数部分, _, 小数部分 = 字符串.partition('.')
            else:
                整数部分 = 字符串
                小数部分 = ''
            解析整数 = 多进制有理数(整数部分, 1, 进制, 符号表)._分子值
            解析小数 = 多进制有理数(小数部分, 1, 进制, 符号表)._分子值
            分子, 分母 = 有理数重建(
                解析整数 * 进制 ** len(小数部分) + 解析小数,
                进制 ** len(整数部分 + 小数部分),
            )
            return 多进制有理数(分子, 分母 * 进制 ** len(小数部分), 进制, 符号表)

        else:
            if "(" in 字符串 and ")" in 字符串:
                左括号前, _, 左括号后 = 字符串.partition("(")
                循环节, _, 右括号后 = 左括号后.partition(")")
                if 左括号前:
                    raise ValueError("精确表示必须以循环节开始")
                循环节值 = 多进制有理数(循环节, 1, 进制, 符号表)._分子值
                循环节系数 = 进制 ** len(循环节) - 1
            else:
                循环节值 = 0
                右括号后 = 字符串
                循环节系数 = 1

            整数部分, _, 小数部分 = 右括号后.partition(".")
            整数值 = 多进制有理数(整数部分, 1, 进制, 符号表)._分子值
            小数值 = 多进制有理数(小数部分, 1, 进制, 符号表)._分子值
            分子值 = (
                -循环节值 * 进制 ** len(整数部分 + 小数部分)
                + 循环节系数 * (整数值 * 进制 ** len(小数部分) + 小数值)
            )
            分母值 = 进制 ** len(小数部分) * 循环节系数
            return 多进制有理数(分子值, 分母值, 进制, 符号表)