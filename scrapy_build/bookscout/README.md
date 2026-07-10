# BookScout — Scrapy Build

Scrapes [books.toscrape.com](https://books.toscrape.com) using **Scrapy** —
the same site as the BeautifulSoup/Streamlit demo, showing how the two tools
compare at fleet scale.

## Why Scrapy alongside BeautifulSoup?

| | BeautifulSoup | Scrapy |
|---|---|---|
| **Best for** | Single scrapers, quick scripts, Streamlit demos | Fleet of 40+ scrapers in production |
| **Retry logic** | Manual | Built-in (`RETRY_TIMES`, `RETRY_HTTP_CODES`) |
| **Rate limiting** | Manual `time.sleep()` | `DOWNLOAD_DELAY` + AutoThrottle middleware |
| **Deduplication** | Manual | Pipeline stage |
| **Output formats** | Manual | CSV, JSON, JSONL via `-o` flag |
| **Middleware** | N/A | Proxy rotation, user-agent spoofing in one place |

## Project structure

```
bookscout/
├── bookscout/
│   ├── spiders/
│   │   └── books_spider.py   # spider: crawls listing pages, follows pagination
│   ├── pipelines.py          # validate → deduplicate → write to .jsonl
│   └── settings.py           # politeness, retry, autothrottle, pipeline config
├── scrapy.cfg
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
# Scrape all books, print items to stdout
scrapy crawl books

# Save to JSON
scrapy crawl books -o output/books.json

# Save to CSV
scrapy crawl books -o output/books.csv

# Scrape a single category
scrapy crawl books -s CATEGORY=mystery
```

Output is also written to `output/books.jsonl` via the pipeline (one JSON object per line).

## Pipeline stages

Every scraped item passes through three stages:

1. **ValidateBookPipeline** — drops items missing title, price, stars, or URL; validates price is parseable and stars is 1–5
2. **DeduplicatePipeline** — drops items whose URL has already been seen this run
3. **JsonWriterPipeline** — writes clean items to `output/books.jsonl`

This validate → deduplicate → persist pattern mirrors production scraper fleet thinking,
where silent data corruption is worse than a loud failure.
