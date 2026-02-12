#!/usr/bin/env python3
"""
Content Generator - Uses Claude to generate Instagram caption variants.
"""

import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

PROMPT_TEMPLATES = {
    "iconic_moment": """
You are creating Instagram content for @YNWA4Reds, a Liverpool FC community account focused on club history and identity.

FIXTURE: Liverpool vs {opponent}, {date}
CONTENT TYPE: Iconic Moment
SELECTED ASSET: {asset_description}
HISTORICAL CONTEXT: {context}

Create 3 caption variants optimized for Instagram engagement:

VARIANT A - HEROIC/EMOTIONAL:
- Tone: Goosebumps, pride, "this is why we support this club"
- Hook: Powerful opening line that stops the scroll
- Length: 200-280 characters

VARIANT B - CEREBRAL/STAT-DRIVEN:
- Tone: Intelligent, pattern-spotting
- Include 2-3 specific stats or historical facts
- Hook: Question or surprising fact
- Length: 180-250 characters

VARIANT C - CHEEKY/BANTER:
- Tone: Scouse wit, confident, playful dig at rivals
- Reference {opponent} without being mean-spirited
- Hook: Provocative but clever
- Length: 150-220 characters

RULES:
- First sentence must grab attention immediately
- No corporate speak or clichés
- Authentic Scouse voice where appropriate
- Include call-to-action at the end
- Max 3 emojis per variant
- 10-15 hashtags per variant

Return JSON only:
{{"variant_a": {{"caption": "...", "hashtags": [...], "cta": "..."}}, "variant_b": {{...}}, "variant_c": {{...}}}}
""",

    "stat_graphic": """
You are creating Instagram content for @YNWA4Reds, a Liverpool FC stats and history account.

FIXTURE: Liverpool vs {opponent}, {date}
STAT DATA: {stat_json}

Create 3 caption variants for a stat graphic:

VARIANT A - DOMINANCE:
- "The numbers don't lie" angle
- Emphasize Liverpool's historical superiority

VARIANT B - NARRATIVE:
- Tell a story with the stats
- "History has a pattern" angle

VARIANT C - PROVOCATIVE:
- Challenge rivals
- "Can they handle the pressure?" angle

RULES:
- Present stats compellingly, not just numbers
- Max 200 characters
- 10-12 hashtags
- Include CTA

Return JSON only:
{{"variant_a": {{"caption": "...", "hashtags": [...], "cta": "..."}}, "variant_b": {{...}}, "variant_c": {{...}}}}
""",

    "famous_red": """
You are creating Instagram content connecting Liverpool FC to notable supporters.

FAMOUS RED: {name}
ACHIEVEMENT: {achievement}  
CONNECTION TO LFC: {lfc_connection}
UPCOMING FIXTURE: Liverpool vs {opponent}

Create 3 caption variants:

VARIANT A - ASPIRATIONAL:
- "From the Kop to [achievement]" narrative
- Celebrate their success as part of LFC family

VARIANT B - CEREBRAL:
- Draw parallels between their work and football
- Intelligence/excellence theme

VARIANT C - PLAYFUL:
- Subtle contrast with rivals
- Confident, cheeky

RULES:
- Don't be cringy about the connection
- Authentic appreciation
- Max 220 characters
- 10-12 hashtags

Return JSON only:
{{"variant_a": {{"caption": "...", "hashtags": [...], "cta": "..."}}, "variant_b": {{...}}, "variant_c": {{...}}}}
""",

    "crowd_atmosphere": """
You are creating Instagram content showcasing Anfield's legendary atmosphere.

FIXTURE: Liverpool vs {opponent}, {date}
ASSET: {asset_description}

Create 3 caption variants:

VARIANT A - EMOTIONAL:
- Goosebumps-inducing
- "This is what it means" tone

VARIANT B - EDUCATIONAL:
- "This is why Anfield is special"
- Include historical context

VARIANT C - PROVOCATIVE:
- "Other grounds wish they had this"
- Confident, not arrogant

RULES:
- Capture the feeling of being there
- Max 200 characters
- 10-12 hashtags
- Strong CTA for engagement

Return JSON only:
{{"variant_a": {{"caption": "...", "hashtags": [...], "cta": "..."}}, "variant_b": {{...}}, "variant_c": {{...}}}}
""",

    "comedy_banter": """
You are creating Instagram banter content for @YNWA4Reds.

FIXTURE: Liverpool vs {opponent}, {date}
TOPIC: {topic}
ANGLE: {angle}

Create 3 caption variants:

VARIANT A - SUBTLE/CLEVER:
- Understated wit
- Smart reference

VARIANT B - DIRECT/BOLD:
- Confident jab
- Clear but not cruel

VARIANT C - SELF-AWARE:
- Self-deprecating confidence
- Shows we don't take ourselves too seriously

RULES:
- Institutional critique only (finances, ownership) - no player attacks
- Funny without being mean-spirited
- Max 180 characters
- 8-10 hashtags

Return JSON only:
{{"variant_a": {{"caption": "...", "hashtags": [...], "cta": "..."}}, "variant_b": {{...}}, "variant_c": {{...}}}}
"""
}


def generate_variants(content_type: str, context: dict) -> dict:
    """Generate 3 caption variants using Claude."""
    
    if content_type not in PROMPT_TEMPLATES:
        raise ValueError(f"Unknown content type: {content_type}")
    
    prompt = PROMPT_TEMPLATES[content_type].format(**context)
    
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    message = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse JSON from response
    response_text = message.content[0].text
    
    # Handle markdown code blocks
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]
    
    variants = json.loads(response_text.strip())
    return variants


def test_generator():
    """Test the generator with sample content."""
    
    # Test Famous Red (Demis Hassabis)
    context = {
        "name": "Demis Hassabis",
        "achievement": "Nobel Prize in Chemistry 2024 for AI protein structure prediction",
        "lfc_connection": "Lifelong Liverpool supporter, often seen at Anfield",
        "opponent": "Manchester City"
    }
    
    print("Testing Famous Red generation...")
    print("=" * 50)
    
    try:
        variants = generate_variants("famous_red", context)
        print(json.dumps(variants, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        print("(Make sure ANTHROPIC_API_KEY is set)")


if __name__ == "__main__":
    test_generator()
