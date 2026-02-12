# LFC SOCIAL AGENT - TECHNICAL SPECIFICATION

## Project Overview

**Goal:** Automated social media content generation and posting system for Liverpool FC community engagement, starting with Instagram, expanding to Facebook, X, and TikTok.

**Launch Target:** Pre-match content for LFC vs Manchester City, Sunday 9 Feb 2025, 4:30pm Anfield kickoff.

**Timeline:** 48 hours to MVP (Thursday/Friday build, Saturday/Sunday posting).

**Instagram Account:** @YNWA4Reds

---

## System Architecture

```
┌─────────────────┐
│ Fixture Monitor │──> Triggers content cycle based on next match
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Content Sourcer │──> Scrapes/downloads images, videos, quotes, stats
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Content DB    │──> PostgreSQL storage of all assets + metadata
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Content Generator│──> Claude generates captions + selects assets
│   (Claude API)   │──> Produces 3 variants per post type
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Visual Compositor│──> FFmpeg/Pillow creates final images/videos
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Review Gate    │──> Human approval via web dashboard (Phase 1)
│   (Next.js UI)  │──> Auto-publish in Phase 2
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Scheduler     │──> Meta Graph API posts to Instagram
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Analytics Tracker│──> Pulls engagement data, feeds back to generator
└─────────────────┘
```

---

## Component Specifications

### 1. FIXTURE MONITOR

**File:** `src/fixtures/monitor.py`

**Purpose:** Detect upcoming fixtures and trigger content generation cycles.

**Inputs:**
- LFC official fixture calendar (primary source)
- API-Football.com (backup/validation)

**Logic:**
```python
def should_trigger_content(fixture):
    days_until_match = (fixture.date - today).days
    
    if fixture.is_rival and days_until_match == 7:
        return True  # Big games: 7 days out
    elif days_until_match == 3:
        return True  # Regular games: 3 days out
    elif days_since_last_match == 1:
        return True  # Day after match: prep for next
    
    return False
```

**Rival detection:**
```python
RIVALS = [
    "Manchester City",
    "Manchester United", 
    "Arsenal",
    "Chelsea",
    "Everton",
    "Real Madrid",
    "Barcelona"
]
```

**Output:** 
```json
{
    "fixture_id": 12345,
    "opponent": "Manchester City",
    "date": "2025-02-09T16:30:00Z",
    "competition": "Premier League",
    "venue": "Anfield",
    "is_rival": true,
    "days_until": 3
}
```

**Schedule:** Runs daily at 9am GMT via cron.

---

### 2. CONTENT SOURCER

**File:** `src/content/sourcer.py`

**Purpose:** Gather raw content assets from multiple sources.

**Sources:**

#### 2.1 YouTube (via yt-dlp)
```python
# Search queries for LFC vs City
queries = [
    "Liverpool Manchester City Gerrard",
    "Liverpool Manchester City 2019 Champions League",
    "Liverpool Manchester City Anfield atmosphere",
    "Liverpool fans YNWA",
]

# Download constraints
max_duration = 180  # 3 minutes
resolution = "720p"
format = "mp4"
```

**Attribution:** Store channel name + video URL in DB.

#### 2.2 Twitter/X Scraping
```python
# Accounts to monitor
accounts = [
    "@LFC",
    "@TheKopTimes", 
    "@AnfieldWatch",
    "@JamieCarragher",
    "@Robbo_Scotland",
    # Add fan content creators
]

# Content filters
filters = {
    "media_only": True,
    "min_likes": 100,
    "exclude_retweets": True
}
```

**Attribution:** Include original tweet URL + author handle.

#### 2.3 Wikimedia Commons
```python
# Search terms
search_terms = [
    "Liverpool FC 1970s",
    "Liverpool FC 1980s",
    "Anfield stadium historical",
    "Liverpool FC trophy celebrations"
]

# License filter
allowed_licenses = [
    "CC0",
    "CC-BY",
    "CC-BY-SA",
    "Public Domain"
]
```

#### 2.4 Quotes Database (Manual Curation + Web Scraping)

**Sources:**
- LFC official site interviews
- This Is Anfield articles
- Player autobiographies (Gerrard, Dalglish, etc.)
- Manager press conferences

**Schema:**
```json
{
    "quote": "This means more",
    "author": "Jürgen Klopp",
    "context": "2019 Champions League Final",
    "year": 2019,
    "tags": ["Champions League", "emotional", "identity"]
}
```

