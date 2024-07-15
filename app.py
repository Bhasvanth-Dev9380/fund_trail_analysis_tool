from flask import Flask, request, redirect, url_for, send_from_directory, render_template
import os
import subprocess
import threading
import pandas as pd

UPLOAD_FOLDER = 'uploads'
RETRIEVE_FOLDER = 'retrieved'
RETRIEVED_FILE = 'retrieved_transactions.csv'
VENV_PYTHON = r'.venv\Scripts\python.exe'  # Path to the virtual environment's Python executable
SCRIPT_PATH = r'D:\fund_trail_analysis\pythonProject1\financial_fraud_dashboard4.py'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(RETRIEVE_FOLDER):
    os.makedirs(RETRIEVE_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def run_dash_app():
    try:
        subprocess.Popen([VENV_PYTHON, SCRIPT_PATH])
    except Exception as e:
        print(f"Failed to run the Dash app: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        process_file(filepath)
        return redirect(url_for('show_transactions'))

def process_file(filepath):
    result = subprocess.run(['node', 'script.js', filepath], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running script.js: {result.stderr}")
    else:
        print("Transaction successfully posted.")
        retrieved_file = os.path.join(RETRIEVE_FOLDER, RETRIEVED_FILE)
        if os.path.exists(retrieved_file):
            threading.Thread(target=run_dash_app).start()
        else:
            print("Retrieved file not found. Ensure that script.js correctly saves the file.")

@app.route('/transactions')
def show_transactions():
    transactions = None
    if os.path.exists(os.path.join(RETRIEVE_FOLDER, RETRIEVED_FILE)):
        transactions = pd.read_csv(os.path.join(RETRIEVE_FOLDER, RETRIEVED_FILE)).to_html()
    return render_template('transactions.html', transactions=transactions)

@app.route('/dashboard')
def dashboard():
    return redirect("http://localhost:8050")

if __name__ == '__main__':
    app.run(port=5000)
