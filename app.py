from flask import Flask, render_template, jsonify, request, redirect, url_for, abort, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'XRpX9lXBsg2cb9i5MKkntthZmgVNRMt6' 
API_SECRET = 'mypassword'

# Stato iniziale delle tappe (bloccate)
detailed_tappe = {
    "1 - Partenza": {
        "default": True,
        "unlocked": True, 
        "start": "13:45 (Ritrovo)", 
        "end": "14:00 (Partenza)",
        "luogo": "Campo di calcio Avegno"
    },
    "2 - Antipasto": {
        "unlocked": False, 
        "start": "14:45", 
        "end": "15:30",
        "cibo": ["Minestrone 🍲",
                 "Pane 🍞",
                 "Formaggio grattuggiato 🧀"], 
        "bevande": ["La Murata (Merlot - Ghidossi) 🍷",
                    "Birra Feldschlösschen 🍺",
                    "Soft drinks 🥤"],
        "hosts": ["Valeria", "Luigi"],
        "unlock_time": "2025-04-26T14:45:00",
        "luogo": "Casa Rossa"
        },
    "3 - Snack": {
        "unlocked": False, 
        "start": "15:45", 
        "end": "16:30",
        "cibo": ["Torte salate 🥧"], 
        "bevande": ["Prosecco 🍾",
                    "Vino bianco (Pralis) 🥂",
                    "Birra Moretti 🍺",
                    "Soft drinks 🥤"],
        "hosts": ["Albina", "Paola"],
        "unlock_time": "2025-04-26T15:45:00",
        "luogo": "Grotti Vinzott"
        },
    "4 - Aperitivo": {
        "unlocked": False, 
        "start": "16:45", 
        "end": "18:15",
        "cibo": ["Arrosticini 🍢🍖",
                 "Formaggi 🧀",
                 "Chips 🍟"], 
        "bevande": ["Aperol/Campari Spritz 🍹",
                    "Vino bianco (Pralis) 🥂",
                    "Birra Feldschlosschen 🍺",
                    "Soft drinks 🥤"],
        "hosts": ["Luigi", "Alle", "Valeria"],
        "unlock_time": "2025-04-26T16:45:00",
        "luogo": "Balomina"
        },
    "5 - Cena": {
        "unlocked": False,
        "start": "18:30",
        "end": "01:00 (Fine)",
        "cibo": ["Polenta 🍛",
                 "Spezzatino di manzo 🍖",
                 "Gorgonzola 🧀",
                 "Leftovers 🍱",
                 "Torta 🎂"],
        "bevande": ["Nuwanda (Barbera D'Asti - BelColle) 🍷",
                    "Soft drinks 🥤",
                    "Git Tonic 🧊",
                    "Leftovers 🥂"],
        "hosts": ["Gabriele"],
        "unlock_time": "2025-04-26T18:30:00",
        "luogo": "Sala parrocchiale"
    }
}

preview_tappe = {
    "1 - Partenza": {
        "default": True,
        "unlocked": True, 
        "start": "13:45 (Ritrovo)", 
        "end": "14:00 (Partenza)",
        "hosts": [],
        "luogo": "Campo di calcio Avegno"
    },
    "2 - Antipasto": {
        "unlocked": False, 
        "start": "14:45", 
        "end": "15:30",
        "cibo": [], 
        "bevande": [],
        "hosts": [],
        "luogo": ""
        },
    "3 - Snack": {
        "unlocked": False, 
        "start": "15:45", 
        "end": "16:30",
        "cibo": [], 
        "bevande": [],
        "hosts": [],
        "luogo": ""
        },
    "4 - Aperitivo": {
        "unlocked": False, 
        "start": "16:45", 
        "end": "18:15",
        "cibo": [], 
        "bevande": [],
        "hosts": [],
        "luogo": ""
        },
    "5 - Cena": {
        "unlocked": False,
        "start": "18:30",
        "end": "01:00 (Fine)",
        "cibo": [],
        "bevande": [],
        "hosts": [],
        "luogo": ""
    }
}

event_threshold = datetime(2025, 4, 26, 13, 30)
# Conditional assignment
now = datetime.now()

tappe = detailed_tappe

@app.route('/')
def index():
    now = datetime.now()
    show_full_qr = now >= event_threshold
    return render_template('index.html', show_full_qr=show_full_qr)

@app.route('/api/tappe')
def get_tappe():
    token = request.headers.get('X-API-TOKEN')
    if token != API_SECRET:
        abort(403)
    now = datetime.now()

    updated_tappe = {}
    for id, tappa in tappe.items():
        tappa_copy = tappa.copy()

        unlock_time_str = tappa.get("unlock_time")
        if unlock_time_str:
            unlock_time = datetime.fromisoformat(unlock_time_str)
            # Unlock if the current time has passed unlock time
            if now >= unlock_time:
                tappa_copy["unlocked"] = True

        updated_tappe[id] = tappa_copy

    return jsonify(updated_tappe)

@app.route('/unlock/<tappa_id>', methods=['POST'])
def unlock_tappa(tappa_id):
    if tappa_id in tappe:
        tappe[tappa_id]["unlocked"] = True
        return redirect(url_for('admin'))  # Torna al pannello admin
    return "Tappa non trovata", 404

@app.route('/lock/<tappa_id>', methods=['POST'])
def lock_tappa(tappa_id):
    if tappa_id in tappe:
        tappe[tappa_id]["unlocked"] = False
        return redirect(url_for('admin'))
    return "Tappa non trovata", 404


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # If the user is already logged in, skip the password check
    if 'logged_in' in session and session['logged_in']:
        return render_template('admin_panel.html', tappe=tappe)

    if request.method == 'POST':
        password = request.form.get('password')
        if password == API_SECRET:
            # Set a session variable to indicate the user is logged in
            session['logged_in'] = True
            return render_template('admin_panel.html', tappe=tappe)
        else:
            return render_template('admin_login.html', error="Password errata")

    return render_template('admin_login.html')


@app.route('/logout')
def logout():
    # Clear the session and redirect to login
    session.clear()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
