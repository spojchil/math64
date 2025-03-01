import csv

# 输入文件名
input_file = 'electricity_data.csv'
# 输出文件名
output_file = 'updated_electricity_data.csv'

# 初始化变量来存储上一行的电量值
previous_balance = None

# 打开输入文件和输出文件
with open(input_file, mode='r', newline='') as infile, open(output_file, mode='w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # 遍历CSV文件的每一行
    for row in reader:
        timestamp, balance = row  # 解包行数据为时间戳和电量值
        balance = float(balance)  # 确保电量值是浮点数以便比较

        # 如果电量值与上一行不同，则写入输出文件
        if previous_balance is None or previous_balance != balance:
            writer.writerow(row)
            previous_balance = balance  # 更新上一行的电量值

print(f"已更新数据并保存到 {output_file}")