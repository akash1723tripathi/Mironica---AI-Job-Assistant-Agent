from playwright.sync_api import sync_playwright
from pathlib import Path

STATE_FILE = Path("storage_state.json")

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        slow_mo=200
    )

    context = browser.new_context(
        viewport={"width": 1440, "height": 900}
    )

    page = context.new_page()

    page.goto("https://www.linkedin.com/login")

    print("=" * 60)
    print("1. Login to your LinkedIn account manually")
    print("2. Wait until the home feed opens")
    print("3. Come back to this terminal")
    input("Press ENTER to save session...")

    context.storage_state(path=STATE_FILE)

    print(f"\n✅ Session saved to {STATE_FILE}")

    browser.close()