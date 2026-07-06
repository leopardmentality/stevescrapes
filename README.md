# Steven Adeneye — Data Engineering Portfolio

**Data engineer specializing in web scraping, data quality, and ETL pipelines.**

Python · BeautifulSoup · Selenium · Scrapy · AWS · Snowflake

---

## Featured Project: Book Scout

A Streamlit dashboard that scrapes [books.toscrape.com](https://books.toscrape.com) in real time, displaying cover images, prices, and star ratings in a filterable card grid.

### What it demonstrates

- **Scraper fleet thinking** — polite crawl delays, user-agent headers, paginated navigation
- **Break/fix ownership** — encoding normalization, relative URL resolution, per-page error handling
- **Data quality** — input validation, filter/sort on scraped output, clean empty states
- **Streamlit UI** — session state management, reactive sidebar controls, card grid layout

### Stack

`Python 3` · `BeautifulSoup4` · `Requests` · `Streamlit`

### Run it locally

```bash
git clone https://github.com/leopardmentality/jazzlearnsmandarin.github.io.git
cd jazzlearnsmandarin.github.io
pip install streamlit beautifulsoup4 requests
streamlit run book_scraper.py
```

Opens at `http://localhost:8501`. Pick a category, set the page count (1–10), and hit **Scrape books**.

---

## About

- **Email:** solvedbysteve@gmail.com  
- **LinkedIn:** [linkedin.com/in/steven-adeneye](https://www.linkedin.com/in/steven-adeneye/)  
- **Portfolio:** [solvedbysteve.github.io](https://solvedbysteve.github.io/)
