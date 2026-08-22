from datetime import datetime, timezone
from pathlib import Path
from time import sleep
from urllib.parse import urljoin
import json

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl, ValidationError


BASE_URL = "https://books.toscrape.com/"
CATALOGUE_PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

BOOKS_FILE = OUTPUT_DIR / "books.json"
ERRORS_FILE = OUTPUT_DIR / "errors.json"

USER_AGENT = (
    "FlyRankInternshipA9/1.0 "
    "(+https://github.com/PaulRiachy/Backend-AI-FlyRank)"
)

TIMEOUT = 10
REQUEST_DELAY = 0.5

def create_stats():
    return {
        "pages_fetched": 0,
        "cache_hits": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "failed_pages": 0,
    }

class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: str | None
    source_page: HttpUrl
    fetched_at: datetime


def fetch_page(
    url: str,
    cache_file: Path,
    stats: dict,
):
    if cache_file.exists():
        content = cache_file.read_text(encoding="utf-8")

        stats["cache_hits"] += 1

        print(
            f"CACHE HIT url={url} "
            f"size={len(content.encode('utf-8'))} bytes"
        )

        return content

    print(f"FETCH url={url}")

    for attempt in range(2):
        try:
            response = requests.get(
                url,
                headers={"User-Agent": USER_AGENT},
                timeout=TIMEOUT,
            )

        except requests.RequestException as error:
            if attempt == 0:
                print(
                    f"RETRY url={url} "
                    f"reason={type(error).__name__}"
                )
                sleep(REQUEST_DELAY)
                continue

            raise RuntimeError(
                f"Request failed for {url}: {error}"
            ) from error

        if response.status_code == 200:
            content = response.text

            cache_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            cache_file.write_text(
                content,
                encoding="utf-8",
            )

            stats["pages_fetched"] += 1

            print(
                f"FETCHED url={url} "
                f"status=200 "
                f"size={len(response.content)} bytes"
            )

            return content

        if response.status_code in (403, 404):
            raise RuntimeError(
                f"Failed to fetch {url}: "
                f"HTTP {response.status_code}"
            )

        if 500 <= response.status_code <= 599:
            if attempt == 0:
                print(
                    f"RETRY url={url} "
                    f"status={response.status_code}"
                )
                sleep(REQUEST_DELAY)
                continue

        raise RuntimeError(
            f"Failed to fetch {url}: "
            f"HTTP {response.status_code}"
        )

    raise RuntimeError(
        f"Failed to fetch {url}"
    )


def get_catalogue_page_cache_file(page_number: int) -> Path:
    return CACHE_DIR / f"catalogue-page-{page_number}.html"


def get_book_cache_file(book_number: int) -> Path:
    return CACHE_DIR / f"book-{book_number}.html"


def discover_books_from_page(
    html: str,
    page_url: str,
) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")

    book_urls = []

    for article in soup.select("article.product_pod"):
        link = article.select_one("h3 a")

        if link is None:
            continue

        href = link.get("href")

        if not href:
            continue

        absolute_url = urljoin(page_url, href)

        book_urls.append(absolute_url)

    return book_urls


def find_next_page(
    html: str,
    page_url: str,
) -> str | None:
    soup = BeautifulSoup(html, "html.parser")

    next_link = soup.select_one("li.next a")

    if next_link is None:
        return None

    href = next_link.get("href")

    if not href:
        return None

    return urljoin(page_url, href)


def discover_catalogue(stats):
    current_url = CATALOGUE_PAGE_URL

    discovered_books = []
    catalogue_pages = 0

    while current_url and catalogue_pages < 3:
        catalogue_pages += 1

        cache_file = get_catalogue_page_cache_file(
            catalogue_pages
        )

        html = fetch_page(
            current_url,
            cache_file,
            stats,
        )

        book_urls = discover_books_from_page(
            html,
            current_url,
        )

        for book_url in book_urls:
            discovered_books.append(
                {
                    "product_url": book_url,
                    "source_page": current_url,
                }
            )

        current_url = find_next_page(
            html,
            current_url,
        )

    unique_books = []
    seen_urls = set()

    for book in discovered_books:
        if book["product_url"] in seen_urls:
            continue

        seen_urls.add(book["product_url"])
        unique_books.append(book)

    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(discovered_books)}")
    print(f"unique_urls={len(unique_books)}")

    return unique_books

def extract_text(element):
    if element is None:
        return None

    text = element.get_text(
        " ",
        strip=True,
    )

    return text if text else None


