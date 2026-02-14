# AlphaENRG Multi-Platform Automation

Automate publishing of energy intelligence to X/Twitter, Facebook, and Substack simultaneously.

## 🚀 Quick Setup

```bash
# 1. Install automation dependencies
./install_automation.sh

# 2. Configure all platforms
python setup_automation.py

# 3. Test publishing
python multi_platform_publisher.py test

# 4. Run full daily intelligence + publishing
python main_with_publishing.py --mode publish
```

## 📋 Platform Configuration

### X/Twitter API

1. Go to [developer.twitter.com](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app or use existing
3. Generate API keys and tokens
4. Add to `.env`:

```env
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

### Facebook Page API

1. Go to [developers.facebook.com](https://developers.facebook.com/)
2. Create a new app → Add Facebook Login and Pages products
3. Get a Page Access Token with permissions:
   - `pages_show_list`
   - `pages_read_engagement` 
   - `pages_manage_posts`
4. Use Graph API Explorer to get long-lived token
5. Add to `.env`:

```env
FACEBOOK_ACCESS_TOKEN=your_page_access_token
FACEBOOK_PAGE_ID=your_page_id
```

### Substack

1. Use your existing Substack account credentials
2. Add to `.env`:

```env
SUBSTACK_EMAIL=your_email@example.com
SUBSTACK_PASSWORD=your_password
SUBSTACK_URL=https://alphaenergy.substack.com
```

3. **Important**: Run authentication setup:
```bash
python substack_integration.py setup
```

This saves authentication cookies for automated publishing.

### Email Digest

1. Enable 2-factor authentication on Gmail
2. Generate an App Password:
   - Google Account settings → Security → 2-Step Verification → App passwords
   - Generate password for 'Mail'
3. Add to `.env`:

```env
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## 🤖 Automation Scripts

### `multi_platform_publisher.py`

Main publishing coordinator:

```bash
# Setup authentication for all platforms
python multi_platform_publisher.py setup

# Test posting to all platforms
python multi_platform_publisher.py test

# Post breaking alert
python multi_platform_publisher.py alert
```

### `main_with_publishing.py`

Full intelligence collection + publishing:

```bash
# Run daily intelligence collection and publish everywhere
python main_with_publishing.py --mode publish

# Run collection only (no publishing)
python main_with_publishing.py --mode daily

# Test collection (no database)
python main_with_publishing.py --mode test
```

### Individual Platform Scripts

```bash
# Facebook only
python facebook_integration.py

# Substack only  
python substack_integration.py

# X/Twitter only
python x_integration.py
```

## 📅 Daily Automation

The setup script creates `daily_publish.sh` for cron automation:

```bash
# Edit crontab
crontab -e

# Add line for daily 7 AM execution
0 7 * * * /path/to/energy-agent/daily_publish.sh
```

## 🔧 Content Templates

### X/Twitter Format
- Character limit optimized (280 chars)
- Uses emojis and hashtags
- 3-4 key bullet points

### Facebook Format  
- Longer form content
- Detailed signal counts
- Call-to-action for engagement
- Professional branding

### Substack Format
- Full article with methodology
- Detailed intelligence analysis
- Professional investment-focused tone
- Tagged with energy/investing topics

## 📊 Publishing Flow

1. **Collection**: Gather signals from ArXiv, SEC, Patents, OSINT
2. **Scoring**: AI-powered relevance and impact scoring
3. **Intelligence**: Generate platform-optimized summaries
4. **Publishing**: Simultaneous distribution across platforms
5. **Reporting**: Email digest to oc@cloudmonkey.io

## ⚠️ Troubleshooting

### Chrome/ChromeDriver Issues
```bash
# macOS
brew install --cask chromedriver

# Linux
sudo apt-get install chromium-chromedriver
```

### Substack Authentication
```bash
# Re-run authentication setup
python substack_integration.py setup

# Check cookies file
ls substack_cookies.json
```

### Facebook API Errors
- Check token expiration (Graph API Explorer)
- Verify page permissions
- Test with Graph API manually

### Twitter API Rate Limits
- Built-in rate limiting with `wait_on_rate_limit=True`
- Monitor rate limit status in logs

## 🎯 Integration with Existing Agent

The automation integrates seamlessly with your existing energy intelligence agent:

- **Database**: Uses same SQLite database for signal storage
- **Scoring**: Same AI scoring engine for signal ranking  
- **Configuration**: Extends existing `.env` configuration
- **Logging**: Unified logging to `logs/agent.log`

## 📈 Monitoring

Check logs for publishing status:
```bash
tail -f logs/agent.log | grep -E "(SUCCESS|FAILED|ERROR)"
```

## 🔐 Security Notes

- Store credentials in `.env` file (never commit to git)
- Use app-specific passwords for email
- Substack cookies contain session data (keep secure)
- Facebook tokens should be long-lived for automation

## 🚀 Next Steps

1. **Setup**: Run through platform configuration
2. **Test**: Verify all platforms work with test content
3. **Automate**: Add to cron for daily execution
4. **Monitor**: Check logs for any failed publications
5. **Optimize**: Adjust content templates based on engagement