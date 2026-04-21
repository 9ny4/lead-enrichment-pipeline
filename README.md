# lead-enrichment-pipeline

Turn inbound leads into usable contacts automatically, so sales can follow up faster without manual research.
Enrich leads with Hunter.io and persist the results in SQLite for a lightweight pipeline that’s easy to run and demo.

## How It Works

1. Webhook receives lead
2. Hunter.io enriches it
3. SQLite stores the result

## Demo

Screenshot coming soon

## Features

- Reads lead list from `sample_leads.csv`
- Enriches with Hunter.io domain search API
- Falls back to mock enrichment when API key is missing
- Stores enriched leads in SQLite (`leads.db`)
- Tracks enrichment confidence scores
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

