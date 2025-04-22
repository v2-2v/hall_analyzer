#スクレイピングスタート用プログラム。常時起動推奨 完成済み
from datetime import datetime, timedelta
import time
import requests
import os
from datetime import datetime
import func
import makegraph
import json
webhook_url = 'https://discord.com/api/webhooks/1333490037068922971/cWLD4ZEqJP2pR11oK2CRUgpKoFXMj68DAWejYlyEn79YY-MQvggFh4mwVdRPUrxqatfu'
himitu_url="https://discord.com/api/webhooks/1336296441328439316/s74F9QVZ3EkgD1wbPSBMMA8xZKiVbnOhm0jF7ROvbmQK3hC1hL7Hnjm5Rdn4n9VwlPH4"
url = "https://www.slorepo.com/hole/e3839ee383abe3838fe383b3e58e9ae69ca8e58c97e5ba97code/"


def start():
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    data = {
            "content": "おはよ"
            }
    response = requests.post(webhook_url, json=data)
    while True:
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y%m%d')
        while not os.path.exists(f"dayreport/dayreport-{yesterday_str}.json"): #まだファイルがないなら
            print(yesterday_str)
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            yesterday_str = yesterday.strftime('%Y%m%d')
            response = requests.get(url+yesterday_str, headers=headers)
        
            if response.status_code == 200:#新ファイル発見！
                data = {
                "content": "厚木北新ファイル発見!?"
                }
                response = requests.post(webhook_url, json=data)
                func.get_all_kishu(yesterday_str) #最新機種をもらうよ
                func.get_day_report(yesterday_str) #dayreportをもらうよ
                search=yesterday_str
                filename=f"dayreport/dayreport-{yesterday_str}.json" 
                with open(filename, 'r', encoding='utf-8') as file:#もらったdayreportを読んで
                    data = json.load(file)
                for machine in data:#機種ごとに見てくよ
                    if not "末尾" in machine["machine_name"]:
                        print(machine["machine_name"])
                        func.get_dai_samai(search,machine["machine_name"])
                        makegraph.make_dai_graph(search,machine["machine_name"])
                    time.sleep(5)
                print("OKだよ")
                data = {
                "content": "厚木北新ファイル更新"
                }
                response = requests.post(himitu_url, json=data)
            else:
                print("まだないみたい")
                time.sleep(300)#しばらくまつ
        print("find dayreport file sleep 180s...")
        time.sleep(300)#次の日になるのを待つ