# coding: UTF-8
from settings import *
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class SendgridTools:
    def __init__(self, to_mail, text):
        self.from_mail     = FROM_MAIL
        self.to_mail       = to_mail
        self.subject       = ALERT_TEMP_SUB
        self.html_content  = text
        self.response      = {}
        self.error_message = ''

        # クライアントインスタンス
        self.client = SendGridAPIClient(SENDGRID_API_KEY)

    # メール送信
    def send(self):
        try:
            # 送信内容
            message = Mail(
                from_email   = self.from_mail,
                to_emails    = self.to_mail,
                subject      = self.subject,
                html_content = self.html_content
            )

            # 送信
            response = self.client.send(message)
        except Exception as e:
            self.error_message = str(e)
            return False
        else:
            self.response = response
            return True

    # レスポンス内容を取得
    def get_response(self):
        return self.response

    # エラー内容を取得
    def get_error(self):
        return self.error_message