#### 2.5 Stats Database

**Sources:**
- Transfermarkt (web scraping)
- Football-Data.org API
- LFC official stats
- StatsBomb (if budget allows)

**Key stats for LFC vs City:**
```json
{
    "head_to_head": {
        "total_matches": 195,
        "lfc_wins": 92,
        "city_wins": 58,
        "draws": 45,
        "anfield_record": "LFC 54 wins, City 16 wins"
    },
    "notable_results": [
        {"date": "2018-01-14", "score": "4-3", "competition": "Premier League", "note": "Firmino late winner"},
        {"date": "2014-04-13", "score": "3-2", "competition": "Premier League", "note": "Gerrard slip"},
        {"date": "2022-04-10", "score": "2-2", "competition": "Premier League", "note": "Title race clash"}
    ]
}
```

**Copyright Risk Assessment:**
Each asset tagged:
- `LOW`: User-generated, Wikimedia CC, official LFC (with attribution)
- `MEDIUM`: Twitter screenshots, short YouTube clips (<30s)
- `HIGH`: Broadcaster footage, Getty Images, AP photos

**Store only LOW and MEDIUM initially.**

---

### 3. CONTENT DATABASE

**Database:** PostgreSQL 15+

**Location:** Mac Mini M4 (`localhost:5432`)

**Schema:**

```sql
-- Fixtures
CREATE TABLE fixtures (
    id SERIAL PRIMARY KEY,
    opponent VARCHAR(100) NOT NULL,
    match_date TIMESTAMP NOT NULL,
    competition VARCHAR(50),
    venue VARCHAR(50),
    is_rival BOOLEAN DEFAULT FALSE,
    is_home BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Content Assets
CREATE TABLE content_assets (
    id SERIAL PRIMARY KEY,
    type VARCHAR(20) NOT NULL, -- 'image', 'video', 'quote', 'stat'
    source_type VARCHAR(30), -- 'youtube', 'twitter', 'wikimedia', 'manual'
    source_url TEXT,
    local_path TEXT, -- Storage path on Mac Mini
    attribution TEXT, -- "Image: @username" or "Video: YouTube/ChannelName"
    copyright_risk VARCHAR(10), -- 'low', 'medium', 'high'
    tags TEXT[], -- PostgreSQL array: ['City', 'Gerrard', '2014']
    metadata JSONB, -- Flexible storage for dimensions, duration, etc.
    created_at TIMESTAMP DEFAULT NOW()
);

-- Quotes
CREATE TABLE quotes (
    id SERIAL PRIMARY KEY,
    quote_text TEXT NOT NULL,
    author VARCHAR(100),
    context TEXT,
    year INT,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Stats
CREATE TABLE stats (
    id SERIAL PRIMARY KEY,
    stat_type VARCHAR(50), -- 'head_to_head', 'player_record', 'historical'
    opponent VARCHAR(100),
    stat_data JSONB, -- Flexible JSON structure
    created_at TIMESTAMP DEFAULT NOW()
);

-- Generated Posts
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    fixture_id INT REFERENCES fixtures(id),
    content_type VARCHAR(30), -- 'iconic_moment', 'stat_graphic', 'famous_red', etc.
    variants JSONB, -- Array of 3 variants with captions, hashtags, CTAs
    selected_variant INT, -- 0, 1, or 2 (A, B, or C)
    asset_ids INT[], -- References to content_assets used
    scheduled_time TIMESTAMP,
    posted BOOLEAN DEFAULT FALSE,
    post_url TEXT, -- Instagram post URL after publishing
    performance JSONB, -- {likes, comments, shares, reach, impressions}
    created_at TIMESTAMP DEFAULT NOW()
);

-- Engagement Metrics (time-series tracking)
CREATE TABLE engagement_metrics (
    id SERIAL PRIMARY KEY,
    post_id INT REFERENCES posts(id),
    measured_at TIMESTAMP DEFAULT NOW(),
    likes INT,
    comments INT,
    shares INT,
    saves INT,
    reach INT,
    impressions INT
);

-- Indexes for performance
CREATE INDEX idx_fixtures_date ON fixtures(match_date);
CREATE INDEX idx_assets_tags ON content_assets USING GIN(tags);
CREATE INDEX idx_posts_fixture ON posts(fixture_id);
CREATE INDEX idx_posts_scheduled ON posts(scheduled_time);
```

