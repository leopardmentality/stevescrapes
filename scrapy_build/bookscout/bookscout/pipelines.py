"""
BookScout Pipelines

Three stages every scraped item passes through:

1. ValidateBookPipeline  — drop items missing required fields or with bad data
2. DeduplicatePipeline   — drop duplicate URLs seen in this run
3. JsonWriterPipeline    — write clean items to a .jsonl file (one JSON obj per line)

This pattern mirrors production scraper fleet thinking:
validate → deduplicate → persist. Each stage is independent and testable.
"""

import json
import logging
import os
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

logger = logging.getLogger(__name__)


class ValidateBookPipeline:
    """Drop items that are missing required fields or have invalid values."""

    REQUIRED_FIELDS = ["title", "price", "stars", "url"]

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Check required fields are present and non-empty
        for field in self.REQUIRED_FIELDS:
            if not adapter.get(field):
                raise DropItem(f"Missing field '{field}' in item: {dict(item)}")

        # Validate star rating is in expected range
        stars = adapter.get("stars")
        if not isinstance(stars, int) or stars not in range(1, 6):
            raise DropItem(f"Invalid star rating '{stars}' for: {adapter.get('title')}")

        # Validate price looks like a number after stripping £
        price_str = adapter.get("price", "").replace("£", "").replace(",", "")
        try:
            float(price_str)
        except ValueError:
            raise DropItem(f"Unparseable price '{adapter.get('price')}' for: {adapter.get('title')}")

        return item


class DeduplicatePipeline:
    """Drop items whose URL has already been seen this run."""

    def __init__(self):
        self.seen_urls = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        url = adapter.get("url")
        if url in self.seen_urls:
            raise DropItem(f"Duplicate URL: {url}")
        self.seen_urls.add(url)
        return item


class JsonWriterPipeline:
    """
    Write each item to a .jsonl file (newline-delimited JSON).
    One record per line — easy to stream, easy to load into pandas or a warehouse.
    """

    def open_spider(self, spider):
        output_path = spider.settings.get("OUTPUT_PATH", "output/books.jsonl")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.file = open(output_path, "w", encoding="utf-8")
        self.count = 0
        logger.info(f"JsonWriterPipeline: writing to {output_path}")

    def close_spider(self, spider):
        self.file.close()
        logger.info(f"JsonWriterPipeline: wrote {self.count} items")

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False)
        self.file.write(line + "\n")
        self.count += 1
        return item
