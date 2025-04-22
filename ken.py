#this program make all kishu data つまり全ての機種のデータを取るわけだ 完成済み
import func
import time
import json
import makegraph


#fruits = ["20250101","20250102","20250103","20250104","20250105","20250106","20250107","20250108","20250109","20250110",
#          "20250111","20250112","20250113","20250114","20250115","20250116","20250117","20250118","20250119","20250120",
#          "20250121","20250122","20250123","20250124","20250125","20250126","20250127","20250128","20250129","20250130",
#          "20250131","20250201","20250202","20250203","20250204","20250205"]
#fruits = ["20250129","20250130",
#          "20250131","20250201","20250202","20250203","20250204","20250205"]



fruits = ["20250325","20250326","20250327"]
#fruits = ["20250320"]

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
        