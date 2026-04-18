# lead-enrichment-pipeline

Flask webhook pipeline that enriches inbound leads using the Hunter.io domain search API (or a mock fallback) and stores results in SQLite.

## Features

- Reads lead list from `sample_leads.csv`
- Enriches with Hunter.io domain search API
- Falls back to mock enrichment when API key is missing
- Stores enriched leads in SQLite (`leads.db`)
- Webhook endpoint: `POST /enrich`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
python app.py
```

Then POST to `http://localhost:5000/enrich`

## Environment Variables

- `HUNTER_API_KEY` (optional)
- `DB_PATH` (default `leads.db`)
```

