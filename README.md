# 仕様
## 注意
 ESP3は2019年9月6日現在で最新のEnocean公式仕様書のバージョン1.49を前提に話を進める。
 EEPは2019年9月6日現在で最新のEnocean公式仕様書のバージョン2.6.8を前提に話を進める。

## ESP3
http://www.enocean.com/esp

のP.13ページから抜粋
### 構造
![構造](https://github.com/borikatsu/read_enocean_sensor_python/readme/esp3.png)

## 解析
実際にアーミン温度センサー（ETB-RHT）から送られてきたサンプルデータを利用。（1バイト毎のデータを16進数に変換済み）
```
55:00:0a:02:0a:9b:22:05:02:e6:af:8e:02:61:08:76:01:4d:f1
```

↑のサンプルを頭から分解すると
| シリアル                      | 備考                                  | 
| ----------------------------- | ------------------------------------- | 
| 55                            | 同期用の信号。固定                    | 
| 00:0a                         | DataフィールドのLength。今回だと10    | 
| 02                            | OptionalフィールドのLength。今回だと2 | 
| 0a                            | パケットタイプ。後述                  | 
| 9b                            | チェックサム                          | 
| 22:05:02:e6:af:8e:02:61:08:76 | Data。後述                            | 
| 01:4d:f1                      | Option Data。後述                     | 
| f1                            | チェックサム                          | 

### バケットタイプ
http://www.enocean.com/esp

のP.13ページから抜粋

![バケットタイプ](https://github.com/borikatsu/read_enocean_sensor_python/readme/packet.png)

今回のセンサーのバケットタイプがRadio_ERP2だということがわかる。
現状Dataフィールド以外のデータは特に必要なデータではない模様。

#### Radio_ERP2
http://www.enocean.com/esp

のP.88ページから抜粋

![erp2](https://github.com/borikatsu/read_enocean_sensor_python/readme/erp2.png)


## ERP2
http://www.enocean.com/erp2

のP.16ページから抜粋

![erp2_1](https://github.com/borikatsu/read_enocean_sensor_python/readme/erp2_1.PNG)

上記の図に従い、Dataフィールドをさらに分解すると
| シリアル    | 備考                | 
| ----------- | ------------------- | 
| 22          | Data長              | 
| 05:02:e6:af | 送信元ID。32bit固定 | 
| 8e:02:61:08 | Data。後述          | 
| 76          | チェックサム        | 


Dataフィールドの構造は送信元のEEP仕様に従う。

## EEP
今回のETB-RHTは公式サイトより「A5-04-03」というプロファイルであることがわかる。
http://www.itec-corp.co.jp/index.php?ETx-RHT

#### A5-04-03
http://www.enocean-alliance.org/eep/

のP.37ページから抜粋

![eep](https://github.com/borikatsu/read_enocean_sensor_python/readme/eep.png)


Dataを2進数に変換すると
```
1000 1110 0000 0010 0110 0001 0000 1000
```

上記の図に従い、2進数に変換したDataフィールドを分解すると
| シリアル     | 備考                       | 
| ------------ | -------------------------- | 
| 1000 1110    | 湿度。「1000 1110 = 8e」   | 
| 0000 00      | Not Used                   | 
| 10 0110 0001 | 温度。「10 0110 0001=261」 | 
| 0000         | Not Used                   | 
| 1            | LRN Bit                    | 
| 00           | Not Used                   | 
| 0            | Teregram Type              | 

あとは仕様に則って計算する。
#### 湿度
「1000 1110」を10進数に変換すると142なので、切り上げして「(142 * 100 / 255 = 55%」となる。
#### 温度
「10 0110 0001」を10進数に変換すると609なので、切り上げして「609 * (60 - (-20)) / 1023 - 20) = 27.6℃」となる。
