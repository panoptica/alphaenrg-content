#!/usr/bin/env python3
"""
Visual Compositor - Creates Instagram-ready images and videos.
Uses Pillow for images, FFmpeg for video.
"""

import os
import uuid
import subprocess
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# LFC brand colors
LFC_RED = '#C8102E'
LFC_GOLD = '#F9DC5C'
WHITE = '#FFFFFF'
BLACK = '#181818'

# Instagram dimensions
FEED_SQUARE = (1080, 1080)
FEED_PORTRAIT = (1080, 1350)
STORY = (1080, 1920)

ASSETS_DIR = Path(__file__).parent.parent.parent / 'assets'
FONTS_DIR = ASSETS_DIR / 'fonts'


def get_font(name: str = 'regular', size: int = 48):
    """Get font, falling back to system fonts if custom not found."""
    font_files = {
        'bold': 'Montserrat-Bold.ttf',
        'regular': 'Montserrat-Regular.ttf', 
        'light': 'Montserrat-Light.ttf'
    }
    
    font_path = FONTS_DIR / font_files.get(name, 'Montserrat-Regular.ttf')
    
    if font_path.exists():
        return ImageFont.truetype(str(font_path), size)
    
    # Fallback to system fonts
    try:
        return ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', size)
    except:
        return ImageFont.load_default()


