from p进数重构 import 多进制有理数 as dy
import time
import random
import math
from decimal import Decimal
from fractions import Fraction

dy.默认符号表 = 默认符号表 = "0123456789abcdefGHIJKLMNOPQRSTUVWXYZ"

def 测试创建对象():
    """测试创建对象的性能"""
    print("测试创建对象性能:")
    times = 10000

    # 整数创建
    start = time.time()
    for _ in range(times):
        x = random.randint(1, 1000000)
    int_creation_time = time.time() - start

    # 多进制有理数创建（十进制）
    start = time.time()
    for _ in range(times):
        x = dy(random.randint(1, 1000000), 进制=10)
    dy_decimal_creation_time = time.time() - start

    # 多进制有理数创建（十六进制）
    start = time.time()
    for _ in range(times):
        x = dy(hex(random.randint(1, 1000000))[2:], 进制=16)
    dy_hex_creation_time = time.time() - start

    print(f"整数创建: {int_creation_time:.4f}s")
    print(
        f"多进制有理数(十进制)创建: {dy_decimal_creation_time:.4f}s, 慢 {dy_decimal_creation_time / int_creation_time:.2f}倍")
    print(
        f"多进制有理数(十六进制)创建: {dy_hex_creation_time:.4f}s, 慢 {dy_hex_creation_time / int_creation_time:.2f}倍")
    print()


def 测试基本运算():
    """测试加减乘除基本运算性能"""
    print("测试基本运算性能:")
    operations = 10000

    # 准备测试数据
    ints = [(random.randint(1, 1000), random.randint(1, 1000)) for _ in range(operations)]
    dys_decimal = [(dy(a, 进制=10), dy(b, 进制=10)) for a, b in ints]
    dys_hex = [(dy(hex(a)[2:], 进制=16), dy(hex(b)[2:], 进制=16)) for a, b in ints]

    # 加法
    start = time.time()
    for a, b in ints:
        _ = a + b
    int_add_time = time.time() - start

    start = time.time()
    for a, b in dys_decimal:
        _ = a + b
    dy_decimal_add_time = time.time() - start

    start = time.time()
    for a, b in dys_hex:
        _ = a + b
    dy_hex_add_time = time.time() - start

    # 减法
    start = time.time()
    for a, b in ints:
        _ = a - b
    int_sub_time = time.time() - start

    start = time.time()
    for a, b in dys_decimal:
        _ = a - b
    dy_decimal_sub_time = time.time() - start

    # 乘法
    start = time.time()
    for a, b in ints:
        _ = a * b
    int_mul_time = time.time() - start

    start = time.time()
    for a, b in dys_decimal:
        _ = a * b
    dy_decimal_mul_time = time.time() - start

    # 除法
    start = time.time()
    for a, b in ints:
        _ = a / b
    int_div_time = time.time() - start

    start = time.time()
    for a, b in dys_decimal:
        _ = a / b
    dy_decimal_div_time = time.time() - start

    print(f"加法:")
    print(f"  整数: {int_add_time:.4f}s")
    print(f"  多进制有理数(十进制): {dy_decimal_add_time:.4f}s, 慢 {dy_decimal_add_time / int_add_time:.2f}倍")
    print(f"  多进制有理数(十六进制): {dy_hex_add_time:.4f}s, 慢 {dy_hex_add_time / int_add_time:.2f}倍")

    print(f"\n减法:")
    print(f"  整数: {int_sub_time:.4f}s")
    print(f"  多进制有理数: {dy_decimal_sub_time:.4f}s, 慢 {dy_decimal_sub_time / int_sub_time:.2f}倍")

    print(f"\n乘法:")
    print(f"  整数: {int_mul_time:.4f}s")
    print(f"  多进制有理数: {dy_decimal_mul_time:.4f}s, 慢 {dy_decimal_mul_time / int_mul_time:.2f}倍")

    print(f"\n除法:")
    print(f"  整数(浮点除): {int_div_time:.4f}s")
    print(f"  多进制有理数: {dy_decimal_div_time:.4f}s, 慢 {dy_decimal_div_time / int_div_time:.2f}倍")
    print()


