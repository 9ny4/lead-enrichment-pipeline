import os
import sqlite3
from app import enrich_lead, init_db, upsert_lead


def test_mock_enrichment_fallback(monkeypatch):
    monkeypatch.setenv('HUNTER_API_KEY', '')
    lead = {'name': 'Test User', 'company': 'Test Co', 'domain': 'example.com'}
    result = enrich_lead(lead)
    assert result['email'] == 'info@example.com'
    assert result['confidence'] == 55


def test_upsert_deduplication(tmp_path):
    db_path = tmp_path / 'leads.db'
    monkeypatch = None
    os.environ['DB_PATH'] = str(db_path)
    init_db()

    conn = sqlite3.connect(db_path)
    lead = {'name': 'Test User', 'company': 'Test Co', 'domain': 'example.com'}
    enrichment = {'email': 'a@example.com', 'confidence': 90}

    upsert_lead(conn, lead, enrichment)
    upsert_lead(conn, lead, {'email': 'b@example.com', 'confidence': 80})

    cur = conn.cursor()
    cur.execute('SELECT COUNT(*), email FROM leads')
    count, email = cur.fetchone()
    conn.close()

    assert count == 1
    assert email == 'b@example.com'
