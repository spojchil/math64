import pandas as pd
import matplotlib.pyplot as plt
import time

plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用 SimHei 字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
# 读取CSV文件
df = pd.read_csv(r'F:\math64\小游戏\updated_electricity_data.csv', header=None, names=['Time', 'Remaining_Energy'])

# 转换时间格式
df['Time'] = pd.to_datetime(df['Time'])

# 计算时间差和能量差
df['Time_Diff'] = df['Time'].diff().dt.total_seconds() / 3600  # 时间差，单位为小时
df['Energy_Diff'] = df['Remaining_Energy'].diff()  # 能量差，单位为度

# 计算功率
df['Power'] = -1000 * df['Energy_Diff'] / df['Time_Diff']
df1 = df
# 计算中点时间
# 将时间转换为时间戳（数值），计算中点后再转换回时间格式
df['Mid_Time'] = pd.to_datetime((df['Time'].astype('int64') + df['Time'].shift(1).astype('int64')) / 2)

# 删除无效行
df = df.drop(0)

# 创建画布和主 y 轴
fig, ax1 = plt.subplots(figsize=(12, 6))

# 绘制功率曲线（左侧 y 轴）
color = 'tab:blue'
ax1.set_xlabel('时间')
ax1.set_ylabel('功率 (瓦)', color=color)
ax1.plot(df['Mid_Time'], df['Power'], marker='o', linestyle='-', color=color, label='功率')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True)

zuixiadainl = df['Remaining_Energy'].iloc[-1]
pengjjun = (-1000 * df['Energy_Diff'].sum()) / df['Time_Diff'].sum()
pengjjun5 = (-1000 * df['Energy_Diff'].tail(5).sum()) / df['Time_Diff'].tail(5).sum()
pengjjun15 = (-1000 * df['Energy_Diff'].tail(15).sum()) / df['Time_Diff'].tail(15).sum()

def seconds_to_dhms(seconds):
    days = seconds // 86400
    remaining_seconds = seconds % 86400

    hours = remaining_seconds // 3600
    remaining_seconds %= 3600

    minutes = remaining_seconds // 60

    return f"{int(days)}天{int(hours)}小时{int(minutes)}分"


shengyv5 = seconds_to_dhms(zuixiadainl / pengjjun5 * 3600000)
shengyv15 = seconds_to_dhms(zuixiadainl / pengjjun15 * 3600000)
shengyv = seconds_to_dhms(zuixiadainl / pengjjun * 3600000)

# 创建右侧 y 轴
ax2 = ax1.twinx()

# 绘制剩余电量曲线（右侧 y 轴）
color = 'tab:red'
ax2.set_ylabel('剩余电量 (度)', color=color)
ax2.plot(df1['Time'], df1['Remaining_Energy'], marker='s', linestyle='--', color=color, label='剩余电量')
ax2.tick_params(axis='y', labelcolor=color)

# 添加图例
fig.legend(loc='upper left', bbox_to_anchor=(0.0, 0.8))
# 设置标题
plt.title('功率与剩余电量随时间变化图')
plt.figtext(0.8, 0.9, f'平均功率{pengjjun:.2f}瓦，距离用完还有{shengyv}', fontsize=12, color='blue', ha='center')
plt.figtext(0.8, 0.93, f'近十五次平均功率{pengjjun15:.2f}瓦，距离用完还有{shengyv15}', fontsize=12, color='blue',
            ha='center')
plt.figtext(0.8, 0.96, f'近五次平均功率{pengjjun5:.2f}瓦，距离用完还有{shengyv5}', fontsize=12, color='blue',
            ha='center')
output_file = r'F:\math64\tupian\power_and_energy_plot.png'
plt.savefig(output_file, dpi=200)
plt.savefig(r"C:\Users\20695\Desktop\电量变化图.png", dpi=300)
# 显示图表
# plt.show()
time.sleep(5)
import subprocess

subprocess.run([r'F:\math64\.venv\Scripts\pythonw.exe', r'F:\math64\小游戏\版本.py'], capture_output=True, text=True)
