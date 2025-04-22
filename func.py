#collectorに使われている関数リスト

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import urllib.parse
# ベースURL
url = "https://www.slorepo.com/hole/e3839ee383abe3838fe383b3e58e9ae69ca8e58c97e5ba97code/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_all_kishu(dday):
    response = requests.get(url+dday, headers=headers)
    if response.status_code == 200:
        # HTMLを解析
        soup = BeautifulSoup(response.text, "html.parser")
        
        filename = f"allkishu.json"
        # ページタイトルを取得
        rows = soup.find_all("tr")  # テーブルの行をすべて取得
        data=[]
        for row in rows:
            cells = row.find_all("td")  # 各行のセルを取得
            if cells:
                machine_name = cells[0].get_text(strip=True)  # 1列目のテキストを取得
                if "末尾" in machine_name:
                    continue
                if machine_name.replace(",","").replace("-","").replace("+","").isdigit():       
                    continue
                machine_count = cells[3].get_text(strip=True).split("/")[-1]
                if not any(machine['machine_name'] == machine_name for machine in data):
                    data.append({
                                    "machine_name": machine_name,
                                    "machine_count": machine_count
                                    })
        sorted_data = sorted(data, key=lambda x: int(x["machine_count"]), reverse=True)
        with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(sorted_data, f, ensure_ascii=False, indent=2)
    else:
        print(url+dday,"allkishu.json ページの取得に失敗しました。ステータスコード:", response.status_code)

