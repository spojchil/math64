import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.preprocessing import StandardScaler

# 数据生成函数（改进后）
def generate_data(num_samples):
    heads = np.random.randint(1, 100, num_samples)
    legs = np.random.randint(2 * heads, 4 * heads + 1, num_samples)
    chickens = (4 * heads - legs) / 2
    rabbits = (legs - 2 * heads) / 2
    return heads, legs, chickens, rabbits

# 转换为PyTorch张量
def to_tensor(data):
    return torch.tensor(data, dtype=torch.float32)

# 生成训练数据
num_samples = 10000
heads, legs, chickens, rabbits = generate_data(num_samples)

# 输入特征和标签
X = np.column_stack((heads, legs))
y = np.column_stack((chickens, rabbits))

# 数据标准化
scaler_X = StandardScaler()
X_scaled = scaler_X.fit_transform(X)

# 转换为PyTorch张量
X_tensor = to_tensor(X_scaled)
y_tensor = to_tensor(y)

# 定义模型（简化结构）
class SimpleNet(nn.Module):
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(2, 16)
        self.fc2 = nn.Linear(16, 16)
        self.fc3 = nn.Linear(16, 2)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# 初始化模型、损失函数和优化器
model = SimpleNet()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.0001)  # 调整学习率

# 训练模型
num_epochs = 200  # 减少训练轮数
for epoch in range(num_epochs):
    # 前向传播
    outputs = model(X_tensor)
    loss = criterion(outputs, y_tensor)

    # 反向传播和优化
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if (epoch+1) % 20 == 0:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

# 测试模型
def test_model(model, heads, legs):
    with torch.no_grad():
        inputs = np.column_stack((heads, legs))
        inputs_scaled = scaler_X.transform(inputs)
        inputs_tensor = to_tensor(inputs_scaled)
        predictions = model(inputs_tensor)
        return predictions.numpy()

# 生成测试数据
test_heads = np.array([35, 20, 10])
test_legs = np.array([94, 56, 32])
predictions = test_model(model, test_heads, test_legs)

# 打印结果
print("Test Heads:", test_heads)
print("Test Legs:", test_legs)
print("Predicted Chickens:", predictions[:, 0])
print("Predicted Rabbits:", predictions[:, 1])