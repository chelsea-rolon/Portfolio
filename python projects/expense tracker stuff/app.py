"""
app.py  —  Bank Statement Processor web app
Run with:  uvicorn app:app --reload --app-dir "python projects"
Or simply: python -m uvicorn app:app --reload
"""

import io
import json
import os
import sys

import pandas as pd
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from statement_processor import (
    build_summary,
    filter_categories,
    load,
    normalize,
)

app = FastAPI(title="Bank Statement Processor")

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
templates  = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# ---------------------------------------------------------------------------
# In-memory session store (single-user local tool — no auth needed)
# ---------------------------------------------------------------------------
_session: dict = {}


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame to JSON-safe list of dicts."""
    return json.loads(df.to_json(orient="records", date_format="iso"))


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """Parse and normalise an uploaded CSV or PDF. Returns table data + categories."""
    file_bytes = await file.read()

    try:
        raw_df, load_warnings = load(file_bytes, file.filename)
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)

    try:
        cleaned_df, cat_col, amount_col, desc_col, norm_warnings = normalize(raw_df)
    except Exception as exc:
        return JSONResponse({"error": f"Normalisation failed: {exc}"}, status_code=400)

    # Persist processed data in memory for filter/download calls
    _session["cleaned_df"]  = cleaned_df
    _session["cat_col"]     = cat_col
    _session["amount_col"]  = amount_col
    _session["desc_col"]    = desc_col
    _session["filename"]    = file.filename

    categories = sorted(cleaned_df[cat_col].dropna().astype(str).unique().tolist())

    return JSONResponse({
        "warnings":   load_warnings + norm_warnings,
        "categories": categories,
        "columns":    list(cleaned_df.columns),
        "rows":       _df_to_records(cleaned_df),
        "total_rows": len(cleaned_df),
    })


@app.post("/filter")
async def filter_data(payload: Request):
    """Apply category exclusions and return filtered rows + summary."""
    if "cleaned_df" not in _session:
        return JSONResponse({"error": "No file uploaded yet."}, status_code=400)

    body    = await payload.json()
    exclude = body.get("exclude", [])

    cleaned_df = _session["cleaned_df"]
    cat_col    = _session["cat_col"]
    amount_col = _session["amount_col"]

    filtered_df = filter_categories(cleaned_df, cat_col, exclude)
    summary_df  = build_summary(filtered_df, cat_col, amount_col)

    grand_total = None
    if amount_col is not None:
        grand_total = round(float(pd.to_numeric(filtered_df[amount_col], errors="coerce").sum()), 2)

    _session["filtered_df"] = filtered_df
    _session["summary_df"]  = summary_df

    return JSONResponse({
        "rows":        _df_to_records(filtered_df),
        "summary":     _df_to_records(summary_df),
        "grand_total": grand_total,
        "filtered_count": len(filtered_df),
    })


@app.get("/download/{which}")
async def download(which: str):
    """Stream a CSV download. `which` is one of: cleaned, filtered, summary."""
    mapping = {
        "cleaned":  ("cleaned_df",  "cleaned_transactions.csv"),
        "filtered": ("filtered_df", "filtered_transactions.csv"),
        "summary":  ("summary_df",  "category_totals.csv"),
    }
    if which not in mapping:
        return JSONResponse({"error": "Unknown download type."}, status_code=400)

    key, filename = mapping[which]
    if key not in _session:
        # filtered/summary may not exist yet — fall back to cleaned
        if key in ("filtered_df", "summary_df") and "cleaned_df" in _session:
            df = _session["cleaned_df"] if key == "filtered_df" else build_summary(
                _session["cleaned_df"], _session["cat_col"], _session["amount_col"]
            )
        else:
            return JSONResponse({"error": "No data available. Upload a file first."}, status_code=400)
    else:
        df = _session[key]

    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)

    return StreamingResponse(
        io.BytesIO(buf.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
