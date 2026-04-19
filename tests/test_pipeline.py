import sqlite3
import requests
from unittest.mock import patch, MagicMock
from app import enrich_lead, init_db, upsert_lead


def test_mock_enrichment_fallback(monkeypatch):
    monkeypatch.setenv('HUNTER_API_KEY', '')
    lead = {'name': 'Test User', 'company': 'Test Co', 'domain': 'example.com'}
    result = enrich_lead(lead)
    assert result['email'] == 'info@example.com'
    assert result['confidence'] == 55


def test_upsert_deduplication(tmp_path, monkeypatch):
    db_path = tmp_path / 'leads.db'
    monkeypatch.setenv('DB_PATH', str(db_path))
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


def test_enrich_lead_http_error_returns_empty(monkeypatch):
    """Hunter.io returning a non-2xx response must not raise; pipeline should continue."""
    monkeypatch.setenv('HUNTER_API_KEY', 'fake-key')

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        '429 Client Error: Too Many Requests'
    )

    with patch('app.requests.get', return_value=mock_response):
        lead = {'name': 'Test User', 'company': 'Test Co', 'domain': 'example.com'}
        result = enrich_lead(lead)

    assert result == {'email': None, 'confidence': 0}


def test_enrich_lead_connection_error_returns_empty(monkeypatch):
    """A network-level failure must not raise; pipeline should continue."""
    monkeypatch.setenv('HUNTER_API_KEY', 'fake-key')

    with patch('app.requests.get', side_effect=requests.exceptions.ConnectionError('unreachable')):
        lead = {'name': 'Test User', 'company': 'Test Co', 'domain': 'example.com'}
        result = enrich_lead(lead)

    assert result == {'email': None, 'confidence': 0}
