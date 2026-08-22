from pathlib import Path

import requests


BASE_URL = "https://books.toscrape.com/"
CATALOGUE_PAGE_URL = "https://books.toscrape.com/catalogue/page-1.html"

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"

USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/PaulRiachy/Backend-AI-FlyRank)"

TIMEOUT = 10


def fetch_catalogue_page():
    if CACHE_FILE.exists():
        content = CACHE_FILE.read_text(encoding="utf-8")

        print(
            f"CACHE HIT status=200 "
            f"size={len(content.encode('utf-8'))} bytes"
        )

        return content

    print(f"FETCH url={CATALOGUE_PAGE_URL}")

    response = requests.get(
        CATALOGUE_PAGE_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch catalogue page: HTTP {response.status_code}"
        )

    content = response.text

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(content, encoding="utf-8")

    print(f"FETCHED status=200 size={len(response.content)} bytes")

    return content


def main():
    fetch_catalogue_page()


if __name__ == "__main__":
    main()