import warnings
import requests
import csv
import os
import json
from datetime import datetime
import time
import subprocess
warnings.filterwarnings("ignore")
def read_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config
def write_config(file_path, config_data):
    with open(file_path, 'w') as file:
        json.dump(config_data, file, indent=4)
base_config=read_config(r"基础配置.json")
# 第一步：登录获取 token
def step1_login(username,password):
    login_url = "https://mycas.haut.edu.cn/token/password/passwordLogin"
    login_params = {
        "username": username,
        "password": password,
        "appId": "com.supwisdom.haut",
        "geo": "",
        "deviceId": "ZO6cVuH+/1UDAElLPJpu7AFi",
        "osType": "android",
        "clientId": "b08f7f00db0e2a1a14a31517ae7592d3",
        "mfaState": ""
    }
    headers = {
        "User-Agent": "SWSuperApp/1.2.6(OPPOPGX110OPPO14)",
        "Host": "mycas.haut.edu.cn",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    response = requests.post(login_url, params=login_params, headers=headers, verify=False)
    if response.status_code == 200:
        login_data = response.json()
        if login_data["code"] == 0:
            id_token = login_data["data"]["idToken"]
            # print("Step 1: Login successful, id_token:", id_token)
            return id_token
        else:
            print("Step 1: Login failed:", login_data)
            exit()
    else:
        print("Step 1: Login request failed:", response.status_code)
        exit()

# 第二步：获取重定向 URL 和 cookies
def step2_get_redirect_url(id_token):
    url = "https://hub.17wanxiao.com/bsacs/light.action"
    params = {
        "flag": "supwisdomapp_hgdswjf",
        "ecardFunc": "index",
        "token": id_token
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; PGX110 Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/117.0.0.0 Mobile Safari/537.36 SuperApp",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "X-Requested-With": "com.supwisdom.haut",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    cookies = {
        "userToken": id_token,
        "Domain": "hub.17wanxiao.com",
        "Path": "/"
    }
    response = requests.get(url, params=params, headers=headers, cookies=cookies, allow_redirects=False, verify=False)
    if response.status_code == 302:
        redirect_url = response.headers["Location"]
        supwisdomapptoken = response.cookies.get('supwisdomapptoken')
        sid = response.cookies.get('sid')
        b_host = response.cookies.get('b_host')
        # print("Step 2: Redirect URL:", redirect_url,response.cookies)
        return redirect_url, response.cookies, supwisdomapptoken, sid, b_host
    else:
        print("Step 2: Failed to get redirect URL:", response.status_code, response.cookies)
        exit()

# 第三步：获取授权码和新的 cookies
def step3_get_auth_code(redirect_url, cookies):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; PGX110 Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/117.0.0.0 Mobile Safari/537.36 SuperApp",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "X-Requested-With": "com.supwisdom.haut",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    response = requests.get(redirect_url, headers=headers, cookies=cookies, allow_redirects=False, verify=False)
    if response.status_code == 302:
        auth_url = response.headers["Location"]
        # print("Step 3: Auth URL:", auth_url,response.cookies)
        return auth_url, response.cookies
    else:
        print("Step 3: Failed to get auth URL:", response.status_code)
        exit()

# 第四步：获取最终的支付页面 URL 和 cookies
def step4_get_payment_url(auth_url, cookies):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; PGX110 Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/117.0.0.0 Mobile Safari/537.36 SuperApp",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "X-Requested-With": "com.supwisdom.haut",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    response = requests.get(auth_url, headers=headers, cookies=cookies, allow_redirects=False, verify=False)
    if response.status_code == 302:
        payment_url = response.headers["Location"]
        SESSION = response.cookies.get('SESSION')
        # print("Step 4: Payment URL:", payment_url,response.cookies)
        return payment_url, response.cookies, SESSION
    else:
        print("Step 4: Failed to get payment URL:", response.status_code)
        exit()

# 第五步：获取cookies
def step5_get_cookies(supwisdomapptoken, sid, b_host, SESSION):
    cookies = {
        "supwisdomapptoken": supwisdomapptoken,
        "sid": sid,
        "b_host": b_host,
        "SESSION": SESSION
    }
    return cookies

# 主函数
def get_new_cookies():
    # 第一步：登录
    username = base_config["username"]
    password = base_config["password"]
    id_token = step1_login(username,password)

    # 第二步：获取重定向 URL 和 cookies
    redirect_url, cookies_step2, supwisdomapptoken, sid, b_host = step2_get_redirect_url(id_token)

    # 第三步：获取授权码和新的 cookies
    auth_url, cookies_step3 = step3_get_auth_code(redirect_url, cookies_step2)

    # 第四步：获取支付页面 URL 和 cookies
    payment_url, cookies_step4, SESSION = step4_get_payment_url(auth_url, cookies_step3)

    # 第五步：获取电费数据
    return step5_get_cookies(supwisdomapptoken, sid, b_host, SESSION)

def is_cookie_valid(response):
    try:
        # 尝试将响应体解析为JSON
        response_json = response.json()
        # 如果能够成功解析，通常意味着Cookie是有效的（假设API在Cookie无效时不会返回JSON）
        return True
    except (json.JSONDecodeError, ValueError):
        # 如果解析失败（可能是因为响应体不是有效的JSON），则可能意味着Cookie无效
        return False

# 定义请求的URL
url = "https://h5cloud.17wanxiao.com:18443/CloudPayment/user/getRoomState.do"
roomverify = base_config["roomverify"]
params = {
    "payProId": 726,
    "schoolcode": 43,
    "businesstype": 2,
    "roomverify": roomverify
}

# 定义请求头
headers = {
    "Host": "h5cloud.17wanxiao.com:18443",
    "Connection": "keep-alive",
    "sec-ch-ua": '"Android WebView";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?1",
    "User-Agent": "Mozilla/5.0 (Linux; Android 14; PGX110 Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/117.0.0.0 Mobile Safari/537.36 SuperApp",
    "sec-ch-ua-platform": '"Android"',
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://h5cloud.17wanxiao.com:18443/CloudPayment/bill/selectPayProject.do?txcode=elecdetails&interurl=elecdetails&payProId=726&amtflag=0&payamt=0&payproname=%E7%94%A8%E7%94%B5%E6%94%AF%E5%87%BA&img=https://payicons.59wanmei.com/cloudpayment/images/project/img-nav_2.png&subPayProId=",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}

cookies = base_config['cookies']

# 数据存储文件
DATA_FILE = r"电量数据.csv"

def get_electricity(max_retries=3):
    global cookies
    global base_config
    retries = 0
    while retries < max_retries:
        response = requests.get(url, headers=headers, params=params, verify=False, cookies=cookies)

        if response.status_code == 200:
            if is_cookie_valid(response):
                return response.json()

        print("Cookie 过期")
        del base_config['cookies']
        base_config['cookies'] = get_new_cookies()
        cookies=base_config['cookies']
        write_config(r"基础配置.json", base_config)
        retries += 1

        # 可选：添加延迟
        time.sleep(10)

    print("Failed to acquire valid electricity data after multiple retries.")
    return None

def save_data(data):
    """保存数据到CSV文件"""
    if base_config["up_et"]!=float(data['quantity']):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_quantity = float(data['quantity'])
        base_config["up_et"] = float(data['quantity'])
        write_config(r"基础配置.json", base_config)

        # 检查文件是否存在
        file_exists = os.path.isfile(DATA_FILE)

        with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['时间', '剩余电量（度）'])
            writer.writerow([current_time, current_quantity])
        time.sleep(3)
        subprocess.run([r'F:/math64/.venv/Scripts/pythonw.exe', r'F:/math64/电费分析/作图.py'], capture_output=True, text=True)


if __name__ == "__main__":
    # 获取数据
    data = get_electricity()

    if data and data.get('returncode') == '100':
        #print(f"当前剩余电量：{data['quantity']} 度")

        # 保存数据并生成图表
        save_data(data)
    else:
        print("获取数据失败，请检查网络或参数")