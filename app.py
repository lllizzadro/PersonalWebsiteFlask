from flask import Flask, render_template, redirect, url_for, request
from datetime import datetime, timezone
import sqlite3

app = Flask(__name__)

PROJECTS = [
    {
        'name': 'Personal Website',
        'description': 'Website to host personal content and projects.',
    },
    {
        'name': 'Music Generating Neural Network',
        'description': 'Generative Adversarial Network and Recurrent Neural Network that'
                       ' produced music after learning on MIDI data.',
    },
]


@app.route('/')
def home():
    return render_template('index.html', projects=PROJECTS)

@app.route('/guestbook')
def guestbook():
    db = get_db()
    entries = db.execute("SELECT * FROM guestbook ORDER BY timestamp DESC").fetchall()
    return render_template('guestbook.html', entries=entries)

@app.route('/guestbook', methods=['POST'])
def add_message():
    db = get_db()
    name = request.form['name']
    message = request.form['message']
    db.execute("INSERT INTO guestbook (name, message) VALUES (?, ?)", (name, message))
    db.commit()
    db.close()
    return redirect(url_for('guestbook'))

@app.route('/dice')
def dice():
    return render_template('dice.html')

@app.template_filter('prettydate')
def prettydate(timestamp):
    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    return dt.strftime('%b %d, %Y %I:%M %p')

@app.template_filter('isodate')
def isodate(timestamp):
    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    return dt.isoformat()

def get_db():
    db = sqlite3.connect('guestbook.db')
    db.row_factory = sqlite3.Row
    return db

def init_db(db):
    if db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='guestbook'").fetchone() is None:
        db.execute('CREATE TABLE guestbook (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, message TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
        db.commit()
    return

db = get_db()
init_db(db)
db.close()


        

if __name__ == '__main__':
    app.run(debug=True)
