import argparse
import csv
import json
import sys
import time
from collections import deque
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def make_headers() -> dict:
    return {"User-Agent": DEFAULT_USER_AGENT}


def fetch_html(url: str, timeout: int = 15, retries: int = 3, backoff: float = 1.5) -> str:
    headers = make_headers()
    retries = max(1, retries)

    last_error: requests.RequestException | None = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=timeout, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_error = exc
            if attempt == retries:
                break
            sleep_seconds = backoff ** (attempt - 1)
            time.sleep(sleep_seconds)

    raise last_error if last_error else RuntimeError("Failed to fetch HTML")


def get_robots_parser(url: str, cache: dict[str, RobotFileParser]) -> RobotFileParser:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    if robots_url in cache:
        return cache[robots_url]

    parser = RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
    except Exception:
        pass

    cache[robots_url] = parser
    return parser


def is_allowed_by_robots(url: str, cache: dict[str, RobotFileParser]) -> bool:
    parser = get_robots_parser(url, cache)
    return parser.can_fetch(DEFAULT_USER_AGENT, url)


def normalize_link(base_url: str, href: str) -> str | None:
    if not href:
        return None

    absolute = urljoin(base_url, href.strip())
    absolute, _ = urldefrag(absolute)
    parsed = urlparse(absolute)
    if parsed.scheme not in {"http", "https"}:
        return None
    return absolute


def parse_page(base_url: str, html: str, selector: str | None = None) -> dict:
    soup = BeautifulSoup(html, "lxml")
    title = soup.title.get_text(strip=True) if soup.title else ""

    links = []
    for a in soup.select("a[href]"):
        href = a.get("href", "").strip()
        if not href:
            continue
        links.append({"text": a.get_text(" ", strip=True), "href": urljoin(base_url, href)})

    selected_text = []
    if selector:
        for node in soup.select(selector):
            value = node.get_text(" ", strip=True)
            if value:
                selected_text.append(value)

    return {
        "url": base_url,
        "title": title,
        "selector": selector,
        "selected_text": selected_text,
        "links": links,
        "link_count": len(links),
    }


def scrape_single_page(
    url: str,
    selector: str | None,
    timeout: int,
    retries: int,
    backoff: float,
    delay: float,
    check_robots: bool,
) -> dict:
    robots_cache: dict[str, RobotFileParser] = {}

    if check_robots and not is_allowed_by_robots(url, robots_cache):
        raise PermissionError(f"Blocked by robots.txt: {url}")

    if delay > 0:
        time.sleep(delay)

    html = fetch_html(url, timeout=timeout, retries=retries, backoff=backoff)
    return parse_page(url, html, selector)


def crawl_site(
    start_url: str,
    selector: str | None,
    timeout: int,
    retries: int,
    backoff: float,
    delay: float,
    max_pages: int,
    same_domain_only: bool,
    check_robots: bool,
) -> dict:
    visited: set[str] = set()
    queue: deque[str] = deque([start_url])
    pages: list[dict] = []
    skipped_by_robots: list[str] = []
    failed_urls: list[dict[str, str]] = []
    robots_cache: dict[str, RobotFileParser] = {}

    start_domain = urlparse(start_url).netloc
    first_request = True

    while queue and len(pages) < max_pages:
        current_url = queue.popleft()
        if current_url in visited:
            continue

        visited.add(current_url)

        if check_robots and not is_allowed_by_robots(current_url, robots_cache):
            skipped_by_robots.append(current_url)
            continue

        if delay > 0 and not first_request:
            time.sleep(delay)
        first_request = False

        try:
            html = fetch_html(current_url, timeout=timeout, retries=retries, backoff=backoff)
        except requests.RequestException as exc:
            failed_urls.append({"url": current_url, "error": str(exc)})
            continue

        page_data = parse_page(current_url, html, selector)
        pages.append(page_data)

        for link in page_data["links"]:
            normalized = normalize_link(current_url, link["href"])
            if not normalized or normalized in visited:
                continue
            if same_domain_only and urlparse(normalized).netloc != start_domain:
                continue
            queue.append(normalized)

    return {
        "start_url": start_url,
        "selector": selector,
        "max_pages": max_pages,
        "same_domain_only": same_domain_only,
        "visited_count": len(visited),
        "scraped_count": len(pages),
        "skipped_by_robots": skipped_by_robots,
        "failed_urls": failed_urls,
        "pages": pages,
    }


def save_csv(path: str, result: dict) -> None:
    if "pages" in result:
        rows = [
            {
                "url": page.get("url", ""),
                "title": page.get("title", ""),
                "link_count": page.get("link_count", 0),
                "selected_text": " | ".join(page.get("selected_text", [])),
            }
            for page in result.get("pages", [])
        ]
    else:
        rows = [
            {
                "url": result.get("url", ""),
                "title": result.get("title", ""),
                "link_count": result.get("link_count", 0),
                "selected_text": " | ".join(result.get("selected_text", [])),
            }
        ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "title", "link_count", "selected_text"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Simple general webscraper")
    parser.add_argument("url", help="Target page URL")
    parser.add_argument("--selector", help="Optional CSS selector", default=None)
    parser.add_argument("--output", help="Optional output JSON file path", default=None)
    parser.add_argument("--csv-output", help="Optional output CSV file path", default=None)
    parser.add_argument("--crawl", help="Follow links and scrape multiple pages", action="store_true")
    parser.add_argument("--max-pages", help="Max pages in crawl mode", type=int, default=10)
    parser.add_argument("--allow-offsite", help="Follow links outside start domain", action="store_true")
    parser.add_argument("--delay", help="Delay between requests in seconds", type=float, default=1.0)
    parser.add_argument("--retries", help="Retry attempts", type=int, default=3)
    parser.add_argument("--backoff", help="Exponential backoff base", type=float, default=1.5)
    parser.add_argument("--timeout", help="Request timeout in seconds", type=int, default=15)
    parser.add_argument("--ignore-robots", help="Skip robots.txt checks", action="store_true")
    args = parser.parse_args()

    try:
        if args.crawl:
            result = crawl_site(
                start_url=args.url,
                selector=args.selector,
                timeout=args.timeout,
                retries=args.retries,
                backoff=args.backoff,
                delay=args.delay,
                max_pages=max(1, args.max_pages),
                same_domain_only=not args.allow_offsite,
                check_robots=not args.ignore_robots,
            )
        else:
            result = scrape_single_page(
                url=args.url,
                selector=args.selector,
                timeout=args.timeout,
                retries=args.retries,
                backoff=args.backoff,
                delay=args.delay,
                check_robots=not args.ignore_robots,
            )
    except PermissionError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except requests.RequestException as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Saved scrape result to {args.output}")

    if args.csv_output:
        save_csv(args.csv_output, result)
        print(f"Saved scrape result to {args.csv_output}")

    if not args.output and not args.csv_output:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
