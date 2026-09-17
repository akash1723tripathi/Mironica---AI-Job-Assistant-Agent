import re
import time
from pathlib import Path
from urllib.parse import quote

import pandas as pd
from playwright.sync_api import sync_playwright

STATE = "storage_state.json"
OUTPUT = "data/recruiter_posts.csv"

SEARCHES = [
    "hiring backend engineer",
    "hiring backend developer",
    "hiring software engineer",
    "hiring full stack engineer",
    "hiring backend intern",
    "hiring software engineer intern",
    "hiring golang engineer",
]

EMAIL_REGEX = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
URL_REGEX = r"https?://[^\s)]+"


def clean(txt: str):
    return " ".join(txt.split())


def find_email(text):
    m = re.findall(EMAIL_REGEX, text)
    return m[0] if m else ""


def find_apply(text):
    links = re.findall(URL_REGEX, text)

    for l in links:
        l = l.rstrip(".,)")
        if any(
            x in l.lower()
            for x in [
                "forms.gle",
                "google.com/forms",
                "careers",
                "jobs",
                "greenhouse",
                "lever",
                "ashby",
            ]
        ):
            return l

    return ""


rows = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    context = browser.new_context(storage_state=STATE)

    page = context.new_page()

    for query in SEARCHES:

        print(f"\nSearching -> {query}")

        url = (
            "https://www.linkedin.com/search/results/content/"
            f"?keywords={quote(query)}"
        )

        page.goto(url, wait_until="domcontentloaded")

        page.wait_for_timeout(5000)

        # Scroll
        for _ in range(5):
            page.mouse.wheel(0, 3500)
            page.wait_for_timeout(1500)

        cards = page.locator(
            "div[data-view-name='search-entity-result-universal-template']"
        )

        count = min(cards.count(), 15)

        print("Found:", count)

        for i in range(count):

            card = cards.nth(i)

            try:

                text = clean(card.inner_text())
                lower = text.lower()

                if "hiring" not in lower:
                    continue

                if (
                    "dm me" in lower
                    or "dm if interested" in lower
                    or "message me" in lower
                ):
                    continue

                email = find_email(text)
                apply = find_apply(text)

                if email == "" and apply == "":
                    continue

                recruiter = ""
                company = ""
                post_url = ""

                # Recruiter
                try:
                    recruiter = (
                        card.locator("span[dir='ltr']")
                        .first.inner_text()
                        .strip()
                    )
                except:
                    pass

                # Company
                try:
                    company = (
                        card.locator("span.t-12")
                        .first.inner_text()
                        .strip()
                    )
                except:
                    pass

                # Post URL
                try:
                    post_url = card.locator(
                        "a[href*='/posts/']"
                    ).first.get_attribute("href")
                except:
                    pass

                rows.append(
                    {
                        "query": query,
                        "recruiter": recruiter,
                        "company": company,
                        "email": email,
                        "apply_link": apply,
                        "post_url": post_url,
                        "description": text[:500],
                    }
                )

            except:
                continue

    browser.close()

df = pd.DataFrame(rows)

if not df.empty:
    df = df.drop_duplicates(subset=["description"])

Path("data").mkdir(exist_ok=True)

df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")

print(f"\nSaved {len(df)} recruiter posts -> {OUTPUT}")