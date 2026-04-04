import re
import time
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
        # Try all known patterns for the youtube-transcript-api
        try:
            return " ".join([t['text'] for t in YouTubeTranscriptApi.get_transcript(yt_id)])
        except: pass
        
        try:
            return " ".join([t['text'] for t in youtube_transcript_api.get_transcript(yt_id)])
        except: pass

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(yt_id)
            return " ".join([t['text'] for t in next(iter(transcript_list)).fetch()])
        except: pass

        try:
            # Try instantiation if it's an instance method issue
            api = YouTubeTranscriptApi()
            return " ".join([t['text'] for t in api.get_transcript(yt_id)])
        except: pass

        try:
            api = YouTubeTranscriptApi()
            return " ".join([t['text'] for t in api.list(yt_id).fetch()])
        except: pass

        # SUPER FALLBACK: If transcript fails, scrape the YouTube Page metadata/description
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find title and description from meta tags (YouTube hides them inside scripts usually, but meta is reliable)
            title = soup.find("meta", property="og:title")
            desc = soup.find("meta", property="og:description")
            
            title_text = title["content"] if title else "Unknown Video"
            desc_text = desc["content"] if desc else "No description available"
            
            return f"VIDEO_TITLE: {title_text}\nVIDEO_DESCRIPTION: {desc_text}\n(Note: Using video description as transcript was unavailable)"
        except Exception as scrap_e:
            return f"TRANSCRIPT_ERROR: {scrap_e}. Could not retrieve transcript from {yt_id}."
    
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