---

### 4. CONTENT GENERATOR (Claude Integration)

**File:** `src/generation/generator.py`

**Purpose:** Generate caption variants using Claude Sonnet 4.

**Prompt Templates:**

#### Template: Iconic Moment
```python
PROMPT_ICONIC = """
You are creating Instagram content for a Liverpool FC community account focused on club history and identity.

FIXTURE: Liverpool vs {opponent}, {date}
CONTENT TYPE: Iconic Moment
SELECTED ASSET: {asset_description}
HISTORICAL CONTEXT: {context}

Create 3 caption variants optimized for Instagram engagement:

VARIANT A - HEROIC/EMOTIONAL:
- Tone: Goosebumps, pride, "this is why we support this club"
- Hook: Powerful opening line that stops the scroll
- Length: 200-280 characters
- Hashtags: 12-15 mix of popular (#LFC, #YNWA) + niche (#Anfield, #ThisMeansMore)

VARIANT B - CEREBRAL/STAT-DRIVEN:
- Tone: Intelligent, pattern-spotting, "notice this detail"
- Include 2-3 specific stats or historical facts
- Hook: Question or surprising fact
- Length: 180-250 characters
- Hashtags: 10-12, include #LFCHistory

VARIANT C - CHEEKY/BANTER:
- Tone: Scouse wit, confident, playful dig at rivals
- Reference {opponent} without being mean-spirited
- Hook: Provocative but clever
- Length: 150-220 characters
- Hashtags: 10-12, can include #PremierLeague

RULES:
- First sentence must grab attention immediately
- No corporate speak or clichés
- Authentic Scouse voice where appropriate (but accessible to international audience)
- Build the Liverpool mythology without exaggeration
- Include call-to-action: "Drop your favourite memory 👇" or similar
- No emojis except strategically (1-3 max per variant)

OUTPUT FORMAT (JSON):
{
    "variant_a": {
        "caption": "...",
        "hashtags": ["LFC", "YNWA", ...],
        "cta": "..."
    },
    "variant_b": {...},
    "variant_c": {...}
}
"""
```

#### Template: Famous Red
```python
PROMPT_FAMOUS_RED = """
You are creating Instagram content connecting Liverpool FC to notable supporters.

FAMOUS RED: {name}
ACHIEVEMENT: {achievement}
CONNECTION TO LFC: {lfc_connection}
UPCOMING FIXTURE: Liverpool vs {opponent}

Create 3 caption variants that:
1. Celebrate the individual's achievement
2. Highlight their Liverpool connection
3. Tie it subtly to the upcoming match

VARIANT A - ASPIRATIONAL:
"From the Kop to [achievement venue]" narrative

VARIANT B - CEREBRAL:  
Facts + connection theme (e.g., "intelligence" for Demis)

VARIANT C - PLAYFUL:
Contrast achievement with rival (e.g., Nobel Prize vs oil money)

Same formatting rules as above.
"""
```

#### Template: Stat Graphic
```python
PROMPT_STAT_GRAPHIC = """
FIXTURE: Liverpool vs {opponent}
STAT DATA: {stat_json}

Create 3 caption variants that:
- Present the stat compellingly
- Add context or narrative
- Make it Instagram-friendly (not just numbers)

VARIANT A: History repeats itself angle
VARIANT B: Dominance/rivalry angle  
VARIANT C: "The numbers don't lie" angle

Include visual composition suggestions for the graphic:
- Primary stat (headline)
- Supporting stats (2-3 data points)
- Color scheme (LFC red + neutral)
- Font hierarchy
"""
```

**Claude API Configuration:**
```python
import anthropic

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

def generate_variants(prompt_template, context):
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt_template.format(**context)}
        ]
    )
    
    # Parse JSON response
    variants = json.loads(message.content[0].text)
    return variants
```

---

### 5. VISUAL COMPOSITOR

**File:** `src/visuals/compositor.py`

**Purpose:** Create final Instagram-ready images and videos.

**Image Composition (Pillow/PIL):**

