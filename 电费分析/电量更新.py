import warnings
import requests
import csv
import os
import json
from datetime import datetime
import time
import subprocess

# 新增在 imports 部分
from loguru import logger
import sys
from pathlib import Path

# 配置日志（添加到所有 import 之后，其他代码之前）
log_dir = Path(r"F:\math64\电费分析\logs")  # 日志目录
log_dir.mkdir(parents=True, exist_ok=True)  # 自动创建目录

logger.add(
    log_dir / "runtime_{time}.log",  # 日志文件路径
    rotation="10 MB",                # 每个日志文件最大10MB
    retention="3 days",              # 保留3天日志
    compression="zip",               # 旧日志压缩保存
    encoding="utf-8",
    level="DEBUG",                   # 记录所有级别日志
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# 添加单独的错误日志
logger.add(
    log_dir / "error.log",
    level="ERROR",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    encoding="utf-8"
)

logger.info("====== 程序启动 ======")

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
    try:
        logger.debug("开始执行登录流程")
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
                logger.success("登录成功，获取到 id_token")
                return login_data["data"]["idToken"]
            else:
                logger.error(f"登录失败 | 响应内容: {login_data}")
                sys.exit(1)
        else:
            logger.error(f"登录请求失败 | 状态码: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        logger.exception("登录过程中发生未捕获的异常")
        sys.exit(1)

# 第二步：获取重定向 URL 和 cookies
def step2_get_redirect_url(id_token):
    try:
        logger.debug("正在获取 cookies部分1")
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
            logger.success("成功获取到 cookies部分1")
            return redirect_url, response.cookies, supwisdomapptoken, sid, b_host
        else:
            logger.error(f"获取 cookies部分1失败 | 状态码: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        logger.exception("获取 cookies部分1异常")
        sys.exit(1)

# 第三步：获取授权码和新的 cookies
def step3_get_auth_code(redirect_url, cookies):
    try:
        logger.debug("正在获取 cookies部分2")
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
            logger.success("成功获取到 cookies部分2")
            return auth_url, response.cookies
        else:
            logger.error(f"获取 cookies部分2失败 | 状态码: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        logger.exception("获取 cookies部分2异常")
        sys.exit(1)

# 第四步：获取最终的支付页面 URL 和 cookies
def step4_get_payment_url(auth_url, cookies):
    try:
        logger.debug("正在获取 cookies部分3")
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
            logger.success("成功获取到 cookies部分3")
            return payment_url, response.cookies, SESSION
        else:
            logger.error(f"获取 cookies部分3失败 | 状态码: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        logger.exception("获取 cookies部分3异常")
        sys.exit(1)
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
    global cookies,base_config
    retries = 0

    logger.info(f"开始查询电费数据，最大重试次数: {max_retries}")
    while retries < max_retries:
        try:
            logger.debug(f"第 {retries + 1} 次尝试请求接口")
            response = requests.get(url, headers=headers, params=params, verify=False, cookies=cookies)

            if response.status_code == 200:
                if is_cookie_valid(response):
                    logger.success("成功获取有效电费数据")
                    return response.json()

                logger.warning("Cookie 已过期，触发更新流程")
                del base_config['cookies']
                base_config['cookies'] = get_new_cookies()
                cookies = base_config['cookies']
                write_config(r"基础配置.json", base_config)
                logger.info("Cookie 更新完成，等待重试...")
                time.sleep(10)
                retries += 1
            else:
                logger.error(f"接口请求失败 | 状态码: {response.status_code}")
                retries += 1
        except Exception as e:
            logger.exception("电费数据获取过程中发生异常")
            retries += 1

    logger.critical("达到最大重试次数仍未获取有效数据")
    return None

def save_data(data):
    try:
        logger.debug("进入数据保存流程")
        if base_config["up_et"]!=float(data['quantity']):
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            current_quantity = float(data['quantity'])
            logger.info(f"检测到电量变化: {base_config['up_et']} -> {current_quantity}")
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
            try:
                logger.debug("启动图表生成子进程")
                result = subprocess.run(
                    [r'F:/math64/.venv/Scripts/pythonw.exe', r'F:/math64/电费分析/作图.py'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )

                # 记录子进程的标准输出
                if result.stdout:
                    logger.info(f"作图脚本输出:\n{result.stdout}")

                # 记录子进程的错误输出
                if result.stderr:
                    logger.error(f"作图脚本错误:\n{result.stderr}")

                # 检查子进程退出码
                if result.returncode == 0:
                    logger.success("图表生成成功")
                else:
                    logger.error(f"图表生成失败 | 错误码: {result.returncode}")
            except Exception as e:
                logger.exception("执行子进程时发生异常")
    except Exception as e:
        logger.exception("数据保存过程中发生异常")
if __name__ == "__main__":
    try:
        logger.info("====== 主程序开始执行 ======")
        data = get_electricity()

        if data and data.get('returncode') == '100':
            logger.success(f"成功获取电量数据: {data['quantity']} 度")
            save_data(data)
        else:
            logger.error("获取数据失败，返回码无效")
            sys.exit(1)

        logger.info("====== 程序正常结束 ======")
    except Exception as e:
        logger.exception("主程序发生未捕获异常")
        sys.exit(1)