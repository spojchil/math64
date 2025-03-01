import random


def play_game(n, initial_funds, f):
    funds = initial_funds
    rounds = n
    win_probability = 0.4
    win_multiplier = 1.4
    lose_multiplier = 0.8
    fee_rate = 0.02

    for _ in range(rounds):
        # 计算投入金额
        bet = funds * f

        # 模拟游戏结果
        if random.random() < win_probability:
            # 胜利
            funds += bet * win_multiplier * (1 - fee_rate) - bet
        else:
            # 失败
            funds += bet * lose_multiplier * (1 - fee_rate) - bet

        # 确保资金不会变成负数（由于浮点数精度问题，这里设置一个非常小的正数作为下限）
        funds = max(funds, 1e-9)

    return funds


# 设定游戏轮数和投入比例
n = 1000 # 游戏轮数
f = 0.5  # 每轮投入比例

# 开始游戏
initial_funds = 100
final_funds = play_game(n, initial_funds, f)

print(f"经过{n}轮游戏后，最终资金为：{final_funds:.4f}")