```python
from PIL import Image, ImageDraw, ImageFont

def create_stat_graphic(stat_data, template="modern"):
    # Base canvas
    img = Image.new('RGB', (1080, 1350), color='#C8102E')  # LFC red
    draw = ImageDraw.Draw(img)
    
    # Fonts
    font_headline = ImageFont.truetype("fonts/Montserrat-Bold.ttf", 72)
    font_stat = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 48)
    font_label = ImageFont.truetype("fonts/Montserrat-Light.ttf", 32)
    
    # Headline stat (centered, large)
    headline = stat_data['headline']  # e.g., "92 WINS"
    draw.text((540, 400), headline, fill='white', font=font_headline, anchor="mm")
    
    # Context label
    label = stat_data['label']  # e.g., "Liverpool vs City (All Time)"
    draw.text((540, 500), label, fill='#F9DC5C', font=font_label, anchor="mm")
    
    # Supporting stats (bottom third)
    # ... layout logic
    
    # Watermark
    draw.text((50, 1300), "@YNWA4Reds", fill='rgba(255,255,255,0.7)', font=font_label)
    
    return img
```

**Video Composition (FFmpeg):**

```python
import subprocess

def create_video_post(video_path, text_overlay, duration=30):
    output_path = f"output/{uuid.uuid4()}.mp4"
    
    # FFmpeg command
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-ss', '0',  # Start time
        '-t', str(duration),  # Duration
        '-vf', f"drawtext=text='{text_overlay}':fontcolor=white:fontsize=48:box=1:boxcolor=black@0.5:boxborderw=10:x=(w-text_w)/2:y=h-th-50",
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-aspect', '4:5',  # Instagram feed ratio
        output_path
    ]
    
    subprocess.run(cmd, check=True)
    return output_path
```

**Asset Storage:**
```
/Users/macmini/lfc-agent/assets/
    ├── images/
    │   ├── raw/
    │   └── processed/
    ├── videos/
    │   ├── raw/
    │   └── processed/
    └── fonts/
        ├── Montserrat-Bold.ttf
        ├── Montserrat-Regular.ttf
        └── Montserrat-Light.ttf
```

---

### 6. REVIEW DASHBOARD (Human-in-the-Loop)

**Framework:** Next.js 14 + React + TailwindCSS

**Deployment:** Vercel (free tier)

**File Structure:**
```
dashboard/
├── app/
│   ├── page.tsx          # Main review interface
│   ├── api/
│   │   ├── posts/route.ts
│   │   └── approve/route.ts
├── components/
│   ├── PostCard.tsx      # Shows 3 variants side-by-side
│   ├── PerformanceChart.tsx
│   └── Calendar.tsx
└── lib/
    └── db.ts             # PostgreSQL connection
```

**Key Features:**

1. **Pending Posts View:**
   - Shows all posts awaiting approval
   - 3 variants displayed side-by-side
   - Preview how it will look on Instagram (mobile mockup)

2. **Approval Actions:**
   - Approve Variant A/B/C
   - Edit caption before approval
   - Reject all variants (regenerate)
   - Schedule time override

3. **Performance Dashboard:**
   - Chart showing engagement over time
   - "Top Performers" (best posts this week)
   - Content type breakdown (which types get most engagement)

---

### 7. SCHEDULER & PUBLISHER

**File:** `src/publishing/publisher.py`

**Meta Graph API Integration:**

```python
import requests

class InstagramPublisher:
    def __init__(self, access_token, instagram_account_id):
        self.access_token = access_token
        self.ig_account_id = instagram_account_id
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def publish_image(self, image_path, caption):
        # Step 1: Create media container
        container_url = f"{self.base_url}/{self.ig_account_id}/media"
        
        # Upload image to hosting (use AWS S3 or imgbb for now)
        image_url = self.upload_to_s3(image_path)
        
        container_params = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }
        
        container_response = requests.post(container_url, data=container_params)
        creation_id = container_response.json()['id']
        
        # Step 2: Publish the container
        publish_url = f"{self.base_url}/{self.ig_account_id}/media_publish"
        publish_params = {
            "creation_id": creation_id,
            "access_token": self.access_token
        }
        
        publish_response = requests.post(publish_url, data=publish_params)
        return publish_response.json()
```

**Posting Schedule Logic:**

