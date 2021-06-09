# coding: UTF-8
import os
import os.path
import dotenv
import logzero
import logging

# env読み込み
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

# 定数として定義
PORT              = os.environ.get('PORT')
API_URL           = os.environ.get('API_URL')
API_KEY           = os.environ.get('API_KEY')
COSMOS_HOST       = os.environ.get('COSMOS_HOST')
COSMOS_P_KEY      = os.environ.get('COSMOS_P_KEY')
COSMOS_DB         = os.environ.get('COSMOS_DB')
COSMOS_COLLECTION = os.environ.get('COSMOS_COLLECTION')
SENDGRID_API_KEY  = os.environ.get('SENDGRID_API_KEY')
FROM_MAIL         = os.environ.get('FROM_MAIL')
ALERT_TEMP_SUB    = os.environ.get('ALERT_TEMP_SUB')

# ログ設定
logger = logzero.setup_logger(
    disableStderrLogger = False,
    name                = 'receive-enocean',
    logfile             = os.path.join(os.path.dirname(__file__), 'logs/app.log'),
    level               = 20,
    formatter           = logging.Formatter('%(asctime)s %(levelname)s: %(message)s'),
    maxBytes            = 1048576,
    backupCount         = 5,
    fileLoglevel        = 20,
)