import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
import os

load_dotenv()

# Environment variables
advance = os.getenv("HighLevelSecurityCode")
mainpass = os.getenv("mainpass")

# File for storing codes and rules
DATA_FILE = 'data.json'

# Load data from JSON or create defaults if file does not exist
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        default_data = {
            "high_codes": ["0001", "0002", "00004", "0005"],
            "medium_codes": ["1234", "2345", "3456"],
            "low_codes": ["4444", "4445", "4446"],
            "rules": {
                "high": {"disable_alarms": False, "unlock_bolt": False},
                "medium": {"disable_alarms": False, "unlock_bolt": False},
                "low": {"disable_alarms": False, "unlock_bolt": False},
            },
        }
        save_data(default_data)
        return default_data

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Load initial data
data = load_data()

# Extract codes and rules
high_codes = data["high_codes"]
medium_codes = data["medium_codes"]
low_codes = data["low_codes"]
rules = data["rules"]

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('login'))
    return render_template('index.html', high_codes=high_codes, medium_codes=medium_codes, low_codes=low_codes, rules=rules)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == mainpass:
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            return "Invalid password", 403
    return '''
        <form method="POST">
            <label for="password">Enter Password:</label>
            <input type="password" name="password" id="password">
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.route('/update/rules', methods=['POST'])
def update_rules():
    if 'authenticated' not in session or not session['authenticated']:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    level = data.get('level')
    rules[level] = data['settings']
    save_data({"high_codes": high_codes, "medium_codes": medium_codes, "low_codes": low_codes, "rules": rules})
    return jsonify({"success": True, "rules": rules})

@app.route('/update/codes', methods=['POST'])
def update_codes():
    if 'authenticated' not in session or not session['authenticated']:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    global high_codes, medium_codes, low_codes
    high_codes = data.get('high', high_codes)
    medium_codes = data.get('medium', medium_codes)
    low_codes = data.get('low', low_codes)
    save_data({"high_codes": high_codes, "medium_codes": medium_codes, "low_codes": low_codes, "rules": rules})
    return jsonify({"success": True, "high": high_codes, "medium": medium_codes, "low": low_codes})

@app.route('/validate/code', methods=['POST'])
def validate_code():
    data = request.json
    code = data.get('code')

    if code == advance:
        return jsonify({"level": "advance", "rules": {"full_access": True}})
    elif code in high_codes:
        return jsonify({"level": "high", "rules": rules["high"]})
    elif code in medium_codes:
        return jsonify({"level": "medium", "rules": rules["medium"]})
    elif code in low_codes:
        return jsonify({"level": "low", "rules": rules["low"]})
    else:
        return jsonify({"error": "Invalid code"}), 404

if __name__ == '__main__':
    app.run(debug=True)