```python
def calculate_post_times(fixture_date, num_posts=7):
    """
    Generate optimal posting times leading up to match.
    
    For a Sunday 4:30pm kickoff:
    - Friday: 11am, 7pm
    - Saturday: 9am, 1pm, 5pm
    - Sunday: 10am, 2pm (2.5hrs before kickoff)
    """
    times = []
    
    # Best Instagram engagement times (GMT)
    weekday_slots = ["11:00", "13:00", "19:00"]
    weekend_slots = ["09:00", "12:00", "17:00"]
    matchday_slots = ["10:00", "14:00"]  # Avoid posting during match
    
    # Logic to distribute posts...
    
    return times
```

---

### 8. ANALYTICS TRACKER

**File:** `src/analytics/tracker.py`

**Meta Insights API:**

```python
def fetch_post_insights(post_id, access_token):
    """
    Fetch engagement metrics 24 hours after posting.
    """
    url = f"https://graph.facebook.com/v18.0/{post_id}/insights"
    
    params = {
        "metric": "impressions,reach,engagement,likes,comments,saves,shares",
        "access_token": access_token
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    return {
        "impressions": data['impressions'],
        "reach": data['reach'],
        "likes": data['likes'],
        "comments": data['comments'],
        "saves": data['saves'],
        "shares": data['shares'],
        "engagement_rate": (data['likes'] + data['comments'] + data['saves']) / data['reach']
    }
```

**Learning Loop:**

```python
def analyze_performance(time_period="week"):
    """
    Weekly analysis of what content types performed best.
    """
    query = """
    SELECT 
        content_type,
        AVG((performance->>'likes')::int) as avg_likes,
        AVG((performance->>'engagement_rate')::float) as avg_engagement
    FROM posts
    WHERE posted = TRUE 
    AND created_at > NOW() - INTERVAL '7 days'
    GROUP BY content_type
    ORDER BY avg_engagement DESC
    """
    
    results = db.execute(query)
    
    return results
```

---

## Content Types Definition

For **LFC vs Manchester City**, generate these 5 content types:

### 1. ICONIC MOMENT
**Description:** Historical photo/video from memorable LFC vs City matches.

**Examples:**
- Gerrard celebration (any era)
- 2014 "slip" match (handled carefully - acknowledge pain, celebrate resilience)
- 2019 CL Quarter-Final (Anfield roar)
- Vintage 70s/80s footage

**Assets needed:**
- 1 hero image or 15-30s video clip
- Historical context (date, score, significance)

**Variants:**
- A: Emotional/heroic
- B: Factual/educational
- C: Nostalgic/reflective

---

### 2. STAT GRAPHIC
**Description:** Visual presentation of head-to-head stats, records, patterns.

**Examples:**
- "92 wins at Anfield: LFC domination over City"
- "Goals scored in last 10 meetings"
- "Anfield fortress: City's record at L4"

**Assets needed:**
- Raw stats data
- Graphic template (created by compositor)

**Variants:**
- A: Dominance angle
- B: Pattern/trend angle
- C: Challenge/provocation angle

---

### 3. FAMOUS RED
**Description:** Notable LFC supporter in the news, tied to upcoming match.

**Examples:**
- Demis Hassabis (Nobel Prize)
- Daniel Craig (new film release)
- Political figures, musicians, athletes who support LFC

**Assets needed:**
- Photo of the person (press/official)
- Their achievement/news hook
- Verified LFC connection

**Variants:**
- A: Aspirational (their success reflects LFC values)
- B: Cerebral (draw parallels between their work and football)
- C: Playful (contrast with rivals)

---

### 4. CROWD/ATMOSPHERE
**Description:** Raw emotion of being at Anfield - YNWA, crowd reactions, fan culture.

**Examples:**
- YNWA sung before kickoff
- Crowd roar after goal
- Traveling Kop at away games
- Fan traditions (flags, banners, chants)

**Assets needed:**
- Fan-shot video or high-quality crowd image
- Audio crucial (if video)

**Variants:**
- A: Goosebumps-inducing emotional
- B: "This is why Anfield is special" educational
- C: "Other grounds wish they had this" provocative

---

### 5. COMEDY/BANTER
**Description:** Witty, sharp, but not mean-spirited jabs at rivals or football absurdity.

**Examples:**
- 115 charges jokes (financial fair play)
- Oil money vs organic growth
- Guardiola's record at Anfield
- Transfer spending comparisons

**Assets needed:**
- Meme-style image or graphic
- Clever copy that's funny without being cruel

**Variants:**
- A: Subtle/clever
- B: Direct/bold
- C: Self-deprecating (shows confidence)

