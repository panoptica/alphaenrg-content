#!/usr/bin/env python3
"""
AlphaENRG Automation Setup Script

Helps configure all required API keys and credentials for multi-platform publishing.
"""

import os
from pathlib import Path
from dotenv import load_dotenv, set_key
import json

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def check_env_var(var_name, description, current_value=None):
    """Check and optionally set environment variable"""
    
    if current_value:
        print(f"✅ {var_name}: Already configured")
        return True
    else:
        print(f"❌ {var_name}: Missing")
        print(f"   Description: {description}")
        return False

def setup_twitter_credentials():
    """Setup Twitter/X API credentials"""
    
    print_header("Twitter/X API Setup")
    
    env_vars = {
        'TWITTER_API_KEY': 'Twitter API Key (from developer.twitter.com)',
        'TWITTER_API_SECRET': 'Twitter API Secret',
        'TWITTER_ACCESS_TOKEN': 'Twitter Access Token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'Twitter Access Token Secret'
    }
    
    all_configured = True
    
    for var_name, description in env_vars.items():
        current_value = os.getenv(var_name)
        if not check_env_var(var_name, description, current_value):
            all_configured = False
    
    if not all_configured:
        print("\n📝 To configure Twitter/X:")
        print("1. Go to https://developer.twitter.com/en/portal/dashboard")
        print("2. Create a new app or use existing")
        print("3. Generate API keys and tokens")
        print("4. Add them to your .env file:")
        print("\nTWITTER_API_KEY=your_api_key")
        print("TWITTER_API_SECRET=your_api_secret")
        print("TWITTER_ACCESS_TOKEN=your_access_token")
        print("TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret")
        
        return False
    
    return True

def setup_facebook_credentials():
    """Setup Facebook API credentials"""
    
    print_header("Facebook API Setup")
    
    env_vars = {
        'FACEBOOK_ACCESS_TOKEN': 'Facebook Page Access Token (long-lived)',
        'FACEBOOK_PAGE_ID': 'Facebook Page ID'
    }
    
    all_configured = True
    
    for var_name, description in env_vars.items():
        current_value = os.getenv(var_name)
        if not check_env_var(var_name, description, current_value):
            all_configured = False
    
    if not all_configured:
        print("\n📝 To configure Facebook:")
        print("1. Go to https://developers.facebook.com/")
        print("2. Create a new app or use existing")
        print("3. Add Facebook Login and Pages products")
        print("4. Get a Page Access Token with these permissions:")
        print("   - pages_show_list")
        print("   - pages_read_engagement") 
        print("   - pages_manage_posts")
        print("5. Use Graph API Explorer to get long-lived token")
        print("6. Add to your .env file:")
        print("\nFACEBOOK_ACCESS_TOKEN=your_page_access_token")
        print("FACEBOOK_PAGE_ID=your_page_id")
        
        return False
    
    return True

def setup_substack_credentials():
    """Setup Substack credentials"""
    
    print_header("Substack Setup")
    
    env_vars = {
        'SUBSTACK_EMAIL': 'Your Substack account email',
        'SUBSTACK_PASSWORD': 'Your Substack account password',
        'SUBSTACK_URL': 'Your Substack URL (e.g., https://alphaenergy.substack.com)'
    }
    
    all_configured = True
    
    for var_name, description in env_vars.items():
        current_value = os.getenv(var_name)
        if not check_env_var(var_name, description, current_value):
            all_configured = False
    
    if not all_configured:
        print("\n📝 To configure Substack:")
        print("1. Use your existing Substack account credentials")
        print("2. Add to your .env file:")
        print("\nSUBSTACK_EMAIL=your_email@example.com")
        print("SUBSTACK_PASSWORD=your_password")
        print("SUBSTACK_URL=https://alphaenergy.substack.com")
        print("\n⚠️  Note: After setup, run 'python substack_integration.py setup'")
        print("   to save authentication cookies for automation")
        
        return False
    
    return True

