from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import markdown2
import os
import hvac
import signal
import sys
import subprocess
from dotenv import load_dotenv
import atexit

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

def start_vault():
    try:
        # Start vault using the manager script
        subprocess.run(['./vault_manager.sh', 'start'], check=True)
        print("Vault started successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error starting Vault: {e}")
        sys.exit(1)

def stop_vault():
    try:
        subprocess.run(['./vault_manager.sh', 'stop'], check=True)
        print("Vault stopped successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error stopping Vault: {e}")

# Initialize Vault client with error handling and auto-unsealing
def initialize_vault():
    try:
        client = hvac.Client(
            url=os.getenv('VAULT_ADDR'),
            token=os.getenv('VAULT_TOKEN')
        )
        
        # Check if Vault needs to be unsealed
        if client.sys.is_sealed():
            print("Vault is sealed. Attempting to unseal...")
            try:
                # Read unseal key from init file
                with open('vault/init.txt', 'r') as f:
                    init_data = f.read()
                    unseal_key = next(line.split(': ')[1] for line in init_data.split('\n') if 'Unseal Key 1' in line)
                
                # Unseal vault
                client.sys.submit_unseal_key(unseal_key)
                print("Vault unsealed successfully")
            except Exception as e:
                print(f"Error unsealing Vault: {str(e)}")
                return None
        
        # Verify connection
        if client.sys.is_initialized() and not client.sys.is_sealed():
            print("Connected to Vault successfully")
            print(f"Root Token: {os.getenv('VAULT_TOKEN')}")
            print(f"UI available at: {os.getenv('VAULT_ADDR')}/ui")
            return client
        else:
            print("Warning: Vault is not properly initialized")
            return None
            
    except Exception as e:
        print(f"Error connecting to Vault: {str(e)}")
        print("Warning: Proceeding without Vault connection")
        return None

# Start Vault when Flask starts
start_vault()
vault_client = initialize_vault()

# Register cleanup on Flask shutdown
atexit.register(stop_vault)

# Database Models
class GitRepo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(200), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    username = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Git Repo routes
@app.route('/repos', methods=['GET'])
def list_repos():
    repos = GitRepo.query.all()
    return render_template('repos/index.html', repos=repos)

@app.route('/repos/new', methods=['GET', 'POST'])
def new_repo():
    if request.method == 'POST':
        repo = GitRepo(
            name=request.form['name'],
            url=request.form['url'],
            description=request.form['description']
        )
        db.session.add(repo)
        db.session.commit()
        return redirect(url_for('list_repos'))
    return render_template('repos/new.html')

# Host routes
@app.route('/hosts', methods=['GET'])
def list_hosts():
    hosts = Host.query.all()
    return render_template('hosts/index.html', hosts=hosts)

@app.route('/hosts/new', methods=['GET', 'POST'])
def new_host():
    if request.method == 'POST':
        host = Host(
            hostname=request.form['hostname'],
            ip_address=request.form['ip_address'],
            username=request.form['username'],
            description=request.form['description']
        )
        db.session.add(host)
        db.session.commit()
        return redirect(url_for('list_hosts'))
    return render_template('hosts/new.html')

# Notes routes
@app.route('/notes', methods=['GET'])
def list_notes():
    notes = Note.query.all()
    return render_template('notes/index.html', notes=notes)

@app.route('/notes/new', methods=['GET', 'POST'])
def new_note():
    if request.method == 'POST':
        note = Note(
            title=request.form['title'],
            content=request.form['content']
        )
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('list_notes'))
    return render_template('notes/new.html')

@app.route('/notes/<int:id>', methods=['GET'])
def view_note(id):
    note = Note.query.get_or_404(id)
    html_content = markdown2.markdown(note.content, extras=["fenced-code-blocks", "tables", "mermaid"])
    return render_template('notes/view.html', note=note, html_content=html_content)

@app.route('/notes/<int:id>/edit', methods=['GET', 'POST'])
def edit_note(id):
    note = Note.query.get_or_404(id)
    if request.method == 'POST':
        note.title = request.form['title']
        note.content = request.form['content']
        db.session.commit()
        return redirect(url_for('view_note', id=note.id))
    return render_template('notes/edit.html', note=note)

@app.route('/notes/<int:id>/delete', methods=['POST'])
def delete_note(id):
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('list_notes'))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    notes = Note.query.filter(
        (Note.title.ilike(f'%{query}%')) | 
        (Note.content.ilike(f'%{query}%'))
    ).all()
    return render_template('search.html', notes=notes, query=query)

def signal_handler(sig, frame):
    print('\nShutting down...')
    if vault_client:
        print('Closing Vault client connection...')
        vault_client.adapter.session.close()
        print('Vault client connection closed.')
    stop_vault()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    app.run(host='127.0.0.1', port=5010)
