import requests
import json
from urllib.parse import urlparse, parse_qs, unquote


def login(username, password):
    login_url = "https://mycas.haut.edu.cn/token/password/passwordLogin"
    params = {
        "username": username,
        "password": password,
        "appId": "com.supwisdom.haut",
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
    response = requests.post(login_url, params=params, headers=headers, verify=False)
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 0:
            return data["data"]["idToken"]
    raise Exception("登录失败")


def get_electricity_info(username, password):
    session = requests.Session()

    # 1. 登录获取 token
    token = login(username, password)
    print("登录成功，获取到 token:", token)

    # 2. 设置固定 Cookie（根据你的日志）
    cookies = {
        "SESSION": "61a4bd2f-8d0d-4125-986b-2c8a7e65a422",
        "supwisdomapptoken": token,
        "sid": "QzZiYkN4eEEtQ2I5Qy1ZWFhXLUFHUDktWVhQUFBaeHI5dDly",
        "b_host": "eyJmbGFnIjoic3Vwd2lzZG9tYXBwIiwic2NoZW1lQW5kcmlvZCI6IiIsInNjaGVtZUlPUyI6IiJ9"
    }
    session.cookies.update(cookies)

    # 3. 访问电费页面接口（触发 Cookie 验证）
    page_url = "https://h5cloud.17wanxiao.com:18443/CloudPayment/bill/selectPayProject.do"
    page_params = {
        "txcode": "elecdetails",
        "interurl": "elecdetails",
        "payProId": "726",
        "amtflag": "0",
        "payamt": "0",
        "payproname": "用电支出",
        "img": "https://payicons.59wanmei.com/cloudpayment/images/project/img-nav_2.png",
        "subPayProId": ""
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; PGX110 Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/117.0.0.0 Mobile Safari/537.36 SuperApp",
        "Referer": "https://h5cloud.17wanxiao.com:18443/CloudPayment/bill/type.do",
        "X-Requested-With": "com.supwisdom.haut",
        "sec-ch-ua": '"Android WebView";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"'
    }
    session.get(page_url, params=page_params, headers=headers, verify=False)

    # 4. 调用数据接口
    data_url = "https://h5cloud.17wanxiao.com:18443/CloudPayment/user/getRoomState.do"
    data_params = {
        "payProId": "726",
        "schoolcode": "43",
        "businesstype": "2",
        "roomverify": "102-2--124-2517"
    }
    response = session.get(data_url, params=data_params, headers=headers, verify=False)

    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            print("响应内容:", response.text)
            raise Exception("JSON 解析失败")
    else:
        raise Exception(f"请求失败，状态码: {response.status_code}")


def save_data(data, filename="electricity_info.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"数据已保存到 {filename}")


if __name__ == "__main__":
    username = "231030200313"
    password = "Sun2069510482"

    try:
        electricity_info = get_electricity_info(username, password)
        print("获取电费信息成功:", electricity_info)
        save_data(electricity_info)
    except Exception as e:
        print("程序出错:", str(e))