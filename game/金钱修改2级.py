import tkinter as tk
import hashlib
import random


# --------------------------
# 防御层1：修复校验逻辑 + 强化加密
# --------------------------
class MoneyVault:
    def __init__(self, initial):
        self.key1 = random.randint(0x00, 0xFF)  # 动态密钥
        self.key2 = 0x55AA55AA  # 固定密钥
        self.encrypted = self._encrypt(initial)
        self.checksum = self._generate_checksum(initial)

    def _encrypt(self, value):
        # 修复加密逻辑：确保可逆性
        value ^= self.key1
        # 字节交换：低8位和高8位交换（避免数据丢失）
        low_byte = (value & 0xFF)
        high_byte = (value >> 8) & 0xFF
        value = (low_byte << 8) | high_byte
        value ^= self.key2
        return value

    def _decrypt(self):
        # 解密逆向操作
        value = self.encrypted ^ self.key2
        low_byte = (value >> 8) & 0xFF
        high_byte = value & 0xFF
        value = (high_byte << 8) | low_byte
        return value ^ self.key1

    def _generate_checksum(self, value):
        # 更健壮的校验（HMAC风格）
        data = f"{value}|{self.key1}|{self.key2}".encode()
        return int(hashlib.sha256(data).hexdigest()[:8], 16)

    def validate(self):
        try:
            decrypted = self._decrypt()
            return self.checksum == self._generate_checksum(decrypted)
        except:
            return False  # 防止解密异常导致崩溃

    def update(self, new_value):
        self.encrypted = self._encrypt(new_value)
        self.checksum = self._generate_checksum(new_value)


# --------------------------
# 防御层2：安全初始化 + 反篡改
# --------------------------
def safe_init():
    global vault
    vault = MoneyVault(500)
    if not vault.validate():
        # 如果初始化校验失败，直接隐藏窗口并退出
        root.withdraw()
        root.quit()
        raise RuntimeError("校验失败：检测到内存篡改！")


# --------------------------
# GUI界面
# --------------------------
root = tk.Tk()
root.title("金钱管理器-安全模式")

try:
    safe_init()  # 安全初始化

    # 显示金钱（通过安全接口获取）
    current_money = vault._decrypt()
    money_label = tk.Label(root, text=f"金钱: {current_money}", font=("Arial", 24))
    money_label.pack(pady=20)


    # 按钮操作（封装校验逻辑）
    def update_money(delta):
        try:
            current = vault._decrypt()
            vault.update(current + delta)
            money_label.config(text=f"金钱: {current + delta}")
            if not vault.validate():
                root.withdraw()
                root.quit()
                print("检测到篡改！程序终止。")
        except:
            pass  # 防止异常导致界面卡死


    tk.Button(root, text="增加金钱", command=lambda: update_money(1), font=("Arial", 14)).pack(pady=10)
    tk.Button(root, text="减少金钱", command=lambda: update_money(-1), font=("Arial", 14)).pack(pady=10)

    root.mainloop()

except Exception as e:
    print("安全错误:", e)