**Guardrails:**
- No personal attacks on players
- No discriminatory content
- Institutional critique only (City's ownership, finances, etc.)

---

## Posting Schedule (LFC vs City Example)

**Match:** Sunday, 9 Feb 2025, 4:30pm GMT

**Posting Plan:**

| Day | Time | Content Type | Rationale |
|-----|------|--------------|-----------|
| **Thu 6 Feb** | 6:00pm | Famous Red (Demis) | News hook, crossover appeal |
| **Fri 7 Feb** | 11:00am | Iconic Moment | Build anticipation |
| **Fri 7 Feb** | 7:00pm | Stat Graphic | Evening engagement |
| **Sat 8 Feb** | 9:00am | Crowd/Atmosphere | Weekend morning energy |
| **Sat 8 Feb** | 1:00pm | Comedy/Banter | Saturday banter prime time |
| **Sat 8 Feb** | 5:00pm | Iconic Moment | Evening storytelling |
| **Sun 9 Feb** | 10:00am | Stat Graphic | Pre-match facts |
| **Sun 9 Feb** | 2:00pm | Crowd/Atmosphere | Final hype (2.5hrs before KO) |

**Post-Match:**
- Wait 24 hours for emotions to settle
- Post match reaction content (if available)
- Begin cycle for next fixture

---

## Environment Setup

### Mac Mini M4 Configuration

**Prerequisites:**
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# Install Python 3.11+
brew install python@3.11

# Install FFmpeg
brew install ffmpeg

# Install Node.js (for dashboard)
brew install node@20
```

**Project Structure:**
```
/Users/macmini/lfc-agent/
├── src/
│   ├── fixtures/
│   ├── content/
│   ├── generation/
│   ├── visuals/
│   ├── publishing/
│   └── analytics/
├── dashboard/          # Next.js app
├── assets/            # Stored media
├── db/
│   └── seeds/
├── scripts/           # Utility scripts
├── .env              # Environment variables
├── requirements.txt  # Python dependencies
└── README.md
```

**Environment Variables (`.env`):**
```bash
# Database
DATABASE_URL=postgresql://macmini:password@localhost:5432/lfc_agent

# APIs
ANTHROPIC_API_KEY=sk-ant-...
FACEBOOK_ACCESS_TOKEN=...
INSTAGRAM_ACCOUNT_ID=...
YOUTUBE_API_KEY=...

# Storage (if using S3)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=lfc-agent-media

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Python Dependencies (`requirements.txt`):**
```
anthropic==0.18.0
psycopg2-binary==2.9.9
requests==2.31.0
Pillow==10.2.0
yt-dlp==2024.2.1
python-dotenv==1.0.0
schedule==1.2.0
tweepy==4.14.0
beautifulsoup4==4.12.3
```

---

## Development Workflow

### Phase 1: Infrastructure (Today - 3 hours)

**Tasks:**
1. Set up PostgreSQL database
2. Run schema migrations (`init_db.sql`)
3. Seed initial quotes + stats (`seed_content.py`)
4. Build fixture scraper (`monitor.py`)
5. Test scraper: Detect LFC vs City fixture
6. Set up Meta Business Manager + get API tokens

**Testing:**
```bash
# Test database connection
python scripts/test_db.py

# Test fixture scraper
python src/fixtures/monitor.py --test

# Verify seed data
psql -d lfc_agent -c "SELECT COUNT(*) FROM quotes;"
```

---

### Phase 2: Content Generation (Today/Tomorrow - 4 hours)

**Tasks:**
1. Build content sourcer (YouTube, Twitter, Wikimedia)
2. Download 10-15 assets for LFC vs City
3. Integrate Claude API (`generator.py`)
4. Generate caption variants for Demis post
5. Test visual compositor (create stat graphic)

**Testing:**
```bash
# Test content sourcing
python src/content/sourcer.py --query "Liverpool Manchester City" --limit 5

# Test Claude generation
python src/generation/generator.py --test --content-type famous_red

# Test visual creation
python src/visuals/compositor.py --test-stat-graphic
```

---

### Phase 3: Publishing Pipeline (Tomorrow - 3 hours)

**Tasks:**
1. Build review dashboard (Next.js)
2. Deploy dashboard to Vercel
3. Build Instagram publisher (`publisher.py`)
4. Generate 7 posts for LFC vs City
5. Review and approve posts via dashboard
6. Schedule posts for Fri/Sat/Sun

**Testing:**
```bash
# Generate full post set
python scripts/generate_match_content.py --fixture-id 12345

# Test Instagram API (don't actually post)
python src/publishing/publisher.py --dry-run

# Launch dashboard locally
cd dashboard && npm run dev
```

---

### Phase 4: Launch & Monitor (Sat/Sun - 2 hours)

**Tasks:**
1. First post goes live Friday 11am
2. Monitor engagement in real-time
3. Collect analytics data after 24 hours
4. Document learnings for next iteration

---

## Success Metrics

**MVP Success = 3 Criteria:**

1. **Technical:** All 7 posts publish successfully on schedule
2. **Engagement:** Average engagement rate >2% (baseline for new accounts)
3. **Quality:** Zero copyright strikes or content takedowns

**Phase 2 Goals (Week 2):**

1. Engagement rate >4%
2. Follower growth >100/week
3. Identify top-performing content type
4. Automate 50% of review process

**Phase 3 Goals (Month 1):**

1. Engagement rate >6%
2. Follower growth >500/week
3. Fully automated posting (no human review)
4. Expand to 2nd platform (Facebook or TikTok)

---

## Risk Mitigation

### Copyright Strikes
- **Prevention:** Only use LOW/MEDIUM risk assets initially
- **Detection:** Monitor Instagram notifications daily
- **Response:** DMCA counter-notice template ready, immediate takedown script

### Account Suspension
- **Prevention:** Warm up account slowly (don't post 10x/day immediately)
- **Backup:** Have 2 backup Instagram accounts ready
- **Recovery:** Appeal process documented, backup content hosted elsewhere

### API Rate Limits
- **Meta Graph API:** 200 calls/hour per user
- **YouTube API:** 10,000 quota units/day (1 search = 100 units)
- **Solution:** Implement exponential backoff, cache aggressively

### Content Quality Issues
- **Prevention:** Human review for Phase 1
- **Detection:** Track negative comment sentiment
- **Response:** Pull post if ratio of negative:positive comments >0.3

---

## Next Steps After MVP

### Week 2-4: Optimisation
- A/B test posting times
- Refine caption styles based on engagement data
- Build user submission form (Phase 2 content sourcing)
- Add video support (Reels)

### Month 2: Scale Platforms
- Expand to Facebook (easy - same API)
- Adapt content for TikTok (vertical video, different trends)
- Cross-post smartly (not just duplicate content)

### Month 3: Monetisation
- Affiliate links (LFC store, StubHub)
- Sponsored posts (ethical brands only - no betting)
- Patreon/membership tier for exclusive content
- Partner with fan podcasts/creators

### Month 4+: Scale Beyond LFC
- Template system: Works for any club
- Sell as SaaS to fan communities
- White-label for clubs' official channels

---

## OpenClaw Integration Points

**OpenClaw can handle:**
1. Fixture Monitor: Cron job setup + scraper reliability
2. Content Sourcer: Parallel download scripts, error handling
3. Database Ops: Migrations, backup scripts, query optimization
4. Visual Compositor: FFmpeg command refinement, template variations
5. Testing: Unit tests for each module
6. Deployment: CI/CD pipeline, Docker containers (if needed)

**Claude handles:**
1. Claude Integration: Prompt engineering, variant generation
2. Content Strategy: What content types, posting schedule, tone
3. Dashboard UI: Review interface design
4. Analytics Interpretation: What metrics matter, how to act on them

**Shared Responsibility:**
1. Meta API Integration: Configure, implement, test
2. Content Database: Design schema, optimize, review
3. Scheduling Logic: Define rules, code, approve

---

## Configuration Checklist

### Before Starting Development:

- [ ] Mac Mini M4 accessible on network
- [ ] PostgreSQL installed and running
- [ ] Python 3.11+ installed
- [ ] FFmpeg installed
- [ ] Meta Business Manager account created
- [ ] Instagram account (YNWA4Reds) connected to Business Manager
- [ ] Meta Developer App created
- [ ] Access tokens generated (temporary → long-lived)
- [ ] Anthropic API key obtained
- [ ] Project directory structure created
- [ ] `.env` file configured with all credentials
- [ ] Git repository initialized

---

**Document Version:** 1.0  
**Last Updated:** 6 Feb 2025  
**Status:** Ready for development

---
