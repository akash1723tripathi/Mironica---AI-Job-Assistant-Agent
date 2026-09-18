"""
LinkedIn login utility.
Launches an interactive browser window to allow logging into LinkedIn
and saves the session cookies/storage to `storage_state.json`.
"""

import sys
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

STORAGE_STATE_PATH = Path("storage_state.json")

def main():
    print("[*] Launching browser for LinkedIn login...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.linkedin.com/login")
        print("[*] Please log into LinkedIn in the browser window.")
        print("[*] Once logged in and on the feed page, press ENTER in this terminal to save session...")
        input()
        context.storage_state(path=str(STORAGE_STATE_PATH))
        print(f"[+] Saved storage state to {STORAGE_STATE_PATH.resolve()}")
        browser.close()

if __name__ == "__main__":
    main()
