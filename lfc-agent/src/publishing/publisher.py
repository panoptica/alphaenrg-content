#!/usr/bin/env python3
"""
Instagram Publisher - Posts content via Meta Graph API.
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

GRAPH_API_VERSION = 'v18.0'
BASE_URL = f'https://graph.facebook.com/{GRAPH_API_VERSION}'


class InstagramPublisher:
    def __init__(self):
        self.access_token = os.environ.get('FACEBOOK_ACCESS_TOKEN')
        self.ig_account_id = os.environ.get('INSTAGRAM_ACCOUNT_ID')
        
        if not self.access_token or not self.ig_account_id:
            print("⚠️  Warning: Meta API credentials not configured")
    
    def _check_credentials(self):
        if not self.access_token or not self.ig_account_id:
            raise ValueError("Meta API credentials not configured. Set FACEBOOK_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID")
    
    def publish_image(self, image_url: str, caption: str, dry_run: bool = False) -> dict:
        """
        Publish a single image post to Instagram.
        
        Args:
            image_url: Publicly accessible URL of the image
            caption: Post caption including hashtags
            dry_run: If True, validate but don't actually post
        
        Returns:
            dict with post details or error
        """
        self._check_credentials()
        
        if dry_run:
            print(f"[DRY RUN] Would post image:")
            print(f"  URL: {image_url}")
            print(f"  Caption: {caption[:100]}...")
            return {"status": "dry_run", "would_post": True}
        
        # Step 1: Create media container
        container_url = f"{BASE_URL}/{self.ig_account_id}/media"
        container_params = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }
        
        container_response = requests.post(container_url, data=container_params)
        container_data = container_response.json()
        
        if 'error' in container_data:
            return {"status": "error", "error": container_data['error']}
        
        creation_id = container_data.get('id')
        
        # Step 2: Wait for container to be ready
        status_url = f"{BASE_URL}/{creation_id}"
        for _ in range(10):  # Max 10 attempts
            status_response = requests.get(status_url, params={
                "fields": "status_code",
                "access_token": self.access_token
            })
            status_data = status_response.json()
            
            if status_data.get('status_code') == 'FINISHED':
                break
            elif status_data.get('status_code') == 'ERROR':
                return {"status": "error", "error": "Media container failed to process"}
            
            time.sleep(2)
        
        # Step 3: Publish the container
        publish_url = f"{BASE_URL}/{self.ig_account_id}/media_publish"
        publish_params = {
            "creation_id": creation_id,
            "access_token": self.access_token
        }
        
        publish_response = requests.post(publish_url, data=publish_params)
        publish_data = publish_response.json()
        
        if 'error' in publish_data:
            return {"status": "error", "error": publish_data['error']}
        
        return {
            "status": "success",
            "post_id": publish_data.get('id'),
            "creation_id": creation_id
        }
    
    def publish_carousel(self, image_urls: list, caption: str, dry_run: bool = False) -> dict:
        """
        Publish a carousel (multiple images) post.
        """
        self._check_credentials()
        
        if dry_run:
            print(f"[DRY RUN] Would post carousel with {len(image_urls)} images")
            return {"status": "dry_run", "would_post": True}
        
        # Create containers for each image
        children = []
        for url in image_urls:
            container_url = f"{BASE_URL}/{self.ig_account_id}/media"
            params = {
                "image_url": url,
                "is_carousel_item": "true",
                "access_token": self.access_token
            }
            response = requests.post(container_url, data=params)
            data = response.json()
            
            if 'error' in data:
                return {"status": "error", "error": data['error'], "stage": "carousel_item"}
            
            children.append(data['id'])
        
        # Create carousel container
        carousel_url = f"{BASE_URL}/{self.ig_account_id}/media"
        carousel_params = {
            "media_type": "CAROUSEL",
            "children": ','.join(children),
            "caption": caption,
            "access_token": self.access_token
        }
        
        carousel_response = requests.post(carousel_url, data=carousel_params)
        carousel_data = carousel_response.json()
        
        if 'error' in carousel_data:
            return {"status": "error", "error": carousel_data['error'], "stage": "carousel_container"}
        
        # Wait and publish
        time.sleep(3)
        
        publish_url = f"{BASE_URL}/{self.ig_account_id}/media_publish"
        publish_params = {
            "creation_id": carousel_data['id'],
            "access_token": self.access_token
        }
        
        publish_response = requests.post(publish_url, data=publish_params)
        publish_data = publish_response.json()
        
        if 'error' in publish_data:
            return {"status": "error", "error": publish_data['error'], "stage": "publish"}
        
        return {
            "status": "success",
            "post_id": publish_data.get('id')
        }
    
    def publish_reel(self, video_url: str, caption: str, cover_url: str = None, dry_run: bool = False) -> dict:
        """
        Publish a Reel (video) to Instagram.
        """
        self._check_credentials()
        
        if dry_run:
            print(f"[DRY RUN] Would post reel")
            return {"status": "dry_run", "would_post": True}
        
        container_url = f"{BASE_URL}/{self.ig_account_id}/media"
        container_params = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": self.access_token
        }
        
        if cover_url:
            container_params["cover_url"] = cover_url
        
        container_response = requests.post(container_url, data=container_params)
        container_data = container_response.json()
        
        if 'error' in container_data:
            return {"status": "error", "error": container_data['error']}
        
        creation_id = container_data.get('id')
        
        # Videos take longer to process
        status_url = f"{BASE_URL}/{creation_id}"
        for _ in range(30):  # Max 30 attempts (60 seconds)
            status_response = requests.get(status_url, params={
                "fields": "status_code",
                "access_token": self.access_token
            })
            status_data = status_response.json()
            
            if status_data.get('status_code') == 'FINISHED':
                break
            elif status_data.get('status_code') == 'ERROR':
                return {"status": "error", "error": "Video processing failed"}
            
            time.sleep(2)
        
        # Publish
        publish_url = f"{BASE_URL}/{self.ig_account_id}/media_publish"
        publish_params = {
            "creation_id": creation_id,
            "access_token": self.access_token
        }
        
        publish_response = requests.post(publish_url, data=publish_params)
        publish_data = publish_response.json()
        
        if 'error' in publish_data:
            return {"status": "error", "error": publish_data['error']}
        
        return {
            "status": "success",
            "post_id": publish_data.get('id')
        }
    
    def get_post_insights(self, post_id: str) -> dict:
        """
        Fetch engagement metrics for a post.
        """
        self._check_credentials()
        
        url = f"{BASE_URL}/{post_id}/insights"
        params = {
            "metric": "impressions,reach,likes,comments,saved,shares",
            "access_token": self.access_token
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'error' in data:
            return {"status": "error", "error": data['error']}
        
        metrics = {}
        for item in data.get('data', []):
            metrics[item['name']] = item['values'][0]['value']
        
        return {"status": "success", "metrics": metrics}


def test_publisher():
    """Test the publisher (dry run)."""
    print("Testing Instagram Publisher")
    print("=" * 50)
    
    publisher = InstagramPublisher()
    
    # Test dry run
    result = publisher.publish_image(
        image_url="https://example.com/test.jpg",
        caption="Test caption #LFC #YNWA",
        dry_run=True
    )
    
    print(f"Result: {result}")


if __name__ == "__main__":
    test_publisher()
