import os
import csv
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import requests
from flask import Flask, jsonify

load_dotenv()

DB_PATH = os.getenv('DB_PATH', 'leads.db')
HUNTER_API_KEY = os.getenv('HUNTER_API_KEY')
HUNTER_API_URL = 'https://api.hunter.io/v2/domain-search'

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            company TEXT,
            domain TEXT,
            email TEXT,
            confidence INTEGER,
            enriched_at TEXT,
            UNIQUE(name, company, domain)
        )
        '''
    )
    conn.commit()
    conn.close()


def read_leads(path='sample_leads.csv'):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def enrich_lead(lead):
    if not HUNTER_API_KEY:
        return {
            'email': f"info@{lead['domain']}",
            'confidence': 55,
        }

    response = requests.get(
        HUNTER_API_URL,
        params={'domain': lead['domain'], 'api_key': HUNTER_API_KEY},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json().get('data', {})
    emails = data.get('emails', [])
    if not emails:
        return {'email': None, 'confidence': 0}

    best = max(emails, key=lambda e: e.get('confidence', 0))
    return {
        'email': best.get('value'),
        'confidence': best.get('confidence', 0),
    }


def upsert_lead(conn, lead, enrichment):
    cur = conn.cursor()
    cur.execute(
        '''
        INSERT INTO leads (name, company, domain, email, confidence, enriched_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(name, company, domain)
        DO UPDATE SET email=excluded.email, confidence=excluded.confidence, enriched_at=excluded.enriched_at
        ''',
        (
            lead['name'],
            lead['company'],
            lead['domain'],
            enrichment.get('email'),
            enrichment.get('confidence'),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()


def run_pipeline():
    init_db()
    leads = read_leads()
    conn = sqlite3.connect(DB_PATH)

    results = []
    for lead in leads:
        enrichment = enrich_lead(lead)
        upsert_lead(conn, lead, enrichment)
        results.append({**lead, **enrichment})

    conn.close()
    return results


@app.route('/enrich', methods=['POST'])
def enrich_endpoint():
    results = run_pipeline()
    return jsonify({'count': len(results), 'results': results})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
