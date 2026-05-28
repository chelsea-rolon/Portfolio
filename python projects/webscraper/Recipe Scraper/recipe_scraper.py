import argparse
import csv
import json
import re
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


def parse_page(base_url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    title = soup.title.get_text(strip=True) if soup.title else ""

    links = []
    for a in soup.select("a[href]"):
        href = a.get("href", "").strip()
        if not href:
            continue
        links.append({"text": a.get_text(" ", strip=True), "href": urljoin(base_url, href)})

    return {"url": base_url, "title": title, "links": links, "link_count": len(links)}


def _extract_json_ld_objects(soup: BeautifulSoup) -> list[dict]:
    objects: list[dict] = []

    for script in soup.select("script[type='application/ld+json']"):
        raw = script.string or script.get_text(strip=True)
        if not raw:
            continue

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    objects.append(item)
        elif isinstance(data, dict):
            objects.append(data)

    return objects


def _flatten_graph_nodes(node: dict) -> list[dict]:
    nodes: list[dict] = []

    graph = node.get("@graph")
    if isinstance(graph, list):
        for item in graph:
            if isinstance(item, dict):
                nodes.append(item)

    nodes.append(node)
    return nodes


def _type_contains_recipe(type_value: object) -> bool:
    if isinstance(type_value, str):
        return type_value.lower() == "recipe"
    if isinstance(type_value, list):
        return any(isinstance(v, str) and v.lower() == "recipe" for v in type_value)
    return False


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _normalize_instructions(raw: object) -> list[str]:
    steps: list[str] = []

    if isinstance(raw, str):
        clean = _clean_text(raw)
        if clean:
            steps.append(clean)
        return steps

    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                clean = _clean_text(item)
                if clean:
                    steps.append(clean)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    clean = _clean_text(text)
                    if clean:
                        steps.append(clean)

    elif isinstance(raw, dict):
        text = raw.get("text")
        if isinstance(text, str):
            clean = _clean_text(text)
            if clean:
                steps.append(clean)

    return steps


def parse_allrecipes_recipe(base_url: str, html: str) -> dict | None:
    soup = BeautifulSoup(html, "lxml")
    objects = _extract_json_ld_objects(soup)

    recipe_node: dict | None = None
    for obj in objects:
        for node in _flatten_graph_nodes(obj):
            if _type_contains_recipe(node.get("@type")):
                recipe_node = node
                break
        if recipe_node is not None:
            break

    if recipe_node is None:
        return None

    image = recipe_node.get("image")
    if isinstance(image, list) and image:
        image_url = image[0]
    else:
        image_url = image

    if isinstance(image_url, dict):
        image_url = image_url.get("url", "")

    author_name = ""
    author = recipe_node.get("author")
    if isinstance(author, dict):
        author_name = author.get("name", "")
    elif isinstance(author, list) and author and isinstance(author[0], dict):
        author_name = author[0].get("name", "")
    elif isinstance(author, str):
        author_name = author

    rating_value = None
    review_count = None
    aggregate = recipe_node.get("aggregateRating")
    if isinstance(aggregate, dict):
        rating_value = aggregate.get("ratingValue")
        review_count = aggregate.get("ratingCount")

    ingredients = recipe_node.get("recipeIngredient", [])
    if not isinstance(ingredients, list):
        ingredients = []

    instructions = _normalize_instructions(recipe_node.get("recipeInstructions"))

    return {
        "url": base_url,
        "title": recipe_node.get("name", ""),
        "description": recipe_node.get("description", ""),
        "author": author_name,
        "rating": rating_value,
        "review_count": review_count,
        "prep_time": recipe_node.get("prepTime", ""),
        "cook_time": recipe_node.get("cookTime", ""),
        "total_time": recipe_node.get("totalTime", ""),
        "yield": recipe_node.get("recipeYield", ""),
        "category": recipe_node.get("recipeCategory", ""),
        "cuisine": recipe_node.get("recipeCuisine", ""),
        "image": image_url or "",
        "ingredients": ingredients,
        "ingredient_count": len(ingredients),
        "instructions": instructions,
        "instruction_count": len(instructions),
    }


def title_matches_keywords(title: str, keywords: list[str] | None) -> bool:
    if not keywords:
        return True
    lowered = title.lower()
    return all(keyword.lower() in lowered for keyword in keywords)


def ingredients_match_keywords(ingredients: list[str], keywords: list[str] | None) -> bool:
    if not keywords:
        return True

    ingredient_blob = " ".join(ingredients).lower()
    return all(keyword.lower() in ingredient_blob for keyword in keywords)


def _normalize_recipe_url(url: str) -> str:
    parsed = urlparse(url)
    cleaned = parsed._replace(query="", fragment="")
    normalized = cleaned.geturl().rstrip("/ ")
    return normalized


def extract_allrecipes_recipe_urls(text: str) -> list[str]:
    # Match direct Allrecipes recipe links inside arbitrary pasted text.
    pattern = re.compile(r"https?://(?:www\.)?allrecipes\.com/recipe/\d+/[^\s\"'<>)]*", re.IGNORECASE)
    matches = pattern.findall(text or "")

    unique_urls: list[str] = []
    seen: set[str] = set()
    for raw_url in matches:
        normalized = _normalize_recipe_url(raw_url.rstrip(".,;!?:)]}"))
        if normalized in seen:
            continue
        seen.add(normalized)
        unique_urls.append(normalized)

    return unique_urls


def scrape_recipe_urls(
    urls: list[str],
    timeout: int,
    retries: int,
    backoff: float,
    delay: float,
    check_robots: bool,
    recipe_keywords: list[str] | None,
    ingredient_keywords: list[str] | None,
) -> dict:
    recipes: list[dict] = []
    failed_urls: list[dict[str, str]] = []
    skipped_by_robots: list[str] = []
    robots_cache: dict[str, RobotFileParser] = {}
    first_request = True

    for url in urls:
        if check_robots and not is_allowed_by_robots(url, robots_cache):
            skipped_by_robots.append(url)
            continue

        if delay > 0 and not first_request:
            time.sleep(delay)
        first_request = False

        try:
            html = fetch_html(url, timeout=timeout, retries=retries, backoff=backoff)
            recipe = parse_allrecipes_recipe(url, html)
            if recipe is None:
                raise ValueError("No recipe data found on page")

            if not title_matches_keywords(recipe.get("title", ""), recipe_keywords):
                continue

            if not ingredients_match_keywords(recipe.get("ingredients", []), ingredient_keywords):
                continue

            recipes.append(recipe)
        except Exception as exc:
            failed_urls.append({"url": url, "error": str(exc)})

    return {
        "mode": "url_batch",
        "input_url_count": len(urls),
        "recipe_keywords": recipe_keywords or [],
        "ingredient_keywords": ingredient_keywords or [],
        "recipe_count": len(recipes),
        "skipped_by_robots": skipped_by_robots,
        "failed_urls": failed_urls,
        "recipes": recipes,
    }


def scrape_recipe_page(
    url: str,
    timeout: int,
    retries: int,
    backoff: float,
    delay: float,
    check_robots: bool,
    recipe_keywords: list[str] | None,
    ingredient_keywords: list[str] | None,
) -> dict:
    robots_cache: dict[str, RobotFileParser] = {}

    if check_robots and not is_allowed_by_robots(url, robots_cache):
        raise PermissionError(f"Blocked by robots.txt: {url}")

    if delay > 0:
        time.sleep(delay)

    html = fetch_html(url, timeout=timeout, retries=retries, backoff=backoff)
    recipe = parse_allrecipes_recipe(url, html)
    if recipe is None:
        raise ValueError(f"No recipe data found on page: {url}")

    if not title_matches_keywords(recipe.get("title", ""), recipe_keywords):
        raise ValueError("Recipe title did not match requested keyword filters")

    if not ingredients_match_keywords(recipe.get("ingredients", []), ingredient_keywords):
        raise ValueError("Recipe ingredients did not match requested ingredient filters")

    return recipe


def crawl_recipes(
    start_url: str,
    timeout: int,
    retries: int,
    backoff: float,
    delay: float,
    max_pages: int,
    same_domain_only: bool,
    check_robots: bool,
    recipe_keywords: list[str] | None,
    ingredient_keywords: list[str] | None,
) -> dict:
    visited: set[str] = set()
    queue: deque[str] = deque([start_url])
    recipes: list[dict] = []
    skipped_by_robots: list[str] = []
    failed_urls: list[dict[str, str]] = []
    robots_cache: dict[str, RobotFileParser] = {}

    start_domain = urlparse(start_url).netloc
    first_request = True

    while queue and len(visited) < max_pages:
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

        page_data = parse_page(current_url, html)
        recipe = parse_allrecipes_recipe(current_url, html)
        if recipe and title_matches_keywords(recipe.get("title", ""), recipe_keywords):
            if ingredients_match_keywords(recipe.get("ingredients", []), ingredient_keywords):
                recipes.append(recipe)

        for link in page_data["links"]:
            normalized = normalize_link(current_url, link["href"])
            if not normalized or normalized in visited:
                continue
            if same_domain_only and urlparse(normalized).netloc != start_domain:
                continue
            queue.append(normalized)

    return {
        "start_url": start_url,
        "recipe_keywords": recipe_keywords or [],
        "ingredient_keywords": ingredient_keywords or [],
        "max_pages": max_pages,
        "same_domain_only": same_domain_only,
        "visited_count": len(visited),
        "recipe_count": len(recipes),
        "skipped_by_robots": skipped_by_robots,
        "failed_urls": failed_urls,
        "recipes": recipes,
    }


def save_csv(path: str, result: dict) -> None:
    if "recipes" in result and isinstance(result.get("recipes"), list):
        rows = [
            {
                "url": recipe.get("url", ""),
                "title": recipe.get("title", ""),
                "rating": recipe.get("rating", ""),
                "review_count": recipe.get("review_count", ""),
                "yield": recipe.get("yield", ""),
                "ingredient_count": recipe.get("ingredient_count", 0),
                "instruction_count": recipe.get("instruction_count", 0),
            }
            for recipe in result.get("recipes", [])
        ]
    else:
        rows = [
            {
                "url": result.get("url", ""),
                "title": result.get("title", ""),
                "rating": result.get("rating", ""),
                "review_count": result.get("review_count", ""),
                "yield": result.get("yield", ""),
                "ingredient_count": result.get("ingredient_count", 0),
                "instruction_count": result.get("instruction_count", 0),
            }
        ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "url",
                "title",
                "rating",
                "review_count",
                "yield",
                "ingredient_count",
                "instruction_count",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Allrecipes-focused recipe scraper")
    parser.add_argument("url", nargs="?", help="Recipe page or start URL")
    parser.add_argument("--output", help="Optional output JSON file path", default=None)
    parser.add_argument("--csv-output", help="Optional output CSV file path", default=None)
    parser.add_argument("--crawl", help="Follow links and collect recipes", action="store_true")
    parser.add_argument("--max-pages", help="Maximum pages to visit in crawl mode", type=int, default=40)
    parser.add_argument("--allow-offsite", help="Follow links outside starting domain", action="store_true")
    parser.add_argument("--delay", help="Delay between requests in seconds", type=float, default=1.0)
    parser.add_argument("--retries", help="Retry attempts", type=int, default=3)
    parser.add_argument("--backoff", help="Exponential backoff base", type=float, default=1.5)
    parser.add_argument("--timeout", help="Request timeout in seconds", type=int, default=15)
    parser.add_argument("--ignore-robots", help="Skip robots.txt checks", action="store_true")
    parser.add_argument(
        "--recipe-keyword",
        help="Filter recipe titles by keyword (repeatable)",
        action="append",
        default=None,
    )
    parser.add_argument(
        "--ingredient-keyword",
        help="Filter recipe ingredients by keyword (repeatable)",
        action="append",
        default=None,
    )
    parser.add_argument(
        "--links-file",
        help="Text/HTML file containing copied Allrecipes recipe URLs",
        default=None,
    )
    parser.add_argument(
        "--links-stdin",
        help="Read copied Allrecipes recipe URLs from standard input",
        action="store_true",
    )

    args = parser.parse_args()

    try:
        if args.links_file or args.links_stdin:
            if args.links_file and args.links_stdin:
                print("Use either --links-file or --links-stdin, not both.", file=sys.stderr)
                return 1

            if args.links_file:
                with open(args.links_file, "r", encoding="utf-8") as f:
                    copied_text = f.read()
            else:
                copied_text = sys.stdin.read()

            urls = extract_allrecipes_recipe_urls(copied_text)
            if not urls:
                print("No Allrecipes recipe URLs were found in the provided text.", file=sys.stderr)
                return 1

            result = scrape_recipe_urls(
                urls=urls,
                timeout=args.timeout,
                retries=args.retries,
                backoff=args.backoff,
                delay=args.delay,
                check_robots=not args.ignore_robots,
                recipe_keywords=args.recipe_keyword,
                ingredient_keywords=args.ingredient_keyword,
            )
        elif args.crawl:
            if not args.url:
                print("URL is required unless --links-file or --links-stdin is used.", file=sys.stderr)
                return 1

            result = crawl_recipes(
                start_url=args.url,
                timeout=args.timeout,
                retries=args.retries,
                backoff=args.backoff,
                delay=args.delay,
                max_pages=max(1, args.max_pages),
                same_domain_only=not args.allow_offsite,
                check_robots=not args.ignore_robots,
                recipe_keywords=args.recipe_keyword,
                ingredient_keywords=args.ingredient_keyword,
            )
        else:
            if not args.url:
                print("URL is required unless --links-file or --links-stdin is used.", file=sys.stderr)
                return 1

            result = scrape_recipe_page(
                url=args.url,
                timeout=args.timeout,
                retries=args.retries,
                backoff=args.backoff,
                delay=args.delay,
                check_robots=not args.ignore_robots,
                recipe_keywords=args.recipe_keyword,
                ingredient_keywords=args.ingredient_keyword,
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
