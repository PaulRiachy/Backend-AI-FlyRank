# The Polite Scraper

A small, polite web-scraping pipeline built for the **FlyRank Internship Backend Track — Week 5 — Assignment A9**.

The scraper:

- Downloads the first **3 catalogue pages** from Books to Scrape.
- Discovers **60 unique book URLs**.
- Fetches and caches each book page.
- Extracts the required book fields.
- Normalizes prices into numeric GBP values.
- Validates records with Pydantic.
- Stores valid records in `output/books.json`.
- Stores invalid records in `output/errors.json`.
- Produces a run report in `output/run-report.json`.
- Survives individual page failures without stopping the entire run.

---

## Target Classification

**Target:** [Books to Scrape](https://books.toscrape.com/)

Books to Scrape is a public practice sandbox specifically designed for learning web scraping.

The scraper is intentionally limited to the **first three catalogue pages**, which contain 60 books.

Before development, `https://books.toscrape.com/robots.txt` was checked and the site's scraping rules were reviewed.

The scraper only collects the data required for this assignment.

> I will not reuse this code on another site without checking its rules and terms first.

---

## Tech Stack

**Python lane**

- Python 3.10+
- Requests
- Beautiful Soup
- Pydantic
- JSON

---

## Run in 5 Minutes

### 1. Clone the repository

```powershell
git clone https://github.com/PaulRiachy/Backend-AI-FlyRank.git
cd Backend-AI-FlyRank/scraper
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Run the scraper

```powershell
python src/main.py
```

The scraper creates:

```text
output/
├── books.json
├── errors.json
└── run-report.json
```

A successful clean run should report:

```text
catalogue_pages=3
discovered=60
unique_urls=60
detail_pages=60
valid_records=60
invalid_records=0
```

The final dataset should contain exactly **60 validated, unique records**.

---

## Record Schema

Each validated record contains:

```json
{
  "title": "A Light in the Attic",
  "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "price_text": "£51.77",
  "price_gbp": 51.77,
  "availability_text": "In stock (22 available)",
  "rating_text": "Three",
  "description": "...",
  "source_page": "https://books.toscrape.com/catalogue/page-1.html",
  "fetched_at": "2026-08-22T12:57:09.183694+00:00"
}
```

### Fields

| Field | Type | Purpose |
|---|---|---|
| `title` | string | Book title |
| `product_url` | URL | Absolute book URL and record identity |
| `price_text` | string | Original scraped price |
| `price_gbp` | number | Normalized GBP price |
| `availability_text` | string | Original availability text |
| `rating_text` | string | Book rating |
| `description` | string/null | Book description |
| `source_page` | URL | Catalogue page where the book was found |
| `fetched_at` | datetime | Fetch timestamp |

The raw price is preserved while `price_gbp` provides a clean numeric value.

Missing descriptions are stored as `null` rather than invented.

---

## Scraping Pipeline

```text
Catalogue Pages
      ↓
Discover 60 URLs
      ↓
Fetch Book Pages
      ↓
Cache HTML
      ↓
Extract Raw Fields
      ↓
Normalize Values
      ↓
Pydantic Validation
      ↓
books.json
      ↓
run-report.json
```

Invalid records are separated into `errors.json` and are never written to `books.json`.

Duplicate product URLs are removed before storage, making the scraper idempotent.

Running it again produces the same 60 records rather than creating duplicates.

---

## Politeness Rules

The scraper follows these rules for every real request:

### Identifying User-Agent

```text
FlyRankInternshipA9/1.0 (+https://github.com/PaulRiachy/Backend-AI-FlyRank)
```

### Timeout

Requests have a **10-second timeout** so the scraper does not wait indefinitely.

### Request Delay

The scraper waits at least **500 ms** between real requests.

Cached pages require no delay because they do not generate network traffic.

### Caching

Downloaded HTML is stored locally in:

```text
cache/
```

During development, cached pages are reused instead of repeatedly requesting the website.

### Status Checking

Only HTTP `200 OK` responses are treated as successful pages.

### Limited Scope

Only the first three catalogue pages are processed.

---

## Failure Handling

Each book page is handled independently.

If one page fails, the scraper records the failure and continues processing the remaining pages.

Temporary failures such as timeouts or server errors can be retried once.

Permanent errors such as `403` or `404` are not repeatedly requested.

The run therefore continues even when an individual page is unavailable.

The final `run-report.json` records:

- start time
- duration
- pages fetched
- cache hits
- valid records
- invalid records
- failed pages

---

## Output

### `output/books.json`

Contains the validated records.

Expected clean result:

```text
60 records
```

### `output/errors.json`

Contains records that failed normalization or schema validation, together with the reason.

Expected clean result:

```text
0 invalid records
```

### `output/run-report.json`

Contains the results of the scraper run and provides evidence that the run completed successfully.

---

## Sample Run Report

```json
{
  "started_at": "2026-08-22T13:38:20.191316+00:00",
  "finished_at": "2026-08-22T13:38:20.640730+00:00",
  "duration_seconds": 0.449414,
  "pages_fetched": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0
}
```

---

## Why No Browser Is Required

The core assignment does not require a browser because the book information is already present in the HTML returned by the server.

A normal HTTP request plus Beautiful Soup is therefore sufficient.

A browser would add additional memory and execution cost without providing additional data for this assignment.

---

## Ethics

This scraper is intended for the provided public practice sandbox.

When applying these techniques elsewhere:

- Use an official API when one exists.
- Check the site's rules and terms first.
- Respect applicable `robots.txt` rules.
- Never bypass logins, paywalls, or access restrictions.
- Never attempt to circumvent blocks.
- Collect only the data that is necessary.
- Use reasonable request rates.

---

## Limitation

The scraper depends on the current HTML structure of Books to Scrape.

If the website changes its HTML structure or CSS selectors, the extraction logic may need to be updated.

The scraper is intentionally limited to the first three catalogue pages and is not a general-purpose crawler.

---

## Project Structure

```text
scraper/
├── src/
│   └── main.py
├── cache/              # ignored by Git
├── output/
│   ├── books.json
│   └── run-report.json
├── .gitignore
├── requirements.txt
└── README.md
```

Cached HTML is excluded from Git so the repository contains only the code and representative output required as evidence.

---

## Assignment Progress

### Stage 0 — Classify Scraping Target
- Identified Books to Scrape as the practice sandbox.
- Checked `robots.txt`.
- Defined the three-page scope.

### Stage 1 — Fetch and Cache HTML
- Added Requests-based fetching.
- Added User-Agent and timeout.
- Added status-code checking.
- Added local HTML caching.

### Stage 2 — Discover Three Catalogue Pages
- Followed the site's `next` links.
- Converted relative URLs to absolute URLs.
- Discovered 60 unique book URLs.

### Stage 3 — Extract Book Details
- Visited all 60 book pages.
- Extracted the eight required raw fields.
- Added source provenance and timestamps.
- Cached detail pages.

### Stage 4 — Validate Normalized Records
- Added numeric `price_gbp`.
- Added Pydantic schema validation.
- Added duplicate protection.
- Added `books.json` and `errors.json`.

### Stage 5 — Survive Failures and Report
- Added per-page failure handling.
- Added retry behavior for temporary failures.
- Added `run-report.json`.
- Verified that a failed page does not terminate the run.

### Stage 6 — Publish Scraper Evidence
- Documented the target and ethics.
- Documented installation and execution.
- Documented the schema and pipeline.
- Documented politeness rules.
- Added representative output.
- Prepared the project for publication.

---

## License

Educational project created for the FlyRank Internship Backend Track.