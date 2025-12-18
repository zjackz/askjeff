import pytest

pytest.skip("手工登录脚本：仅用于联调，不参与自动化测试。", allow_module_level=True)

import requests  # noqa: E402

def test_login():
    url = "http://localhost:8000/api/login/access-token"
    data = {
        "username": "admin",
        "password": "password",
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            token = response.json()
            print("登录成功！")
            print(f"Token 类型：{token['token_type']}")
            print(f"Access token：{token['access_token'][:20]}...")
        else:
            print(f"登录失败：{response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"发生异常：{e}")

if __name__ == "__main__":
    test_login()
