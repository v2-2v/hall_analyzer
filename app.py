from flask import Flask, render_template, jsonify, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
from datetime import date, timedelta,datetime
import os
import requests
import threading
import collector

current_year = date.today().year
start_date = date(current_year, 1, 1)
end_date = date(current_year, 12, 31)
all_dates = []
current_date = start_date
while current_date <= end_date:
    all_dates.append(current_date.strftime("%Y%m%d"))
    current_date += timedelta(days=1)

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'  # セッション用の秘密鍵

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # ログインしていない場合にリダイレクトするページ

webhook_url = 'YOUR_WEBHOOK_URL'

# ユーザーデータの設定（仮のデータ）
users = {'admin': {'password': '0000'}} #EXAM

# ユーザークラス
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# events.jsonから予定データを読み込む
def load_events():
    with open('events.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id in users else None
# ログインページ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('get_home'))
        else:
            return 'ログイン失敗'
    body="""
        <form method="POST">
        <label for="username">ユーザー名:</label>
        <input type="text" name="username" id="username" required><br><br>
        <label for="password">パスワード:</label>
        <input type="password" name="password" id="password" required><br><br>
        <button type="submit">ログイン</button>
    </form>
    """
    return render_template('base.html',title="ログイン",body=body)

# ログアウト
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def homedir():
    return redirect(url_for('login'))

@app.route('/c/<kishu>')
@login_required
def index(kishu):
    if kishu=="総合":
        return render_template('calendar.html',hoge="総合")
    if "末尾" in kishu:
        return render_template('base.html',title="エラー",body="末尾ごとでは見れません")
    daisuu=""
    with open(f'allkishu.json', 'r', encoding='utf-8') as f:
        allkishu = json.load(f)
    for ss in allkishu: #台ごとのループ
        if ss["machine_name"] == kishu:
            daisuu=ss["machine_count"]
    if daisuu=="":
        return render_template('base.html',title="エラー",body="エラー")

    return render_template('calendar.html',hoge=kishu,daisuu=daisuu+"台設置 a,bは平均")

@app.route('/events/<kishu>')
@login_required
def get_events(kishu):
    try:
        if kishu=="news":
            with open('news.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        with open(f'eventday.json', 'r', encoding='utf-8') as f:
            eventday = json.load(f)
        samaidata=[]
        if kishu=="総合":
            
            for day in all_dates: #1dayごと
                if os.path.exists(f"dayreport/dayreport-{day}.json"):
                    daisuu = 0
                    with open(f'dayreport/dayreport-{day}.json', 'r', encoding='utf-8') as f:
                        sougoujson= json.load(f)
                    if int(sougoujson[0]["machine_name"].replace(",","")) <= 0:#その日の総差枚
                        color = "red"
                    else:
                        color = "blue"
                    samaidata.append({
                                    "title": sougoujson[0]["machine_name"],
                                    "start": f"{day[:4]}-{day[4:6]}-{day[6:]}" ,
                                    "color": color
                                    })
                else:
                    continue
            return jsonify(eventday+samaidata)

        for day in all_dates: #1dayごと
            if os.path.exists(f"daidata/{day}/{day}-{kishu}.json"):
                daisuu = 0
                with open(f'daidata/{day}/{day}-{kishu}.json', 'r', encoding='utf-8') as f:
                    daydata = json.load(f)
                for ss in daydata: #台ごとのループ
                    daisuu+=1
                    if ss["machine_daiban"] == "平均":
                        kishusamai=int(ss["machine_samai"].replace(",",""))*int(daisuu-1) #機種の総差枚を求める
                        kaiten=ss["machine_gamecount"]
                        gassan=ss["machine_gassan"]
                if int(kishusamai) <= 0:
                    color = "red"
                else:
                    color = "blue"
                samaidata.append({
                                "title": f"{kishusamai}",
                                "start": f"{day[:4]}-{day[4:6]}-{day[6:]}" ,
                                "color": color
                                })
                samaidata.append({
                                "title": f"a {kaiten}回転",
                                "start": f"{day[:4]}-{day[4:6]}-{day[6:]}" ,
                                "color": "black"
                                })
                samaidata.append({
                                "title": f"b {gassan}",
                                "start": f"{day[:4]}-{day[4:6]}-{day[6:]}" ,
                                "color": "black"
                                })
            else:
                continue
        return jsonify(eventday+samaidata)
    except:
        return "error"


@app.route("/home")
@login_required
def get_home():
    for day in all_dates: #1dayごと
        if os.path.exists(f"dayreport/dayreport-{day}.json"):
            last=day
    addstyle="""
    body {
            font-family: Arial, sans-serif;
            margin: 0;
            height: 100vh; /* ビューポート全体の高さに合わせる */
            display: flex;
            flex-direction: column;
        }
    #calendar {
            
        }
    """
    #flex-grow: 1; /* カレンダーが残りのスペースを占めるように */
    #height: 100%;  /* カレンダーが縦いっぱいになる */
    body=f"""<p>よう。{current_user.id}</p>
    <p>最終更新日 {last}</p>
    <p><a href="https://yoimiya.net/hall">その他のホールデータ</a></p>
    <p>当日のデータは翌日の午前11時くらいまでに更新されます</p>
    <p>そのため稼働する日は前日の一部の機種のデータを<a href="/daidataadd">手動入力</a>します</p>
    <p>現在設置されてる機種が表示されてるよー</p>
    <p></p>
    <p></p>
    <h3>最近のニュース</h3>
    <link href='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.0/main.min.css' rel='stylesheet' />
    <script src='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.0/main.min.js'></script>
    """
    cscript="""
        document.addEventListener('DOMContentLoaded', function() {
            var calendarEl = document.getElementById('calendar');
            var calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: 'dayGridMonth',
                events: '/events/news'
            });
        
            calendar.render();
        });
    """
    with open("top.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()  # 全行をリストで取得
    for line in lines:
            body+=f"<p>{line}</p>"  # 改行を削除して表示
    body+="""<h3>以下フィーバー</h3>
    <div id='calendar'></div>"""
    with open("yoso.json", 'r', encoding='utf-8') as f: #予想更新
        yosos = json.load(f)
    for yoso in yosos:
        if yoso["result"]=="":
            try:
                yosobi=yoso["date"].replace("-", "")
                with open(f"daidata/{yosobi}/{yosobi}-{yoso["dainame"]}.json", 'r', encoding='utf-8') as f:
                    daidatas = json.load(f)
                for daidata in daidatas:
                    if daidata["machine_daiban"]==yoso["daiban"]:
                        yoso["result"]=daidata["machine_samai"]
            except:
                pass
            with open("yoso.json", 'w') as file:
                json.dump(yosos, file, indent=4,ensure_ascii=False)
    return render_template('base.html',title="ホーム",body=body,addstyle=addstyle,cscript=cscript)


@app.route("/yamichan")
@login_required
def get_yamichan():
    alldata=[]
    addstyle="""
        #search-box {
            width: 300px;
            padding: 10px;
            font-size: 16px;
        }
        #suggestions {
            border: 1px solid #ccc;
            display: none;
            position: absolute;
            background-color: white;
            z-index: 1;
            width: 300px; /* テキストボックスと同じ幅 */
        }
        .suggestion-item {
            padding: 8px;
            cursor: pointer;
        }
        .suggestion-item:hover {
            background-color: #f0f0f0;
        }
        """
    
    body="""<p><a href="/c/総合">総合</a></p>"""
    body+=f"""
    <input type="text" id="search-box" placeholder="検索..." autocomplete="off">
    <div id="suggestions"></div>"""
    with open(f'allkishu.json', 'r', encoding='utf-8') as f:
        allkishu = json.load(f)
    for ss in allkishu: #台ごとのループ
        alldata.append(ss["machine_name"])
        body += f'<p><a href="/c/{ss["machine_name"]}">{ss["machine_name"]} {ss["machine_count"]}台</a></p> '
    cscript=f"""
            const suggestions = {str(alldata)};"""
    cscript+="""
        const searchBox = document.getElementById("search-box");
        const suggestionsBox = document.getElementById("suggestions");

        searchBox.addEventListener("input", () => {
            const input = searchBox.value.toLowerCase();
            suggestionsBox.innerHTML = '';
            
            if (input) {
                const filteredSuggestions = suggestions.filter(suggestion => 
                    suggestion.toLowerCase().includes(input)
                );

                if (filteredSuggestions.length > 0) {
                    suggestionsBox.style.display = "block";
                    filteredSuggestions.forEach(suggestion => {
                        const div = document.createElement("div");
                        div.textContent = suggestion;
                        div.classList.add("suggestion-item");
                        div.addEventListener("click", () => {
                            window.location.href = `/c/${suggestion}`; // 候補名をURLに追加
                        });
                        suggestionsBox.appendChild(div);
                    });
                } else {
                    suggestionsBox.style.display = "none";
                }
            } else {
                suggestionsBox.style.display = "none";
            }
        });
    """
    return render_template('base.html',title="機種ごとの総差枚<p>並びが変わったりしたらバグる可能性あり</p>",body=body,addstyle=addstyle,cscript=cscript)

@app.route("/memo", methods=['GET', 'POST'])
@login_required
def memoadd():
    cdaiban = request.args.get('daiban')
    body=""
    style=""
    number = request.form.get('number')
    content = request.form.get('text')
    if number:
        if request.method == 'POST':
            today=datetime.today().date()
            with open("memo.json", 'r') as file:
                memos = json.load(file)
            memos.append({
                "daiban":number,
                "user":current_user.id,
                "date":str(today),
                "time":str(datetime.now().strftime("%H:%M")),
                "content":content.replace("<","").replace(">","")
            })
            with open("memo.json", 'w') as file:
                json.dump(memos, file, indent=4,ensure_ascii=False)
            body+=f"""{number}番台に メモを追加しました"""
            #return render_template('base.html',title="メモを追加しました",body=body)
            return redirect("/memo")
    else:
        body+="""
        <h5>台番号とメモを入力してください。</h5>
            <form method="POST">
                <p><input type="number" name="number" required>番台</p>
                <p><textarea name="text" placeholder="メモを追加" required></textarea></p>              
                <button type="submit">送信</button>
            </form>
        <h2>今日のメモ</h2>
        """
        today=datetime.today().date()
        with open("memo.json", 'r') as file:
            memos = json.load(file)
        todaymemo=""
        if cdaiban:
            body+="""<a href="/memo"><h5>フィルタをやめる</h5></a>"""
        else:
            body+="<h5>台番号を押すとフィルタされます</h5>"
        for memo in reversed(memos):
            if memo["date"]==str(today) and (not cdaiban):
                todaymemo+=f"""
                <a href="/memo?daiban={memo["daiban"]}">{memo["daiban"]}番台</a> {memo["date"]} {memo["time"]} ユーザー名 {memo["user"]}
                    <div class="box">{memo["content"]}</div>
                """
            elif memo["date"]==str(today) and memo["daiban"]==cdaiban:
                todaymemo+=f"""
                <a href="/memo?daiban={memo["daiban"]}">{memo["daiban"]}番台</a> {memo["date"]} {memo["time"]} ユーザー名 {memo["user"]}
                    <div class="box">{memo["content"]}</div>
                """
        if todaymemo=="":
            body+="<p>今日作成されたメモはありません</p>"
        else:
            body+=todaymemo
        style+="""
        button {
                  padding: 10px 20px;
                  background-color: #4CAF50;
                  color: white;
                  border: none;
                  border-radius: 4px;
                  cursor: pointer;
                }
        textarea {
                width: 300px; /* 幅を調整 */
                height: 100px; /* 高さを指定 */
                padding: 10px; /* 内側の余白 */
                resize: vertical; /* 縦方向のリサイズを許可 */
                }
        .box {
            width: 300px; /* 幅 */
            padding: 20px; /* 内側の余白 */
            border: 2px solid black; /* 枠線 */
            border-radius: 10px; /* 角を丸くする */
            background-color: #f9f9f9; /* 背景色 */
            text-align: center; /* 文字を中央寄せ */
            font-size: 16px; /* フォントサイズ */
            font-family: Arial, sans-serif; /* フォント */
            word-wrap: break-word; /* 単語の途中で折り返し */
            }
          
        """
    return render_template('base.html',title="台のメモを追加",body=body,addstyle=style)

@app.route("/yoso", methods=['GET', 'POST']) 
@login_required
def yoso():
    sum=0
    mydata = request.args.get('mydata')
    cday = request.args.get('cday')
    user = request.args.get('user')
    dainame = request.args.get('dainame') 
    number = request.form.get('number') #post
    body=""
    title = f"{current_user.id}の予想"
    if mydata == "true":
        body=""
        table=""
        if cday ==  None:
            table+="<h4>日付をクリックでフィルタ</h4>"
            table+="<h4>機種名をクリックでカレンダー</h4>"
            table+="<h4>台番号をクリックで全台のデータ</h4>"
        else:
            table+="""<h4><a href="/yoso?mydata=true">フィルタをやめる</a></h4>"""
        table+="""
        <table>
            <thead>
                <tr>
                    <th>日付</th>
                    <th>時間</th>
                    <th>機種名</th>
                    <th>台番号</th>
                    <th>差枚</th>
                </tr>
            </thead>
            <tbody>
        """
        with open(f'yoso.json', 'r', encoding='utf-8') as f:
            yosos = json.load(f)
        for i in reversed(yosos):
            if not cday ==  None:
                if not i["date"] == cday:
                    continue
            username=current_user.id
            try:
                if not user == None:
                    username = user
                    title = f"{username}の予想"
            except:
                pass
            if i["user"]==username:
                
                try:
                    sum+=int(i["result"].replace(",",""))
                    if int(i["result"].replace(",",""))>0:
                        color = "blue"
                    else:
                        color = "red"
                except:
                    color = ""
                table+=f"""
                    <tr>
                        <td><a href="/yoso?mydata=true&cday={i["date"]}">{i["date"]}</a></td>
                        <td>{i["time"]}</td>
                        <td><a href="/c/{i["dainame"]}">{i["dainame"]}</a></td>
                        <td><a href="/d/{i["dainame"]}">{i["daiban"]}</a></td>
                        <td><font color="{color}">{i["result"]}</font></td>
                    </tr>"""
        table+="""
            </tbody>
        </table>
        """
        style="""
        table {
                border-collapse: collapse;
                width: 100%;
                margin: 20px auto;
            }
            th, td {
                border: 1px solid #000;
                padding: 8px;
                text-align: center;
            }
        """
        if sum>0:
            color = "blue"
        else:
            color = "red"

        samai=f"""<h3>この表の合計差枚 <font color="{color}">{sum}</font>枚</h3>"""
        return render_template('base.html',title=title,body=samai+body+table,addstyle=style)
    if not dainame:
        body=""
        with open(f'allkishu.json', 'r', encoding='utf-8') as f:
            allkishu = json.load(f)
        for ss in allkishu: #台ごとのループ
            body += f'<p><a href="/yoso?dainame={ss["machine_name"]}">{ss["machine_name"]} {ss["machine_count"]}台</a></p> '
        return render_template('base.html',title="台の予想を追加",body=f"""<h4>予想した台はどれかを押すと見れます</h4><h3><a href="/yoso?mydata=true">過去の結果を見る</a></h3>"""+body)
    if number:
        if request.method == 'POST':
            today=datetime.today().date()
            body=""
            with open(f'allkishu.json', 'r', encoding='utf-8') as f:
                allkishu = json.load(f)
            for ss in allkishu: #台ごとのループ
                body += f'<p><a href="/yoso?dainame={ss["machine_name"]}">{ss["machine_name"]} {ss["machine_count"]}台</a></p> '
            with open("yoso.json", 'r') as file:
                memos = json.load(file)
            for memo in memos:
                if memo["daiban"] == number and memo["user"] == current_user.id and memo["date"] == str(today):
                    memos.remove(memo)
                    with open("yoso.json", 'w') as file:
                        json.dump(memos, file, indent=4,ensure_ascii=False)
                    return redirect(f"/yoso?dainame={dainame}")
                    #return render_template('base.html',title="台の予想を追加",body=f"""<h4><font color="red">{dainame}の{number}台を予測を削除しました</font></h4>"""+body)
            memos.append({
                "daiban":number,
                "dainame":dainame,
                "user":current_user.id,
                "date":str(today),
                "time":str(datetime.now().strftime("%H:%M")),
                "result":""
            })
            with open("yoso.json", 'w') as file:
                json.dump(memos, file, indent=4,ensure_ascii=False)
            return redirect(f"/yoso?dainame={dainame}")
            #return render_template('base.html',title="台の予想を追加",body=f"""<h4><font color="red">{dainame}の{number}台を予測しました</font></h4>"""+body)
    else:
        with open(f'allkishu.json', 'r', encoding='utf-8') as f:
            allkishu = json.load(f)
        body+=f"""
        <h5>{dainame}の台番号を選択してください。</h5>
        <h5>キャンセルしたい場合はもう一度同じ台にいれてください。</h5>
            <form method="POST">
            <p>台番号を選択
                <select name="number" id="number">
              """
        found=False
        for s in allkishu:
            if s["machine_name"] == dainame: #allkishuにあるなら
                found = True
                for day in all_dates: #1dayごと
                    if os.path.exists(f"dayreport/dayreport-{day}.json"):
                        last=day
                date = datetime.strptime(last, "%Y%m%d") - timedelta(days=-1)
                dbdate = datetime.strptime(last, "%Y%m%d")
                body+=f"""<p>追加する当該日{date.strftime("%Y-%m-%d")}</p>"""
                with open(f'daidata/{dbdate.strftime("%Y%m%d")}/{dbdate.strftime("%Y%m%d")}-{s["machine_name"]}.json', 'r', encoding='utf-8') as f:
                    basedata = json.load(f)
                for d in basedata:
                    if not "平均" in d["machine_daiban"]:
                        body+=f"""<option value="{d["machine_daiban"]}">{d["machine_daiban"]}</option>"""
        if found==False:
            return render_template('base.html',title="台の予想を追加",body="エラー")
        body+="""
                </select></p>      
                <button type="submit">送信</button>
            </form>
        <h2>今日の予想</h2>
        """
        today=datetime.today().date()
        with open("yoso.json", 'r') as file:
            memos = json.load(file)
        todaymemo=""
        for memo in reversed(memos):
            if memo["date"]==str(today):
                todaymemo+=f"""
                <p>{memo["date"]} {memo["time"]} ユーザー名 {memo["user"]}</p></p>
                    <div class="box">{memo["dainame"]} {memo["daiban"]}番台 </div>
                """
        if todaymemo=="":
            body+="<p>今日作成された予想はありません</p>"
        else:
            body+=todaymemo
        style="""
        button {
                  padding: 10px 20px;
                  background-color: #4CAF50;
                  color: white;
                  border: none;
                  border-radius: 4px;
                  cursor: pointer;
                }
        textarea {
                width: 300px; /* 幅を調整 */
                height: 100px; /* 高さを指定 */
                padding: 10px; /* 内側の余白 */
                resize: vertical; /* 縦方向のリサイズを許可 */
                }
        .box {
            width: 300px; /* 幅 */
            padding: 20px; /* 内側の余白 */
            border: 2px solid black; /* 枠線 */
            border-radius: 10px; /* 角を丸くする */
            background-color: #f9f9f9; /* 背景色 */
            text-align: center; /* 文字を中央寄せ */
            font-size: 16px; /* フォントサイズ */
            font-family: Arial, sans-serif; /* フォント */
            word-wrap: break-word; /* 単語の途中で折り返し */
            }
          
        """
    return render_template('base.html',title="台の予想を追加",body=body,addstyle=style)


@app.route("/cst")
@login_required
def get_cst():
    body="""
    <h5>注意 手入力された当日のデータはここでは見れません</h5>
    <h4>日付を選択してください</h4>
<div class="date-picker">
  <label for="date">日付</label>
  <input type="date" id="date" name="date" min="2025-01-01" max="2100-12-31">
</div>
<div class="date-picker">
  <label for="hani">その日から何日前まで?</label>
  <input type="number" id="hani" name="hani" min="1" max="30" placeholder="ex. 30">
</div>
<button class="button" onclick="submitDate()">決定</button>

    """
    style="""
    .date-picker {
      display: flex;
      gap: 10px;
      align-items: center;
      font-size: 16px;
    }
    .date-picker input {
      width: 80px;
      text-align: center;
      padding: 5px;
      border: 1px solid #ccc;
      border-radius: 4px;
    }
    .button {
      padding: 10px 20px;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }"""
    script="""
    function submitDate() {
    const dateInput = document.getElementById('date').value;
    const hani = document.getElementById('hani').value;

    if (dateInput && hani) {
      const date = new Date(dateInput);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      
      const url = `/emilia/${hani}?cday=${year}${month}${day}`;
      window.location.href = url;
    } else {
      alert('すべての日付を入力してください');
    }
  }
    """
    return render_template('base.html',title="カスタム範囲",body=body,addstyle=style,cscript=script)

@app.route("/daidataadd", methods=['GET', 'POST'])
@login_required
def daidataadd():
    kishu = request.args.get('kishu')
    if kishu:
        if request.method == 'POST':
            for day in all_dates: #1dayごと
                    if os.path.exists(f"dayreport/dayreport-{day}.json"):
                        last=day
            date = datetime.strptime(last, "%Y%m%d") - timedelta(days=-1)
            dbdate = datetime.strptime(last, "%Y%m%d")
            with open(f'daidata/{dbdate.strftime("%Y%m%d")}/{dbdate.strftime("%Y%m%d")}-{kishu}.json', 'r', encoding='utf-8') as f:
                    basedata = json.load(f)
            daisuu=0
            list=[]
            body=f"""<h4>追加された当該日 {date.strftime("%Y-%m-%d")} 追加された機種名 <a href="/c/{kishu}">{kishu}</a></h4>"""
            for d in basedata:
                    d["machine_samai"]=""
                    d["machine_gamecount"]=""
                    d["machine_bb"]=""
                    d["machine_rb"]=""
                    d["machine_gassan"]=""
                    samai = request.form.get(d["machine_daiban"])  # 入力値を取得
                    if not d["machine_daiban"]=="平均":
                        try:
                            list.append(int(samai))
                            daisuu+=1
                            d["machine_samai"]=samai
                            body+=f"<p>{d["machine_daiban"]}番号 {samai}</p>"
                        except:
                            return render_template('base.html',title="エラー",body="入力された数値にエラー")
                    else:#平均ブロックのとき
                        sum=0
                        for l in list:
                            sum+=l
                        d["machine_samai"]=str(round(sum/daisuu))
                        body+=f"<p>{daisuu}台の{d["machine_daiban"]} {str(round(sum/daisuu))}</p>"

            if not os.path.exists(f"daidata/{date.strftime("%Y%m%d")}"):
                os.makedirs(f"daidata/{date.strftime("%Y%m%d")}")
            with open(f"daidata/{date.strftime("%Y%m%d")}/{date.strftime("%Y%m%d")}-{kishu}.json", "w", encoding="utf-8") as f:
                json.dump(basedata, f, ensure_ascii=False, indent=4)
            return render_template('base.html',title="成功 以下の入力を受け付けました",body=body)

        with open(f'allkishu.json', 'r', encoding='utf-8') as f:
            allkishu = json.load(f)
        for s in allkishu:
            if s["machine_name"] == kishu: #allkishuにあるなら
                body="""<h5>差枚を入力してください。編集するには連絡 or 再入力</h5>
                        <form method="POST">
                    """
                for day in all_dates: #1dayごと
                    if os.path.exists(f"dayreport/dayreport-{day}.json"):
                        last=day
                date = datetime.strptime(last, "%Y%m%d") - timedelta(days=-1)
                dbdate = datetime.strptime(last, "%Y%m%d")
                body+=f"""<p>追加する当該日{date.strftime("%Y-%m-%d")}</p>"""
                with open(f'daidata/{dbdate.strftime("%Y%m%d")}/{dbdate.strftime("%Y%m%d")}-{s["machine_name"]}.json', 'r', encoding='utf-8') as f:
                    basedata = json.load(f)
                for d in basedata:
                    if not "平均" in d["machine_daiban"]:
                        body+=f"""<p>{d["machine_daiban"]}番台 <input type="{d["machine_daiban"]}" name="{d["machine_daiban"]}" required></p>"""
                body+="""<button type="submit">送信</button>
                        </form>"""
                style="""button {
                              padding: 10px 20px;
                              background-color: #4CAF50;
                              color: white;
                              border: none;
                              border-radius: 4px;
                              cursor: pointer;
                            }"""
                script=""
                return render_template('base.html',title=kishu,body=body,addstyle=style,cscript=script)
        return render_template('base.html',title="エラー",body="エラー")
    else:
        body=""
        for day in all_dates: #1dayごと
            if os.path.exists(f"dayreport/dayreport-{day}.json"):
                last=day
        date = datetime.strptime(last, "%Y%m%d")
        body+=f"<p>新台や台番号が変わったものは入力できません。{date.strftime("%Y-%m-%d")}の機種と台番号が適用されています。自動で取得可能になったら上書きされます。</p>"
        with open(f'allkishu.json', 'r', encoding='utf-8') as f:
            allkishu = json.load(f)
        for ss in allkishu: #台ごとのループ
            body += f'<p><a href="/daidataadd?kishu={ss["machine_name"]}">{ss["machine_name"]} {ss["machine_count"]}台</a></p> '
        return render_template('base.html',title="まだ更新されていない台データの手動入力",body=body)

@app.route("/emilia/<nissuu>")
@login_required
def get_emilia(nissuu):
    body=f"<h4><h5>注意 手入力された当日のデータはここでは見れません</h5>過去{nissuu}日 "
    cday = request.args.get('cday')
    if not cday:
        for day in all_dates: #1dayごと 
            if os.path.exists(f"dayreport/dayreport-{day}.json"):
                last=day #自動取得された完全データの最終
    else:
        last=cday
    try:
        date = datetime.strptime(last, "%Y%m%d")
        dict={}
        with open(f'dayreport/dayreport-{date.strftime("%Y%m%d")}.json', 'r', encoding='utf-8') as f:
            basedata = json.load(f)
        for kishu in basedata:
            kishu['machine_count']=0 #basedataを初期化
        for r in range(int(nissuu)): #過去n日
            lookday=date - timedelta(days=r)
            last=lookday.strftime("%Y%m%d")
            try:
                msg="""<p></p>"""
                with open(f'dayreport/dayreport-{lookday.strftime("%Y%m%d")}.json', 'r', encoding='utf-8') as f:
                    dayreport = json.load(f)
            except:
                msg+=f"""<p><font color="red">！{lookday.strftime("%Y%m%d")}のデータがありません！</font></p>"""
                body+=msg
                continue
            for k in dayreport:
                for bas in basedata:
                    if k["machine_name"] == bas["machine_name"]:
                        bas["machine_count"]+=int(k["machine_count"].replace(",",""))
        pluslist=[]
        for samaidata in basedata:
            try:
                int(samaidata["machine_name"].replace(",",""))+samaidata["machine_count"]
            except:
                if True:
                #if samaidata["machine_count"] > 0:
                    pluslist.append(samaidata)
        for h in pluslist:
            pass
        
        body+=str(date.strftime("%Y%m%d"))+"～"+str(last)+""" <a href="/cst">カスタム範囲</a></h4> <a href="/emilia/1">過去1日</a></h4> <a href="/emilia/3">過去3日</a></h4> <a href="/emilia/7">過去7日</a></h4> <a href="/emilia/14">過去14日</a> <a href="/emilia/21">過去21日</a></h4><p>平均差枚の和なので台数が変わるとバグるかも</p><p>一台あたりの平均差枚</p>"""
        sorted_data = sorted(pluslist, key=lambda x: x['machine_count'], reverse=True)
        table="""
        <table>
            <thead>
                <tr>
                    <th>機種名、末尾番号</th>
                    <th>平均差枚</th>
                </tr>
            </thead>
            <tbody>
        """
        for i in sorted_data:
            table+=f"""<tr><td><a href="/c/{i["machine_name"]}">{i["machine_name"]}</a></td><td>{i["machine_count"]}</td></tr>"""
        table+="""
            </tbody>
        </table>
        """
        style="""
        table {
                border-collapse: collapse;
                width: 100%;
                margin: 20px auto;
            }
            th, td {
                border: 1px solid #000;
                padding: 8px;
                text-align: center;
            }
        """
        return render_template('base.html',title="分析",body=body+table,addstyle=style)
    except:
        return render_template('base.html',title="エラーです",body="日付範囲を見直して")

@app.route("/fever", methods=['GET', 'POST']) #総差枚を表示?
@login_required
def get_fever():
    body="""
    <link href='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.0/main.min.css' rel='stylesheet' />
    <script src='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.0/main.min.js'></script>
    <form method="POST">
        <p>編集するには同じ開始日を選択し、編集したい終了日を入力してください。それ以外はお問い合わせ</p>
        <p>開始日</p>
        <input type="date" name="date" required>
        <p>終了日</p>
        <input type="date" name="enddate" required>
        <p></p>
        <select name="device" required>
            <option value="" disabled selected>機種名を選択</option>
    """
    with open(f'allkishu.json', 'r', encoding='utf-8') as f:
        allkishu = json.load(f)
    for ss in allkishu: #台ごとのループ
        body += f'<option value="{ss["machine_name"]}">{ss["machine_name"]}</option>'
    body+=f"""    
        </select>
        <p></p>
        <input type="text" name="eventname" placeholder="何があったか"  value="FEVER" required>
        <p></p>
        <button type="submit">送信</button>
        <p></p>
    </form>"""
    style="""
    button {
      padding: 10px 20px;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    body {
            font-family: Arial, sans-serif;
            margin: 0;
            height: 100vh; /* ビューポート全体の高さに合わせる */
            display: flex;
            flex-direction: column;
    }
    #calendar {
            
        }
    """
    #flex-grow: 1; /* カレンダーが残りのスペースを占めるように */
    #height: 100%;  /* カレンダーが縦いっぱいになる */
    cscript="""
        document.addEventListener('DOMContentLoaded', function() {
            var calendarEl = document.getElementById('calendar');
            var calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: 'dayGridMonth',
                events: '/events/news'
            });
        
            calendar.render();
        });
    """
    if request.method == 'POST':
        date = request.form.get('date')  # 入力値を取得
        enddate = request.form.get('enddate')  # 入力値を取得
        eventname = request.form.get('device')+request.form.get('eventname')  # 入力値を取得
        with open('news.json', 'r') as file:
            events = json.load(file)
        date_obj = datetime.strptime(enddate, "%Y-%m-%d")
        next_date = date_obj + timedelta(days=1)
        enddatep1=next_date.strftime("%Y-%m-%d")
        for e in events:
            print("hogeeee")
            if e["start"]==date and e["title"]==eventname:
                body+=f"""<p>{e["title"]}のフィーバーの終了日{enddate}が上書きされます</p>"""
                e["end"]=enddatep1
                with open('news.json', 'w') as file:
                    json.dump(events, file, indent=4,ensure_ascii=False)
                return render_template('base.html',title="フィーバー入力",body=body+f"{date}に{eventname}を追加+<div id='calendar'></div>",addstyle=style,cscript=cscript)
            else:  
                new_event = {
                "title": eventname,
                "start": date,
                "end": enddatep1,
                "color": "gold"
                }
                events.append(new_event)
                with open('news.json', 'w') as file:
                    json.dump(events, file, indent=4,ensure_ascii=False)
                return render_template('base.html',title="フィーバー入力",body=body+f"{date}に{eventname}を追加+<div id='calendar'></div>",addstyle=style,cscript=cscript)
        if events==[]:
            new_event = {
                "title": eventname,
                "start": date,
                "end": enddatep1,
                "color": "gold"
                }
            events.append(new_event)
            with open('news.json', 'w') as file:
                json.dump(events, file, indent=4,ensure_ascii=False)
            return render_template('base.html',title="フィーバー入力",body=body+f"{date}に{eventname}を追加+<div id='calendar'></div>",addstyle=style,cscript=cscript)
    return render_template('base.html',title="フィーバー入力",body=body+"<div id='calendar'></div>",addstyle=style,cscript=cscript)

@app.route("/index", methods=['GET', 'POST']) #総差枚を表示?
@login_required
def get_index():
    body=f"""    
    <form method="POST">
        <input type="date" name="date" required>
        <input type="text" name="text" placeholder="イベント名" required> 
        <button type="submit">送信</button>
    </form>"""
    style="""
    button {
      padding: 10px 20px;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }"""

    if request.method == 'POST':
        date = request.form.get('date')  # 入力値を取得
        eventname = "特 "+request.form.get('text')  # 入力値を取得
        with open('eventday.json', 'r') as file:
            events = json.load(file)
        for e in events:
            if e["start"]==date:
                return render_template('base.html',title="イベント日入力",body=body+f"その日のイベントは既に追加されています",addstyle=style)
        new_event = {
        "title": eventname,
        "start": date,
        "color": "pink"
        }
        events.append(new_event)
        with open('eventday.json', 'w') as file:
            json.dump(events, file, indent=4,ensure_ascii=False)
        return render_template('base.html',title="イベント日入力",body=body+f"{date}に{eventname}を追加",addstyle=style)
    return render_template('base.html',title="イベント日入力",body=body,addstyle=style)

@app.route("/mikoto") #台別の表を出す
@login_required
def get_mikoto():
    body=""
    alldata=[]
    addstyle="""
        #search-box {
            width: 300px;
            padding: 10px;
            font-size: 16px;
        }
        #suggestions {
            border: 1px solid #ccc;
            display: none;
            position: absolute;
            background-color: white;
            z-index: 1;
            width: 300px; /* テキストボックスと同じ幅 */
        }
        .suggestion-item {
            padding: 8px;
            cursor: pointer;
        }
        .suggestion-item:hover {
            background-color: #f0f0f0;
        }
        """
    
    body+=f"""
    <input type="text" id="search-box" placeholder="検索..." autocomplete="off">
    <div id="suggestions"></div>"""
    with open(f'allkishu.json', 'r', encoding='utf-8') as f:
        allkishu = json.load(f)
    for ss in allkishu: #台ごとのループ
        alldata.append(ss["machine_name"])
        body += f'<p><a href="/d/{ss["machine_name"]}">{ss["machine_name"]} {ss["machine_count"]}台</a></p> '
    cscript=f"""
            const suggestions = {str(alldata)};"""
    cscript+="""
        const searchBox = document.getElementById("search-box");
        const suggestionsBox = document.getElementById("suggestions");

        searchBox.addEventListener("input", () => {
            const input = searchBox.value.toLowerCase();
            suggestionsBox.innerHTML = '';
            
            if (input) {
                const filteredSuggestions = suggestions.filter(suggestion => 
                    suggestion.toLowerCase().includes(input)
                );

                if (filteredSuggestions.length > 0) {
                    suggestionsBox.style.display = "block";
                    filteredSuggestions.forEach(suggestion => {
                        const div = document.createElement("div");
                        div.textContent = suggestion;
                        div.classList.add("suggestion-item");
                        div.addEventListener("click", () => {
                            window.location.href = `/d/${suggestion}`; // 候補名をURLに追加
                        });
                        suggestionsBox.appendChild(div);
                    });
                } else {
                    suggestionsBox.style.display = "none";
                }
            } else {
                suggestionsBox.style.display = "none";
            }
        });
    """
    return render_template('base.html',title="過去の台別の差枚 <p>並びが変わったりしたらバグる可能性あり</p>",body=body,addstyle=addstyle,cscript=cscript)

@app.route("/enter") #台別の表を出す
@login_required
def get_enter():
    body="""
    <p><a href="/daidataadd">台データを入力</a></p>
    <p><a href="/memo">台のメモを入力</a></p>
    <p><a href="/index">イベント入力</a></p>
    <p><a href="/fever">フィーバー入力</a></p>
    <p></p>
    """
    return render_template('base.html',title="データ入力<p></p>",body=body)

@app.route("/graph") #台別の表を出す
@login_required
def get_graph():
    body=""
    kishu = request.args.get('kishu')
    if not None == kishu:
        body+=f"""<p><a href="/graph">グラフを見る機種選択に戻る</a></p>
        """
        day = request.args.get('day')
        if not None == day:
            body+=f"""<h2>{day}の<a href="/d/{kishu}">{kishu}</a>のグラフ</h2>"""
            try:
                with open(f"graph/{day}/{day}-{kishu}.html", "r", encoding="utf-8") as file: #機種グラフを読み込む
                    hoge = file.read()
            except:
                hoge = "error"
            yyyy = datetime.strptime(day, "%Y%m%d")
            mae = yyyy - timedelta(days=1)
            tugi = yyyy - timedelta(days=-1)
            body+=f"""
            <p><a href="/graph?kishu={kishu}&day={mae.strftime('%Y%m%d')}">←前日</a></p>
            <p><a href="/graph?kishu={kishu}&day={tugi.strftime('%Y%m%d')}">翌日→</a></p>
            """
            body+=hoge
            body+="""
            <style>
                table {
                    border-collapse: collapse;
                    width: 100%;
                    border: 1px solid black;
                }

                th, td {
                    border: 1px solid black;
                    padding: 8px;
                    text-align: center;
                }

                th {
                    background-color: #f2f2f2;
                }

                th {
                    background-color: #000000;
                }

            </ style>
            """
            return render_template('base.html',title="グラフを見る",body=body)
        
        body+=f"""
        <p>{kishu}のグラフを見る</p>
        """
        for r in range(100):
            for day in all_dates: #1dayごと
                if os.path.exists(f"dayreport/dayreport-{day}.json"):
                    last=day
            today = datetime.strptime(last, "%Y%m%d")
            day=(today - timedelta(days=r)).strftime('%Y%m%d')
            if not os.path.exists(f"graph/{day}/{day}-{kishu}.html"):
                continue
            body+=f"""<p><a href="/graph?kishu={kishu}&day={day}">{day}のグラフ</a></p>"""
        return render_template('base.html',title="グラフを見る",body=body)
    
    alldata=[]
    addstyle="""
        #search-box {
            width: 300px;
            padding: 10px;
            font-size: 16px;
        }
        #suggestions {
            border: 1px solid #ccc;
            display: none;
            position: absolute;
            background-color: white;
            z-index: 1;
            width: 300px; /* テキストボックスと同じ幅 */
        }
        .suggestion-item {
            padding: 8px;
            cursor: pointer;
        }
        .suggestion-item:hover {
            background-color: #f0f0f0;
        }
        """
    body+=f"""
    <input type="text" id="search-box" placeholder="検索..." autocomplete="off">
    <div id="suggestions"></div>"""
    with open(f'allkishu.json', 'r', encoding='utf-8') as f:
        allkishu = json.load(f)
    for ss in allkishu: #台ごとのループ
        alldata.append(ss["machine_name"])
        body += f'<p><a href="/graph?kishu={ss["machine_name"]}">{ss["machine_name"]} {ss["machine_count"]}台</a></p> '
    cscript=f"""
            const suggestions = {str(alldata)};"""
    cscript+="""
        const searchBox = document.getElementById("search-box");
        const suggestionsBox = document.getElementById("suggestions");

        searchBox.addEventListener("input", () => {
            const input = searchBox.value.toLowerCase();
            suggestionsBox.innerHTML = '';
            
            if (input) {
                const filteredSuggestions = suggestions.filter(suggestion => 
                    suggestion.toLowerCase().includes(input)
                );

                if (filteredSuggestions.length > 0) {
                    suggestionsBox.style.display = "block";
                    filteredSuggestions.forEach(suggestion => {
                        const div = document.createElement("div");
                        div.textContent = suggestion;
                        div.classList.add("suggestion-item");
                        div.addEventListener("click", () => {
                            window.location.href = `/graph?kishu=${suggestion}`; // 候補名をURLに追加
                        });
                        suggestionsBox.appendChild(div);
                    });
                } else {
                    suggestionsBox.style.display = "none";
                }
            } else {
                suggestionsBox.style.display = "none";
            }
        });
    """
    return render_template('base.html',title="グラフを見る<p>並びが変わったりしたらバグる可能性あり</p>",body=body,addstyle=addstyle,cscript=cscript)


@app.route('/d/<kishu>')
@login_required
def mikochan(kishu):
    if kishu == "総合":
        return redirect("/mikoto")
    daisuu=""
    with open(f'allkishu.json', 'r', encoding='utf-8') as f:
        allkishu = json.load(f)
    for ss in allkishu: #台ごとのループ
        if ss["machine_name"] == kishu:
            daisuu=ss["machine_count"]
    if daisuu=="":
        return render_template('base.html',title="エラー",body="エラー")
    data = []
    head=[]
    row = [""]
    for c in range(int(daisuu)):  #一番上の行を確保
        row.append("null")
    head.append(row)

    for day in all_dates: #1dayごと
        if os.path.exists(f"daidata/{day}"): #daidataの日付フォルダがあれば今日とする
            last=day #last=yyyymmdd
    date = datetime.strptime(last, "%Y%m%d")
    for r in range(100):
        row = []  # 各行のリスト
        lookday=date - timedelta(days=r)
        dd=str(lookday.strftime("%Y-%m-%d"))
        row.append(f"""<a href="/graph?kishu={kishu}&day={lookday.strftime("%Y%m%d")}">{dd}</a>""") #--
        lookingday=lookday.strftime("%Y%m%d")
        try:
            with open(f'daidata/{lookingday}/{lookingday}-{kishu}.json', 'r', encoding='utf-8') as f:  #1日前、2日前、3日前...
                daidata = json.load(f)
            for dai in daidata:  
                if not dai["machine_daiban"]=="平均":
                    row.append(dai["machine_samai"].replace(",","")) #差枚を記録
            data.append(row)  # 完成した行をデータに追加
        except:
            pass
    try:
        with open(f'daidata/{date.strftime("%Y%m%d")}/{date.strftime("%Y%m%d")}-{kishu}.json', 'r', encoding='utf-8') as f: #今日のデータ
            daidata = json.load(f)
    except:
        yesterday=date - timedelta(days=1)
        with open(f'daidata/{yesterday.strftime("%Y%m%d")}/{yesterday.strftime("%Y%m%d")}-{kishu}.json', 'r', encoding='utf-8') as f: #今日のデータ
            daidata = json.load(f)
    count=1
    for i in daidata:
        if not i["machine_daiban"]=="平均":
            head[0][count]=(i["machine_daiban"])
            count+=1
            
    return render_template('hyou.html', data=data,name=kishu,head=head)

def run_collector():
    collector.start()

if __name__ == '__main__':
    threading.Thread(target=run_collector, daemon=True).start()
    app.run(port=8192,debug=True, use_reloader=False)