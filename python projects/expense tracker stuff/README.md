# Expense Tracker Stuff

This project is a small FastAPI tool for uploading bank statements, normalizing transactions, filtering categories, and downloading results.

- `app.py` runs the web app.
- `statement_processor.py` contains the parsing and normalization logic.
- `templates/` contains the HTML templates.
- `notebooks/` contains scratch notebooks for processor development and experiments.

Run locally from this folder with `python -m uvicorn app:app --reload`.