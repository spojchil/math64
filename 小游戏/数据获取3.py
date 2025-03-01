import requests


class PowerMonitor:
    def __init__(self, username, password, room_verify):
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.room_verify = room_verify
        self.headers = {
            'User-Agent': 'SWSuperApp/1.2.6(OPPOPGX110OPPO14)',
            'X-Requested-With': 'com.supwisdom.haut'
        }

    def login(self):
        # Step 1: 登录获取token
        login_url = "https://mycas.haut.edu.cn/token/password/passwordLogin"
        params = {
            "username": self.username,
            "password": self.password,
            "appId": "com.supwisdom.haut",
            "deviceId": "ZO6cVuH+/1UDAElLPJpu7AFi",
            "osType": "android",
            "clientId": "b08f7f00db0e2a1a14a31517ae7592d3"
        }

        response = self.session.post(login_url, params=params, headers=self.headers, verify=False)
        if response.json().get("code") == 0:
            self.id_token = response.json()["data"]["idToken"]
            return True
        return False

    def get_electricity(self):
        # Step 2-4: 处理重定向链
        redirect_chain = [
            ("https://hub.17wanxiao.com/bsacs/light.action", {"flag": "supwisdomapp_hgdswjf", "ecardFunc": "index"}),
            ("https://open.17wanxiao.com/api/authorize", {
                "response_type": "code",
                "hidden": "true",
                "customerCode": "43",
                "force_login": "false",
                # 其他参数从登录响应中获取...
            })
        ]

        # 最终请求电费数据的URL
        electricity_url = "https://h5cloud.17wanxiao.com:18443/CloudPayment/user/getRoomState.do"
        params = {
            "payProId": "726",
            "schoolcode": "43",
            "businesstype": "2",
            "roomverify": self.room_verify
        }

        # 添加必要的headers
        self.headers.update({
            'Referer': 'https://h5cloud.17wanxiao.com:18443/CloudPayment/bill/selectPayProject.do',
            'Cookie': f'supwisdomapptoken={self.id_token}'
        })

        response = self.session.get(electricity_url, params=params, headers=self.headers, verify=False)
        if response.status_code == 200:
            return response.json()
        return None


# 使用示例
if __name__ == "__main__":
    monitor = PowerMonitor(
        username="231030200313",
        password="Sun2069510482",
        room_verify="102-2--124-2517"  # 需要替换为实际的房间验证信息
    )

    if monitor.login():
        electricity_data = monitor.get_electricity()
        print("电费数据:", electricity_data)
    else:
        print("登录失败")