def create_stat_graphic(stat_data: dict, output_path: str = None) -> str:
    """
    Create a stat graphic image.
    
    stat_data = {
        "headline": "92 WINS",
        "label": "Liverpool vs City at Anfield (All Time)",
        "supporting": [
            {"value": "54", "label": "LFC Wins"},
            {"value": "16", "label": "City Wins"},
            {"value": "27", "label": "Draws"}
        ]
    }
    """
    # Create canvas (portrait for better feed visibility)
    img = Image.new('RGB', FEED_PORTRAIT, color=LFC_RED)
    draw = ImageDraw.Draw(img)
    
    # Fonts
    font_headline = get_font('bold', 96)
    font_label = get_font('light', 36)
    font_stat = get_font('bold', 64)
    font_stat_label = get_font('light', 28)
    
    # Draw headline stat (centered, upper third)
    headline = stat_data.get('headline', '')
    bbox = draw.textbbox((0, 0), headline, font=font_headline)
    text_width = bbox[2] - bbox[0]
    x = (FEED_PORTRAIT[0] - text_width) // 2
    draw.text((x, 350), headline, fill=WHITE, font=font_headline)
    
    # Draw label below headline
    label = stat_data.get('label', '')
    bbox = draw.textbbox((0, 0), label, font=font_label)
    text_width = bbox[2] - bbox[0]
    x = (FEED_PORTRAIT[0] - text_width) // 2
    draw.text((x, 480), label, fill=LFC_GOLD, font=font_label)
    
    # Draw supporting stats (lower third, evenly spaced)
    supporting = stat_data.get('supporting', [])
    if supporting:
        num_stats = len(supporting)
        spacing = FEED_PORTRAIT[0] // (num_stats + 1)
        y_value = 800
        y_label = 880
        
        for i, stat in enumerate(supporting):
            x = spacing * (i + 1)
            
            # Stat value
            value = stat.get('value', '')
            bbox = draw.textbbox((0, 0), value, font=font_stat)
            text_width = bbox[2] - bbox[0]
            draw.text((x - text_width // 2, y_value), value, fill=WHITE, font=font_stat)
            
            # Stat label
            stat_label = stat.get('label', '')
            bbox = draw.textbbox((0, 0), stat_label, font=font_stat_label)
            text_width = bbox[2] - bbox[0]
            draw.text((x - text_width // 2, y_label), stat_label, fill=LFC_GOLD, font=font_stat_label)
    
    # Watermark
    watermark_font = get_font('light', 24)
    draw.text((50, FEED_PORTRAIT[1] - 50), '@YNWA4Reds', fill=(255, 255, 255, 180), font=watermark_font)
    
    # Save
    if output_path is None:
        output_path = str(ASSETS_DIR / 'images' / 'processed' / f'stat_{uuid.uuid4().hex[:8]}.png')
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG', quality=95)
    
    return output_path


def create_quote_graphic(quote_data: dict, output_path: str = None) -> str:
    """
    Create a quote graphic image.
    
    quote_data = {
        "quote": "This means more.",
        "author": "Jürgen Klopp",
        "year": 2019
    }
    """
    img = Image.new('RGB', FEED_SQUARE, color=BLACK)
    draw = ImageDraw.Draw(img)
    
    # Red accent bar at top
    draw.rectangle([(0, 0), (FEED_SQUARE[0], 10)], fill=LFC_RED)
    
    # Quote
    quote = f'"{quote_data.get("quote", "")}"'
    font_quote = get_font('regular', 56)
    
    # Word wrap the quote
    words = quote.split()
    lines = []
    current_line = []
    max_width = FEED_SQUARE[0] - 120
    
    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font_quote)
        if bbox[2] - bbox[0] > max_width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    
    # Draw quote lines
    y = 300
    line_height = 70
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_quote)
        x = (FEED_SQUARE[0] - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, fill=WHITE, font=font_quote)
        y += line_height
    
    # Author
    author = f"— {quote_data.get('author', 'Unknown')}"
    if quote_data.get('year'):
        author += f", {quote_data['year']}"
    
    font_author = get_font('light', 32)
    bbox = draw.textbbox((0, 0), author, font=font_author)
    x = (FEED_SQUARE[0] - (bbox[2] - bbox[0])) // 2
    draw.text((x, y + 60), author, fill=LFC_RED, font=font_author)
    
    # Watermark
    watermark_font = get_font('light', 24)
    draw.text((50, FEED_SQUARE[1] - 50), '@YNWA4Reds', fill=(255, 255, 255, 128), font=watermark_font)
    
    # Save
    if output_path is None:
        output_path = str(ASSETS_DIR / 'images' / 'processed' / f'quote_{uuid.uuid4().hex[:8]}.png')
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG', quality=95)
    
    return output_path


def add_overlay_to_image(image_path: str, overlay_text: str, output_path: str = None) -> str:
    """Add text overlay to an existing image."""
    img = Image.open(image_path)
    
    # Resize to Instagram dimensions if needed
    if img.size != FEED_PORTRAIT:
        img = img.resize(FEED_PORTRAIT, Image.Resampling.LANCZOS)
    
    draw = ImageDraw.Draw(img)
    
    # Semi-transparent overlay at bottom
    overlay_height = 200
    overlay = Image.new('RGBA', (img.width, overlay_height), (0, 0, 0, 180))
    img.paste(overlay, (0, img.height - overlay_height), overlay)
    
    # Text
    font = get_font('bold', 40)
    draw.text((50, img.height - overlay_height + 50), overlay_text, fill=WHITE, font=font)
    
    # Watermark
    watermark_font = get_font('light', 24)
    draw.text((50, img.height - 50), '@YNWA4Reds', fill=WHITE, font=watermark_font)
    
    if output_path is None:
        output_path = str(ASSETS_DIR / 'images' / 'processed' / f'overlay_{uuid.uuid4().hex[:8]}.png')
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG', quality=95)
    
    return output_path


def create_video_clip(video_path: str, text_overlay: str, duration: int = 30, output_path: str = None) -> str:
    """
    Create a video clip with text overlay using FFmpeg.
    """
    if output_path is None:
        output_path = str(ASSETS_DIR / 'videos' / 'processed' / f'clip_{uuid.uuid4().hex[:8]}.mp4')
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # FFmpeg command for video with text overlay
    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-t', str(duration),
        '-vf', (
            f"scale=1080:1350:force_original_aspect_ratio=decrease,"
            f"pad=1080:1350:(ow-iw)/2:(oh-ih)/2:black,"
            f"drawtext=text='{text_overlay}':fontcolor=white:fontsize=36:"
            f"box=1:boxcolor=black@0.6:boxborderw=10:"
            f"x=(w-text_w)/2:y=h-th-80,"
            f"drawtext=text='@YNWA4Reds':fontcolor=white:fontsize=24:"
            f"x=50:y=h-50"
        ),
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        raise


def test_compositor():
    """Test the compositor with sample data."""
    print("Testing Visual Compositor")
    print("=" * 50)
    
    # Test stat graphic
    stat_data = {
        "headline": "92 WINS",
        "label": "Liverpool vs City at Anfield (All Time)",
        "supporting": [
            {"value": "54", "label": "Home Wins"},
            {"value": "16", "label": "City Wins"},
            {"value": "27", "label": "Draws"}
        ]
    }
    
    try:
        path = create_stat_graphic(stat_data)
        print(f"✅ Stat graphic created: {path}")
    except Exception as e:
        print(f"❌ Stat graphic failed: {e}")
    
    # Test quote graphic
    quote_data = {
        "quote": "This means more.",
        "author": "Jürgen Klopp",
        "year": 2019
    }
    
    try:
        path = create_quote_graphic(quote_data)
        print(f"✅ Quote graphic created: {path}")
    except Exception as e:
        print(f"❌ Quote graphic failed: {e}")


if __name__ == "__main__":
    test_compositor()
