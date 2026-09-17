
import json
import time
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import requests
from bs4 import BeautifulSoup

# ==============================
# CONFIG
# ==============================

CONFIG = "config/search.json"
OUTPUT = "data/jobs.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/139.0.0.0 Safari/537.36"
    )
}

# ==============================
# LOAD CONFIG
# ==============================

with open(CONFIG, "r", encoding="utf-8") as f:
    config = json.load(f)

LOCATIONS = config["locations"]
ROLES = config["roles"]
BLOCKED = [k.lower() for k in config["blocked_keywords"]]
PRIORITY = config["priority"]

# ==============================
# FILTER ENGINE
# ==============================


def is_relevant(title: str) -> bool:
    """
    Reject senior / java / dotnet / freelance etc.
    """
    t = title.lower()

    for word in BLOCKED:
        if word.lower() in t:
            return False

    # Must contain one of these
    allowed = [
        "backend",
        "software engineer",
        "software developer",
        "full stack",
        "sde",
        "golang",
        "intern",
    ]

    return any(a in t for a in allowed)


# ==============================
# SCRAPER
# ==============================

all_jobs = []

print("\n=========== LINKEDIN JOB SCRAPER ===========\n")

for location in LOCATIONS:
    for role in ROLES:

        print(f"Searching → {role} | {location}")

        url = (
            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            f"?keywords={quote(role)}"
            f"&location={quote(location)}"
            "&f_TPR=r86400"
            "&start=0"
        )

        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=30
            )

            if response.status_code != 200:
                print(f"  Failed : {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.find_all("li")

            for card in cards:

                title = card.find("h3")
                company = card.find("h4")
                place = card.find(
                    "span",
                    class_="job-search-card__location"
                )
                link = card.find(
                    "a",
                    class_="base-card__full-link"
                )
                date = card.find("time")

                if not title:
                    continue

                job_title = title.get_text(strip=True)

                if not is_relevant(job_title):
                    continue

                all_jobs.append({
                    "role": job_title,
                    "company": company.get_text(strip=True)
                    if company else "",
                    "location": place.get_text(strip=True)
                    if place else "",
                    "posted": date.get("datetime", "")
                    if date else "",
                    "apply_link": link["href"]
                    if link else "",
                    "search_location": location,
                    "source": "linkedin_jobs"
                })

            time.sleep(1)

        except Exception as e:
            print("Error:", e)

# ==============================
# DATAFRAME
# ==============================

df = pd.DataFrame(all_jobs)

if df.empty:
    print("\nNo jobs found.")
    raise SystemExit

# remove duplicates
df = df.drop_duplicates(
    subset=["role", "company"]
)

# location priority
df["priority"] = (
    df["search_location"]
    .map(PRIORITY)
    .fillna(99)
)

df = (
    df.sort_values(
        ["priority", "company", "role"]
    )
    .drop(columns="priority")
    .reset_index(drop=True)
)

# ==============================
# SAVE
# ==============================

Path("data").mkdir(exist_ok=True)

df.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig"
)

print("\n===================================")
print(f"Saved {len(df)} relevant jobs")
print(f"CSV : {OUTPUT}")
print("===================================")