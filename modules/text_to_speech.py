from gtts import gTTS
import os

def generate_tts(text, filepath, lang='en'):
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(filepath)
        return True
    except Exception as e:
        print(f"TTS Error: {e}")
        return False