def 测试复杂运算():
    """测试复杂运算性能"""
    print("测试复杂运算性能:")
    operations = 5000

    # 准备数据
    int_pairs = [(random.randint(1, 100), random.randint(1, 100)) for _ in range(operations)]
    dy_pairs = [(dy(a, b, 进制=10), dy(c, d, 进制=10)) for a, b, c, d in
                [(random.randint(1, 100), random.randint(1, 100),
                  random.randint(1, 100), random.randint(1, 100)) for _ in range(operations)]]

    # 复杂表达式测试
    # 整数测试: (a+b) * (c-d) / (e+f)
    start = time.time()
    for (a, b) in int_pairs:
        c, d = random.randint(1, 100), random.randint(1, 100)
        e, f = random.randint(1, 100), random.randint(1, 100)
        _ = (a + b) * (c - d) / (e + f)
    int_complex_time = time.time() - start

    # 多进制有理数测试
    start = time.time()
    for (a, b) in dy_pairs:
        c, d = dy(random.randint(1, 100), 进制=10), dy(random.randint(1, 100), 进制=10)
        e, f = dy(random.randint(1, 100), 进制=10), dy(random.randint(1, 100), 进制=10)
        _ = (a + b) * (c - d) / (e + f)
    dy_complex_time = time.time() - start

    print(f"复杂表达式运算:")
    print(f"  整数: {int_complex_time:.4f}s")
    print(f"  多进制有理数: {dy_complex_time:.4f}s, 慢 {dy_complex_time / int_complex_time:.2f}倍")
    print()


def 测试幂运算():
    """测试幂运算性能"""
    print("测试幂运算性能:")
    operations = 1000

    # 整数幂运算
    start = time.time()
    for _ in range(operations):
        a = random.randint(1, 100)
        b = random.randint(1, 10)
        _ = a ** b
    int_pow_time = time.time() - start

    # 多进制有理数幂运算
    start = time.time()
    for _ in range(operations):
        a = dy(random.randint(1, 100), 进制=10)
        b = random.randint(1, 10)
        _ = a ** b
    dy_pow_time = time.time() - start

    print(f"幂运算:")
    print(f"  整数: {int_pow_time:.4f}s")
    print(f"  多进制有理数: {dy_pow_time:.4f}s, 慢 {dy_pow_time / int_pow_time:.2f}倍")
    print()


def 测试分数运算():
    """与Python内置Fraction比较"""
    print("测试与Fraction比较:")
    operations = 5000

    # 准备数据
    frac_pairs = [(Fraction(random.randint(1, 100), random.randint(1, 100)),
                   Fraction(random.randint(1, 100), random.randint(1, 100)))
                  for _ in range(operations)]

    dy_pairs = [(dy(random.randint(1, 100), random.randint(1, 100), 进制=10),
                 dy(random.randint(1, 100), random.randint(1, 100), 进制=10))
                for _ in range(operations)]

    # Fraction运算
    start = time.time()
    for a, b in frac_pairs:
        _ = a + b
        _ = a - b
        _ = a * b
        _ = a / b
    frac_ops_time = time.time() - start

    # 多进制有理数运算
    start = time.time()
    for a, b in dy_pairs:
        _ = a + b
        _ = a - b
        _ = a * b
        _ = a / b
    dy_ops_time = time.time() - start

    print(f"四则运算:")
    print(f"  Fraction: {frac_ops_time:.4f}s")
    print(f"  多进制有理数: {dy_ops_time:.4f}s, 慢 {dy_ops_time / frac_ops_time:.2f}倍")

    # 测试大数性能
    print("\n测试大数性能:")
    big_num = 123456789012345678901234567890

    # Fraction
    start = time.time()
    for _ in range(1000):
        f1 = Fraction(big_num, big_num + 1)
        f2 = Fraction(big_num + 2, big_num + 3)
        _ = f1 + f2
    frac_big_time = time.time() - start

    # 多进制有理数
    start = time.time()
    for _ in range(1000):
        d1 = dy(big_num, big_num + 1, 进制=10)
        d2 = dy(big_num + 2, big_num + 3, 进制=10)
        _ = d1 + d2
    dy_big_time = time.time() - start

    print(f"大数运算:")
    print(f"  Fraction: {frac_big_time:.4f}s")
    print(f"  多进制有理数: {dy_big_time:.4f}s, 慢 {dy_big_time / frac_big_time:.2f}倍")
    print()


