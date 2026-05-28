# Webscraper Project

This folder now has two separate scripts:

- `scraper.py`: general-purpose web scraper (titles, links, selectors, crawl, CSV)
- `recipe_scraper.py`: recipe-only scraper for Allrecipes structured recipe data

General scraper features (`scraper.py`):

- Fetch one URL
- Print the page title
- Extract links
- Optionally scrape text from a CSS selector
- Save results as JSON
- Save summary results as CSV
- Crawl multiple pages by following links
- Retry failed requests with exponential backoff
- Add polite delay between requests
- Respect robots.txt by default

Recipe scraper features (`recipe_scraper.py`):

- Extract structured recipe details from Allrecipes pages
- Filter recipes by title keywords
- Crawl and collect multiple recipe pages

## Setup

1. Open a terminal in this folder.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic scrape (title + links)

```bash
python scraper.py https://example.com
```

### Scrape specific elements with a CSS selector

```bash
python scraper.py https://example.com --selector "h1"
```

### Save output to a file

```bash
python scraper.py https://example.com --output result.json
```

### Save CSV output

```bash
python scraper.py https://example.com --csv-output result.csv
```

### Crawl multiple pages (same domain)

```bash
python scraper.py https://example.com --crawl --max-pages 20 --output crawl.json
```

### Crawl with custom delay, retries, and backoff

```bash
python scraper.py https://example.com --crawl --delay 1.5 --retries 4 --backoff 2.0
```

### Crawl offsite links too

```bash
python scraper.py https://example.com --crawl --allow-offsite
```

### Skip robots.txt checks (not recommended)

```bash
python scraper.py https://example.com --ignore-robots
```

### General scraper (one page)

```bash
python scraper.py https://example.com --selector "h1" --output result.json
```

### Pull one Allrecipes recipe (structured fields)

```bash
python recipe_scraper.py "https://www.allrecipes.com/recipe/10813/best-chocolate-chip-cookies/" --output recipe.json
```

### Pull only certain Allrecipes recipes by keyword

```bash
python recipe_scraper.py "https://www.allrecipes.com/" --crawl --recipe-keyword chicken --recipe-keyword soup --max-pages 40 --output recipes.json --csv-output recipes.csv
```

This keeps recipes whose titles contain both keywords.

### Filter by ingredient content (recommended for ground beef)

```bash
python recipe_scraper.py "https://www.allrecipes.com/search?q=ground%20beef" --crawl --ingredient-keyword ground --ingredient-keyword beef --max-pages 80 --output groundbeef-recipes.json --csv-output groundbeef-recipes.csv
```

This keeps recipes whose ingredient lists contain both keywords.

### Browser-export workflow (copied links -> automatic scrape)

1. Copy recipe links from your browser search/results page.
2. Paste them into a text file, for example `copied-links.txt`.
3. Run:

```bash
python recipe_scraper.py --links-file copied-links.txt --ingredient-keyword ground --ingredient-keyword beef --output groundbeef-recipes.json --csv-output groundbeef-recipes.csv
```

You can also paste links directly through stdin:

```bash
Get-Content copied-links.txt | python recipe_scraper.py --links-stdin --ingredient-keyword ground --ingredient-keyword beef --output groundbeef-recipes.json --csv-output groundbeef-recipes.csv
```

The scraper will extract only valid Allrecipes recipe URLs from the pasted text and ignore duplicates.

## Key Options

- `--crawl`: follow links and scrape multiple pages
- `--max-pages`: limit number of pages in crawl mode (default: `10`)
- `--csv-output`: save summary rows as CSV
- `--delay`: delay between requests in seconds (default: `1.0`)
- `--retries`: retry attempts per request (default: `3`)
- `--backoff`: exponential backoff base (default: `1.5`)
- `--ignore-robots`: disable robots.txt checks
- `--allow-offsite`: follow links outside start domain
- In `recipe_scraper.py`, use `--recipe-keyword` to filter recipe titles (repeat for more)
- In `recipe_scraper.py`, use `--ingredient-keyword` to filter by ingredients (repeat for more)
- In `recipe_scraper.py`, use `--links-file` or `--links-stdin` for copied browser links

## Notes

- Only scrape websites you are allowed to scrape.
- Respect robots.txt and website terms of service.
- Add delays and retries before scraping at scale.
