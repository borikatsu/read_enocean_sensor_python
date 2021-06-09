#!/usr/bin/python3
#coding: UTF-8
from utilities import *
from settings import *

import sys
import serial
import codecs
import json
from datetime import datetime

def main():
    # シリアルポートを開く
    try:
        ser = serial.Serial(PORT, 57600)
        logger.info('open serial port: %s' % PORT)
    except:
        logger.error('cannot open serial port: %s' % PORT)
        return

    # 初期化
    cnt, data_len, opt_len = 0, 0, 0
    telegraph, head_list, data_list, opt_list = [], [], [], []

    # 電文開始のフラグ管理
    ready = True

    # データの解釈とログの記録
    while True:
        # 1byteずつ読み込み
        tt = ser.read()
        ss = codecs.encode(tt, 'hex_codec')

        # 電文開始
        if ss == b'55' and ready:
            # 変数のリセット
            cnt, data_len, opt_len = 0, 0, 0
            telegraph, head_list, data_list, opt_list = [], [], [], []
            ready = False

        cnt += 1
        telegraph.append(ss.decode('utf-8'))

        # header
        if 2 <= cnt <= 5:
            head_list.append(ss.decode('utf-8'))

        # data length取得
        if cnt == 5:
            data_len = int(head_list[1], 16)
            opt_len  = int(head_list[2], 16)

         # data
        if 7 <= cnt <= (6 + data_len):
            data_list.append(ss.decode('utf-8'))

        # optional data
        if (7 + data_len) <= cnt <= (6 + data_len + opt_len):
            opt_list.append(ss.decode('utf-8'))

        # 電文終了
        if cnt == (6 + data_len + opt_len + 1):
            ready = True

            # ログ出力
            logger.info('【telegraph】' + ':'.join(telegraph))
            logger.info('【header】' + ':'.join(head_list))
            logger.info('【data】' + ':'.join(data_list) + '(length = %d)' % data_len)
            logger.info('【option】' + ':'.join(opt_list) + '(length = %d)' % opt_len)

            # センサーID
            if data_len > 10:
                sensor_id = '' .join(data_list[3:7])
            else:
                sensor_id = '' .join(data_list[1:5])
            sensor_id = sensor_id.upper()
            logger.info('【SensorId】' + sensor_id)

            # Teach inは無視
            if data_len > 10 or data_len == 9 or data_len < 7:
                logger.info('This is Teach in.Bye.')
                continue

            # センサー情報問い合わせ
            request = rest.ApiClient('/device')
            result = request.post(
                {
                    'device_code': sensor_id,
                }
            )

            # エラー
            if result != True:
                logger.error(request.get_error())
                continue

            # レスポンス
            response = request.get_response()

            # 正常系レスポンスかチェック
            if request.check_response_code() == False:
                logger.info('Not success response.')
                logger.info(
                    json.dumps(
                        response,
                        ensure_ascii = False,
                        indent = 4
                    )
                )
                continue

            # リクエストデータ
            now = datetime.now()
            item = {
                'sensor_id': sensor_id,
                'location_id': int(response['data']['location_id']),
                'category': response['data']['category_key'],
                'date': now.strftime('%Y-%m-%d'),
                'time': now.strftime('%H:%M:%S')
            }

            # センサー種別判定
            if response['data']['category_key'] == 'temperature':
                # 温度
                val = int('' .join(data_list[6:8]), 16)
                temp = round((val * 80.0 / 1023.0) - 20.0, 1)

                # 湿度
                val = int(data_list[5], 16)
                hum = round((val * 100.0 / 255.0), 1)

                logger.info('【temperature】{:.1f}'.format(temp))
                logger.info('【humidity】{:.1f}'.format(hum))

                # リクエストデータに追加
                item['temperature'] = temp
                item['humidity']    = hum
            elif response['data']['category_key'] == 'door':
                # 開閉ステータス
                val = int(data_list[5], 16)

                if val == 8:
                    status    = 'open'
                    is_closed = 0
                else:
                    status    = 'close'
                    is_closed = 1

                logger.info('【status】' + status)
                item['is_closed'] = is_closed
            elif response['data']['category_key'] == 'illuminance':
                # どちらのレンジのデータを利用するか
                target_data = int(data_list[9], 16)
                # 2進数からの判定なのでバイナリに戻す
                binary = bin(target_data)
                # 末尾の値でどちらを使うか判定
                target = binary[-1:]
                if target == 1:
                    val   = int(data_list[6], 16)
                    scale = 5100.0
                else:
                    val   = int(data_list[7], 16)
                    scale = 10200.0

                illum = round(val * scale / 255.0, 0)

                logger.info('【illuminance】{:.0f}'.format(illum))
                item['illuminance'] = illum
            elif response['data']['category_key'] == 'human':
                # 検知状況
                val = int(data_list[7], 16)

                if val < 128:
                    status = 'off'
                    is_pir = 0
                else:
                    status = 'on'
                    is_pir = 1

                logger.info('【status】' + status)
                item['is_pir'] = is_pir
            else:
                continue

            # レコード作成
            cosmos_tool   = cosmos.CosmosTools()
            cosmos_result = cosmos_tool.create_item(item)

            # エラー
            if cosmos_result != True:
                logger.error('Failed save data.Because...' + cosmos_tool.get_error())
                continue

            # 計測時間内で初めての計測かどうか
            if response['data']['is_measure'] == 1:
                # 温度アラートメール
                if response['data']['category_key'] == 'temperature':
                    # 閾値外ならメール送信
                    if temp < response['data']['min_limit'] or response['data']['max_limit'] < temp:
                        mail_text_path = get_pass('mail/temp_alert.txt')
                        file = open(mail_text_path, 'r')

                        # テキスト内置換
                        mail_txt = file.read().replace('{{ locationName }}', response['data']['location_name'])

                        # メール送信
                        sendgrid_tool = sendgrid.SendgridTools(response['data']['mail'], mail_txt)
                        sendgrid_result = sendgrid_tool.send()

                        # エラー
                        if sendgrid_result != True:
                            logger.error('Failed send e-mail.Because...' + sendgrid_tool.get_error())
                        else:
                            logger.info('Sent e-mail for temperature.')

try:
    main()
except KeyboardInterrupt:
    logger.info('Bye.')
    sys.exit()