def 测试字符串转换():
    """测试字符串表示转换性能"""
    print("测试字符串转换性能:")
    operations = 1000

    # 准备数据
    ints = [random.randint(1, 1000000) for _ in range(operations)]
    dys = [dy(x, 进制=10) for x in ints]
    dys_hex = [dy(hex(x)[2:], 进制=16) for x in ints]

    # 整数转字符串
    start = time.time()
    for x in ints:
        _ = str(x)
    int_str_time = time.time() - start

    # 多进制有理数转字符串（十进制）
    start = time.time()
    for x in dys:
        _ = str(x)
    dy_str_time = time.time() - start

    # 多进制有理数转字符串（十六进制）
    start = time.time()
    for x in dys_hex:
        _ = str(x)
    dy_hex_str_time = time.time() - start

    # 测试浮点数表示
    start = time.time()
    for x in dys[:100]:  # 只测试100个，因为浮点数转换较慢
        _ = x.浮点数()
    dy_float_repr_time = time.time() - start

    print(f"转字符串:")
    print(f"  整数: {int_str_time:.4f}s")
    print(f"  多进制有理数(十进制): {dy_str_time:.4f}s, 慢 {dy_str_time / int_str_time:.2f}倍")
    print(f"  多进制有理数(十六进制): {dy_hex_str_time:.4f}s, 慢 {dy_hex_str_time / int_str_time:.2f}倍")
    print(f"  浮点数表示(100次): {dy_float_repr_time:.4f}s")
    print()


def 测试内存使用():
    """测试内存使用情况"""
    print("测试内存使用:")
    import sys

    # 整数内存
    int_obj = 1234567890
    int_size = sys.getsizeof(int_obj)

    # Fraction内存
    frac_obj = Fraction(1234567890, 987654321)
    frac_size = sys.getsizeof(frac_obj)

    # 多进制有理数内存
    dy_obj = dy(1234567890, 987654321, 进制=10)
    dy_size = sys.getsizeof(dy_obj)

    # 获取实际对象大小（包括引用对象）
    def get_total_size(obj, seen=None):
        """递归获取对象总大小"""
        if seen is None:
            seen = set()

        obj_id = id(obj)
        if obj_id in seen:
            return 0

        seen.add(obj_id)
        size = sys.getsizeof(obj)

        if isinstance(obj, dict):
            size += sum(get_total_size(k, seen) + get_total_size(v, seen) for k, v in obj.items())
        elif hasattr(obj, '__dict__'):
            size += get_total_size(obj.__dict__, seen)
        elif hasattr(obj, '__slots__'):
            for slot in obj.__slots__:
                if hasattr(obj, slot):
                    size += get_total_size(getattr(obj, slot), seen)
        elif isinstance(obj, (list, tuple, set)):
            size += sum(get_total_size(item, seen) for item in obj)

        return size

    dy_total_size = get_total_size(dy_obj)

    print(f"整数大小: {int_size} 字节")
    print(f"Fraction大小: {frac_size} 字节")
    print(f"多进制有理数大小: {dy_size} 字节")
    print(f"多进制有理数总大小(包括引用): {dy_total_size} 字节")
    print()


def 测试特殊运算():
    """测试特殊运算性能"""
    print("测试特殊运算性能:")

    # 测试进制转换
    dy_obj = dy("123456789abcdef", 进制=16)

    start = time.time()
    for _ in range(1000):
        _ = dy_obj.进制转换(进制=10)
    convert_time = time.time() - start

    print(f"进制转换(1000次): {convert_time:.4f}s")

    # 测试p-adic表示
    dy_obj2 = dy("355", "113", 进制=10)  # π的近似

    start = time.time()
    for _ in range(100):
        _ = dy_obj2.padic表示(截断位数=30)
    padic_time = time.time() - start

    print(f"p-adic表示(100次): {padic_time:.4f}s")

    # 测试有理数逼近
    start = time.time()
    for _ in range(100):
        _ = dy.有理数逼近("3.14159265358979323846...", 进制=10)
    approx_time = time.time() - start

    print(f"有理数逼近(100次): {approx_time:.4f}s")
    print()


def 综合性能测试():
    """综合性能测试场景"""
    print("=" * 50)
    print("多进制有理数类性能测试")
    print("=" * 50)
    print()

    测试创建对象()
    测试基本运算()
    测试复杂运算()
    测试幂运算()
    测试分数运算()
    测试字符串转换()
    测试特殊运算()
    测试内存使用()

    print("=" * 50)
    print("测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    综合性能测试()

    # 添加一个实际使用场景的示例
    print("\n实际使用场景示例:")
    print("在16进制下进行分数运算:")
    a = dy("", 进制=16)  # 10
    b = dy("3", 进制=16)  # 3
    c = dy("1","2", 进制=16)  # 0.5

    result = (a + b) * c
    print(f"({a} + {b}) * {c} = {result}")
    print(f"十进制值: {float(result)}")

    print("\n进制转换示例:")
    num = dy("255", 进制=10)
    print(f"十进制: {num}")
    print(f"转二进制: {num.进制转换(进制=2)}")
    print(f"转十六进制: {num.进制转换(进制=16)}")