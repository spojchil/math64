import requests

# 第一步：登录获取 token
def step1_login():
    login_url = "https://mycas.haut.edu.cn/token/password/passwordLogin"
    login_params = {
        "username": "231030200313",
        "password": "Sun2069510482",
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
            print("Step 1: Login successful, id_token:", id_token)
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
        print("Step 2: Redirect URL:", redirect_url)
        return redirect_url, response.cookies
    else:
        print("Step 2: Failed to get redirect URL:", response.status_code)
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
        print("Step 3: Auth URL:", auth_url)
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
        print("Step 4: Payment URL:", payment_url)
        return payment_url, response.cookies
    else:
        print("Step 4: Failed to get payment URL:", response.status_code)
        exit()

# 第五步：获取电费数据
def step5_get_electricity_data(payment_url, cookies):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; PGX110 Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/117.0.0.0 Mobile Safari/537.36 SuperApp",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://h5cloud.17wanxiao.com:18443/CloudPayment/bill/selectPayProject.do?txcode=elecdetails&interurl=elecdetails&payProId=726&amtflag=0&payamt=0&payproname=用电支出&img=https://payicons.59wanmei.com/cloudpayment/images/project/img-nav_2.png&subPayProId=",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    electricity_url = "https://h5cloud.17wanxiao.com:18443/CloudPayment/user/getRoomState.do"
    params = {
        "payProId": "726",
        "schoolcode": "43",
        "businesstype": "2",
        "roomverify": "102-2--124-2517"
    }
    # 确保 cookies 是 latin-1 可编码的
    cookies_latin1 = {k: v.encode('latin-1', 'ignore').decode('latin-1') for k, v in cookies.items()}
    response = requests.get(electricity_url, params=params, headers=headers, cookies=cookies_latin1, verify=False)
    if response.status_code == 200:
        electricity_data = response.json()
        if electricity_data["returncode"] == "100":
            print("Step 5: Electricity data:", electricity_data)
        else:
            print("Step 5: Failed to get electricity data:", electricity_data)
    else:
        print("Step 5: Electricity request failed:", response.status_code)

# 主函数
def main():
    # 第一步：登录
    id_token = step1_login()

    # 第二步：获取重定向 URL 和 cookies
    redirect_url, cookies_step2 = step2_get_redirect_url(id_token)

    # 第三步：获取授权码和新的 cookies
    auth_url, cookies_step3 = step3_get_auth_code(redirect_url, cookies_step2)

    # 第四步：获取支付页面 URL 和 cookies
    payment_url, cookies_step4 = step4_get_payment_url(auth_url, cookies_step3)

    # 第五步：获取电费数据
    step5_get_electricity_data(payment_url, cookies_step4)

if __name__ == "__main__":
    main()