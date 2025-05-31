#スクレイピングスタート用プログラム
from datetime import datetime, timedelta
import time
import requests
import os
from datetime import datetime
import func
import makegraph
import json
webhook_url = 'ADMIN_DISCORD_URL'
himitu_url="NOTIFY_DISCORD_URL"
url = "YOUR_HALL_URL"
"""
EXAM: https://www.slorepo.com/hole/e382a8e382b9e38391e382b9e697a5e68b93e7a78be89189e58e9fe9a785e5898de5ba97code/

from slorepo
"""

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