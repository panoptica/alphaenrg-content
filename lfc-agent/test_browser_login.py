#!/usr/bin/env python3
"""
Test Instagram browser login - with better field detection
"""

from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv()

def test_login():
    username = os.environ.get("INSTAGRAM_USERNAME", "YNWA4Reds")
    password = os.environ.get("INSTAGRAM_PASSWORD", "")
    
    print(f"🔐 Testing login as: {username}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("1️⃣ Loading Instagram login page...")
        page.goto("https://www.instagram.com/accounts/login/")
        page.wait_for_timeout(5000)  # Wait longer for page to fully load
        
        print("2️⃣ Handling cookie popup...")
        try:
            for text in ["Allow all cookies", "Allow essential and optional cookies", "Accept all", "Accept"]:
                try:
                    page.click(f"button:has-text('{text}')", timeout=2000)
                    print(f"   🍪 Clicked: {text}")
                    page.wait_for_timeout(3000)
                    break
                except:
                    pass
        except:
            pass
        
        print("3️⃣ Looking for login fields...")
        page.screenshot(path="/Users/macmini/lfc-agent/before_login.png")
        
        # Try multiple selectors
        selectors = [
            "input[name='username']",
            "input[aria-label='Phone number, username, or email']",
            "input[type='text']",
            "#loginForm input[type='text']",
        ]
        
        username_field = None
        for sel in selectors:
            try:
                username_field = page.wait_for_selector(sel, timeout=5000)
                if username_field:
                    print(f"   ✅ Found username field: {sel}")
                    break
            except:
                print(f"   ❌ Not found: {sel}")
        
        if not username_field:
            print("❌ Could not find username field - saving debug screenshot")
            page.screenshot(path="/Users/macmini/lfc-agent/no_field.png")
            # Print page content for debugging
            print("   Page URL:", page.url)
            browser.close()
            return
        
        print("4️⃣ Filling login form...")
        username_field.fill(username)
        print("   ✅ Username entered")
        
        # Find password field
        password_field = page.query_selector("input[name='password'], input[type='password']")
        if password_field:
            password_field.fill(password)
            print("   ✅ Password entered")
        
        print("5️⃣ Clicking login button...")
        page.click("button[type='submit']")
        page.wait_for_timeout(8000)
        
        print(f"6️⃣ Current URL: {page.url}")
        page.screenshot(path="/Users/macmini/lfc-agent/login_result.png")
        print("📸 Screenshot saved: login_result.png")
        
        if "login" not in page.url.lower():
            print("✅ LOGIN SUCCESS!")
        else:
            print("❌ Still on login page")
        
        browser.close()

if __name__ == "__main__":
    test_login()