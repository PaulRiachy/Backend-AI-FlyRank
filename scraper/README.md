# Books to Scrape — Polite Scraper

A small Python scraping pipeline built for FlyRank Internship Backend Track —
Week 5, Assignment A9.

## Target Classification

The target for this assignment is [Books to Scrape](https://books.toscrape.com/),
a public practice sandbox provided by ToScrape specifically for learning and
testing web scraping.

The scraper is limited to the first three catalogue pages, which contain
60 books in total.

The data collected from each book page will be limited to:

- title
- product URL
- price text
- availability text
- rating text
- description
- source catalogue page
- fetch timestamp

The purpose of this project is to practise responsible scraping against a
sandbox specifically intended for this purpose. The scraper will use a clear
user-agent, request timeouts, caching during development, and a delay between
real requests.

## Robots Check

I checked:

https://books.toscrape.com/robots.txt

Result: the robots.txt URL returned HTTP 404 Not Found. No robots file was
found.

A missing robots.txt file is not treated as permission to scrape other sites.
This assignment uses Books to Scrape because the ToScrape site explicitly
identifies it as a scraping practice sandbox.

I will not reuse this code on another site without checking its rules and
terms first.