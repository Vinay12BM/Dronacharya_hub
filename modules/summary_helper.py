import re
import time
import json
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi
from modules.text_generation import client, model_id, fallback_models

def get_youtube_video_id(url):
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None

def fetch_url_content(url):
    # Check if youtube
    yt_id = get_youtube_video_id(url)
    if yt_id:
        # 1. Try Official Transcript API (only once to avoid triggering 429)
        try:
            transcript = YouTubeTranscriptApi.get_transcript(yt_id)
            return " ".join([t['text'] for t in transcript])
        except Exception as e:
            # Check if it's a rate limit error to avoid further spamming
            if "429" in str(e):
                print(f"YouTube Transcript 429: {e}")
            pass
        
        # 2. Try the Official OEmbed API for metadata (more reliable than scraping)
        try:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={yt_id}&format=json"
            oembed_req = urllib.request.Request(oembed_url, headers={'User-Agent': 'Mozilla/5.0'})
            oembed_resp = urllib.request.urlopen(oembed_req, timeout=5).read().decode('utf-8')
            metadata = json.loads(oembed_resp)
            title = metadata.get('title', 'Unknown Title')
            author = metadata.get('author_name', 'Unknown Author')
            return f"VIDEO_TITLE: {title}\nVIDEO_AUTHOR: {author}\n(Note: Official transcript was unavailable due to rate limits. Summary will be based on available metadata.)"
        except:
            pass

        # 3. Last Resort: Scrape the YouTube Page for metadata
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            # We use a shorter timeout and small read to minimize footprint
            html = urllib.request.urlopen(req, timeout=10).read(50000).decode('utf-8', errors='ignore')
            
            title_match = re.search(r'<title>(.*?)</title>', html)
            desc_match = re.search(r'name="description"\s+content="(.*?)"', html) or re.search(r'property="og:description"\s+content="(.*?)"', html)
            
            title_text = title_match.group(1).replace(' - YouTube', '') if title_match else "Metadata Unavailable"
            desc_text = desc_match.group(1) if desc_match else "Description Unavailable"
            
            return f"VIDEO_TITLE: {title_text}\nVIDEO_DESCRIPTION: {desc_text}\n(Note: Transcript was unavailable. Using video metadata.)"
        except Exception as scrap_e:
            return f"TRANSCRIPT_ERROR: {scrap_e}. YouTube is currently restricting automated access. Please share the key points you'd like summarized instead."
    
    # Generic web page
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=10).read()
        soup = BeautifulSoup(html, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=' ')
        return re.sub(r'\s+', ' ', text).strip()[:20000]
    except Exception as e:
        return f"WEBSITE_ERROR: {e}"

def generate_ai_summary(url, language="English"):
    content = fetch_url_content(url)
    
    if "TRANSCRIPT_ERROR:" in content or "WEBSITE_ERROR:" in content:
        return content

    prompt = f"""
    Please provide a complete summary of the following content in {language}.
    Follow these rules strictly:
    1. Use only very SIMPLE, everyday common language. NO complex academic words.
    2. Make it comprehensive and clear for a student to understand quickly.
    3. Use proper markdown for readability.
    
    Content:
    {content[:30000]}
    """
    
    try:
        from modules.text_generation import generate_with_fallback
        summary_text = generate_with_fallback(prompt)
        return summary_text
    except Exception as e:
        return f"AI Generation Error: All AI models are currently overwhelmed. Please try again in 5 minutes! Detail: {e}"
