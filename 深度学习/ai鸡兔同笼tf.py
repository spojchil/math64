import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

# 生成数据集
def generate_data(num_samples):
    heads = np.random.randint(1, 100, num_samples)
    legs = np.random.randint(2 * heads, 4 * heads + 1, num_samples)
    chickens = (4 * heads - legs) / 2
    rabbits = (legs - 2 * heads) / 2
    return heads, legs, chickens, rabbits

num_samples = 10000
heads, legs, chickens, rabbits = generate_data(num_samples)

# 合并数据
X = np.column_stack((heads, legs))
y = np.column_stack((chickens, rabbits))

# 构建模型
inputs = Input(shape=(2,))
x = Dense(16, activation='relu')(inputs)
x = Dense(16, activation='relu')(x)
outputs = Dense(2)(x)
model = Model(inputs, outputs)

# 编译模型
model.compile(optimizer='adam', loss='mse')

# 训练模型
model.fit(X, y, epochs=50, batch_size=32, validation_split=0.2)

# 保存模型为 .keras 格式
model.save("chicken_rabbit_model.keras")

# 加载模型时的代码
loaded_model = tf.keras.models.load_model("chicken_rabbit_model.keras")

# 测试数据
test_heads = np.array([35, 20, 10])
test_legs = np.array([94, 56, 32])
test_X = np.column_stack((test_heads, test_legs))

# 预测
predictions = loaded_model.predict(test_X)
print(predictions)