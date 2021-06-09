# coding: UTF-8
from settings import *
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as cosmos_errors
import json

class CosmosTools:
    def __init__(self):
        self.result = {}
        self.error_message = ''

        # クライアントインスタンス
        self.client = cosmos_client.CosmosClient(
            url_connection = COSMOS_HOST,
            auth = {
                'masterKey': COSMOS_P_KEY
            }
        )

        # DB
        self.database_link = 'dbs/' + COSMOS_DB
        # コレクション
        self.container_link = self.database_link + '/colls/{0}'.format(COSMOS_COLLECTION)

    # レコード作成
    def create_item(self, item):
        try:
            result = self.client.CreateItem(self.container_link, item)
        except cosmos_errors.HTTPFailure as e:
            error = json.loads(e._http_error_message)
            self.error_message = error['message']
            return False
        except Exception as e:
            self.error_message = str(e)
            return False
        else:
            self.result = result
            return True

    # レスポンス内容を取得
    def get_result(self):
        return self.result

    # エラー内容を取得
    def get_error(self):
        return self.error_message