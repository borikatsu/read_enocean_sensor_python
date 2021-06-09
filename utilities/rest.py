# coding: UTF-8
from settings import *
import requests
import json

class ApiClient:
    def __init__(self, endpoint):
        self.url = API_URL + endpoint
        self.response = {}
        self.error_message = ''

    # POST実行
    def post(self, param):
        try:
            response = requests.post(
                self.url,
                json.dumps(param),
                headers = {
                    'Content-Type': 'application/json',
                    'X-Api-Request-Token': API_KEY
                }
            )
        except Exception as e:
            self.error_message = str(e)
            return False
        else:
            self.response = response.json()
            return True

    # レスポンス内容を取得
    def get_response(self):
        return self.response

    # レスポンスコードチェック
    def check_response_code(self):
        if self.response['code'] == 200 or self.response['code'] == 201:
            return True
        return False

    # エラー内容を取得
    def get_error(self):
        return self.error_message