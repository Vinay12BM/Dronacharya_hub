import yt_dlp

def search_videos(query, max_results=3):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'skip_download': True,
        'force_generic_extractor': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ytsearchX:query fetches top X results
            info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            if 'entries' in info:
                return [{
                    'title': e.get('title'),
                    'video_url': f"https://www.youtube.com/watch?v={e.get('id')}",
                    'thumbnail': e.get('thumbnail')
                } for e in info['entries']]
    except Exception as e:
        print(f"yt-dlp Error: {e}")
    return []
