import json
import time
def read_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

# 使用示例
config_data = read_config('config.json')
print(config_data['database']['port'])
def write_config(file_path, config_data):
    with open(file_path, 'w') as file:
        json.dump(config_data, file, indent=4)

# 使用示例
# 假设我们要修改端口号和日志级别
config_data['port'] = 90910
config_data['logging']['level'] = 'IN123FO'
write_config('config.json', config_data)
db=config_data['database']
time.sleep(20)
db1={
        "host": "localhost",
        "port": 3306,
        "username": "admin",
        "password": "123456"
    }
print(db==db1)