def get_dai_samai(day,kishu):
    day=str(day)
    encodingkishu = urllib.parse.quote(kishu) #URL encodingg!?
    response = requests.get(url+day+"/kishu/?kishu="+encodingkishu,headers=headers)
    if kishu.startswith(("+", "-")):
        return
    if response.status_code == 200:
        directory = f"daidata"
        if not os.path.exists("daidata"):
            os.makedirs("daidata")  # ディレクトリが存在しない場合は作成
        directory = f"daidata/{day}"
        if not os.path.exists(f"daidata/{day}"):
            os.makedirs(f"daidata/{day}")  # ディレクトリが存在しない場合は作成
        # HTMLを解析
        soup = BeautifulSoup(response.text, "html.parser")
        filename = f"daidata/{day}/{day}-{kishu}.json"
        # ページタイトルを取得
        rows = soup.find_all("tr")  # テーブルの行をすべて取得
        data=[]
        for row in rows:
            cells = row.find_all("td")  # 各行のセルを取得
            if cells:
                machine_daiban = cells[0].get_text(strip=True)  # 1列目のテキストを取得
                if not ("+" in machine_daiban or "-" in machine_daiban or "0" == machine_daiban): #個別データなら
                    machine_samai = cells[1].get_text(strip=True)
                    machine_gamecount = cells[2].get_text(strip=True)
                    machine_bb = cells[3].get_text(strip=True)
                    machine_rb = cells[4].get_text(strip=True)
                    machine_gassan = cells[5].get_text(strip=True)
                    if not any(machine['machine_daiban'] == machine_daiban for machine in data):
                        data.append({
                                    "machine_daiban": machine_daiban,
                                    "machine_samai": machine_samai,
                                    "machine_gamecount": machine_gamecount,
                                    "machine_bb": machine_bb,
                                    "machine_rb": machine_rb,
                                    "machine_gassan": machine_gassan
                                    })
        #print(data)
        if data==[]: #1台しかないとき
            if not len(soup.find_all("strong"))==1: #0台を検知
                dainame = soup.find_all("strong")[1].get_text(strip=True)  # テーブルの行をすべて取得
                data.append({
                                        "machine_daiban": dainame,
                                        "machine_samai": cells[0].get_text(strip=True),
                                        "machine_gamecount": cells[1].get_text(strip=True),
                                        "machine_bb": cells[2].get_text(strip=True),
                                        "machine_rb": cells[3].get_text(strip=True),
                                        "machine_gassan": cells[4].get_text(strip=True)
                                        })
                data.append({
                                        "machine_daiban": "平均",
                                        "machine_samai": cells[0].get_text(strip=True),
                                        "machine_gamecount": cells[1].get_text(strip=True),
                                        "machine_bb": cells[2].get_text(strip=True),
                                        "machine_rb": cells[3].get_text(strip=True),
                                        "machine_gassan": cells[4].get_text(strip=True)
                                        })
        elif len(data)==2: #2台のとき
            if data[0]["machine_gassan"]== "0" or data[1]["machine_gassan"] == "0": #2台かつどらかがあたり0のとき
                if data[0]["machine_gassan"]=="0":
                    kaku =data[1]["machine_gassan"]
                else:
                    kaku =data[0]["machine_gassan"]
                data.append({
                                        "machine_daiban": "平均",
                                        "machine_samai": str(int(((int(data[0]["machine_samai"].replace(',', '')))+int(data[1]["machine_samai"].replace(',', '')))/2)),
                                        "machine_gamecount": str(int(((int(data[0]["machine_gamecount"].replace(',', '')))+int(data[1]["machine_gamecount"].replace(',', '')))/2)),
                                        "machine_bb": str(int(((int(data[0]["machine_bb"].replace(',', '')))+int(data[1]["machine_bb"].replace(',', '')))/2)),
                                        "machine_rb": str(int(((int(data[0]["machine_rb"].replace(',', '')))+int(data[1]["machine_rb"].replace(',', '')))/2)),
                                        "machine_gassan":kaku
                                        })
            else: #2台かつどちらも回されている
                a=int(data[0]["machine_gamecount"].replace(',', ''))/int(data[0]["machine_gassan"].replace(',', '')[2:])
                b=int(data[1]["machine_gamecount"].replace(',', ''))/int(data[1]["machine_gassan"].replace(',', '')[2:])
                n=int(((int(data[0]["machine_gamecount"].replace(',', '')))+int(data[1]["machine_gamecount"].replace(',', ''))))
                data.append({
                                        "machine_daiban": "平均",
                                        "machine_samai": str(int(((int(data[0]["machine_samai"].replace(',', '')))+int(data[1]["machine_samai"].replace(',', '')))/2)),
                                        "machine_gamecount": str(int(((int(data[0]["machine_gamecount"].replace(',', '')))+int(data[1]["machine_gamecount"].replace(',', '')))/2)),
                                        "machine_bb": str(int(((int(data[0]["machine_bb"].replace(',', '')))+int(data[1]["machine_bb"].replace(',', '')))/2)),
                                        "machine_rb": str(int(((int(data[0]["machine_rb"].replace(',', '')))+int(data[1]["machine_rb"].replace(',', '')))/2)),
                                        "machine_gassan":"1/"+str(int(n/(a+b)))
                                        })

        if data==[]: #0台?
            print("skip")
            return 
        with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        print(f"daidata/{day}/{day}-{kishu}.json","  ページの取得に失敗しました。ステータスコード:", response.status_code)

def get_day_report(day):
    response = requests.get(url+day, headers=headers)
    if not os.path.exists("dayreport"):
        os.makedirs("dayreport")  # ディレクトリが存在しない場合は作成
    if response.status_code == 200:
        # HTMLを解析
        soup = BeautifulSoup(response.text, "html.parser")

        today = day
        filename = f"dayreport/dayreport-{today}.json"

        # ページタイトルを取得
        rows = soup.find_all("tr")  # テーブルの行をすべて取得
        data=[]
        for row in rows:
            cells = row.find_all("td")  # 各行のセルを取得
            if cells:
                machine_name = cells[0].get_text(strip=True)  # 1列目のテキストを取得
                machine_count = cells[1].get_text(strip=True)
                if not any(machine['machine_name'] == machine_name for machine in data):
                    data.append({
                                    "machine_name": machine_name,
                                    "machine_count": machine_count
                                    })
        with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        print(f"dayreport/dayreport-{day}.json","ページの取得に失敗しました。ステータスコード:", response.status_code)


#get_dai_samai(20250109,"バンドリ！") #機種のすべての台の情報を取得

#get_all_kishu("20250216") #最新の機種と設置台数を取得

#get_day_report("20250101") #指定日の機種ごとの差枚、総差枚、末尾を取得