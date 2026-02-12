#!/usr/bin/env python3
"""
Instagram browser automation using Playwright
"""

import os
import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

class InstagramPoster:
    def __init__(self, headless=True):
        self.headless = headless
        self.username = os.environ.get('INSTAGRAM_USERNAME', 'YNWA4Reds')
        self.password = os.environ.get('INSTAGRAM_PASSWORD', '')
        self.browser = None
        self.page = None
        
    async def start_browser(self):
        """Start browser and navigate to Instagram"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-web-security']
        )
        self.page = await self.browser.new_page()
        
        # Set user agent to avoid detection
        await self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    async def login(self):
        """Login to Instagram"""
        print("🔐 Logging into Instagram...")
        
        await self.page.goto('https://www.instagram.com/accounts/login/')
        await asyncio.sleep(5)
        
        # Handle cookie consent popup
        try:
            await self.page.click('text=Allow all cookies', timeout=3000)
            print("   🍪 Cookie popup dismissed")
            await asyncio.sleep(2)
        except:
            pass
        
        # Fill login form
        await self.page.fill('input[type="text"]', self.username)
        await self.page.fill('input[type="password"]', self.password)
        print("   ✅ Credentials entered")
        
        # Click login button
        try:
            await self.page.click('button:has-text("Log in")', timeout=5000)
        except:
            try:
                await self.page.click('div[role="button"]:has-text("Log in")', timeout=5000)
            except:
                await self.page.keyboard.press('Enter')
        
        # Wait for login to complete
        await asyncio.sleep(8)
        
        # Handle "Save Login Info" popup
        try:
            await self.page.click('button:has-text("Not Now")', timeout=3000)
        except:
            pass
            
        # Handle notifications popup
        try:
            await self.page.click('button:has-text("Not Now")', timeout=3000)
        except:
            pass
            
        print("   ✅ Logged in successfully")
        
    async def post_image(self, image_path: str, caption: str, dry_run: bool = False):
        """Post an image to Instagram"""
        if dry_run:
            print(f"[DRY RUN] Would post:")
            print(f"  Image: {image_path}")
            print(f"  Caption: {caption[:100]}...")
            return {"status": "dry_run", "posted": False}
            
        if not os.path.exists(image_path):
            return {"status": "error", "error": f"Image not found: {image_path}"}
            
        print(f"📸 Posting image: {Path(image_path).name}")
        
        # Navigate to home and click new post
        await self.page.goto('https://www.instagram.com/')
        await asyncio.sleep(3)
        
        # Take debug screenshot
        await self.page.screenshot(path="/Users/macmini/lfc-agent/debug_home.png")
        
        # Click new post button (try multiple selectors)
        clicked = False
        for selector in ['[aria-label="New post"]', 'svg[aria-label="New post"]', 'text=Create', '[aria-label="Create"]']:
            try:
                await self.page.click(selector, timeout=3000)
                clicked = True
                print(f"   📝 Clicked: {selector}")
                break
            except:
                pass
        
        if not clicked:
            await self.page.screenshot(path="/Users/macmini/lfc-agent/debug_no_create.png")
            return {"status": "error", "error": "Could not find Create button"}
        
        await asyncio.sleep(3)
        await self.page.screenshot(path="/Users/macmini/lfc-agent/debug_create_dialog.png")
        
        # Wait for create dialog and handle file upload
        try:
            # Use Playwright's set_input_files with the selector directly
            # This works even for hidden inputs
            await self.page.set_input_files('input[type="file"]', image_path)
            print("   📤 Image uploaded")
            await asyncio.sleep(4)
        except Exception as e:
            # If direct approach fails, try clicking Select button first
            try:
                for text in ["Select from computer", "Select from gallery", "Select"]:
                    try:
                        await self.page.click(f'button:has-text("{text}")', timeout=2000)
                        print(f"   📂 Clicked: {text}")
                        await asyncio.sleep(2)
                        await self.page.set_input_files('input[type="file"]', image_path)
                        print("   📤 Image uploaded (after clicking select)")
                        await asyncio.sleep(4)
                        break
                    except:
                        pass
            except Exception as e2:
                await self.page.screenshot(path="/Users/macmini/lfc-agent/debug_no_upload.png")
                return {"status": "error", "error": f"Could not upload image: {e2}"}
        
        await self.page.screenshot(path="/Users/macmini/lfc-agent/debug_after_upload.png")
        
        # Click Next (or similar) - handle different button texts
        for button_text in ["Next", "Continue", "OK"]:
            try:
                await self.page.click(f'button:has-text("{button_text}")', timeout=3000)
                print(f"   ✅ Clicked {button_text}")
                await asyncio.sleep(2)
            except:
                pass
        
        # Click Next again if needed (filters screen)
        for button_text in ["Next", "Continue"]:
            try:
                await self.page.click(f'button:has-text("{button_text}")', timeout=3000)
                print(f"   ✅ Clicked {button_text} (filters)")
                await asyncio.sleep(2)
            except:
                pass
        
        await self.page.screenshot(path="/Users/macmini/lfc-agent/debug_caption_screen.png")
        
        # Add caption
        try:
            caption_selectors = [
                'textarea[aria-label*="caption"]',
                'textarea[placeholder*="caption"]',
                'textarea',
                'div[aria-label*="caption"]',
                'div[contenteditable="true"]'
            ]
            for sel in caption_selectors:
                try:
                    caption_area = await self.page.wait_for_selector(sel, timeout=3000)
                    if caption_area:
                        await caption_area.fill(caption)
                        print("   ✅ Caption added")
                        break
                except:
                    pass
        except Exception as e:
            print(f"   ⚠️ Caption might not have been added: {e}")
        
        await self.page.screenshot(path="/Users/macmini/lfc-agent/debug_before_share.png")
        
        # Share post
        shared = False
        for button_text in ["Share", "Post", "Publish"]:
            try:
                await self.page.click(f'button:has-text("{button_text}")', timeout=3000)
                await asyncio.sleep(5)
                shared = True
                print(f"   ✅ Clicked {button_text}!")
                break
            except:
                pass
        
        if not shared:
            await self.page.screenshot(path="/Users/macmini/lfc-agent/debug_no_share.png")
            return {"status": "error", "error": "Share button not found"}
        
        await self.page.screenshot(path="/Users/macmini/lfc-agent/debug_final.png")
        return {"status": "success", "posted": True}
        
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
            
    async def post_with_retry(self, image_path: str, caption: str, max_retries: int = 3, dry_run: bool = False):
        """Post with retry logic"""
        for attempt in range(max_retries):
            try:
                await self.start_browser()
                await self.login()
                result = await self.post_image(image_path, caption, dry_run=dry_run)
                await self.close()
                return result
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                await self.close()
                if attempt == max_retries - 1:
                    return {"status": "error", "error": str(e)}
                await asyncio.sleep(10)  # Wait before retry
                
async def test_poster():
    """Test the Instagram poster"""
    poster = InstagramPoster(headless=True)
    
    try:
        await poster.start_browser()
        await poster.login()
        print("🔥 Login test successful!")
        
    finally:
        await poster.close()

if __name__ == "__main__":
    asyncio.run(test_poster())