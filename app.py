import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for, abort, session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY', 'default_secret_key_change_me')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'mypassword')
API_TOKEN = os.getenv('API_TOKEN', 'mypassword')
# Persistence configuration
# In Docker/Fly.io, we mount a volume at /data
if os.path.exists('/data'):
    STORAGE_FILE = '/data/data.json'
else:
    STORAGE_FILE = os.getenv('STORAGE_FILE', 'data.json')

# Base Stage Data (Configuration)
# In a larger app, this would be in a database
STAGES_CONFIG = {
    "1 - Partenza": {
        "start": "13:45 (Ritrovo)", 
        "end": "14:00 (Partenza)",
        "luogo": "Campo di calcio Avegno",
        "default_unlocked": True
    },
    "2 - Antipasto": {
        "start": "14:45", 
        "end": "15:30",
        "cibo": ["Minestrone 🍲", "Pane 🍞", "Formaggio grattuggiato 🧀"], 
        "bevande": ["La Murata (Merlot - Ghidossi) 🍷", "Birra Feldschlösschen 🍺", "Soft drinks 🥤"],
        "hosts": ["Valeria", "Luigi"],
        "unlock_time": "2025-04-26T14:45:00",
        "luogo": "Casa Rossa"
    },
    "3 - Snack": {
        "start": "15:45", 
        "end": "16:30",
        "cibo": ["Torte salate 🥧"], 
        "bevande": ["Prosecco 🍾", "Vino bianco (Pralis) 🥂", "Birra Moretti 🍺", "Soft drinks 🥤"],
        "hosts": ["Albina", "Paola"],
        "unlock_time": "2025-04-26T15:45:00",
        "luogo": "Grotti Vinzott"
    },
    "4 - Aperitivo": {
        "start": "16:45", 
        "end": "18:15",
        "cibo": ["Arrosticini 🍢🍖", "Formaggi 🧀", "Chips 🍟"], 
        "bevande": ["Aperol/Campari Spritz 🍹", "Vino bianco (Pralis) 🥂", "Birra Feldschlosschen 🍺", "Soft drinks 🥤"],
        "hosts": ["Luigi", "Alle", "Valeria"],
        "unlock_time": "2025-04-26T16:45:00",
        "luogo": "Balomina"
    },
    "5 - Cena": {
        "start": "18:30",
        "end": "01:00 (Fine)",
        "cibo": ["Polenta 🍛", "Spezzatino di manzo 🍖", "Gorgonzola 🧀", "Leftovers 🍱", "Torta 🎂"],
        "bevande": ["Nuwanda (Barbera D'Asti - BelColle) 🍷", "Soft drinks 🥤", "Git Tonic 🧊", "Leftovers 🥂"],
        "hosts": ["Gabriele"],
        "unlock_time": "2025-04-26T18:30:00",
        "luogo": "Sala parrocchiale"
    }
}

# Threshold for showing the full QR code
EVENT_THRESHOLD = datetime(2025, 4, 26, 13, 30)

def load_state():
    """Load the manual unlock state from disk."""
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r') as f:
                content = json.load(f)
                # Migration: if old format (list), convert to new format (dict)
                if isinstance(content.get("unlocked_stages"), list):
                    overrides = {stage_id: True for stage_id in content["unlocked_stages"]}
                    return {"overrides": overrides}
                return content
        except (json.JSONDecodeError, IOError):
            return {"overrides": {}}
    return {"overrides": {}}

def save_state(state):
    """Save the manual unlock state to disk."""
    with open(STORAGE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def get_current_stages():
    """Compute current stage state based on manual overrides, then automatic logic."""
    now = datetime.now()
    state = load_state()
    overrides = state.get("overrides", {})
    
    current_stages = {}
    for stage_id, data in STAGES_CONFIG.items():
        stage = data.copy()
        
        # Priority 1: Manual Override
        if stage_id in overrides:
            stage["unlocked"] = overrides[stage_id]
        else:
            # Priority 2: Automatic Logic
            is_default = stage.get("default_unlocked", False)
            unlocked_by_time = False
            if "unlock_time" in stage:
                try:
                    unlock_time = datetime.fromisoformat(stage["unlock_time"])
                    unlocked_by_time = now >= unlock_time
                except ValueError:
                    pass
            stage["unlocked"] = is_default or unlocked_by_time
            
        current_stages[stage_id] = stage
        
    return current_stages

@app.route('/')
def index():
    now = datetime.now()
    show_full_qr = now >= EVENT_THRESHOLD
    return render_template('index.html', show_full_qr=show_full_qr)

@app.route('/api/tappe')
def get_tappe():
    token = request.headers.get('X-API-TOKEN')
    if token != API_TOKEN:
        abort(403)
    
    return jsonify(get_current_stages())

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('admin_login.html', error="Password errata")

    if not session.get('logged_in'):
        return render_template('admin_login.html')

    return render_template('admin_panel.html', tappe=get_current_stages())

@app.route('/admin/unlock/<path:stage_id>', methods=['POST'])
def unlock_stage(stage_id):
    if not session.get('logged_in'):
        abort(401)
        
    state = load_state()
    state.setdefault("overrides", {})[stage_id] = True
    save_state(state)
        
    return redirect(url_for('admin'))

@app.route('/admin/lock/<path:stage_id>', methods=['POST'])
def lock_stage(stage_id):
    if not session.get('logged_in'):
        abort(401)
        
    state = load_state()
    state.setdefault("overrides", {})[stage_id] = False
    save_state(state)
        
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    # Get port from environment or use default 5000
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)
