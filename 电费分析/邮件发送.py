import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_email_to_self(file_path):
    # 配置信息
    sender_email = "2069510482@qq.com"  # 发送方邮箱
    receiver_email = "2069510482@qq.com"  # 接收方邮箱（可以是同一个）
    password = "pumqldiwthpndcbh"  # 替换为SMTP授权码，不是邮箱密码！
    smtp_server = "smtp.qq.com"
    smtp_port = 465  # SSL端口

    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "电量变化更新"  # 邮件主题

    # 添加附件
    with open(file_path, "rb") as f:
        attachment = MIMEApplication(f.read(), Name=file_path.split("/")[-1])
        attachment['Content-Disposition'] = f'attachment; filename="{file_path.split("/")[-1]}"'
        msg.attach(attachment)

    # 发送邮件
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("邮件发送成功！")
    except Exception as e:
        print(f"发送失败: {e}")
    finally:
        server.quit()

# 使用示例
#send_email_to_self(r"电量图.png")