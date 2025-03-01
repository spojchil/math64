import numpy as np
import tensorflow as tf
loaded_model = tf.keras.models.load_model("chicken_rabbit_model.keras")

# 测试数据
test_heads = np.array([350000,10])
test_legs = np.array([940000, 32])
test_X = np.column_stack((test_heads, test_legs))

# 预测
predictions = loaded_model.predict(test_X)
print(predictions)