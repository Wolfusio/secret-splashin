from flask import Flask, render_template_string, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = "splashin_secret_key"

# Stockage temporaire des participants
participants = []
targets = {}

# Page d'accueil
@app.route("/", methods=["GET", "POST"])
def home():
    global participants, targets
    if request.method == "POST":
        name = request.form.get("name").strip()
        if name and name not in participants:
            participants.append(name)
        return redirect(url_for("home"))

    html = """
    <h2>🎯 Secret Splashin'</h2>
    <p>Entre ton prénom pour rejoindre la partie :</p>
    <form method="post">
      <input type="text" name="name" placeholder="Ton prénom" required>
      <button type="submit">Rejoindre</button>
    </form>
    <h3>Participants :</h3>
    <ul>
    {% for p in participants %}
        <li>{{ p }}</li>
    {% endfor %}
    </ul>
    {% if participants|length >= 3 %}
      <a href="{{ url_for('start_game') }}">🚀 Lancer la partie</a>
    {% else %}
      <p><i>Il faut au moins 3 participants.</i></p>
    {% endif %}
    """
    return render_template_string(html, participants=participants)

# Lancement du jeu
@app.route("/start")
def start_game():
    global participants, targets
    names = participants.copy()
    shuffled = names.copy()
    random.shuffle(shuffled)

    for i, name in enumerate(names):
        target = shuffled[i]
        # éviter qu'une personne tombe sur elle-même
        if target == name:
            random.shuffle(shuffled)
            return redirect(url_for("start_game"))
        targets[name] = target

    return redirect(url_for("choose_player"))

# Sélection du joueur qui va voir sa cible
@app.route("/choose", methods=["GET", "POST"])
def choose_player():
    global participants, targets
    if request.method == "POST":
        name = request.form.get("player")
        if name in targets:
            session["current_player"] = name
            return redirect(url_for("show_target"))
    html = """
    <h2>🎯 Qui veut voir sa cible ?</h2>
    <form method="post">
      <select name="player" required>
        {% for p in participants %}
          <option value="{{ p }}">{{ p }}</option>
        {% endfor %}
      </select>
      <button type="submit">Voir ma cible</button>
    </form>
    """
    return render_template_string(html, participants=participants)

# Page qui affiche la cible d'un joueur
@app.route("/target")
def show_target():
    player = session.get("current_player")
    if not player:
        return redirect(url_for("choose_player"))

    target = targets.get(player, "Erreur : aucune cible trouvée 😅")

    html = f"""
    <h2>🎯 Secret Splashin'</h2>
    <p><b>{player}</b>, ta cible est :</p>
    <h1 style='color: red;'>{target}</h1>
    <a href='{url_for('choose_player')}'>⬅️ Retour</a>
    """
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)