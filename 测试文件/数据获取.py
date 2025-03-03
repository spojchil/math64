import requests
import json
import re
from urllib.parse import urlparse, parse_qs
import warnings
warnings.filterwarnings("ignore")

# 1. 登录并获取 token
'''
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
        "Content-Length": "0",
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
'''
token="eyJhbGciOiJSUzUxMiJ9.eyJBVFRSX3VzZXJObyI6IjIzMTAzMDIwMDMxMyIsInN1YiI6IjIzMTAzMDIwMDMxMyIsImlzcyI6Im15Y2FzLmhhdXQuZWR1LmNuIiwiZGV2aWNlSWQiOiJaTzZjVnVIKy8xVURBRWxMUEpwdTdBRmkiLCJBVFRSX2lkZW50aXR5VHlwZUlkIjoiUzAxIiwiQVRUUl9hY2NvdW50SWQiOiIzNjgxYTY3MDNjMGExMWVlMTQ5ZmNiNTA4MmVkMjUwOCIsIkFUVFJfdXNlcklkIjoiMzY3M2VhZDAzYzBhMTFlZTE0OWZjYjUwODJlZDI1MDgiLCJBVFRSX2lkZW50aXR5VHlwZUNvZGUiOiJzdHVkZW50IiwiQVRUUl9pZGVudGl0eVR5cGVOYW1lIjoi5pys56eRL-S4k-enkeeUnyIsIkFUVFJfb3JnYW5pemF0aW9uTmFtZSI6IuWcn-acqOW3peeoi-WtpumZoijlu7rnrZHlrabpmaIpIiwiQVRUUl91c2VyTmFtZSI6IuWtmei_m-ejiiIsImV4cCI6MTc0MjQ0NDgxNCwiQVRUUl9vcmdhbml6YXRpb25JZCI6IjAxMDMiLCJpYXQiOjE3Mzk4NTI4MTQsImp0aSI6IklkLVRva2VuLUZzRXFzVUd2VW51Y01rUkUiLCJyZXEiOiJjb20uc3Vwd2lzZG9tLmhhdXQiLCJBVFRSX29yZ2FuaXphdGlvbkNvZGUiOiIwMTAzIn0.uEe-L-COyOY5KHVDE6iaQ4A45nzHeNWnj8KxTzA-nIYzMAnhnLCZsY941AYZpLnZ16coJzlUsAUmZHyjdbjWse3b17KKBRrPh8ZWvJ-RkTFBkWrs5gz9MU9EnYpE84U5m9BzwTsm8jo7t_52UULSBGy0CD4qzld_2YpRqlMgoy3-9aBECduCUuQqYeyd6LnyxNkVNCMzhEmHe0KfTxnIZ6B8r-mD1V7I_v1DBApfCT2QIbDgoLKaiZDUTLu5khpTakN3x7iuRx9thJJqvgEfktedM11nSmFDTvXIxSp6hx6iWHXnuwO6AuYeQJ4aRrIMR6wQWAfnwe0CCeo3ualTKw"
# 2. 跳转到电费页面
def redirect_to_electricity_page(token):
    redirect_url = "https://hub.17wanxiao.com/bsacs/light.action"
    params = {
        "flag": "supwisdomapp_hgdswjf",
        "ecardFunc": "index",
        "token": token
    }
    headers = {
        "User-Agent": "SWSuperApp/1.2.6(OPPOPGX110OPPO14)",
        "Cookie": f"supwisdomapptoken={token}"
    }
    response = requests.get(redirect_url, params=params, headers=headers, allow_redirects=False, verify=False)
    if response.status_code == 302:
        setcookie = response.headers.get("Set-Cookie")
        supwisdomapptoken = re.search(r"supwisdomapptoken=([^\s;]+)", setcookie).group(1)
        sid = re.search(r"sid=([^\s;]+)", setcookie).group(1)
        b_host = re.search(r"b_host=([^\s;]+)", setcookie).group(1)
        Location = response.headers.get("Location")
        return supwisdomapptoken,sid,b_host,Location
    raise Exception("跳转到电费页面失败")

# 2.5 跳转到电费页面
def redirect_to_electricity(supwisdomapptoken,sid,b_host,Location):
    redirect_url = "https://open.17wanxiao.com/api/authorize"
    params = {
        "response_type": "code",
        "hidden": "true",
        "customerCode": "43",
        "force_login":"false",
        "redirect_uri":re.search(r"redirect_uri=([^\s&]+)", Location).group(1),
        "client_id":
    }
    headers = {
        "User-Agent": "SWSuperApp/1.2.6(OPPOPGX110OPPO14)",
        "Cookie": f"supwisdomapptoken={token}"
    }
    response = requests.get(redirect_url, params=params, headers=headers, allow_redirects=False, verify=False)
    if response.status_code == 302:
        setcookie = response.headers.get("Set-Cookie")
        supwisdomapptoken = re.search(r"supwisdomapptoken=([^\s;]+)", setcookie).group(1)
        sid = re.search(r"sid=([^\s;]+)", setcookie).group(1)
        b_host = re.search(r"b_host=([^\s;]+)", setcookie).group(1)
        return supwisdomapptoken,sid,b_host
    raise Exception("跳转到电费页面失败")

# 3. 获取电费信息
def get_electricity_info(location):
    try:
        # 解析 URL，提取查询参数
        parsed_url = urlparse(location)
        query_params = parse_qs(parsed_url.query)

        # 获取 supwisdomapptoken
        supwisdomapptoken = query_params.get("supwisdomapptoken", [None])[0]
        if not supwisdomapptoken:
            raise Exception("无法从重定向地址中提取 supwisdomapptoken")

        headers = {
            "User-Agent": "SWSuperApp/1.2.6(OPPOPGX110OPPO14)",
            "Cookie": f"supwisdomapptoken={supwisdomapptoken}"
        }

        # 发送请求获取电费信息
        response = requests.get(location, headers=headers, allow_redirects=False, verify=False)
        if response.status_code == 302:
            final_url = response.headers.get("Location")
            if final_url:
                final_response = requests.get(final_url, headers=headers, verify=False)
                if final_response.status_code == 200:
                    return final_response.json()
        raise Exception("获取电费信息失败")
    except Exception as e:
        raise Exception(f"解析重定向地址失败: {str(e)}")


# 4. 保存数据到文件
def save_data(data, filename="electricity_info.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"数据已保存到 {filename}")


# 主函数
def main():
    username = "231030200313"  # 替换为你的用户名
    password = "Sun2069510482"  # 替换为你的密码

    try:
        '''
        # 1. 登录
        token = login(username, password)
        print("登录成功，获取到 token:", token)
'''
        # 2. 跳转到电费页面
        supwisdomapptoken,sid,b_host,Location = redirect_to_electricity_page(token)
        print("跳转到电费页面成功，重定向地址:", supwisdomapptoken,sid,b_host)

        # 3. 获取电费信息
        electricity_info = get_electricity_info(redirect_location)
        print("获取电费信息成功:", electricity_info)

        # 4. 保存数据
        save_data(electricity_info)
    except Exception as e:
        print("程序出错:", str(e))


if __name__ == "__main__":
    main()