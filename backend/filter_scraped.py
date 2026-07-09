"""
Filters scraped_data.json to keep only pages relevant to student queries.
Run: python filter_scraped.py
Produces: scraped_data_filtered.json
"""

import json
import re

with open("scraped_data.json", encoding="utf-8") as f:
    pages = json.load(f)

print(f"Total scraped pages: {len(pages)}")

# ── URL patterns to EXCLUDE (noise, not useful for students) ─────────────────
EXCLUDE_URL_PATTERNS = [
    r"/paper-presentations",
    r"/paper-publications",
    r"/workshops-training",
    r"/workshops-seminars",
    r"/conferences-attended",
    r"/conferences-organized",
    r"/journal-archives",
    r"/previous-archives",
    r"/books-published",
    r"/industrial-academia",
    r"/research-thesis",
    r"/availed-research",
    r"/on-going-research",
    r"/research-related",
    r"/dr-iram-anjum",
    r"/dr-shahnaz",
    r"/dr-hooria",
    r"/dr-atia-alam",
    r"/ms-almas",
    r"/year-201[1-9]",
    r"/year-202[0-5]",
    r"oric\.kinnaird",
    r"journal\.kinnaird",
    r"jnasp\.kinnaird",
    r"bic\.kinnaird",
    r"/1stcohort",
    r"/2ndcohort",
    r"/3rdcohort",
    r"/visits",
    r"/incubation-process",
    r"/product-showcasing",
    r"/idea-competition",
    r"/national-partners",
    r"/international-partners",
    r"/industrial-partners",
    r"/peer-review",
    r"/authors-guidelines",
    r"/reviewers-guidelines",
    r"/editorial-policy",
    r"/abstract-indexing",
    r"/publication-charges",
    r"/copyright",
    r"/important-links",
    r"/wp-",
    r"page/[2-9]",    # pagination pages (usually low-value)
    r"page/[1-9][0-9]",
]

# ── Title patterns to EXCLUDE ────────────────────────────────────────────────
EXCLUDE_TITLE_PATTERNS = [
    r"paper presentations? in conferences",
    r"paper publications? in 20",
    r"workshops? / training attended",
    r"workshops? / seminars",
    r"journal archives",
    r"previous archives",
    r"authors? guidelines",
    r"reviewers? guidelines",
    r"editorial policy",
    r"peer review",
    r"advisory board",
    r"^university 0[12]$",   # generic placeholder pages
    r"^about$",              # very short about pages
    r"kinnaird – page [2-9]",
    r"news – page [2-9]",
    r"dr\. farooq babar – page",
    r"^events$",
    r"calendar$",
]

# ── Minimum content length ───────────────────────────────────────────────────
MIN_CHARS = 300


def should_exclude(page):
    url = page.get("url", "").lower()
    title = page.get("title", "").lower()
    text = page.get("text", "")

    for pat in EXCLUDE_URL_PATTERNS:
        if re.search(pat, url):
            return True, f"url:{pat}"

    for pat in EXCLUDE_TITLE_PATTERNS:
        if re.search(pat, title):
            return True, f"title:{pat}"

    if len(text) < MIN_CHARS:
        return True, f"too_short({len(text)})"

    return False, ""


kept = []
dropped = []

for page in pages:
    exclude, reason = should_exclude(page)
    if exclude:
        dropped.append((page.get("url", ""), reason))
    else:
        kept.append(page)

print(f"\nKept  : {len(kept)} pages")
print(f"Dropped: {len(dropped)} pages")

print("\nDropped pages:")
for url, reason in dropped:
    print(f"  [{reason}] {url}")

with open("scraped_data_filtered.json", "w", encoding="utf-8") as f:
    json.dump(kept, f, ensure_ascii=False, indent=2)

print(f"\nSaved → scraped_data_filtered.json ({len(kept)} pages)")
