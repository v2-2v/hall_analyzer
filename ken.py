#欠損日手動取得プログラム
import func
import time
import json
import makegraph

#fruits = ["20250129","20250130",
#          "20250131","20250201","20250202","20250203","20250204","20250205"]



fruits = [] #欠損日入力


for fruit in fruits:
    func.get_all_kishu(fruit)
    func.get_day_report(fruit)
    search=fruit
    filename=f"dayreport/dayreport-{fruit}.json"
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    for machine in data:
        print(fruit)
        if not "末尾" in machine["machine_name"]:
            print(machine["machine_name"])
            func.get_dai_samai(search,machine["machine_name"])
            makegraph.make_dai_graph(search,machine["machine_name"])
        time.sleep(0.5)
        