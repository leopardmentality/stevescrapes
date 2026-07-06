"""
Book Scraper — books.toscrape.com
Run with: streamlit run book_scraper.py
Requires: pip install streamlit beautifulsoup4 requests
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

# ── Config ────────────────────────────────────────────────────────────────────
BASE_URL = "https://books.toscrape.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

st.set_page_config(
    page_title="Book Scout",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --ink:     #1a1a2e;
    --paper:   #f7f3ec;
    --amber:   #c9882a;
    --amber-lt:#f0d9b0;
    --muted:   #6b6459;
    --border:  #ddd4c4;
    --card-bg: #ffffff;
}

/* Page background */
.stApp { background: var(--paper); }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--ink) !important;
    border-right: none;
}
[data-testid="stSidebar"] * { color: #e8e0d4 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stMultiSelect label { color: #b8ad9e !important; font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; }
[data-testid="stSidebar"] hr { border-color: #2e2e4a !important; }

/* Header */
.book-header {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    color: var(--ink);
    line-height: 1.1;
    margin-bottom: 0;
}
.book-subhead {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: var(--muted);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

/* Metric strip */
.metric-strip {
    display: flex;
    gap: 2rem;
    background: var(--ink);
    border-radius: 8px;
    padding: 0.9rem 1.4rem;
    margin-bottom: 1.5rem;
    color: var(--paper);
    font-family: 'Inter', sans-serif;
}
.metric-item { display: flex; flex-direction: column; }
.metric-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--amber);
}
.metric-lbl { font-size: 0.7rem; color: #9a9098; letter-spacing: 0.07em; text-transform: uppercase; }

/* Cards */
.book-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 1.2rem;
}
.book-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem 1rem 0.8rem;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    transition: box-shadow 0.15s;
}
.book-card:hover { box-shadow: 0 4px 18px rgba(26,26,46,0.10); }
.book-img-wrap {
    width: 100%;
    display: flex;
    justify-content: center;
    margin-bottom: 0.5rem;
}
.book-img-wrap img {
    height: 160px;
    object-fit: contain;
    border-radius: 2px;
}
.book-title {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.88rem;
    color: var(--ink);
    line-height: 1.3;
    min-height: 2.4em;
}
.book-price {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--amber);
}
.book-rating {
    font-size: 1rem;
    letter-spacing: 0.05em;
}
.star-on  { color: #c9882a; }
.star-off { color: #ddd4c4; }
.book-category {
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
.book-link a {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    color: var(--ink);
    text-decoration: underline;
    opacity: 0.55;
}
.book-link a:hover { opacity: 1; }

/* Error / info boxes */
.scrape-error {
    background: #fff3f3;
    border: 1px solid #f5c6c6;
    border-radius: 6px;
    padding: 1rem;
    color: #8b1a1a;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
}

/* Spinner override */
.stSpinner > div { border-top-color: var(--amber) !important; }

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Scraper ───────────────────────────────────────────────────────────────────

def fetch_categories() -> dict[str, str]:
    """Return {category_name: relative_url} from the sidebar nav."""
    try:
        r = requests.get(BASE_URL, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        cats = {}
        for a in soup.select("ul.nav-list ul a"):
            name = a.text.strip()
            href = a["href"]  # e.g. "catalogue/category/books/mystery_3/index.html"
            cats[name] = href
        return cats
    except Exception as e:
        return {}


def parse_stars(word: str) -> int:
    return RATING_MAP.get(word, 0)


def stars_html(n: int) -> str:
    return "".join(
        f'<span class="star-on">★</span>' if i < n else f'<span class="star-off">★</span>'
        for i in range(5)
    )


def scrape_page(url: str) -> tuple[list[dict], str | None]:
    """Scrape one page. Returns (books, next_page_url or None)."""
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    books = []
    for art in soup.select("article.product_pod"):
        title = art.h3.a["title"]
        price_raw = art.select_one("p.price_color").text.strip()
        price = price_raw.replace("Â", "").replace("£", "£")  # encoding fix
        rating_word = art.p["class"][1]  # e.g. ['star-rating', 'Three']
        stars = parse_stars(rating_word)
        img_src = art.img["src"].replace("../../", "")  # strip relative dots
        img_url = f"{BASE_URL}/{img_src}"
        rel_link = art.h3.a["href"].replace("../", "catalogue/")
        full_link = f"{BASE_URL}/catalogue/{rel_link.split('catalogue/')[-1]}"
        books.append({
            "title": title,
            "price": price,
            "stars": stars,
            "img_url": img_url,
            "link": full_link,
        })

    next_btn = soup.select_one("li.next a")
    if next_btn:
        # resolve relative next-page URL
        current_dir = url.rsplit("/", 1)[0]
        next_url = current_dir + "/" + next_btn["href"]
    else:
        next_url = None

    return books, next_url


def scrape_all(start_url: str, max_pages: int = 5) -> tuple[list[dict], list[str]]:
    """Scrape up to max_pages pages from start_url. Returns (books, errors)."""
    books, errors = [], []
    url = start_url
    page = 0
    while url and page < max_pages:
        try:
            new_books, next_url = scrape_page(url)
            books.extend(new_books)
            url = next_url
            page += 1
            time.sleep(0.3)  # polite crawl delay
        except requests.exceptions.RequestException as e:
            errors.append(f"Network error on page {page+1}: {e}")
            break
        except Exception as e:
            errors.append(f"Parse error on page {page+1}: {e}")
            break
    return books, errors


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 📖 Book Scout")
    st.markdown("---")

    st.markdown("**Source**")
    scope = st.selectbox(
        "Scope",
        ["All Books", "By Category"],
        label_visibility="collapsed",
    )

    category_url = None
    if scope == "By Category":
        with st.spinner("Loading categories…"):
            cats = fetch_categories()
        if cats:
            chosen_cat = st.selectbox("Category", list(cats.keys()))
            category_url = f"{BASE_URL}/{cats[chosen_cat]}"
        else:
            st.warning("Couldn't load categories.")

    st.markdown("---")
    st.markdown("**Pages to scrape**")
    max_pages = st.slider("Pages", 1, 10, 3, label_visibility="collapsed")
    st.caption(f"≈ {max_pages * 20} books max")

    st.markdown("---")
    st.markdown("**Filter results**")
    min_stars = st.select_slider(
        "Minimum rating",
        options=[1, 2, 3, 4, 5],
        value=1,
        format_func=lambda x: "★" * x,
    )

    price_cap = st.slider("Max price (£)", 0, 60, 60)

    sort_by = st.selectbox(
        "Sort by",
        ["Default", "Price: Low → High", "Price: High → Low", "Rating: High → Low"],
    )

    scrape_btn = st.button("🔍 Scrape books", use_container_width=True)


# ── Main ──────────────────────────────────────────────────────────────────────

st.markdown('<div class="book-header">Book Scout</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="book-subhead">Live data from books.toscrape.com · '
    'Built with BeautifulSoup &amp; Streamlit</div>',
    unsafe_allow_html=True,
)

if "books" not in st.session_state:
    st.session_state.books = []
    st.session_state.errors = []
    st.session_state.scraped = False

if scrape_btn:
    start_url = (
        category_url
        if (scope == "By Category" and category_url)
        else f"{BASE_URL}/catalogue/page-1.html"
    )

    with st.spinner(f"Scraping up to {max_pages} page(s)…"):
        books, errors = scrape_all(start_url, max_pages=max_pages)

    st.session_state.books = books
    st.session_state.errors = errors
    st.session_state.scraped = True

if st.session_state.scraped:
    all_books = st.session_state.books

    # ── Filter
    filtered = [
        b for b in all_books
        if b["stars"] >= min_stars
        and float(b["price"].replace("£", "").replace(",", "")) <= price_cap
    ]

    # ── Sort
    if sort_by == "Price: Low → High":
        filtered.sort(key=lambda b: float(b["price"].replace("£", "").replace(",", "")))
    elif sort_by == "Price: High → Low":
        filtered.sort(key=lambda b: float(b["price"].replace("£", "").replace(",", "")), reverse=True)
    elif sort_by == "Rating: High → Low":
        filtered.sort(key=lambda b: b["stars"], reverse=True)

    # ── Errors
    for err in st.session_state.errors:
        st.markdown(f'<div class="scrape-error">⚠️ {err}</div>', unsafe_allow_html=True)

    # ── Metrics
    if all_books:
        prices = [float(b["price"].replace("£", "").replace(",", "")) for b in all_books]
        avg_price = sum(prices) / len(prices)
        avg_stars = sum(b["stars"] for b in all_books) / len(all_books)

        st.markdown(f"""
        <div class="metric-strip">
            <div class="metric-item">
                <span class="metric-val">{len(all_books)}</span>
                <span class="metric-lbl">Books scraped</span>
            </div>
            <div class="metric-item">
                <span class="metric-val">{len(filtered)}</span>
                <span class="metric-lbl">Shown</span>
            </div>
            <div class="metric-item">
                <span class="metric-val">£{avg_price:.2f}</span>
                <span class="metric-lbl">Avg price</span>
            </div>
            <div class="metric-item">
                <span class="metric-val">{avg_stars:.1f} ★</span>
                <span class="metric-lbl">Avg rating</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if not filtered:
        st.info("No books match your filters. Try relaxing the rating or price cap.")
    else:
        # ── Card grid (5 columns max)
        cols_per_row = 5
        rows = [filtered[i:i+cols_per_row] for i in range(0, len(filtered), cols_per_row)]

        for row in rows:
            cols = st.columns(len(row))
            for col, book in zip(cols, row):
                with col:
                    st.markdown(f"""
                    <div class="book-card">
                        <div class="book-img-wrap">
                            <img src="{book['img_url']}" alt="{book['title']}">
                        </div>
                        <div class="book-title">{book['title']}</div>
                        <div class="book-price">{book['price']}</div>
                        <div class="book-rating">{stars_html(book['stars'])}</div>
                        <div class="book-link"><a href="{book['link']}" target="_blank">View on site →</a></div>
                    </div>
                    """, unsafe_allow_html=True)

else:
    # Empty state
    st.markdown("""
    <div style="text-align:center; padding: 5rem 2rem; color: #6b6459; font-family: 'Inter', sans-serif;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📚</div>
        <div style="font-size: 1.1rem; font-weight: 600; color: #1a1a2e; margin-bottom: 0.4rem;">
            Ready to scrape
        </div>
        <div style="font-size: 0.85rem;">
            Choose your scope and page count in the sidebar, then hit <strong>Scrape books</strong>.
        </div>
    </div>
    """, unsafe_allow_html=True)
