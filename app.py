from flask import Flask, render_template_string, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = "super_secret_splashin_key"

# Interface HTML (intégrée pour Render)
html_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secret Splashin 💦</title>
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(120deg, #8EC5FC, #E0C3FC);
            color: #222;
            text-align: center;
            padding: 40px;
        }
        h1 {
            font-size: 2.2em;
            color: #3A006B;
        }
        input {
            padding: 10px;
            border-radius: 12px;
            border: none;
            width: 80%%;
            max-width: 300px;
            margin: 10px;
            text-align: center;
            font-size: 1.1em;
        }
        button {
            background: #3A006B;
            color: white;
            border: none;
            border-radius: 15px;
            padding: 12px 25px;
            font-size: 1em;
            margin-top: 10px;
            cursor: pointer;
            transition: 0.2s;
        }
        button:hover {
            background: #5E17EB;
        }
        .box {
            background: white;
            border-radius: 25px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            padding: 30px;
            margin: auto;
            max-width: 400px;
        }
        .fade-in {
            animation: fadein 0.8s ease-in-out;
        }
        @keyframes fadein {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
<div class="box fade-in">
    {% if step == "start" %}
        <h1>Secret Splashin 💦</h1>
        <p>Ajoute le prénom de chaque joueur :</p>
        <form action="{{ url_for('add_player') }}" method="post">
            <input type="text" name="player_name" placeholder="Ex : Korëntin" required>
            <br>
            <button type="submit">Ajouter</button>
        </form>
        {% if players %}
            <h3>Joueurs inscrits :</h3>
            <p>{{ ", ".join(players) }}</p>
            <form action="{{ url_for('launch_game') }}" method="post">
                <button type="submit">🎯 Lancer la distribution</button>
            </form>
        {% endif %}
    {% elif step == "target" %}
        <h1>👀 Salut {{ player }} !</h1>
        <p>Ta cible est :</p>
        <h2 style="color:#5E17EB;">{{ target }}</h2>
        <form action="{{ url_for('next_player') }}" method="post">
            <button type="submit">OK, suivant</button>
        </form>
    {% elif step == "done" %}
        <h1>✅ Tous les joueurs ont reçu leur cible !</h1>
        <p>Le jeu Secret Splashin peut commencer 🎉</p>
    {% endif %}
</div>
</body>
</html>
"""

# Variables globales
players = []
targets = []
current_index = 0

@app.route('/', methods=['GET'])
def home():
    global players
    return render_template_string(html_template, step="start", players=players)

@app.route('/add', methods=['POST'])
def add_player():
    global players
    name = request.form['player_name'].strip()
    if name and name not in players:
        players.append(name)
    return redirect(url_for('home'))

@app.route('/launch', methods=['POST'])
def launch_game():
    global players, targets, current_index
    if len(players) < 2:
        return "Il faut au moins deux joueurs pour jouer 😅"
    
    shuffled = players[:]
    random.shuffle(shuffled)
    
    # Empêche qu'un joueur tombe sur lui-même
    for i in range(len(shuffled)):
        if shuffled[i] == players[i]:
            random.shuffle(shuffled)
            break

    targets = list(zip(players, shuffled))
    current_index = 0
    return redirect(url_for('show_target'))

@app.route('/target', methods=['GET'])
def show_target():
    global current_index
    if current_index < len(targets):
        player, target = targets[current_index]
        return render_template_string(html_template, step="target", player=player, target=target)
    else:
        return render_template_string(html_template, step="done")

@app.route('/next', methods=['POST'])
def next_player():
    global current_index
    current_index += 1
    return redirect(url_for('show_target'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
