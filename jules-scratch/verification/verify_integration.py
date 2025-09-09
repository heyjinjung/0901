import re
from playwright.sync_api import sync_playwright, Page, expect
import os

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        # Navigate to the app
        page.goto("http://localhost:3000/")

        # Get the absolute path to the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        screenshot_path = os.path.join(script_dir, "initial_page.png")

        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
