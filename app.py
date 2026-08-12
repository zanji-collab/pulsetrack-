from flask import Flask,request,jsonify,render_template_string
import sqlite3

app=Flask(__name__)
DB="health.db"

def db():
    c=sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS health(
    id INTEGER PRIMARY KEY,date TEXT,steps INTEGER,water INTEGER,
    sleep REAL,weight REAL,calories INTEGER,note TEXT)""")
    return c

HTML="""
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PulseTrack</title>
<style>
*{box-sizing:border-box}body{margin:0;font-family:Arial;background:#0b1020;color:white}
header{padding:25px 20px;background:linear-gradient(135deg,#6c5ce7,#00cec9)}
h1{margin:0;font-size:30px}.sub{opacity:.8}
main{padding:18px;max-width:600px;margin:auto}
.card{background:#151c32;padding:18px;border-radius:20px;margin-bottom:14px;box-shadow:0 8px 25px #0004}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.stat{font-size:28px;font-weight:bold;margin-top:8px}
input,textarea,button{width:100%;padding:13px;border:0;border-radius:12px;margin-top:8px}
input,textarea{background:#252e49;color:white}
button{background:#6c5ce7;color:white;font-weight:bold;font-size:16px}
button:active{transform:scale(.98)}
.progress{
background:#252e49;
height:12px;
border-radius:20px;
overflow:hidden;
margin-bottom:15px
}

.bar{
height:100%;
width:0%;
background:linear-gradient(90deg,#6c5ce7,#00cec9);
transition:width .5s
}
label{font-size:13px;color:#aaa}
</style></head><body>
<header><h1>PulseTrack 💙</h1><div class="sub">Your daily health dashboard</div></header>
<main>
<div class="card">
<h2>Today's Progress</h2>
<div class="grid">
<div>👟 Steps<div class="stat" id="steps">0</div></div>
<div>💧 Water<div class="stat" id="water">0 ml</div></div>
<div>😴 Sleep<div class="stat" id="sleep">0 h</div></div>
<div>⚖️ Weight<div class="stat" id="weight">0 kg</div></div>
</div></div>
<div class="card">
<h2>🎯 Daily Goals</h2>

<p>👟 Steps: <span id="stepGoal">0%</span></p>
<div class="progress">
<div id="stepBar" class="bar"></div>
</div>

<p>💧 Water: <span id="waterGoal">0%</span></p>
<div class="progress">
<div id="waterBar" class="bar"></div>
</div>

<p>😴 Sleep: <span id="sleepGoal">0%</span></p>
<div class="progress">
<div id="sleepBar" class="bar"></div>
</div>

</div>

<div class="card"><h2>Update Today</h2>
<label>Steps</label><input id="s" type="number" placeholder="e.g. 5000">
<label>Water (ml)</label><input id="w" type="number" placeholder="e.g. 1500">
<label>Sleep (hours)</label><input id="sl" type="number" step=".1" placeholder="e.g. 8">
<label>Weight (kg)</label><input id="we" type="number" step=".1" placeholder="e.g. 65">

<label>Calories</label><input id="cal" type="number" placeholder="e.g. 2000">

<label>Notes</label><textarea id="n" placeholder="How was your day?"></textarea>
<button onclick="save()">SAVE TODAY</button></div>

<div class="card"><h2>Recent Records</h2><div id="history">Loading...</div></div>
</main>
<script>
async function load(){
 let d=await (await fetch('/api')).json();

 if(d.length){

  let x=d[0];

  steps.innerText=x.steps||0;
  water.innerText=(x.water||0)+' ml';
  sleep.innerText=(x.sleep||0)+' h';
  weight.innerText=(x.weight||0)+' kg';

  let stepPercent=Math.min(((x.steps||0)/5000)*100,100);
  let waterPercent=Math.min(((x.water||0)/2000)*100,100);
  let sleepPercent=Math.min(((x.sleep||0)/8)*100,100);

  stepGoal.innerText=Math.round(stepPercent)+'%';
  waterGoal.innerText=Math.round(waterPercent)+'%';
  sleepGoal.innerText=Math.round(sleepPercent)+'%';

  stepBar.style.width=stepPercent+'%';
  waterBar.style.width=waterPercent+'%';
  sleepBar.style.width=sleepPercent+'%';
 }

 history.innerHTML=d.map(x=>`<p>📅 ${x.date}<br>
 👟 ${x.steps||0} steps · 💧 ${x.water||0} ml · 😴 ${x.sleep||0}h · ⚖️ ${x.weight||0}kg</p>`).join('');
}
async function save(){
 await fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},
 body:JSON.stringify({steps:s.value,water:w.value,sleep:sl.value,weight:we.value,note:n.value})});
 s.value=w.value=sl.value=we.value=n.value='';load();
}
load();
</script></body></html>
"""

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/api",methods=["GET","POST"])
def api():
 c=db()
 if request.method=="POST":
  x=request.json
  c.execute("INSERT INTO health VALUES(NULL,date('now'),?,?,?,?,?)",
   (x.get("steps",0),x.get("water",0),x.get("sleep",0),x.get("weight",0),x.get("note","")))
  c.commit()
 rows=c.execute("SELECT date,steps,water,sleep,weight,note FROM health ORDER BY id DESC LIMIT 30").fetchall()
 return jsonify([dict(zip(["date","steps","water","sleep","weight","note"],r)) for r in rows])

app.run(host="0.0.0.0",port=5000)
