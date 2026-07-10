"""
BookScout Scrapy Spider
Scrapes books.toscrape.com — titles, prices, star ratings, categories, and URLs.
Handles pagination automatically across all 50 categories or the full catalogue.

Run:
    scrapy crawl books                          # scrape all books, print to stdout
    scrapy crawl books -o output/books.json     # save to JSON
    scrapy crawl books -o output/books.csv      # save to CSV
    scrapy crawl books -s CATEGORY=mystery      # scrape one category
"""

import scrapy

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    custom_settings = {
        # --- Politeness ---
        "DOWNLOAD_DELAY": 0.5,           # wait 0.5s between requests
        "RANDOMIZE_DOWNLOAD_DELAY": True, # jitter: 0.25s–0.75s
        "CONCURRENT_REQUESTS": 1,        # one request at a time (polite)

        # --- Retry logic ---
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 3,
        "RETRY_HTTP_CODES": [429, 500, 502, 503, 504],

        # --- Auto-throttle (backs off if server slows down) ---
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 0.5,
        "AUTOTHROTTLE_MAX_DELAY": 10,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,

        # --- Output ---
        "FEEDS": {},  # controlled via CLI -o flag
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, category=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: scrapy crawl books -s CATEGORY=mystery
        if category:
            self.start_urls = [
                f"https://books.toscrape.com/catalogue/category/books/{category}/index.html"
            ]
        self.category_filter = category

    # ── Parse listing page ───────────────────────────────────────────────────

    def parse(self, response):
        """Parse a book listing page, yield items, follow next page."""

        # Detect current category from breadcrumb
        breadcrumb = response.css("ul.breadcrumb li")
        category = breadcrumb[-2].css("a::text").get("All").strip() if len(breadcrumb) >= 2 else "All"

        for article in response.css("article.product_pod"):
            relative_url = article.css("h3 a::attr(href)").get("")
            # Resolve relative ../ links to absolute
            book_url = response.urljoin(
                relative_url.replace("../", "catalogue/")
                if relative_url.startswith("../")
                else relative_url
            )

            rating_word = article.css("p.star-rating::attr(class)").get("")
            rating_word = rating_word.replace("star-rating", "").strip()
            stars = RATING_MAP.get(rating_word, 0)

            price_raw = article.css("p.price_color::text").get("").strip()
            price = price_raw.encode("ascii", "ignore").decode().replace("Â", "").strip()

            yield {
                "title":    article.css("h3 a::attr(title)").get("").strip(),
                "price":    price,
                "stars":    stars,
                "category": category,
                "url":      book_url,
            }

        # Follow pagination
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
