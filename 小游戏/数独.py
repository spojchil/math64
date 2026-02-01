from multiprocessing import Pool
import time
import os
import random


class 数独分析:
    def __init__(self, 数独矩阵, *, 解上限=2, 回溯传递=None, 步骤记录=False, 步骤记录解数=2, 启用并行=None):
        if 回溯传递 is None:
            规范, 阶 = self.阶处理(数独矩阵)
            if not 规范:
                print(阶)
                return
        self.数独 = [行[:] for 行 in 数独矩阵]
        self.解集 = set()
        if 回溯传递 is None:
            开始时间 = time.perf_counter()
            self.初始数独 = [行[:] for 行 in 数独矩阵]
            self.共享信息 = [0, 解上限, 0, 阶, 0, [], 步骤记录, True, 步骤记录解数]
            self.当前深度 = 0
            规范, 阶 = self.阶处理(数独矩阵)
            self.格候选值 = {i: {} for i in range(阶 ** 2)}
            相容, 位置 = self.计算候选值()
            if 相容 and self.约束传播():
                if 启用并行 is False or (启用并行 is None and 阶 <= 4):
                    self.递归回溯()
                else:
                    # 高约束使用较快
                    self.并行寻找()
                    if self.共享信息[6]:
                        print("并行无法记录步骤")
                        self.共享信息[6] = False
                    self.共享信息[0] = len(self.解集)
                    self.共享信息[7] = True if self.共享信息[0] < self.共享信息[1] else False
                    # 由于递归算法已经优化的相当好了，所以小的数独并行更慢
                if self.共享信息[7]:
                    if self.共享信息[6]:
                        self.共享信息[5].append("已完全遍历")

                self.信息 = {"找到解": self.共享信息[0],
                             "解上限": self.共享信息[1],
                             "最大深度": self.共享信息[2],
                             "用时": f"{time.perf_counter() - 开始时间:.6f} 秒",
                             "猜测次数": self.共享信息[4],
                             "是否遍历完全": self.共享信息[7]}
            elif 位置 is not None:
                print(位置)
            else:
                print("初始数独无解")

        else:
            self.格候选值, self.共享信息 = 回溯传递

    def 阶处理(self, 数独):
        # 检查输入是否为二维列表
        if not isinstance(数独, list) or not all(isinstance(row, list) for row in 数独):
            return False, "需要输入二维数字数组"

        # 计算阶数
        行数 = len(数独)
        for 阶 in range(1, 100):
            if 阶 ** 2 == 行数:
                break
        else:  # 如果循环正常结束（没找到合适的阶数）
            return False, "行数非法"

        # 检查每行长度和数字范围
        for 行号, 行 in enumerate(数独):
            if len(行) != 行数:
                return False, f"第{行号 + 1}行长度不为{行数}"

            for 列号, 格 in enumerate(行):
                if 格 not in range(行数 + 1):  # 使用 in 检查是否在允许范围内
                    return False, f"第{行号 + 1}行第{列号 + 1}列的元素非法（应为0或1~{行数}之间的整数）"

        return True, 阶

    def 计算候选值(self):
        区域候选值 = {i: {} for i in range(3)}
        所有候选 = {i for i in range(1, 1 + self.共享信息[3] ** 2)}

        # 计算行的候选值
        for 行号, 行 in enumerate(self.数独):
            区域候选值[0][行号] = set()
            for 值 in 行:
                if 值 == 0: continue
                if 值 in 区域候选值[0][行号]:
                    return False, f"第{行号 + 1}行的{值}重复"
                区域候选值[0][行号].add(值)
            区域候选值[0][行号] = 所有候选 - 区域候选值[0][行号]

        # 计算列的候选值
        for 列号 in range(self.共享信息[3] ** 2):
            区域候选值[1][列号] = set()
            for 行号 in range(self.共享信息[3] ** 2):
                值 = self.数独[行号][列号]
                if 值 == 0: continue
                if 值 in 区域候选值[1][列号]:
                    return False, f"第{列号 + 1}列的{值}重复"
                区域候选值[1][列号].add(值)
            区域候选值[1][列号] = 所有候选 - 区域候选值[1][列号]

        # 计算宫的候选值
        for 宫行 in range(0, self.共享信息[3] ** 2, self.共享信息[3]):
            for 宫列 in range(0, self.共享信息[3] ** 2, self.共享信息[3]):
                行 = 宫行 // self.共享信息[3]
                列 = 宫列 // self.共享信息[3]
                宫号 = 行 * self.共享信息[3] + 列
                区域候选值[2][宫号] = set()
                for 行号 in range(宫行, 宫行 + self.共享信息[3]):
                    for 列号 in range(宫列, 宫列 + self.共享信息[3]):
                        值 = self.数独[行号][列号]
                        if 值 == 0:
                            continue
                        if 值 in 区域候选值[2][宫号]:
                            return False, f"第{宫号 + 1}宫的{值}重复"
                        区域候选值[2][宫号].add(值)
                区域候选值[2][宫号] = 所有候选 - 区域候选值[2][宫号]

        # 计算每个格的候选值
        for 行号 in range(self.共享信息[3] ** 2):
            for 列号 in range(self.共享信息[3] ** 2):
                if self.数独[行号][列号] != 0: continue
                宫号 = (行号 // self.共享信息[3]) * self.共享信息[3] + 列号 // self.共享信息[3]
                self.格候选值[行号][列号] = (
                        区域候选值[0][行号] &
                        区域候选值[1][列号] &
                        区域候选值[2][宫号])

        return True, None

    def 显式唯一候选(self):
        for 行号 in self.格候选值:
            for 列号 in self.格候选值[行号]:
                候选集合 = self.格候选值[行号][列号]
                if len(候选集合) == 0:
                    return False, True
                elif len(候选集合) == 1:
                    值 = 候选集合.pop()
                    self.填入数字(行号, 列号, 值, 信息="显式")
                    return True, False
        return False, False

    def 隐式唯一候选(self):
        # 检查行的隐式唯一候选
        for 行号 in range(self.共享信息[3] ** 2):
            行候选统计 = {}
            for 列号 in self.格候选值[行号]:
                for 候选值 in self.格候选值[行号][列号]:
                    行候选统计[候选值] = 行候选统计.get(候选值, 0) + 1
            for 候选值, 计数 in 行候选统计.items():
                if 计数 == 1:
                    for 列号 in self.格候选值[行号]:
                        if 候选值 in self.格候选值[行号][列号]:
                            self.填入数字(行号, 列号, 候选值, 信息="行隐")
                            return True

        # 检查列的隐式唯一候选
        for 列号 in range(self.共享信息[3] ** 2):
            列候选统计 = {}
            存在候选的列 = False
            for 行号 in self.格候选值:
                if 列号 in self.格候选值[行号]:
                    存在候选的列 = True
                    for 候选值 in self.格候选值[行号][列号]:
                        列候选统计[候选值] = 列候选统计.get(候选值, 0) + 1
            if not 存在候选的列:
                continue
            for 候选值, 计数 in 列候选统计.items():
                if 计数 == 1:
                    for 行号 in self.格候选值:
                        if 列号 in self.格候选值[行号] and 候选值 in self.格候选值[行号][列号]:
                            self.填入数字(行号, 列号, 候选值, 信息="列隐")
                            return True

        # 检查宫的隐式唯一候选
        for 宫号 in range(self.共享信息[3] ** 2):
            宫候选统计 = {}
            宫行 = (宫号 % self.共享信息[3]) * self.共享信息[3]
            宫列 = (宫号 // self.共享信息[3]) * self.共享信息[3]
            for 行号 in range(宫行, 宫行 + self.共享信息[3]):
                for 列号 in range(宫列, 宫列 + self.共享信息[3]):
                    if 列号 in self.格候选值[行号]:
                        for 候选值 in self.格候选值[行号][列号]:
                            宫候选统计[候选值] = 宫候选统计.get(候选值, 0) + 1
            for 候选值, 计数 in 宫候选统计.items():
                if 计数 == 1:
                    for 行号 in range(宫行, 宫行 + self.共享信息[3]):
                        for 列号 in range(宫列, 宫列 + self.共享信息[3]):
                            if 列号 in self.格候选值[行号] and 候选值 in self.格候选值[行号][列号]:
                                self.填入数字(行号, 列号, 候选值, 信息="宫隐")
                                return True
        return False

    def 填入数字(self, 行号, 列号, 值, 回溯=False, 信息=""):
        self.数独[行号][列号] = 值
        if self.共享信息[6]:
            if 回溯:
                self.共享信息[5].append(f"尝试在{行号 + 1}行{列号 + 1}列填入{值}")
            else:
                self.共享信息[5].append(f"{信息}约束使{行号 + 1}行{列号 + 1}列填入{值}")

        # 从同行中删除该候选值
        for 其他列 in self.格候选值[行号]:
            self.格候选值[行号][其他列].discard(值)

        # 从同列中删除该候选值
        for 其他行 in self.格候选值:
            if 列号 in self.格候选值[其他行]:
                self.格候选值[其他行][列号].discard(值)

        # 从同宫中删除该候选值
        宫行 = (行号 // self.共享信息[3]) * self.共享信息[3]
        宫列 = (列号 // self.共享信息[3]) * self.共享信息[3]
        for i in range(宫行, 宫行 + self.共享信息[3]):
            for j in range(宫列, 宫列 + self.共享信息[3]):
                if j in self.格候选值[i]:
                    self.格候选值[i][j].discard(值)

        # 删除已填入的格子
        del self.格候选值[行号][列号]

    def 约束传播(self):
        while True:
            更新, 冲突 = self.显式唯一候选()
            if 冲突:
                return False
            elif not (更新 or self.隐式唯一候选()):
                return True

    def 寻找候选位(self, 最大=False):
        长度 = self.共享信息[3] ** 2 + 1 if not 最大 else 0
        for 行号 in self.格候选值:
            for 列号 in self.格候选值[行号]:
                候选集合 = self.格候选值[行号][列号]
                if not 最大:
                    if len(候选集合) == 2:
                        return 行号, 列号
                    elif len(候选集合) < 长度:
                        位置 = (行号, 列号)
                        长度 = len(候选集合)
                else:
                    if len(候选集合) > 长度:
                        位置 = (行号, 列号)
                        长度 = len(候选集合)
        return 位置

    def 格字典复制(self):
        字典 = {}
        for 外层键, 字典值 in self.格候选值.items():
            内侧字典 = {}
            for 内层键, 集合值 in 字典值.items():
                内侧字典[内层键] = set(集合值) if 集合值 else set()
            字典[外层键] = 内侧字典
        return 字典

    def 递归回溯(self):
        回溯数独 = 数独分析(数独矩阵=self.数独, 回溯传递=(self.格字典复制(), self.共享信息))
        回溯数独.解集 = self.解集
        回溯数独.当前深度 = self.当前深度  # 继承父级深度

        if 回溯数独.当前深度 > self.共享信息[2]:
            self.共享信息[2] = 回溯数独.当前深度

        if 回溯数独.格候选值 == {i: {} for i in range(self.共享信息[3] ** 2)}:
            self.解集.add(tuple(tuple(行) for 行 in 回溯数独.数独))
            self.共享信息[0] += 1
            if self.共享信息[6]:
                self.共享信息[5].append(f"找到解{self.共享信息[0]}")
                if self.共享信息[0] >= self.共享信息[8]:
                    self.共享信息[6] = False
            if self.共享信息[0] >= self.共享信息[1]:  # 解数达到上限
                self.共享信息[7] = False
            return True

        行号, 列号 = 回溯数独.寻找候选位()
        if self.共享信息[6]:
            self.共享信息[5].append(
                f"尝试该支的{行号 + 1}行{列号 + 1}列的位置候选值{回溯数独.格候选值[行号][列号]}，当期深度{回溯数独.当前深度 + 1}")
        for 值 in 回溯数独.格候选值[行号][列号]:
            if not self.共享信息[7]:
                return True
            迭代数独 = 数独分析(数独矩阵=[行[:] for 行 in 回溯数独.数独],
                                回溯传递=(回溯数独.格字典复制(), self.共享信息))
            迭代数独.解集 = self.解集
            迭代数独.当前深度 = 回溯数独.当前深度 + 1  # 深度加1

            # 更新最大深度（即使后续失败也记录最深探索）
            if 迭代数独.当前深度 > self.共享信息[2]:
                self.共享信息[2] = 迭代数独.当前深度

            迭代数独.填入数字(行号, 列号, 值, True)
            self.共享信息[4] += 1
            if not 迭代数独.约束传播():
                if self.共享信息[6]:
                    self.共享信息[5].append(f"在{行号 + 1}行{列号 + 1}列填入的{值}冲突")
                continue
            迭代数独.递归回溯()


        else:
            if self.共享信息[6]:
                self.共享信息[5].append(f"该支的{行号 + 1}行{列号 + 1}列迭代结束")
        return False

    def 迭代回溯(self):
        pass

    def 单个搜索(self, 值):
        行, 列 = self.位置
        解集 = set()
        迭代副本 = 数独分析(数独矩阵=self.数独, 回溯传递=(self.格字典复制(), self.共享信息))
        迭代副本.解集 = 解集
        迭代副本.当前深度 = 1
        迭代副本.填入数字(行, 列, 值)
        if not 迭代副本.约束传播():
            return 解集
        迭代副本.递归回溯()
        return 解集, self.共享信息[2], self.共享信息[4]

    # 优化潜力很大
    def 并行寻找(self):
        self.位置 = self.寻找候选位(True)  # 可以优化
        行, 列 = self.位置
        候选值 = self.格候选值[行][列]
        解集 = set()
        print(len(候选值))

        with Pool() as pool:
            try:
                for 返回值 in pool.imap_unordered(self.单个搜索, 候选值):
                    解, 深度, 猜测数 = 返回值
                    self.共享信息[2] = max(self.共享信息[2], 深度)
                    self.共享信息[4] += 猜测数
                    解集 |= 解
                    if len(解集) >= self.共享信息[1]:
                        pool.terminate()  # 强制终止进程池
                        break
            finally:
                pool.close()  # 确保资源释放
                pool.join()  # 等待进程真正结束
        self.解集 = 解集
        if not self.共享信息[7]:
            self.共享信息[2] = f"至少{self.共享信息[2]}"
            self.共享信息[4] = f"至少{self.共享信息[4]}"

    @staticmethod
    def 生成数独(阶=3, 难度="中"):
        对应表 = {"易": int(2 * 阶 ** 4 / 3), "中": int(阶 ** 4 / 2), "难": 0}
        # 这里是不检查的数量，不是保留的格子数量
        数独 = [[0 for _ in range(阶 ** 2)] for _ in range(阶 ** 2)]
        for i in range(1, 阶):  # 生成一个种子数独，3阶的话只有3个数字是为了保证一定有解
            数独[random.randint(0, 阶 ** 2 - 1)][random.randint(0, 阶 ** 2 - 1)] = i
        完整数独 = [list(i) for i in 数独分析(数独).解集.pop()]
        return 数独分析(完整数独).保留指定位(对应表[难度]), 完整数独

    def 保留指定位(self, 位数=0):
        未检查的位置 = set()
        数独 = [行[:] for 行 in self.初始数独]
        for 行号, 行 in enumerate(数独):
            for 列号, 值 in enumerate(行):
                if 值 == 0: continue
                未检查的位置.add((行号, 列号))

        while len(未检查的位置) > 位数:
            行号, 列号 = random.sample(list(未检查的位置), 1)[0]
            未检查的位置.remove((行号, 列号))  # 检查后移除，无论是否重复
            修改值 = 数独[行号][列号]
            数独[行号][列号] = 0
            解 = 数独分析(数独, 解上限=2)
            if 解.共享信息[0] > 1:
                数独[行号][列号] = 修改值
        return 数独


def 清晰步骤(output):
    result = []  # 存储格式化后的输出
    depth_stack = []  # 栈用于管理分支深度
    indent_width = 2  # 每层缩进的空格数

    # 用于合并相同类型的连续约束
    current_batch = {
        'type': None,
        'depth': None,
        'items': [],
        'indent': None
    }

    def flush_batch():
        """将批量收集的约束条目刷新到结果中"""
        if current_batch['items']:
            items_str = "  ".join(current_batch['items'])
            prefix = "· "
            if current_batch['type'] == "显式约束":
                prefix = "✱ "
            elif "隐约束" in current_batch['type']:
                prefix = "· "
            result.append(f"{current_batch['indent']}{prefix}{current_batch['type']}: {items_str}")
            current_batch['items'] = []

    for line in output:
        # 处理分支开始（尝试该支的...）
        if '尝试该支的' in line and '当期深度' in line:
            flush_batch()  # 开始新分支前刷新批量
            # 解析位置和候选值
            parts = line.split('，当期深度')
            depth = int(parts[1])
            location_desc = parts[0].split('的')[1].split('的位置候选值')[0]
            values_desc = parts[0].split('{')[1].split('}')[0]

            # 更新分支栈
            depth_stack = depth_stack[:depth]  # 清除更深层的分支
            depth_stack.append(location_desc)  # 压入当前分支

            # 格式化输出
            indent = ' ' * (depth * indent_width)
            result.append(f"{indent}▼ 分支深度{depth}: {location_desc} 候选值 {{{values_desc}}}")

        # 处理分支结束
        elif '迭代结束' in line:
            flush_batch()  # 结束分支前刷新批量
            location_desc = line.split('的')[1].split('迭代结束')[0]
            if depth_stack and depth_stack[-1] == location_desc:
                depth = len(depth_stack) - 1
                indent = ' ' * (depth * indent_width)
                result.append(f"{indent}▲ 分支结束: {location_desc}")
                depth_stack.pop()  # 弹出栈顶分支

        # 处理尝试填入
        elif line.startswith('尝试在'):
            flush_batch()  # 尝试新填值前刷新批量
            parts = line.split('填入')
            location_desc = parts[0][3:].strip()
            value = parts[1]
            depth = len(depth_stack)
            indent = ' ' * (depth * indent_width)
            result.append(f"{indent}→ 尝试填入 {location_desc}: {value}")

        # 处理找到解
        elif line.startswith('找到解'):
            flush_batch()  # 找到解前刷新批量
            sol_num = line.split('解')[1]
            depth = len(depth_stack)
            indent = ' ' * (depth * indent_width)
            result.append(f"{indent}★ 找到解 {sol_num}")

        # 处理约束操作（显式/行隐/列隐/宫隐）
        elif '约束使' in line:
            # 提取位置和值
            constraint_type = line.split('约束')[0]
            location_desc = line.split('使')[1].split('填入')[0].strip()
            value = line.split('填入')[1]

            # 统一约束类型名称
            if constraint_type == "显式":
                constraint_type = "显式约束"
            elif constraint_type == "行隐":
                constraint_type = "行隐约束"
            elif constraint_type == "列隐":
                constraint_type = "列隐约束"
            elif constraint_type == "宫隐":
                constraint_type = "宫隐约束"

            # 当前信息
            depth = len(depth_stack)
            indent = ' ' * (depth * indent_width)
            item = f"{location_desc} → {value}"

            # 检查是否可合并
            if (current_batch['type'] == constraint_type and
                    current_batch['depth'] == depth and
                    current_batch['indent'] == indent and
                    len(current_batch['items']) <= 6):
                current_batch['items'].append(item)
            else:
                # 类型/深度/缩进变化时刷新批量
                flush_batch()
                current_batch['type'] = constraint_type
                current_batch['depth'] = depth
                current_batch['indent'] = indent
                current_batch['items'].append(item)

        # 处理其他情况（如结束消息）
        else:
            flush_batch()  # 非约束行前刷新批量
            depth = len(depth_stack)
            indent = ' ' * (depth * indent_width)
            result.append(f"{indent}{line}")

    # 循环结束后刷新剩余批量
    flush_batch()
    return '\n'.join(result)


if __name__ == "__main__":
    sudoku_puzzle1 = [
        [8, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 3, 6, 0, 0, 0, 0, 0],
        [0, 7, 0, 0, 9, 0, 2, 0, 0],
        [0, 5, 0, 0, 0, 7, 0, 0, 0],
        [0, 0, 0, 0, 4, 5, 7, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 3, 0],
        [0, 0, 1, 0, 0, 0, 0, 6, 8],
        [0, 0, 8, 5, 0, 0, 0, 1, 0],
        [0, 9, 0, 0, 0, 0, 4, 0, 0]
    ]

    a = 数独分析(sudoku_puzzle1, 解上限=2,步骤记录=False)
    #b = 数独分析.生成数独(3, "难")
    #c, d = b
    for i in a.初始数独:
        print(i)
    print()
    for i in a.解集.pop():
        print(i)

    #d = 数独分析(a, 步骤记录=True)
    print(a.信息)

    #print(清晰步骤(a.共享信息[5]))

    # print(a.信息)
    # a.保留必要位()
    '''
        #松弛数独，多解
    sudoku_puzzle = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 4, 0, 7, 3, 0],
        [13, 0, 12, 0, 0, 0, 0, 9, 8, 0, 14, 0, 0, 0, 0, 4],
        [0, 5, 0, 1, 2, 0, 0, 0, 13, 0, 0, 0, 11, 0, 10, 8],
        [8, 0, 0, 0, 0, 0, 1, 0, 2, 3, 0, 0, 13, 12, 0, 0],
        [1, 0, 0, 0, 5, 0, 4, 0, 6, 0, 7, 0, 0, 15, 0, 0],
        [0, 3, 4, 0, 0, 0, 2, 0, 0, 8, 0, 0, 7, 9, 0, 10],
        [6, 0, 0, 8, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 11, 2],
        [0, 12, 7, 0, 9, 0, 0, 8, 16, 0, 0, 2, 0, 4, 0, 0],
        [10, 0, 0, 0, 0, 0, 0, 7, 0, 2, 0, 16, 1, 0, 6, 0],
        [4, 0, 0, 0, 6, 0, 10, 0, 3, 0, 5, 0, 0, 0, 0, 15],
        [0, 8, 0, 0, 3, 0, 0, 2, 0, 12, 0, 0, 16, 0, 0, 7],
        [14, 0, 6, 0, 0, 0, 0, 0, 1, 0, 4, 15, 0, 8, 5, 0],
        [3, 0, 0, 0, 16, 0, 14, 0, 10, 5, 0, 0, 0, 6, 0, 11],
        [0, 4, 14, 0, 0, 1, 12, 0, 0, 0, 0, 6, 0, 0, 16, 0],
        [0, 0, 0, 0, 8, 0, 7, 3, 0, 0, 0, 0, 0, 0, 0, 0],
        [16, 0, 0, 5, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0]
]

    def 去除多余(数独):
        for 行号,行 in enumerate(数独):
            for 值 in 行:
                if 值 == 0: continue

        数独=数独分析(数独, 解上限=2)
        for i in d.共享信息[5]:
        if "尝试" in i:
            print()
        if "迭代" in i:
            print()
        if "冲突" in i:
            print()
        print(i, end=" ")

    print(d.共享信息[5])

    print()
    for i in a.解集:
        for j in i:
            print(j)
        print()

    b = a.解集.pop()
    for i in b:
        print(i)


    '''

    简单数独 = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    # solver = 数独求解器(简单数独, 步骤记录=True)
    # print("\n".join(solver.共享信息[5]))

    # a.保留必要位()