def setup_email_credentials():
    """Setup email credentials for digest"""
    
    print_header("Email Setup")
    
    env_vars = {
        'EMAIL_USER': 'Your Gmail address for sending digests',
        'EMAIL_PASSWORD': 'Gmail App Password (not your regular password)',
        'SMTP_SERVER': 'SMTP server (default: smtp.gmail.com)',
        'SMTP_PORT': 'SMTP port (default: 587)'
    }
    
    all_configured = True
    
    for var_name, description in env_vars.items():
        current_value = os.getenv(var_name)
        if not check_env_var(var_name, description, current_value):
            all_configured = False
    
    if not all_configured:
        print("\n📝 To configure email:")
        print("1. Enable 2-factor authentication on Gmail")
        print("2. Generate an App Password:")
        print("   - Go to Google Account settings")
        print("   - Security → 2-Step Verification → App passwords")
        print("   - Generate password for 'Mail'")
        print("3. Add to your .env file:")
        print("\nEMAIL_USER=your_email@gmail.com")
        print("EMAIL_PASSWORD=your_app_password")
        print("SMTP_SERVER=smtp.gmail.com")
        print("SMTP_PORT=587")
        
        return False
    
    return True

def create_cron_script():
    """Create cron script for daily automation"""
    
    script_path = Path(__file__).parent / "daily_publish.sh"
    
    script_content = f"""#!/bin/bash

# AlphaENRG Daily Publishing Script
# Run this daily via cron for automated intelligence publishing

cd {Path(__file__).parent}

# Activate virtual environment
source venv/bin/activate

# Run daily collection and publishing
echo "$(date): Starting AlphaENRG daily run..."
python main_with_publishing.py --mode publish

echo "$(date): AlphaENRG daily run completed."
"""
    
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        print(f"✅ Created executable script: {script_path}")
        print("\n📅 To add to cron for daily 7 AM execution:")
        print(f"   crontab -e")
        print(f"   Add line: 0 7 * * * {script_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create cron script: {e}")
        return False

def test_integrations():
    """Test all platform integrations"""
    
    print_header("Testing Platform Integrations")
    
    try:
        # Test multi-platform publisher
        from multi_platform_publisher import MultiPlatformPublisher
        
        publisher = MultiPlatformPublisher()
        
        if not publisher.failed_platforms:
            print("✅ All platforms initialized successfully")
            print("🧪 Run 'python multi_platform_publisher.py test' to test posting")
            return True
        else:
            print(f"❌ Failed platforms: {', '.join(publisher.failed_platforms)}")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Main setup function"""
    
    print("🚀 AlphaENRG Multi-Platform Automation Setup")
    print("=" * 60)
    
    # Load existing environment
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
    
    # Check all platforms
    twitter_ok = setup_twitter_credentials()
    facebook_ok = setup_facebook_credentials() 
    substack_ok = setup_substack_credentials()
    email_ok = setup_email_credentials()
    
    # Create automation script
    print_header("Automation Setup")
    cron_ok = create_cron_script()
    
    # Test integrations
    if all([twitter_ok, facebook_ok, substack_ok, email_ok]):
        test_ok = test_integrations()
    else:
        test_ok = False
        print("⚠️ Skipping integration test (credentials missing)")
    
    # Final summary
    print_header("Setup Summary")
    
    platforms = {
        'Twitter/X': twitter_ok,
        'Facebook': facebook_ok,
        'Substack': substack_ok,
        'Email': email_ok,
        'Automation': cron_ok
    }
    
    for platform, status in platforms.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {platform}")
    
    configured_count = sum(platforms.values())
    total_count = len(platforms)
    
    if configured_count == total_count:
        print(f"\n🎉 All platforms configured! ({configured_count}/{total_count})")
        print("\n🚀 Next steps:")
        print("1. Test posting: python multi_platform_publisher.py test")
        print("2. Setup Substack auth: python substack_integration.py setup")
        print("3. Run daily digest: python main_with_publishing.py --mode publish")
        print("4. Add to cron: crontab -e")
        
    else:
        print(f"\n⚠️ {total_count - configured_count} platforms need configuration")
        print("📝 See instructions above for missing platforms")

if __name__ == "__main__":
    main()