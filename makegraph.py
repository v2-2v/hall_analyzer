import requests
import os
from bs4 import BeautifulSoup
import urllib.parse

#"https://www.slorepo.com/hole/e3839ee383abe3838fe383b3e58e9ae69ca8e58c97e5ba97code/20250125/kishu/?kishu=%E3%83%9E%E3%82%A4%E3%82%B8%E3%83%A3%E3%82%B0%E3%83%A9%E3%83%BCV"

def make_dai_graph(day,kishu):
    encodingkishu = urllib.parse.quote(kishu) #URL encodingg!?
    url="https://www.slorepo.com/hole/e3839ee383abe3838fe383b3e58e9ae69ca8e58c97e5ba97code/"+day+"/kishu/?kishu="+encodingkishu
    #url="https://www.slorepo.com/hole/e3839ee383abe3838fe383b3e58e9ae69ca8e58c97e5ba97code/20250308/kishu/?kishu=A%E2%80%90SLOT%2B+%E3%81%93%E3%81%AE%E7%B4%A0%E6%99%B4%E3%82%89%E3%81%97%E3%81%84%E4%B8%96%E7%95%8C%E3%81%AB%E7%A5%9D%E7%A6%8F%E3%82%92%EF%BC%81"
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"error {day} {kishu}")
        return
    soup = BeautifulSoup(response.text, "html.parser")
    #print(soup)
    elements = soup.find_all(class_="wp-block-columns are-vertically-aligned-top is-not-stacked-on-mobile has-small-font-size is-layout-flex wp-container-core-columns-is-layout-1 wp-block-columns-is-layout-flex")
    if elements==[]:
        elements = soup.find_all(class_="wp-block-column is-vertically-aligned-top is-layout-flow wp-container-core-column-is-layout-1 wp-block-column-is-layout-flow")
    html_content = "<html><body>\n"

    for element in elements:
        html_content += str(element) + "\n"

    
    html_content += "</body></html>"
    os.makedirs(f"graph/{day}", exist_ok=True)
    with open(f"graph/{day}/{day}-{kishu}.html", "w", encoding="utf-8") as file:
        file.write(html_content)
    print(url)
    print(f"graph/{day}に保存")