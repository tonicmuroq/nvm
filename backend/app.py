from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
DB_PATH = 'anger.db'

# Add CORS headers to every response
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person TEXT,
                    timestamp TEXT,
                    content TEXT,
                    anger INTEGER
                )''')
    conn.commit()
    conn.close()

init_db()


def calc_anger(content):
    level = 1
    if not content:
        return level
    exclam = content.count('!')
    length = len(content)
    level = min(5, 1 + exclam + length // 50)
    return level


@app.route('/events', methods=['POST', 'OPTIONS'])
def add_event():
    if request.method == 'OPTIONS':
        # Preflight request
        return '', 204
    data = request.get_json()
    person = data.get('person')
    content = data.get('content')
    timestamp = data.get('timestamp') or datetime.utcnow().isoformat()
    anger = calc_anger(content)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO events (person, timestamp, content, anger) VALUES (?,?,?,?)',
              (person, timestamp, content, anger))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok', 'anger': anger})


@app.route('/events', methods=['GET', 'OPTIONS'])
def list_events():
    if request.method == 'OPTIONS':
        return '', 204
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, person, timestamp, content, anger FROM events ORDER BY timestamp DESC')
    rows = c.fetchall()
    conn.close()
    events = [{'id': r[0], 'person': r[1], 'timestamp': r[2], 'content': r[3], 'anger': r[4]} for r in rows]
    return jsonify(events)


@app.route('/summary', methods=['GET', 'OPTIONS'])
def summary():
    if request.method == 'OPTIONS':
        return '', 204
    date = request.args.get('date')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if date:
        start = date + ' 00:00:00'
        end = date + ' 23:59:59'
        c.execute('SELECT anger FROM events WHERE timestamp BETWEEN ? AND ?', (start, end))
    else:
        c.execute('SELECT anger FROM events')
    rows = c.fetchall()
    conn.close()
    total = sum(r[0] for r in rows)
    return jsonify({'total_anger': total, 'count': len(rows)})


@app.route('/scores', methods=['GET', 'OPTIONS'])
def scores():
    if request.method == 'OPTIONS':
        return '', 204
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT person, SUM(anger) as total FROM events GROUP BY person ORDER BY total DESC')
    rows = c.fetchall()
    conn.close()
    scores = []
    for person, score in rows:
        if score >= 20:
            grade = 'Arch Nemesis'
        elif score >= 10:
            grade = 'Enemy'
        elif score >=5:
            grade = 'Annoying'
        else:
            grade = 'Petty'
        scores.append({'person': person, 'score': score, 'grade': grade})
    return jsonify(scores)


@app.route('/filter', methods=['GET', 'OPTIONS'])
def filter_events():
    if request.method == 'OPTIONS':
        return '', 204
    start = request.args.get('start')
    end = request.args.get('end')
    level = request.args.get('level')
    q = 'SELECT person, anger FROM events WHERE 1=1'
    params = []
    if start:
        q += ' AND timestamp >= ?'
        params.append(start)
    if end:
        q += ' AND timestamp <= ?'
        params.append(end)
    if level:
        q += ' AND anger = ?'
        params.append(level)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(q, params)
    rows = c.fetchall()
    conn.close()
    result = [{'person': r[0], 'anger': r[1]} for r in rows]
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
