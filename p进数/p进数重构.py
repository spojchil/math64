class 多进制有理数:
    默认进制 = 10
    默认符号表 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    __slots__ = ("_进制", "_符号表", "_分子值", "_分子表示",
                 "_分母值", "_分母表示", "_映射字典")

    def __init__(self, 分子: int | str, 分母: int | str = 1,
                 进制: int = None, 符号表: str = None):
        self._进制 = 进制 if 进制 is not None else self.默认进制
        self._符号表 = 符号表 if 符号表 is not None else self.默认符号表
        self._验证进制和符号表()
        self._分子表示 = None
        self._分母表示 = None
        self._映射字典 = None
        分母,分母符号 = self._处理输入(分母)
        分子,分子符号 = self._处理输入(分子)
        公因子 = 多进制有理数._欧几里得算法(分母,分子)
        分母 //= 公因子
        分子 //= 公因子
        self._分母值 = 分母
        self._分子值 = 分子 * 分母符号 * 分子符号
        if self._分母值 == 0:
            raise ZeroDivisionError("分母不能为0")


    @property
    def 进制(self):
        return self._进制

    @property
    def 符号表(self):
        return self._符号表

    @property
    def 分子值(self):
        return self._分子值

    @property
    def 分母值(self):
        return self._分母值

    @property
    def 分子表示(self):
        if self._分子表示 is None:
            self._分子表示 = "-" if self._分子值 < 0 else ""
            self._分子表示 += self._十进转n(abs(self._分子值))
        return self._分子表示

    @property
    def 分母表示(self):
        if self._分母表示 is None:
            self._分母表示 = self._十进转n(abs(self._分母值))
        return self._分母表示

    def __str__(self):
        return f"{self.分子表示}/{self.分母表示}" if self._分母值 != 1 else self.分子表示

    def __repr__(self):
        return (f"十进制: {self._分子值}/{self._分母值}, "
                f"当前进制为: {self._进制}, 表示: {self.分子表示}/{self.分母表示}")

    def _验证进制和符号表(self):
        if not isinstance(self._进制, int):
            raise TypeError("进制必须是int类型")
        if not isinstance(self._符号表, str):
            raise TypeError("符号表必须是str")
        if any(char in r"./ \-" for char in self._符号表):
            raise ValueError("符号表中不允许有点，空格，斜杠，反斜杠和减号")
        if len(set(self._符号表)) != len(self._符号表):
            raise ValueError("符号表重复")
        if not (2 <= self._进制 <= len(self._符号表)):
            raise ValueError(f"进制{self._进制}不合法！"
                             f"符号表长度为{len(self._符号表)}，"
                             f"进制需在2到该长度之间")

    def _处理输入(self, 值: int | str):
        if isinstance(值, int):
            return abs(值),1 if 值 >= 0 else -1
        if isinstance(值, str):
            self._验证输入字符串(值)
            符号 = 1
            if 值.startswith('-'):
                符号 = -1
                值 = 值[1:]
            return self._n进转十(值),符号
        raise TypeError("分子和分母必须是整数或者字符串")

    def _验证输入字符串(self, 字符串: str):
        if 字符串 == "-":
            raise ValueError("输入字符串不能仅包含负号")

        if '-' in 字符串[1:]:
            raise ValueError("负号仅允许出现在字符串开头")

        字符集合 = set(self._符号表[:self._进制])
        清理后字符 = 字符串.lstrip('-')
        if not all(字符 in 字符集合 for 字符 in 清理后字符):
            raise ValueError(
                f"输入字符串{字符串}包含非法字符！当前进制{self._进制}的合法集合为：{''.join(字符集合)}")

    def _读取映射(self):
        if self._映射字典 is None:
            self._映射字典 = {c: idx for idx, c in enumerate(self._符号表)}
        return self._映射字典

    def _十进转n(self, 值: int) -> str:
        if 值 == 0:
            return self._符号表[0]
        进制 = self._进制
        符号表 = self._符号表

        字符表 = []
        while 值 > 0:
            字符表.append(符号表[值 % 进制])
            值 = 值 // 进制

        return ''.join(reversed(字符表))

    def _n进转十(self, 字符串: str) -> int:
        字典映射 = self._读取映射()
        进制 = self._进制

        十进值 = 0
        当前基 = 1
        for char in reversed(字符串):
            十进值 += 字典映射[char] * 当前基
            当前基 *= 进制
        return 十进值

    @classmethod
    def _快速创建(cls, 分子值, 分母值, 进制, 符号表):
        """快速创建不验证进制和符号表"""
        if 分母值 == 0:
            raise ZeroDivisionError("分母不能为0")
        if 分母值 < 0:
            分母值,分子值 = -分母值,-分子值

        公因子 = 多进制有理数._欧几里得算法(分母值,abs(分子值))
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
    def _欧几里得算法(a, b):
        while b != 0:
            a, b = b, a % b

        return a

    def 进制转换(self, 进制 = None, 符号表 = None):
        return 多进制有理数(self._分子值,self._分母值, 进制,符号表)

    def __float__(self):
        return self._分子值 / self._分母值

    def __bool__(self):
        return bool(self._分子值)

    def __hash__(self):
        if self._分母值 == 1:
            return hash(self._分子值)
        else:
            return hash((self._分子值,self._分母值))

    def __int__(self):
        return self._分子值 // self._分母值

    def __abs__(self):
        return 多进制有理数(abs(self._分子值), self._分母值,self._进制,self._符号表)

    def __add__(self, other):
        if not isinstance(other, (int, 多进制有理数)):
            return NotImplemented

        if isinstance(other, int):
            新分子 = self._分子值 + self._分母值 * other
            新分母 = self._分母值
        else:
            新分子 = self._分子值 * other._分母值 + self._分母值 * other._分子值
            新分母 = self._分母值 * other._分母值
        return 多进制有理数._快速创建(新分子, 新分母, self._进制, self._符号表)

    # 实现反向加法后 int += self和 self += int 均无问题，无需额外实现iadd
    # 注意经过测试 int + 多进制有理数 的返回会正确保持多进制有理数的进制和符号表
    def __radd__(self, other):
        return self.__add__(other)

    # 理论上返回原对象速度更快，但是我们的属性都是不可变的
    # 所以我们应该让类也表现的不可变，因为我们的初始化成本并不小，
    def __neg__(self):
        return 多进制有理数._快速创建(-self._分子值, self._分母值,self._进制,self._符号表)

    # 效率优先，尽量少使用类重载后的运算
    def __sub__(self, other):
        if not isinstance(other, (int,多进制有理数)):
            return NotImplemented

        if isinstance(other, int):
            新分子 = self._分子值 - self._分母值 * other
            新分母 = self._分母值
        else:
            新分子 = self._分子值 * other._分母值 - self._分母值 * other._分子值
            新分母 = self._分母值 * other._分母值
        return 多进制有理数._快速创建(新分子, 新分母, self._进制, self._符号表)

    # 这里不进行使用sub是，无交换律，不好保持进制和符号表
    def __rsub__(self, other):
        # 另一个不可能是 多进值有理数，
        if not isinstance(other, int):
            return NotImplemented
        新分子 = self._分母值 * other - self._分子值
        新分母 = self._分母值

        return 多进制有理数._快速创建(新分子, 新分母 ,self._进制,self._符号表)
    # 重载~用于取倒数
    def __invert__(self):
        return 多进制有理数._快速创建(self._分母值, self._分子值,self._进制,self._符号表)

    def __mul__(self, other):
        if not isinstance(other, (int, 多进制有理数)):
            return NotImplemented

        if isinstance(other, int):
            新分子 = self._分子值 * other
            新分母 = self._分母值
        else:
            新分子 = self._分子值 * other._分子值
            新分母 = self._分母值 * other._分母值
        return 多进制有理数._快速创建(新分子, 新分母, self._进制, self._符号表)

    def __rmul__(self, other):
        return self.__mul__(other)

    #更方便的办法是使用~倒数和前面定义的乘法,但是那样效率不好
    def __truediv__(self, other):
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

    def __rtruediv__(self, other):
        if not isinstance(other, int):
            return NotImplemented

        if self._分子值 == 0:
            raise ZeroDivisionError("被除数不能为0")
        新分子 = self._分母值 * other
        新分母 = self._分子值

        return 多进制有理数._快速创建(新分子, 新分母, self._进制, self._符号表)

    @staticmethod
    def _整数根(m, n):
        # 处理0的特殊情况
        if m == 0:
            return 0

        if abs(m) == 1:
            return m

        # 处理负数的符号逻辑
        符号 = 1
        if m < 0:
            if n % 2 == 0:  # 负数的偶次方根无实数解
                return None
            符号 = -1
            m = -m

        # 优化边界：由于k^n = m，所以k ≤ m
        # 但可以进一步缩小边界：当n≥2时，k ≤ m^(1/n) ≤ m
        左, 右 = 0, m

        # 进一步优化右边界
        if n > 1:
            # 对于较大的n，k的最大值会小得多
            # 例如：m=1000, n=3，k ≤ 10
            if m > 1:
                右 = min(右, 1 << ((m.bit_length() + n - 1) // n))

        # 二分查找
        while 左 <= 右:
            中 = (左 + 右) // 2

            # 计算mid^n，使用快速幂并在过程中检查溢出
            结果 = 1
            基 = 中
            指数 = n
            溢出 = False

            while 指数 > 0:
                if 指数 & 1:  # 如果当前指数位为1
                    # 检查乘法是否会导致溢出
                    if 结果 > m // 基:
                        溢出 = True
                        break
                    结果 *= 基
                    if 结果 > m:
                        溢出 = True
                        break

                指数 >>= 1
                if 指数 > 0:
                    # 检查平方是否会导致溢出
                    if 基 > m // 基:
                        溢出 = True
                        break
                    基 *= 基

            if 溢出 or 结果 > m:
                右 = 中 - 1
            elif 结果 < m:
                左 = 中 + 1
            else:  # result == m
                return 符号 * 中

        return None

    def __pow__(self, other):
        """允许封闭的有理数幂次"""
        if not isinstance(other,(int, 多进制有理数)):
            return NotImplemented

        if isinstance(other, int):
            if other >= 0: # python中 0 ** 0=1
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
                新分母,新分子 = 新分子 ** (-other._分子值),新分母 ** (-other._分子值)
        return 多进制有理数._快速创建(新分子,新分母,self._进制,self._符号表)

    def __rpow__(self, other):
        if not isinstance(other, int):
            return NotImplemented

        新分子 = 多进制有理数._整数根(other, self._分母值)
        if 新分子 is None:
            raise ValueError(f"无法在有理数中开{self._分母值}开方")
        新分子 = 新分子 ** self._分子值
        return 多进制有理数._快速创建(新分子,1,self._进制,self._符号表)

    def __mod__(self, other):
        """只允许整数"""
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

    def __rmod__(self, other):
        if not isinstance(other, int):
            return NotImplemented

        if self._分母值 != 1:
            raise ValueError("取模只允许分母值为1")

        新分子 = other % self._分子值
        return 多进制有理数._快速创建(新分子,1,self._进制,self._符号表)

    def __floordiv__(self, other):
        """只允许整数"""
        if not isinstance(other, (int,多进制有理数)):
            return NotImplemented

        if isinstance(other, int):
            if self._分母值 != 1:
                raise ValueError("整除只允许分母值为1")
            新分子 = self._分子值 // other
        else:
            if self._分母值 != 1 or other._分母值 != 1:
                raise ValueError("整除只允许分母值为1")
            新分子 = self._分子值 // other._分子值
        return 多进制有理数._快速创建(新分子,1,self._进制,self._符号表)

    def __rfloordiv__(self, other):
        if not isinstance(other, int):
            return NotImplemented

        if self._分母值 != 1:
            raise ValueError("整除只允许分母值为1")

        新分子 = other // self._分子值
        return 多进制有理数._快速创建(新分子, 1, self._进制, self._符号表)

    def __eq__(self, other):
        if not isinstance(other, (int,多进制有理数)):
            return False

        if isinstance(other, int):
            if self._分母值 != 1:
                return False
            return self._分子值 == other
        else:
            return self._分子值 == other._分子值 and self._分母值 == other._分母值

    def __lt__(self, other):
        if not isinstance(other, (int, 多进制有理数)):
            return NotImplemented

        if isinstance(other, int):
            return self._分子值 < other * self._分母值
        else:
            return self._分子值 * other._分母值 < self._分母值 * other._分子值

    def __gt__(self, other):
        if not isinstance(other, (int, 多进制有理数)):
            return NotImplemented
        return not self.__lt__(other) and not self.__eq__(other)

    def __le__(self, other):
        if not isinstance(other, (int, 多进制有理数)):
            return NotImplemented
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other):
        if not isinstance(other, (int, 多进制有理数)):
            return NotImplemented
        return not self.__lt__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def 浮点数(self, 截断位数=30):
        """
        将当前有理数转换为当前进制下的小数表示
        返回格式：
        - 整数部分.小数部分
        - 循环节用括号标记，如"3.1(4)" 表示 3.14444...
        - 有限小数直接显示，如"B.32"
        - 达到截断位数但未发现循环则用"..."，如"3.A4..."
        """

        # 处理符号
        符号 = "-" if self._分子值  < 0 else ""

        # 处理整数部分
        整数部分 = abs(self._分子值) // self._分母值
        整数部分表示 = self._十进转n(整数部分)

        # 处理小数部分
        余数 = abs(self._分子值) % self._分母值

        if 余数 == 0:
            # 整数
            return 符号 + 整数部分表示 + "." + self._符号表[0]

        # 记录余数出现的位置，用于检测循环
        余数位置 = {}
        小数位列表 = []
        循环开始位置 = -1

        for 位置 in range(截断位数):
            if 余数 == 0:
                # 除尽，有限小数
                break

            if 余数 in 余数位置:
                # 发现循环
                循环开始位置 = 余数位置[余数]
                break

            # 记录当前余数的位置
            余数位置[余数] = 位置

            # 计算下一位
            余数 *= self._进制
            商 = 余数 // self._分母值
            小数位列表.append(商)
            余数 = 余数 % self._分母值

        # 构建小数部分字符串
        小数位字符列表 = [self._符号表[数字] for 数字 in 小数位列表]

        if 循环开始位置 >= 0:
            # 有循环节
            非循环部分 = 小数位字符列表[:循环开始位置]
            循环部分 = 小数位字符列表[循环开始位置:]

            if 非循环部分:
                小数部分表示 = "".join(非循环部分) + "(" + "".join(循环部分) + ")"
            else:
                小数部分表示 = "(" + "".join(循环部分) + ")"
        else:
            # 无循环节
            小数部分表示 = "".join(小数位字符列表)
            if 余数 != 0 and len(小数位列表) >= 截断位数:
                # 达到截断位数但未除尽
                小数部分表示 += "..."

        # 返回最终结果
        if 小数部分表示:
            return 符号 + 整数部分表示 + "." + 小数部分表示
        else:
            return 符号 + 整数部分表示

    @staticmethod
    def 有理数逼近(字符串:str, 进制 = 默认进制, 符号表 = 默认符号表):
        def 连分数展开(p, q):
            """
            计算最简正分数 p/q 的连分数展开

            参数:
            p: 分子 (整数)
            q: 分母 (整数)

            返回:
            列表，表示连分数展开的系数 [a0, a1, a2, ...]
            """
            结果 = []

            while q != 0:
                # 计算整数部分
                a = p // q
                结果.append(a)

                # 计算余数部分
                p, q = q, p - a * q
            return 结果

        def 连分数截断(列表):
            if len(列表) < 2:
                return 列表[:]

            历史最大比例, 对应的索引 = 1, 0
            for i in range(1, len(列表)):
                if 列表[i] >= 历史最大比例 * max(列表[i - 1], 1):
                    历史最大比例 = 列表[i] // max(列表[i - 1], 1)

                    对应的索引 = i
            return 列表[:对应的索引]

        def 连分数重建(列表):
            """
            从连分数展开系数恢复分数

            参数:
            列表: 连分数展开系数列表 [a0, a1, a2, ...]

            返回:
            元组 (分子, 分母)
            """
            if not 列表:
                return 0, 1

            # 从最后一个系数开始计算
            n = len(列表)

            # 初始化分子和分母
            分子 = 列表[-1]  # 最后一个系数
            分母 = 1

            # 从倒数第二个系数向前计算
            for i in range(n - 2, -1, -1):
                新分子 = 列表[i] * 分子 + 分母
                新分母 = 分子

                # 更新分子和分母
                分子, 分母 = 新分子, 新分母

            return 分子, 分母

        符号 = 1
        if '-' in 字符串:
            if '-' in 字符串[1:]:
                raise ValueError("负号仅允许出现在字符串开头")
            字符串=字符串[1:]
            符号 = -1
        if 字符串.endswith("..."):
            字符串 = 字符串[:-3]
            整数部分, _,小数部分 = 字符串.partition('.')
            if '.' in 小数部分:
                raise ValueError("除尾部的省略号外，必须有且只有一个'.'")
            解析整数 = 多进制有理数(整数部分,1,进制,符号表)._分子值 #借助类实例检查输入
            解析小数 = 多进制有理数(小数部分,1,进制,符号表)._分子值

            展开结果 = 连分数展开(解析小数 + 解析整数 * 进制 ** len(小数部分), 进制 ** len(小数部分))
            分子值,分母值 = 连分数重建(连分数截断(展开结果))
            return 多进制有理数(符号 * 分子值,分母值,进制,符号表)
        else:
            if "(" in 字符串 and ")" in 字符串:
                左括号前, _, 左括号后= 字符串.partition("(")
                循环节,_,右括号后 = 左括号后.partition(")")
                if 右括号后:
                   raise ValueError("精确的表示必须以循环节结束")
                循环节值 = 多进制有理数(循环节, 1, 进制, 符号表)._分子值
                循环节系数 = 进制 ** len(循环节) - 1
            else:
                循环节值 = 0
                左括号前 = 字符串
                循环节系数 = 1

            整数部分,_,不循环部分 = 左括号前.partition(".")
            整数值 = 多进制有理数(整数部分,1,进制,符号表)._分子值
            不循环值 = 多进制有理数(不循环部分,1,进制,符号表)._分子值
            分子值 = (整数值 * 进制 ** len(不循环部分) + 不循环值) * 循环节系数 + 循环节值
            分母值 = 进制 ** len(不循环部分) * 循环节系数
            return 多进制有理数(符号 * 分子值, 分母值,进制,符号表)

    def padic表示(self,截断位数=30):
        """self.p进制表示(截断位数),带循环节
        支持p进小数，也就是不要求p是质数
        对于10-adic 下7/30
        可以这样理解 (7/3) * 10^-1
        也既
        ...6666.9 因为 ...6666.9*30 =7
        在本方法中 会返回带循环节标记的(6).9 如果截断允许的情况下
        对于无限向左延伸的情况也是会出现()或者...标记
        """
        负指数 = 0
        分子,分母 = self._分子值,self._分母值
        进制,符号表 = self._进制,self._符号表

        def 扩展欧几里得(a, b):
            """
            返回 (d, x, y) 使得 d = gcd(a, b) = a*x + b*y
            参数:
                a, b: 整数
            返回:
                (gcd, x, y) 三元组
            """
            # 初始化系数
            x0, x1 = 1, 0  # x0 对应 a 的系数，x1 是中间变量
            y0, y1 = 0, 1  # y0 对应 b 的系数，y1 是中间变量

            while b != 0:
                q = a // b
                # 更新 a, b
                a, b = b, a % b
                # 更新系数
                x0, x1 = x1, x0 - q * x1
                y0, y1 = y1, y0 - q * y1

            return a, x0, y0

        def 解同余方程(m, n):
            p = 进制
            d, x, y = 扩展欧几里得(n, p)
            a0 = (x * (m // d)) % (p // d)
            b = (a0 * n - m) // p
            # 计算对应的值满足n*a0 - p*b = m
            return a0, -b
        # 使分母与进制互质
        公因子,_,_ = 扩展欧几里得(分母,进制)
        while 公因子 != 1:
            分子,分母 = (进制 // 公因子) * 分子 , ((进制 // 公因子) * 分母) // 进制
            负指数 += 1
            公因子 = 扩展欧几里得(分母, 进制)

        余数字典={}
        商列表=[]
        索引 = 0
        while 索引 <= 截断位数 and 分子 not in 余数字典:
            余数字典[分子] = 索引
            商,分子 = 解同余方程(分子,分母)
            商列表.append(商)
            索引 += 1

        # 反向的字符列表
        字符列表=[符号表[商值] for 商值 in 商列表]
        if 索引 <= 截断位数:
            循环部分 = 字符列表[余数字典[分子]:]
            if 负指数 != 0:
                if len(字符列表) < 负指数:
                    扩展次数 = (负指数-len(字符列表)) // len(循环部分) + 1
                    字符列表.extend(循环部分 * 扩展次数)

                整数部分 = 字符列表[负指数:]

                # 调整循环节
                # 如 (123)124.54，调整为(312)4.54
                while 整数部分 and 整数部分[-1] == 循环部分[-1]:
                    整数部分.pop()
                    循环部分 = 循环部分[-1:] + 循环部分[:-1]
                if len(循环部分) == 1 and 循环部分[0] == 符号表[0]:
                    if len(整数部分) == 0:
                        整数部分.append(符号表[0])
                    结果列表 = 字符列表[:负指数] + ['.'] + 整数部分
                # 构造结果列表：[小数部分, '.', 整数部分, ')', 循环部分, '(']
                else:
                    结果列表 = (字符列表[:负指数] + ['.'] + 整数部分 +
                            [')'] + 循环部分 + ['('])

            else:
                # 无小数部分
                if len(循环部分) == 1 and 循环部分[0] == 符号表[0]:
                    结果列表 = 字符列表[:余数字典[分子]] # 这个其实就是分母为1是的分子表示
                    # 因为正整数的p-adic表示和自身表示相同，不过需要注意符号，adic无符号
                else:
                    结果列表 = 字符列表[:余数字典[分子]] +[')'] + 循环部分 + ['(']
        elif 负指数 != 0:
            if 负指数 >= len(字符列表):
                raise ValueError("截断位数不足以计算完小数部分")
            结果列表 = 字符列表[:负指数] + ['.'] + 字符列表[负指数:] + ["..."]
        else:
            结果列表 = 字符列表 + ["..."]
        # 反转并返回字符串
        反转列表 = 结果列表[::-1]
        return ''.join(反转列表)

    @staticmethod
    def 有理数重构(字符串:str, 进制 = 默认进制, 符号表 = 默认符号表):
        def 有理数重建(t,M):
            if t == 0:
                return 0,1

            r_p, r = M, t
            u_p, u = 0, 1
            r_b, r_bp = 1, 1  # 寻找变化最大
            r_m, u_m = 0,1

            while True:
                q = r_p // r
                r_p, r,r_b = r, r_p - q * r,r_p//r
                u_p, u = u, u_p - q * u
                if abs(r_b) >= abs(r_bp):
                    r_m,u_m = r_p,u_p
                    r_bp = r_b
                if r == 0: break

            return r_m,u_m
        if '-' in 字符串:
            raise ValueError("标准的p-adic截断没有符号")

        if 字符串.startswith("..."):
            字符串=字符串[3:]
            if '.' in 字符串:
                整数部分, _,小数部分 = 字符串.partition('.')
            else:
                整数部分 = 字符串
                小数部分 = ''
            解析整数 = 多进制有理数(整数部分, 1, 进制, 符号表)._分子值
            解析小数 = 多进制有理数(小数部分, 1, 进制, 符号表)._分子值
            分子, 分母 = 有理数重建(解析整数 * 进制 **len(小数部分) + 解析小数,
                                    进制 ** len(整数部分+小数部分))

            return 多进制有理数(分子,分母 * 进制**len(小数部分),进制,符号表)

        else:
            #         (         12   )       32.42
            # 左括号前 _ 左括号后 循环节 _ 右括号后
            if "(" in 字符串 and ")" in 字符串:
                左括号前, _, 左括号后= 字符串.partition("(")
                循环节,_,右括号后 = 左括号后.partition(")")
                if 左括号前:
                   raise ValueError("精确表示必须以循环节开始")
                循环节值 = 多进制有理数(循环节, 1, 进制, 符号表)._分子值
                循环节系数 = 进制 ** len(循环节) - 1
            else:
                循环节值 = 0
                右括号后 = 字符串
                循环节系数 = 1

            整数部分,_,小数部分 = 右括号后.partition(".")
            整数值 = 多进制有理数(整数部分,1,进制,符号表)._分子值
            小数值 = 多进制有理数(小数部分,1,进制,符号表)._分子值
            分子值 = -循环节值 * 进制 ** len(整数部分+小数部分)+循环节系数*(整数值*进制**len(小数部分) + 小数值)
            分母值 = 进制 ** len(小数部分) * 循环节系数
            return 多进制有理数(分子值, 分母值, 进制, 符号表)
