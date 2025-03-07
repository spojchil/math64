from loguru import logger
import pandas as pd
import matplotlib.pyplot as plt
import time
import subprocess
import sys
# 配置日志（保存到文件，每天轮换，保留7天）
log_dir = r"电费分析/logs"
logger.add(f"{log_dir}/作图日志.log",
           rotation="10 MB",
           retention=4,  # 仅保留4个最新文件
           compression="zip",  # 自动压缩旧日志（可选参数）
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
           level="DEBUG")
logger.add(
    f"{log_dir}/错误日志.log",
    level="ERROR",
    rotation="10 MB",
    retention=4 ,
    compression="zip",
    encoding="utf-8"
)
@logger.catch  # 自动捕获未处理的异常
def main():
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    try:
        # 记录文件读取操作
        logger.info("开始读取电量数据文件")
        df = pd.read_csv(r'电费分析/电量数据.csv', header=None, names=['Time', 'Remaining_Energy'])
        logger.success(f"成功读取数据，共{len(df)}条记录")
    except FileNotFoundError:
        logger.error("电量数据文件未找到，请确认文件路径")
        sys.exit(1)
    except Exception as e:
        logger.error(f"读取文件时发生未知错误: {str(e)}")
        sys.exit(1)

    # 数据处理流程
    try:
        logger.info("开始处理时间数据")
        df['Time'] = pd.to_datetime(df['Time'])

        logger.debug("计算时间差和能量差")
        df['Time_Diff'] = df['Time'].diff().dt.total_seconds() / 3600
        df['Energy_Diff'] = df['Remaining_Energy'].diff()

        logger.debug("计算功率数据")
        df['Power'] = -1000 * df['Energy_Diff'] / df['Time_Diff']
        df1 = df.copy()

        logger.debug("计算中点时间")
        df['Mid_Time'] = pd.to_datetime((df['Time'].astype('int64') + df['Time'].shift(1).astype('int64')) / 2)

        logger.info("清理无效数据")
        df = df.drop(0)
        logger.success(f"数据处理完成，剩余{len(df)}条有效数据")
    except Exception as e:
        logger.error(f"数据处理过程中发生错误: {str(e)}")
        sys.exit(1)

    # 绘图模块
    try:
        logger.info("开始生成图表")
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # 功率曲线
        ax1.set_xlabel('时间')
        ax1.set_ylabel('功率 (瓦)', color='tab:blue')
        ax1.plot(df['Mid_Time'], df['Power'], marker='o', linestyle='-', color='tab:blue', label='功率')
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        ax1.grid(True)

        # 剩余电量曲线
        ax2 = ax1.twinx()
        ax2.set_ylabel('剩余电量 (度)', color='tab:red')
        ax2.plot(df1['Time'], df1['Remaining_Energy'], marker='s', linestyle='--', color='tab:red', label='剩余电量')
        ax2.tick_params(axis='y', labelcolor='tab:red')

        # 添加图例和标题
        fig.legend(loc='upper left', bbox_to_anchor=(0.0, 0.8))
        plt.title('功率与剩余电量随时间变化图')

        # 计算统计信息
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

        # 记录关键计算结果
        logger.info(f"平均功率计算结果: {pengjjun:.2f}瓦")
        logger.info(f"近5次平均功率: {pengjjun5:.2f}瓦")
        logger.info(f"近15次平均功率: {pengjjun15:.2f}瓦")

        # 添加统计信息到图表
        plt.figtext(0.8, 0.96, f'近五次平均功率{pengjjun5:.2f}瓦，距离用完还有{shengyv5}', fontsize=12, color='blue',
                    ha='center')
        plt.figtext(0.8, 0.93, f'近十五次平均功率{pengjjun15:.2f}瓦，距离用完还有{shengyv15}', fontsize=12, color='blue',
                    ha='center')
        plt.figtext(0.8, 0.9, f'平均功率{pengjjun:.2f}瓦，距离用完还有{shengyv}', fontsize=12, color='blue', ha='center')

        # 保存图表
        output_files = [r'电费分析/电量图.png']
        for path in output_files:
            try:
                plt.savefig(path, dpi=300)
                logger.success(f"图表已保存至: {path}")
            except Exception as e:
                logger.error(f"保存图表到 {path} 失败: {str(e)}")

        time.sleep(5)
    except Exception as e:
        logger.error(f"图表生成过程中发生错误: {str(e)}")
        sys.exit(1)

    # 邮件发送模块
    try:
        logger.info("准备发送邮件")
        cmd = [
            'python',
            r'电费分析/邮件发送.py'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True,encoding='utf-8')
        logger.debug(f"邮件发送命令返回码: {result.returncode}")

        if result.returncode == 0:
            logger.success("邮件发送成功")
        else:
            logger.error(f"邮件发送失败，错误信息:\n{result.stderr}")
    except Exception as e:
        logger.error(f"执行邮件发送时发生错误: {str(e)}")


if __name__ == "__main__":
    logger.info("程序启动")
    main()
    logger.info("程序执行完成")