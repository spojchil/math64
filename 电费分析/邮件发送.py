import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from loguru import logger

# 配置日志
current_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(current_dir, "logs")
os.makedirs(log_dir, exist_ok=True)

logger.add(
    os.path.join(log_dir, "电费分析/邮件日志.log"),
    rotation="10 MB",
    retention=4,
    compression="zip",
    level="DEBUG"
)

def send_email():
    # 从环境变量获取敏感信息
    sender_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    receiver_email = sender_email  # 发送给自己

    if not all([sender_email, password]):
        logger.error("邮箱配置信息缺失")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "电量变化报告"

        # 添加正文
        body = "最新电量统计图表已附上，请查收。\n\n此邮件为自动发送，请勿直接回复。"
        msg.attach(MIMEText(body, 'plain'))

        # 添加附件
        attachment_path = os.path.join(current_dir, "output", "电费分析/电量图.png")
        with open(attachment_path, "rb") as f:
            attachment = MIMEApplication(f.read(), Name="电费分析/电量图.png")
            attachment['Content-Disposition'] = f'attachment; filename="电费分析/电量图.png"'
            msg.attach(attachment)

        # 发送邮件
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            logger.success("邮件发送成功")
    except Exception as e:
        logger.error(f"邮件发送失败: {str(e)}")
        raise

if __name__ == "__main__":
    send_email()