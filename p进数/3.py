import bisect

def adaptive_sampling_safe(f, a, b, n, i, eps=1e-12, min_step=1e-8, max_depth=1000):
    """
    鲁棒的自适应DFS采样算法（支持异常函数处理）

    Args:
        f: 目标函数（需处理异常）
        a: 左区间端点
        b: 右区间端点
        n: 初始分段数
        i: 敏感度阈值
        eps: 浮点精度保护（默认1e-12）
        min_step: 最小细分步长（默认1e-8）
        max_depth: 最大递归深度（防无限循环）

    Returns:
        (points, anomalies) - 采样点列表与异常点标记
    """
    # region 1. 参数校验
    if a >= b:
        raise ValueError(f"Invalid interval [{a}, {b}], must satisfy a < b")
    if n < 1:
        raise ValueError(f"Initial segments {n} must be ≥1")
    if i < 0:
        raise ValueError(f"Sensitivity threshold {i} must be ≥0")
    # endregion

    # region 2. 安全函数包装（处理异常）
    def safe_f(x):
        try:
            return float(f(x))
        except (ZeroDivisionError, OverflowError):
            return float('inf')
        except Exception as e:
            print(f"Warning: Ignored exception at x={x}: {str(e)}")
            return float('nan')
    # endregion

    # region 3. 初始化数据结构
    points = []
    anomalies = {}  # 记录异常点：{position: error_code}
    current_depth = 0

    # 生成初始点（带异常检测）
    for k in range(n+1):
        x = a + k*(b - a)/n
        points.append(x)
        y = safe_f(x)
        if not np.isfinite(y):
            anomalies[x] = 'INIT_FAULT' if np.isnan(y) else 'DIVERGENCE'
    points.sort()

    func_cache = {x: safe_f(x) for x in points}  # 函数值缓存
    # endregion

    # region 4. 深度优先遍历算法
    j = 0
    while j < len(points) - 1 and current_depth < max_depth:
        left, right = points[j], points[j+1]
        interval_width = right - left

        # 终止条件：区间足够小或已达物理极限
        if interval_width < max(eps, min_step):
            anomalies.setdefault(left, 'MIN_STEP')
            j += 1
            continue

        # 获取函数值（处理缓存异常）
        y_left = func_cache[left]
        y_right = func_cache[right]

        # 异常区间处理：跳过包含无穷值的区间
        if not (np.isfinite(y_left) and np.isfinite(y_right)):
            anomalies.setdefault(left, 'EDGE_FAULT')
            j += 1
            continue

        # 计算动态调整的敏感度阈值
        dynamic_i = i * (interval_width / (b - a))  # 窄区间降低敏感度
        delta = abs(y_left - y_right)

        if delta > dynamic_i:
            mid = (left + right) / 2
            # 验证中点有效性
            insert_pos = bisect.bisect_left(points, mid, j, j+2)
            if (insert_pos > j and
                (insert_pos >= len(points) or
                 abs(points[insert_pos] - mid) > eps)):

                # 计算中点函数值并检查异常
                y_mid = safe_f(mid)
                if not np.isfinite(y_mid):
                    anomalies[mid] = 'MID_FAULT'
                    j += 1
                    continue

                # 执行插入
                points.insert(insert_pos, mid)
                func_cache[mid] = y_mid
                current_depth += 1
                continue  # 深度优先：继续处理左侧新区间

        j += 1  # 移至下一个区间
    # endregion

    # 后处理：清理极小间隔（可选）
    final_points = []
    prev = -float('inf')
    for x in points:
        if x - prev > eps:
            final_points.append(x)
            prev = x
        else:
            anomalies.setdefault(x, 'DUPLICATE')

    return final_points, anomalies

if __name__ == "__main__":
    import numpy as np

    # 测试案例：含间断点1.2的函数
    def dangerous_func(x):
        return 1 / (x - 1.2)

    # 执行采样
    points, anomalies = adaptive_sampling_safe(
        dangerous_func,
        a=0,
        b=2,
        n=3,
        i=1,
        min_step=1e-5
    )

    # 结果分析
    print("采样点（已过滤重复）:")
    print(points)

    print("\n异常点报告:")
    for x, code in anomalies.items():
        print(f"x={x:.6f}: {code}")