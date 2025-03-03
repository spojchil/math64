import warnings
warnings.filterwarnings("ignore")
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
            #print("Step 1: Login successful, id_token:", id_token)
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
        supwisdomapptoken=response.cookies.get('supwisdomapptoken')
        sid = response.cookies.get('sid')
        b_host = response.cookies.get('b_host')
        #print("Step 2: Redirect URL:", redirect_url,response.cookies)
        return redirect_url, response.cookies,supwisdomapptoken,sid,b_host
    else:
        print("Step 2: Failed to get redirect URL:", response.status_code,response.cookies)
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
        #print("Step 3: Auth URL:", auth_url,response.cookies)
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
        #print("Step 4: Payment URL:", payment_url,response.cookies)
        return payment_url, response.cookies,SESSION
    else:
        print("Step 4: Failed to get payment URL:", response.status_code)
        exit()

# 第五步：获取电费数据
def step5_get_electricity_data(payment_url ,supwisdomapptoken,sid,b_host,SESSION):
    cookies = {
        "supwisdomapptoken": supwisdomapptoken,
        "sid": sid,
        "b_host": b_host,
        "SESSION":SESSION
    }
    return cookies
# 主函数
def get_electricity():
    # 第一步：登录
    id_token = step1_login()

    # 第二步：获取重定向 URL 和 cookies
    redirect_url, cookies_step2,supwisdomapptoken,sid,b_host = step2_get_redirect_url(id_token)

    # 第三步：获取授权码和新的 cookies
    auth_url, cookies_step3 = step3_get_auth_code(redirect_url, cookies_step2)

    # 第四步：获取支付页面 URL 和 cookies
    payment_url, cookies_step4,SESSION = step4_get_payment_url(auth_url, cookies_step3)

    # 第五步：获取电费数据
    return step5_get_electricity_data(payment_url, supwisdomapptoken,sid,b_host,SESSION)