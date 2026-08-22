from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
CATALOGUE_PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"

USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/PaulRiachy/Backend-AI-FlyRank)"
TIMEOUT = 10
REQUEST_DELAY = 0.5


def fetch_page(url: str, cache_file: Path):
    if cache_file.exists():
        content = cache_file.read_text(encoding="utf-8")

        print(
            f"CACHE HIT url={url} "
            f"size={len(content.encode('utf-8'))} bytes"
        )

        return content

    print(f"FETCH url={url}")

    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch {url}: HTTP {response.status_code}"
        )

    content = response.text

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(content, encoding="utf-8")

    print(
        f"FETCHED url={url} "
        f"status=200 "
        f"size={len(response.content)} bytes"
    )

    return content


def get_catalogue_page_cache_file(page_number: int) -> Path:
    return CACHE_DIR / f"catalogue-page-{page_number}.html"


def discover_books_from_page(html: str, page_url: str) -> list[str]:
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


def find_next_page(html: str, page_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")

    next_link = soup.select_one("li.next a")

    if next_link is None:
        return None

    href = next_link.get("href")

    if not href:
        return None

    return urljoin(page_url, href)


def discover_catalogue():
    current_url = CATALOGUE_PAGE_URL

    all_book_urls = []
    catalogue_pages = 0

    while current_url and catalogue_pages < 3:
        catalogue_pages += 1

        cache_file = get_catalogue_page_cache_file(catalogue_pages)

        html = fetch_page(
            current_url,
            cache_file,
        )

        book_urls = discover_books_from_page(
            html,
            current_url,
        )

        all_book_urls.extend(book_urls)

        current_url = find_next_page(
            html,
            current_url,
        )

    unique_book_urls = list(dict.fromkeys(all_book_urls))

    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(all_book_urls)}")
    print(f"unique_urls={len(unique_book_urls)}")

    return unique_book_urls


def main():
    discover_catalogue()


if __name__ == "__main__":
    main()