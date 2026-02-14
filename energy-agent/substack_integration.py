#!/usr/bin/env python3
"""
Substack Integration for AlphaENRG - Auto-publish articles to Substack
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

load_dotenv()

class SubstackPublisher:
    def __init__(self):
        """Initialize Substack publisher with credentials"""
        self.substack_url = os.getenv('SUBSTACK_URL', 'https://alphaenergy.substack.com')
        self.email = os.getenv('SUBSTACK_EMAIL')
        self.password = os.getenv('SUBSTACK_PASSWORD')
        self.cookies_file = os.getenv('SUBSTACK_COOKIES_FILE', 'substack_cookies.json')
        
        # Chrome options for headless operation
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

    def load_cookies(self):
        """Load saved cookies from file"""
        if os.path.exists(self.cookies_file):
            try:
                with open(self.cookies_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading cookies: {e}")
        return None

    def save_cookies(self, cookies):
        """Save cookies to file"""
        try:
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f)
            print(f"✅ Cookies saved to {self.cookies_file}")
        except Exception as e:
            print(f"❌ Error saving cookies: {e}")

    def login_and_get_cookies(self):
        """Login to Substack and extract cookies for future use"""
        
        if not self.email or not self.password:
            print("⚠️ Substack credentials not found. Please provide SUBSTACK_EMAIL and SUBSTACK_PASSWORD")
            return None

        driver = None
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(f"{self.substack_url}/account/login")
            
            # Wait for and fill email
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_input.send_keys(self.email)
            
            # Fill password
            password_input = driver.find_element(By.NAME, "password")
            password_input.send_keys(self.password)
            
            # Click login
            login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
            login_button.click()
            
            # Wait for login to complete
            WebDriverWait(driver, 10).until(
                EC.url_contains("publish")
            )
            
            # Extract cookies
            cookies = driver.get_cookies()
            self.save_cookies(cookies)
            
            print("✅ Substack login successful and cookies saved!")
            return cookies
            
        except Exception as e:
            print(f"❌ Substack login failed: {e}")
            return None
        finally:
            if driver:
                driver.quit()

    def publish_article(self, title, content, subtitle=None, tags=None):
        """Publish article to Substack using Selenium"""
        
        # Try to load existing cookies first
        cookies = self.load_cookies()
        if not cookies:
            print("🔐 No saved cookies found. Attempting login...")
            cookies = self.login_and_get_cookies()
            if not cookies:
                return False

        driver = None
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            
            # Load Substack and set cookies
            driver.get(self.substack_url)
            
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"⚠️ Could not add cookie: {cookie.get('name', 'unknown')} - {e}")
            
            # Navigate to publish page
            driver.get(f"{self.substack_url}/publish")
            
            # Wait for page to load
            time.sleep(3)
            
            # Check if we're logged in (look for editor)
            try:
                title_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='Post title']"))
                )
            except:
                print("🔐 Session expired. Re-authenticating...")
                cookies = self.login_and_get_cookies()
                if not cookies:
                    return False
                # Retry with new cookies
                driver.refresh()
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
                driver.get(f"{self.substack_url}/publish")
                title_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='Post title']"))
                )
            
            # Fill in the title
            title_input.clear()
            title_input.send_keys(title)
            
            # Add subtitle if provided
            if subtitle:
                try:
                    subtitle_input = driver.find_element(By.CSS_SELECTOR, "textarea[placeholder*='subtitle']")
                    subtitle_input.send_keys(subtitle)
                except:
                    print("⚠️ Could not find subtitle field")
            
            # Find and fill content area
            try:
                # Try different selectors for the content editor
                content_selectors = [
                    "div[contenteditable='true']",
                    ".ProseMirror",
                    "div[role='textbox']",
                    "div.editor"
                ]
                
                content_element = None
                for selector in content_selectors:
                    try:
                        content_element = driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue
                
                if content_element:
                    # Clear and add content
                    content_element.clear()
                    content_element.send_keys(content)
                else:
                    print("❌ Could not find content editor")
                    return False
                    
            except Exception as e:
                print(f"❌ Error filling content: {e}")
                return False
            
            # Add tags if provided
            if tags:
                try:
                    tags_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='tag']")
                    tags_input.send_keys(', '.join(tags))
                except:
                    print("⚠️ Could not find tags field")
            
            # Publish the article
            try:
                publish_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Publish')]")
                publish_button.click()
                
                # Wait for confirmation
                time.sleep(3)
                
                print(f"✅ Article '{title}' published to Substack!")
                return True
                
            except Exception as e:
                print(f"❌ Error publishing: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Substack publishing error: {e}")
            return False
        finally:
            if driver:
                driver.quit()

    def create_daily_intelligence_article(self, intelligence_data, signals_count=0):
        """Create and publish daily intelligence article"""
        
        timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y")
        
        title = f"daily energy intelligence • {timestamp.lower()}"
        
        subtitle = f"institutional-grade analysis of {signals_count} energy market signals"
        
        # Create article content
        content = f"""the energy markets are shifting. here's what institutional investors need to know.

## today's intelligence synthesis

{intelligence_data}

## methodology

our AI systems process multiple data streams simultaneously:

• **arxiv research papers** → emerging technology trends
• **patent filings** → corporate R&D directions  
• **SEC regulatory data** → financial market signals
• **OSINT intelligence** → market sentiment and news flow

## signal quality

today's analysis processed {signals_count} raw signals, identifying the highest-impact developments for energy sector positioning.

---

*this analysis is generated by AlphaENRG's automated intelligence system. not investment advice.*"""

        tags = ['energy', 'intelligence', 'investing', 'cleantech', 'markets']
        
        return self.publish_article(title, content, subtitle, tags)

def integrate_with_daily_agent(intelligence_text, signals_count=0):
    """Integration function for the main energy agent"""
    
    try:
        publisher = SubstackPublisher()
        
        # Create and publish daily intelligence article
        success = publisher.create_daily_intelligence_article(intelligence_text, signals_count)
        
        return success
        
    except Exception as e:
        print(f"❌ Substack publishing error: {e}")
        return False

def setup_substack_auth():
    """Helper function to set up Substack authentication"""
    
    print("🔐 Substack Authentication Setup")
    print("=" * 50)
    
    publisher = SubstackPublisher()
    
    if not publisher.email or not publisher.password:
        print("📝 Please add these to your .env file:")
        print("SUBSTACK_EMAIL=your_email@example.com")
        print("SUBSTACK_PASSWORD=your_password")
        print("SUBSTACK_URL=https://alphaenergy.substack.com")
        return False
    
    print("🔐 Attempting to login and save cookies...")
    cookies = publisher.login_and_get_cookies()
    
    if cookies:
        print("✅ Authentication successful!")
        print("🍪 Cookies saved for future automation")
        return True
    else:
        print("❌ Authentication failed")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        # Run authentication setup
        setup_substack_auth()
    else:
        # Test article publishing
        test_intelligence = """🔋 quantum battery patents surge 47% this quarter, with major breakthroughs in energy density

🌊 offshore wind development accelerating across northern europe, new installations exceeding targets

⚡ grid storage innovations reaching commercial viability, costs dropping below key thresholds

💰 clean energy VC funding up 23% quarter-over-quarter, signaling strong investor confidence"""
        
        result = integrate_with_daily_agent(test_intelligence, signals_count=156)
        print(f"Test publishing result: {result}")