def extract_book_record(
    html: str,
    product_url: str,
    source_page: str,
):
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    product_main = soup.select_one(
        "article.product_page"
    )

    if product_main is None:
        raise ValueError(
            "Product page content not found"
        )

    title_element = product_main.select_one(
        "div.product_main h1"
    )

    price_element = product_main.select_one(
        "p.price_color"
    )

    availability_element = product_main.select_one(
        "p.instock.availability"
    )

    rating_element = product_main.select_one(
        "p.star-rating"
    )

    description_element = soup.select_one(
        "#product_description + p"
    )

    title = extract_text(title_element)
    price_text = extract_text(price_element)
    availability_text = extract_text(
        availability_element
    )
    description = extract_text(
        description_element
    )

    rating_text = None

    if rating_element is not None:
        rating_classes = rating_element.get("class", [])

        rating_text = next(
            (
                class_name
                for class_name in rating_classes
                if class_name != "star-rating"
            ),
            None,
        )

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def fetch_book_pages(
    books: list[dict],
    stats: dict,
):
    records = []

    for index, book in enumerate(
        books,
        start=1,
    ):
        product_url = book["product_url"]
        source_page = book["source_page"]

        cache_file = get_book_cache_file(index)

        try:
            if not cache_file.exists():
                sleep(REQUEST_DELAY)

            html = fetch_page(
                product_url,
                cache_file,
                stats,
            )

            record = extract_book_record(
                html=html,
                product_url=product_url,
                source_page=source_page,
            )

            records.append(record)

            print(
                f"extracted={index}/{len(books)}"
            )

        except Exception as error:
            stats["failed_pages"] += 1

            print(
                f"FAILED url={product_url} "
                f"reason={error}"
            )

    return records

def normalize_price(price_text: str) -> float:
    cleaned = (
        price_text
        .replace("Â£", "")
        .replace("£", "")
        .strip()
    )

    try:
        return float(cleaned)
    except ValueError:
        raise ValueError(
            f"Invalid price: {price_text}"
        )

def normalize_record(raw_record: dict) -> dict:
    return {
        **raw_record,
        "price_gbp": normalize_price(
            raw_record["price_text"]
        ),
    }


def validate_and_store(records: list[dict],stats: dict,):
    valid_records = []
    errors = []

    seen_urls = set()

    for record in records:
        try:
            normalized = normalize_record(
                record
            )

            validated = BookRecord.model_validate(
                normalized
            )

            product_url = str(
                validated.product_url
            )

            if product_url in seen_urls:
                continue

            seen_urls.add(product_url)

            valid_records.append(
                validated.model_dump(
                    mode="json"
                )
            )

        except (
            ValueError,
            ValidationError,
        ) as error:
            errors.append(
                {
                    "record": record,
                    "reason": str(error),
                }
            )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    BOOKS_FILE.write_text(
        json.dumps(
            valid_records,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    ERRORS_FILE.write_text(
        json.dumps(
            errors,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    stats["valid_records"] = len(valid_records)
    stats["invalid_records"] = len(errors)

    print(
        f"valid_records={len(valid_records)}"
    )

    print(
        f"invalid_records={len(errors)}"
    )

    return valid_records, errors

def write_run_report(
    stats: dict,
    started_at: datetime,
):
    finished_at = datetime.now(timezone.utc)

    duration = (
        finished_at - started_at
    ).total_seconds()

    report = {
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "duration_seconds": duration,
        "pages_fetched": stats["pages_fetched"],
        "cache_hits": stats["cache_hits"],
        "valid_records": stats["valid_records"],
        "invalid_records": stats["invalid_records"],
        "failed_pages": stats["failed_pages"],
    }

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_file = OUTPUT_DIR / "run-report.json"

    report_file.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nRun report:")
    print(
        json.dumps(
            report,
            indent=2,
        )
    )

def main():
    started_at = datetime.now(timezone.utc)

    stats = create_stats()

    book_urls = discover_catalogue(
        stats
    )

    records = fetch_book_pages(
        book_urls,
        stats,
    )

    print(
        f"detail_pages={len(records)}"
    )

    if records:
        print("\nFirst raw record:")
        print(records[0])

    valid_records, errors = validate_and_store(
        records,
        stats,
    )

    print(
        f"\nStored {len(valid_records)} "
        f"valid records."
    )

    print(
        f"Stored {len(errors)} "
        f"invalid records."
    )

    write_run_report(
        stats,
        started_at,
    )
if __name__ == "__main__":
    main()