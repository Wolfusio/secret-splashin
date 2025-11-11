from flask import Flask, render_template_string, request, redirect, url_for, session
import random
import string

app = Flask(__name__)
app.secret_key = "super_secret_splashin_key"

rooms = {}

html_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Secret Splashin 💦</title>
<style>
body { font-family: 'Poppins', sans-serif; background: linear-gradient(120deg,#8EC5FC,#E0C3FC); color:#222; text-align:center; padding:40px; }
h1{color:#3A006B;}
input,select{padding:10px;border-radius:12px;border:none;width:80%%;max-width:300px;margin:10px;text-align:center;font-size:1.1em;}
button{background:#3A006B;color:white;border:none;border-radius:15px;padding:12px 25px;font-size:1em;margin-top:10px;cursor:pointer;transition:0.2s;}
button:hover{background:#5E17EB;}
button.reset{background:#FF3B3B;}
.box{background:white;border-radius:25px;box-shadow:0 0 10px rgba(0,0,0,0.1);padding:30px;margin:auto;max-width:400px;}
.fade-in{animation:fadein 0.8s ease-in-out;}
@keyframes fadein{from{opacity:0;transform:translateY(15px);}to{opacity:1;transform:translateY(0);}}
</style>
</head>
<body>
<div class="box fade-in">
{% if step == "home" %}
<h1>Secret Splashin 💦</h1>
<form method="post" action="{{ url_for('create_room') }}">
<button type="submit">Créer un groupe</button>
</form>
<form method="post" action="{{ url_for('join_room') }}">
<input type="text" name="room_code" placeholder="Code du groupe" required><br>
<button type="submit">Rejoindre un groupe</button>
</form>

{% elif step == "setup" %}
<h1>Groupe {{ room_code }}</h1>
<form method="post" action="{{ url_for('set_name', room_code=room_code) }}">
<input type="text" name="player_name" placeholder="Pseudo" required><br>
{% if is_creator %}
<label><input type="checkbox" name="master_option"> Partie avec maître du jeu</label><br>
{% endif %}
<button type="submit">Rejoindre</button>
</form>
<h3>Joueurs inscrits :</h3>
<p>{{ ', '.join(players) }}</p>

{% elif step == "waiting" %}
<h1>Groupe {{ room_code }}</h1>
<h3>Joueurs inscrits :</h3>
<p>{{ ', '.join(players) }}</p>
{% if is_creator %}
<form method="post" action="{{ url_for('start_game', room_code=room_code) }}">
<label>Mode de partie : </label>
<select name="mode">
<option value="unique">Cibles uniques</option>
<option value="enemy">Cibles ennemis</option>
</select><br>
{% if master_option %}
<label><input type="checkbox" name="manual_targets"> Le maître attribue lui-même les cibles</label><br>
{% endif %}
<button type="submit">Lancer la distribution</button>
</form>
<form method="post" action="{{ url_for('reset_game', room_code=room_code) }}">
<button type="submit" class="reset">Réinitialiser la partie 🔄</button>
</form>
{% else %}
<p>Attendez que le créateur lance la partie...</p>
{% endif %}

{% elif step == "manual_targets" %}
<h1>Attribuer les cibles</h1>
<form method="post" action="{{ url_for('submit_manual', room_code=room_code) }}">
{% for p in players %}
<label>{{ p }} → 
<select name="{{ p }}">
{% for t in players %}
{% if t != p %}
<option value="{{ t }}">{{ t }}</option>
{% endif %}
{% endfor %}
</select></label><br>
{% endfor %}
<button type="submit">Valider les cibles</button>
</form>

{% elif step == "target" %}
<h1>👀 Salut {{ player }} !</h1>
<p>Attends ton tour… ta cible sera affichée sur ton appareil uniquement.</p>
<form method="post" action="{{ url_for('reveal_target', room_code=room_code) }}">
<button type="submit">Voir ma cible</button>
</form>

{% elif step == "target_revealed" %}
<h1>👀 Salut {{ player }} !</h1>
<p>Ta cible est :</p>
<h2 style="color:#5E17EB;">{{ target }}</h2>
<form method="post" action="{{ url_for('next_player', room_code=room_code) }}">
<button type="submit">OK, suivant</button>
</form>

{% elif step == "done" %}
<h1>✅ Tous les joueurs ont reçu leur cible !</h1>
<p>Le jeu peut commencer 🎉</p>
{% endif %}
</div>
</body>
</html>
"""

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

@app.route("/", methods=["GET"])
def home():
    return render_template_string(html_template, step="home")

@app.route("/create", methods=["POST"])
def create_room():
    code = generate_code()
    rooms[code] = {
        "players": [],
        "targets": {},
        "current_index": 0,
        "master_option": False,
        "creator": "",  # vide au départ
        "mode": "unique",
        "manual": False
    }
    session['room_code'] = code
    return redirect(url_for('setup_room', room_code=code))

@app.route("/join", methods=["POST"])
def join_room():
    code = request.form['room_code'].strip().upper()
    if code in rooms:
        session['room_code'] = code
        return redirect(url_for('setup_room', room_code=code))
    return f"Groupe {code} inexistant 😅"

@app.route("/setup/<room_code>", methods=["GET","POST"])
def setup_room(room_code):
    room = rooms[room_code]
    players = room['players']
    is_creator = False
    if request.method=="POST":
        name = request.form['player_name'].strip()
        if name not in players:
            players.append(name)
        if room['creator'] == "":
            room['creator'] = name
            is_creator = True
            room['master_option'] = "master_option" in request.form
        session['name'] = name
        return redirect(url_for('waiting_room', room_code=room_code))
    is_creator = (room['creator'] == "")
    return render_template_string(html_template, step="setup", room_code=room_code, players=players, is_creator=is_creator)

@app.route("/waiting/<room_code>", methods=["GET","POST"])
def waiting_room(room_code):
    room = rooms[room_code]
    players = room['players']
    is_creator = session.get('name','') == room['creator']
    return render_template_string(html_template, step="waiting", room_code=room_code, players=players, is_creator=is_creator, master_option=room['master_option'], show_reset=is_creator)

@app.route("/start/<room_code>", methods=["POST"])
def start_game(room_code):
    room = rooms[room_code]
    room['mode'] = request.form.get('mode','unique')
    room['manual'] = "manual_targets" in request.form
    if room['manual']:
        return render_template_string(html_template, step="manual_targets", room_code=room_code, players=room['players'])
    names = room['players'][:]
    shuffled = names[:]
    random.shuffle(shuffled)
    if room['mode']=="unique":
        for i,name in enumerate(names):
            if shuffled[i]==name:
                random.shuffle(shuffled)
                break
        room['targets'] = dict(zip(names, shuffled))
    elif room['mode']=="enemy":
        room['targets'] = {names[i]: names[(i+1)%len(names)] for i in range(len(names))}
    room['current_index'] = 0
    return redirect(url_for('show_target', room_code=room_code))

@app.route("/submit_manual/<room_code>", methods=["POST"])
def submit_manual(room_code):
    room = rooms[room_code]
    room['targets'] = {player: request.form[player] for player in room['players']}
    room['current_index'] = 0
    return redirect(url_for('show_target', room_code=room_code))

@app.route("/reveal/<room_code>", methods=["POST"])
def reveal_target(room_code):
    room = rooms[room_code]
    idx = room['current_index']
    names = list(room['targets'].keys())
    if idx < len(names):
        player = names[idx]
        target = room['targets'][player]
        return render_template_string(html_template, step="target_revealed", player=player, target=target, room_code=room_code)
    return render_template_string(html_template, step="done")

@app.route("/next/<room_code>", methods=["POST"])
def next_player(room_code):
    room = rooms[room_code]
    room['current_index'] +=1
    return redirect(url_for('show_target', room_code=room_code))

@app.route("/reset/<room_code>", methods=["POST"])
def reset_game(room_code):
    room = rooms[room_code]
    room['targets'] = {}
    room['current_index'] = 0
    return redirect(url_for('waiting_room', room_code=room_code))

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)
