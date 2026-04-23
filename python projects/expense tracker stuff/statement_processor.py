"""
statement_processor.py
----------------------
Pure processing logic for bank statement CSV/PDF files.
Accepts file bytes (no local filesystem paths) and returns
structured DataFrames instead of printing output.
"""

import io
import re
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS = {
    'groceries':      ['grocery', 'supermarket', 'market', 'aldi', 'walmart', 'target', 'winn-dixi', 'publix'],
    'dining':         ['taco', 'starbucks', 'restaurant', 'cafe', 'coffee', 'pizza', 'diner', 'doordash', 'uber eats', "mcdonald's"],
    'entertainment':  ['netflix', 'audible', 'spotify', 'hulu', 'cinema', 'movie', 'game'],
    'hobbies/crafts': ['staples', 'goodwill', 'fabric', 'craft', 'yarn', 'hobbylobb', 'sewing', 'studio', 'etsy', 'dollartre', 'dollar'],
    'transport':      ['uber', 'lyft', 'gas', 'fuel', 'shell', 'exxon', 'wawa', '7-eleven', 'racetrac', 'e-pass', 'toll', 'parking'],
    'utilities':      ['electric', 'water', 'internet', 'phone', 'utility'],
    'shopping':       ['amazon', 'store', 'shop', 'purchase', 'afterpay'],
    'health':         ['pharmacy', 'doctor', 'medical', 'clinic', 'fitness', 'gym'],
    'deposit':        ['deposit', 'payroll', 'direct deposit', 'refund'],
}

MERCHANT_CATEGORY_RULES = {
    'aldi': 'groceries',
    'amazon': 'shopping',
    'audible': 'entertainment',
    'afterpay': 'shopping',
    'cafe': 'dining',
    'doordash': 'dining',
    'etsy': 'hobbies/crafts',
    'exxon': 'transport',
    'goodwill': 'hobbies/crafts',
    'gym': 'health',
    'hobby lobby': 'hobbies/crafts',
    'hulu': 'entertainment',
    'lyft': 'transport',
    'mcdonalds': 'dining',
    'netflix': 'entertainment',
    'payroll': 'deposit',
    'pharmacy': 'health',
    'publix': 'groceries',
    'racetrac': 'transport',
    'shell': 'transport',
    'spotify': 'entertainment',
    'staples': 'hobbies/crafts',
    'starbucks': 'dining',
    'target': 'groceries',
    'uber eats': 'dining',
    'uber': 'transport',
    'walmart': 'groceries',
    'wawa': 'transport',
}

BANK_NOISE_PATTERNS = ['www.fairwinds.org', 'fairwinds']


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def infer_category(description):
    text = _normalize_merchant_text(description)

    for merchant, category in MERCHANT_CATEGORY_RULES.items():
        if merchant in text:
            return category

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category
    return 'other'


