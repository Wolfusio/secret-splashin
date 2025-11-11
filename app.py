from flask import Flask, render_template_string, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = "splashin_secret_key"

# --- Chaque salle a ses propres données ---
rooms = {}

# --- HTML global avec style intégré ---
BASE_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Secret Splashin'</title>
  <style>
    body {{
      background: linear-gradient(135deg, #5be7a9, #2d9bf0);
      font-family: 'Segoe UI', sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      color: #fff;
      text-align: center;
      margin: 0;
    }}
    h1, h2, h3 {{
      margin: 10px 0;
    }}
    input, select, button, a {{
      margin-top: 10px;
      padding: 10px 15px;
      border: none;
      border-radius: 8px;
      font-size: 16px;
    }}
    input, select {{
      width: 200px;
      text-align: center;
      outline: none;
    }}
    button, a {{
      background: #fff;
      color: #0077cc;
      text-decoration: none;
      font-weight: bold;
      transition: 0.3s;
      cursor: pointer;
    }}
    button:hover, a:hover {{
      background: #e0f0ff;
    }}
    ul {{
      list-style: none;
      padding: 0;
      margin: 0;
    }}
    li {{
      background: rgba(255,255,255,0.2);
      margin: 5px;
      padding: 5px 15px;
      border-radius: 6px;
    }}
    .small {{
      font-size: 14px;
      opacity: 0.8;
    }}
  </style>
</head>
<body>
  <div style="max-width: 400px;">
    {content}
  </div>
</body>
</html>
"""

# --- Page d'accueil ---
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        room_code = request.form.get("room").strip().lower()
        if room_code not in rooms:
            rooms[room_code] = {"participants": [], "targets": {}}
        session["room"] = room_code
        return redirect(url_for("home", room_code=room_code))

    content = """
    <h1>💦 Secret Splashin'</h1>
    <p>Crée ou rejoins une salle :</p>
    <form method="post">
      <input type="text" name="room" placeholder="Nom de la salle" required>
      <br><button type="submit">Entrer</button>
    </form>
    <p class="small">Exemple : korenparty, team1, soirée123...</p>
    """
    return render_template_string(BASE_HTML.format(content=content))

# --- Accueil de la salle ---
@app.route("/room/<room_code>", methods=["GET", "POST"])
def home(room_code):
    room = rooms.get(room_code)
    if not room:
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name").strip()
        if name and name not in room["participants"]:
            room["participants"].append(name)
        return redirect(url_for("home", room_code=room_code))

    content = f"""
    <h1>🎯 Salle : {room_code}</h1>
    <form method="post">
      <input type="text" name="name" placeholder="Ton prénom" required>
      <br><button type="submit">Rejoindre</button>
    </form>
    <h3>Participants :</h3>
    <ul>
    {{% for p in room["participants"] %}}
      <li>{{{{ p }}}}</li>
    {{% endfor %}}
    </ul>
    <p class="small">{{{{ room["participants"]|length }}} joueur(s)</p>
    {{% if room["participants"]|length >= 3 %}}
      <a href="{{{{ url_for('start_game', room_code=room_code) }}}}">🚀 Lancer la partie</a>
    {{% else %}}
      <p><i>Il faut au moins 3 participants.</i></p>
    {{% endif %}}
    """
    return render_template_string(BASE_HTML.format(content=content), room=room)

# --- Lancer la partie ---
@app.route("/start/<room_code>")
def start_game(room_code):
    room = rooms.get(room_code)
    if not room:
        return redirect(url_for("index"))

    names = room["participants"].copy()
    if len(names) < 3:
        return redirect(url_for("home", room_code=room_code))

    shuffled = names.copy()
    random.shuffle(shuffled)

    for i, name in enumerate(names):
        target = shuffled[i]
        if target == name:
            random.shuffle(shuffled)
            return redirect(url_for("start_game", room_code=room_code))
        room["targets"][name] = target

    return redirect(url_for("choose_player", room_code=room_code))

# --- Choix du joueur ---
@app.route("/choose/<room_code>", methods=["GET", "POST"])
def choose_player(room_code):
    room = rooms.get(room_code)
    if not room:
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("player")
        if name in room["targets"]:
            session["player"] = name
            session["room"] = room_code
            return redirect(url_for("show_target", room_code=room_code))

    content = f"""
    <h2>👀 Salle : {room_code}</h2>
    <form method="post">
      <select name="player" required>
        {{% for p in room["participants"] %}}
          <option value="{{{{ p }}}}">{{{{ p }}}}</option>
        {{% endfor %}}
      </select>
      <br><button type="submit">Voir ma cible</button>
    </form>
    <p class="small">⚠️ Les autres ne doivent pas regarder !</p>
    """
    return render_template_string(BASE_HTML.format(content=content), room=room)

# --- Affichage de la cible ---
@app.route("/target/<room_code>")
def show_target(room_code):
    room = rooms.get(room_code)
    if not room:
        return redirect(url_for("index"))

    player = session.get("player")
    if not player:
        return redirect(url_for("choose_player", room_code=room_code))

    target = room["targets"].get(player, "Erreur : aucune cible trouvée 😅")

    content = f"""
    <h1>🎯 Secret Splashin'</h1>
    <p><b>{player}</b>, ta cible est :</p>
    <h2 style='color: yellow;'>{target}</h2>
    <a href='{url_for('choose_player', room_code=room_code)}'>⬅️ Retour</a>
    """
    return render_template_string(BASE_HTML.format(content=content))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

