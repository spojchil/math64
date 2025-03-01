import tkinter as tk

# 加密密钥（可以自定义）
KEY = 0xAA  # 这是一个简单的密钥，可以更复杂

# 加密函数
def encrypt(value):
    return value ^ KEY  # 使用异或加密

# 解密函数
def decrypt(encrypted_value):
    return encrypted_value ^ KEY  # 使用异或解密

# 初始化加密后的金钱
encrypted_money = encrypt(500)

# 定义增加金钱的函数
def increase_money():
    global encrypted_money
    # 解密当前金钱
    current_money = decrypt(encrypted_money)
    # 增加金钱
    current_money += 1
    # 加密并保存
    encrypted_money = encrypt(current_money)
    # 更新显示
    money_label.config(text=f"金钱: {current_money}")

# 定义减少金钱的函数
def decrease_money():
    global encrypted_money
    # 解密当前金钱
    current_money = decrypt(encrypted_money)
    # 减少金钱
    current_money -= 1
    # 加密并保存
    encrypted_money = encrypt(current_money)
    # 更新显示
    money_label.config(text=f"金钱: {current_money}")

# 创建主窗口
root = tk.Tk()
root.title("金钱管理器")

# 创建显示金钱的标签
current_money = decrypt(encrypted_money)  # 解密初始金钱
money_label = tk.Label(root, text=f"金钱: {current_money}", font=("Arial", 24))
money_label.pack(pady=20)

# 创建增加金钱的按钮
increase_button = tk.Button(root, text="增加金钱", command=increase_money, font=("Arial", 14))
increase_button.pack(pady=10)

# 创建减少金钱的按钮
decrease_button = tk.Button(root, text="减少金钱", command=decrease_money, font=("Arial", 14))
decrease_button.pack(pady=10)

# 运行主循环
root.mainloop()