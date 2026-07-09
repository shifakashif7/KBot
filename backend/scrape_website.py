"""
Scrapes kinnaird.edu.pk and saves clean text + URL + title to scraped_data.json.
Run before rebuilding the index: python scrape_website.py
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse
from collections import deque

BASE_DOMAIN = "kinnaird.edu.pk"
OUTPUT_FILE = "scraped_data.json"
DELAY = 1.0  # seconds between requests — be polite

SEED_URLS = [
    "https://kinnaird.edu.pk/",
    "https://kinnaird.edu.pk/admissions/",
    "https://kinnaird.edu.pk/fee-structure/",
    "https://kinnaird.edu.pk/scholarships/",
    "https://kinnaird.edu.pk/contact/",
    "https://kinnaird.edu.pk/about/",
    # Intermediate
    "https://kinnaird.edu.pk/fsc-intermediate-2/",
    "https://kinnaird.edu.pk/general-science-intermediate/",
    "https://kinnaird.edu.pk/arts-fa-intermediate/",
    "https://kinnaird.edu.pk/commerce-intermediate/",
    # Undergraduate — Life Sciences
    "https://kinnaird.edu.pk/bs-botany/",
    "https://kinnaird.edu.pk/bs-botany-3/",
    "https://kinnaird.edu.pk/bs-biochemistry/",
    "https://kinnaird.edu.pk/bs-biotechnology/",
    "https://kinnaird.edu.pk/bs-food-science-human-nutrition/",
    "https://kinnaird.edu.pk/bs-horticulture/",
    "https://kinnaird.edu.pk/bs-genetics/",
    "https://kinnaird.edu.pk/bs-zoology/",
    # Undergraduate — Mathematical & Physical Sciences
    "https://kinnaird.edu.pk/bs-chemistry/",
    "https://kinnaird.edu.pk/bs-computer-science/",
    "https://kinnaird.edu.pk/bs-environmental-sciences/",
    "https://kinnaird.edu.pk/bs-geography/",
    "https://kinnaird.edu.pk/bs-mathematics/",
    "https://kinnaird.edu.pk/bs-physics/",
    "https://kinnaird.edu.pk/bs-remote-sensing-and-geographical-information-systems/",
    "https://kinnaird.edu.pk/bs-statistics/",
    # Undergraduate — Arts & Humanities
    "https://kinnaird.edu.pk/bs-applied-linguistics/",
    "https://kinnaird.edu.pk/bs-english-language-literature/",
    "https://kinnaird.edu.pk/b-ed-education/",
    "https://kinnaird.edu.pk/bachelor-fine-arts/",
    "https://kinnaird.edu.pk/bachelor-media-studies/",
    "https://kinnaird.edu.pk/bachelor-design/",
    "https://kinnaird.edu.pk/bs-urdu-literature/",
    # Undergraduate — Social Sciences & Law
    "https://kinnaird.edu.pk/bs-accounting-finance/",
    "http://kinnaird.edu.pk/bs-psychology/",
    "https://kinnaird.edu.pk/ba-business-administration-bba/",
    "https://kinnaird.edu.pk/bs-economics/",
    "https://kinnaird.edu.pk/bs-international-relations/",
    "https://kinnaird.edu.pk/bs-law/",
    "https://kinnaird.edu.pk/bs-political-science/",
    "https://kinnaird.edu.pk/bs-sports-sciences-and-physical-education/",
    # MPhil / MS
    "https://kinnaird.edu.pk/mphil-accounting-finance/",
    "https://kinnaird.edu.pk/mphil-applied-linguistics/",
    "https://kinnaird.edu.pk/mphil-biochemistry/",
    "https://kinnaird.edu.pk/mphil-biotechnology/",
    "https://kinnaird.edu.pk/mphil-molecular/",
    "https://kinnaird.edu.pk/mphil-business-administration/",
    "https://kinnaird.edu.pk/mphil-chemistry/",
    "https://kinnaird.edu.pk/ms-clinical-psychology/",
    "https://kinnaird.edu.pk/ms-computer-science/",
    "https://kinnaird.edu.pk/mphil-education/",
    "https://kinnaird.edu.pk/mphil-english-literature/",
    "https://kinnaird.edu.pk/mphil-environmental-sciences/",
    "https://kinnaird.edu.pk/mphil-food-science-human-nutrition/",
    "https://kinnaird.edu.pk/mphil-international-relations/",
    "https://kinnaird.edu.pk/mphil-media-studies/",
    "https://kinnaird.edu.pk/mphil-political-science/",
    "https://kinnaird.edu.pk/mphil-statistics/",
    "https://kinnaird.edu.pk/mphil-urdu/",
    # PhD
    "https://kinnaird.edu.pk/phd-biotechnology/",
    "https://kinnaird.edu.pk/phd-english-literature/",
    "https://kinnaird.edu.pk/phd-food-science-human-nutrition/",
    "https://kinnaird.edu.pk/phd-international-relations/",
]

SKIP_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg",
                   ".zip", ".doc", ".docx", ".mp4", ".mp3", ".webp"}
SKIP_PATTERNS = ["wp-login", "wp-admin", "wp-content/uploads", "wp-json",
                 "/feed", "xmlrpc", "mailto:", "tel:", "javascript:"]

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; KBot-Scraper/1.0)"}


def is_valid_url(url):
    parsed = urlparse(url)
    if parsed.netloc and BASE_DOMAIN not in parsed.netloc:
        return False
    path = parsed.path.lower()
    if any(path.endswith(ext) for ext in SKIP_EXTENSIONS):
        return False
    full = url.lower()
    if any(p in full for p in SKIP_PATTERNS):
        return False
    return True


def normalize_url(url):
    parsed = urlparse(url)
    norm = f"https://{parsed.netloc}{parsed.path}"
    if not norm.endswith("/"):
        norm += "/"
    return norm


def extract_content(soup, url):
    for tag in soup(["script", "style", "nav", "header", "footer", "aside",
                     "noscript", "form", "iframe"]):
        tag.decompose()

    # Title: prefer H1, fallback to <title>
    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True).split("|")[0].strip()

    # Main content area
    content = (
        soup.find("article") or
        soup.find("main") or
        soup.find(class_=re.compile(
            r"entry.content|post.content|page.content|content.area|elementor.section", re.I
        )) or
        soup.find("div", id=re.compile(r"^content$|^main$|^primary$", re.I)) or
        soup.body
    )

    if not content:
        return title, ""

    lines = []
    for elem in content.find_all(["h1", "h2", "h3", "h4", "h5", "p", "li", "td", "th", "dt", "dd"]):
        text = elem.get_text(separator=" ", strip=True)
        if text and len(text) > 15:
            lines.append(text)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return title, text.strip()


def scrape_all():
    visited = set()
    discovered = set()
    queue = deque()

    for u in SEED_URLS:
        n = normalize_url(u)
        if n not in discovered:
            discovered.add(n)
            queue.append(u)

    results = []
    session = requests.Session()
    session.headers.update(HEADERS)

    print(f"Scraping {BASE_DOMAIN} — {len(queue)} seed URLs queued\n")

    while queue:
        raw_url = queue.popleft()
        norm = normalize_url(raw_url)

        if norm in visited:
            continue
        if not is_valid_url(raw_url):
            continue

        visited.add(norm)

        try:
            resp = session.get(raw_url, timeout=15)
            if resp.status_code != 200:
                print(f"  [{resp.status_code}] SKIP: {raw_url}")
                continue
            if "text/html" not in resp.headers.get("Content-Type", ""):
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            title, text = extract_content(soup, raw_url)

            if text and len(text) > 100:
                results.append({
                    "url": raw_url,
                    "title": title,
                    "text": text
                })
                print(f"  OK  [{len(text):>6} chars] {title or raw_url}")
            else:
                print(f"  SKIP (no content): {raw_url}")

            # Discover more internal links
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if not href:
                    continue
                full = urljoin(raw_url, href).split("#")[0].split("?")[0]
                n2 = normalize_url(full)
                if (n2 not in discovered and
                        is_valid_url(full) and
                        BASE_DOMAIN in urlparse(full).netloc):
                    discovered.add(n2)
                    queue.append(full)

        except Exception as e:
            print(f"  ERROR: {raw_url} — {e}")

        time.sleep(DELAY)

    print(f"\nDone. {len(results)} pages scraped.")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Saved → {OUTPUT_FILE}")


if __name__ == "__main__":
    scrape_all()
