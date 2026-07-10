# BookScout Scrapy Settings
# Full settings reference: https://docs.scrapy.org/en/latest/topics/settings.html

BOT_NAME = "bookscout"

SPIDER_MODULES = ["bookscout.spiders"]
NEWSPIDER_MODULE = "bookscout.spiders"

# Crawl responsibly — identify your bot
USER_AGENT = (
    "BookScout/1.0 (+https://github.com/leopardmentality/stevescrapes) "
    "Mozilla/5.0 (compatible)"
)

# Respect robots.txt
ROBOTSTXT_OBEY = True

# Politeness defaults (can be overridden per-spider via custom_settings)
DOWNLOAD_DELAY = 0.5
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# Auto-throttle: backs off when the server slows down
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Retry on transient errors
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [429, 500, 502, 503, 504]

# Item pipelines — enable in order of priority (lower number = runs first)
ITEM_PIPELINES = {
    "bookscout.pipelines.ValidateBookPipeline": 200,
    "bookscout.pipelines.DeduplicatePipeline":  300,
    "bookscout.pipelines.JsonWriterPipeline":   400,
}

# Default output path for JsonWriterPipeline
OUTPUT_PATH = "output/books.jsonl"

# Request fingerprinting
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