def _normalize_merchant_text(description):
    """Normalize transaction text so merchant-name matching is more reliable."""
    text = str(description).lower().strip()

    # Remove common payment-channel prefixes and noise that obscure merchant names.
    text = re.sub(r'\b(pos|debit|credit|purchase|checkcard|deposit|withdrawal|payment|ach)\b', ' ', text)
    text = re.sub(r'\b(card\s*\d+|ref\s*#?\w+|trace\s*#?\w+)\b', ' ', text)

    # Remove store numbers / ids like #1234 or trailing long digit groups.
    text = re.sub(r'#\d+', ' ', text)
    text = re.sub(r'\b\d{3,}\b', ' ', text)

    # Keep letters, spaces, apostrophes and ampersands; collapse punctuation and whitespace.
    text = text.replace("'", "")
    text = re.sub(r'[^a-z&\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _looks_like_header(value):
    s = str(value).strip()
    has_date   = bool(re.match(r'^\d{2}/\d{2}', s))
    has_amount = bool(re.search(r'[+-]?\d+\.\d{2}\s*$', s))
    return not has_date and not has_amount


def _load_csv_bytes(file_bytes: bytes):
    peek      = pd.read_csv(io.BytesIO(file_bytes), nrows=0)
    first_col = peek.columns[0] if len(peek.columns) > 0 else ''
    if _looks_like_header(first_col):
        df = pd.read_csv(io.BytesIO(file_bytes))
        return df, []
    df = pd.read_csv(io.BytesIO(file_bytes), header=None)
    df.columns = [f'col_{i}' for i in range(len(df.columns))]
    return df, ['No header row detected — generic column names assigned.']


def _load_pdf_bytes(file_bytes: bytes):
    try:
        import pdfplumber
    except ImportError:
        raise ImportError('pdfplumber is required for PDF support. Run: pip install pdfplumber')

    rows = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                rows.extend(table)

    if not rows:
        raise ValueError('No table data found in the PDF. The statement layout may not be supported.')

    header = [str(h) if h is not None else f'col_{i}' for i, h in enumerate(rows[0])]
    df = pd.DataFrame(rows[1:], columns=header)
    return df, ['PDF converted to table data.']


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load(file_bytes: bytes, filename: str):
    """Parse raw uploaded bytes into a DataFrame. Returns (df, warnings)."""
    name = filename.lower()
    if name.endswith('.csv'):
        return _load_csv_bytes(file_bytes)
    if name.endswith('.pdf'):
        return _load_pdf_bytes(file_bytes)
    raise ValueError(f'Unsupported file type: {filename}. Please upload a .csv or .pdf file.')


def normalize(df: pd.DataFrame):
    """
    Clean raw DataFrame and ensure category/amount/description columns exist.
    Returns (cleaned_df, cat_col, amount_col, desc_col, warnings).
    """
    warnings = []
    df = df.copy()

    # Remove bank portal noise rows
    noise_mask = df.astype(str).apply(
        lambda col: col.str.contains('|'.join(BANK_NOISE_PATTERNS), case=False, na=False)
    ).any(axis=1)
    removed = int(noise_mask.sum())
    if removed:
        df = df[~noise_mask].reset_index(drop=True)
        warnings.append(f'Removed {removed} rows containing bank portal noise.')

    cat_col    = None
    desc_col   = None
    amount_col = None

    for col in df.columns:
        col_l = str(col).lower()
        if 'category' in col_l and cat_col is None:
            cat_col = col
        if amount_col is None and any(k in col_l for k in ('amount', 'debit', 'credit')):
            amount_col = col
        if desc_col is None and any(k in col_l for k in ('description', 'desc', 'memo', 'transaction', 'name')):
            desc_col = col

    # One-column fallback
    if cat_col is None and len(df.columns) == 1:
        only_col = df.columns[0]
        df['description']       = df[only_col].astype(str)
        df['amount']            = pd.to_numeric(
            df['description'].str.extract(r'([+-]?\d+\.\d{2})\s*$')[0], errors='coerce'
        )
        df['inferred_category'] = df['description'].apply(infer_category)
        cat_col    = 'inferred_category'
        desc_col   = 'description'
        amount_col = 'amount'
        warnings.append('One-column file detected — categories inferred from description text.')

    # Multi-column fallback: no explicit category column
    if cat_col is None:
        fallback_desc = desc_col if desc_col is not None else df.columns[0]
        df['inferred_category'] = df[fallback_desc].apply(infer_category)
        cat_col  = 'inferred_category'
        desc_col = fallback_desc
        warnings.append(f'No category column found — categories inferred from "{desc_col}".')

    if desc_col is None:
        desc_col = df.columns[0]

    if amount_col is not None:
        df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce')

    df = df.reset_index(drop=True)
    return df, cat_col, amount_col, desc_col, warnings


def filter_categories(df: pd.DataFrame, cat_col: str, exclude: list):
    """Return df with rows whose category is in `exclude` removed."""
    if not exclude:
        return df.copy()
    excluded = {c.lower() for c in exclude}
    return df[~df[cat_col].astype(str).str.lower().isin(excluded)].copy()


def build_summary(df: pd.DataFrame, cat_col: str, amount_col):
    """Aggregate by category. Returns a summary DataFrame."""
    if amount_col is not None:
        summary = (
            df.groupby(cat_col, sort=False)
            .agg(
                **{
                    'Transaction Count': (cat_col, 'count'),
                    'Total Amount':      (amount_col, lambda x: pd.to_numeric(x, errors='coerce').sum()),
                }
            )
            .reset_index()
            .rename(columns={cat_col: 'Category'})
            .sort_values('Total Amount', ascending=False)
            .reset_index(drop=True)
        )
    else:
        summary = df[cat_col].value_counts().reset_index()
        summary.columns = ['Category', 'Transaction Count']
    return summary
