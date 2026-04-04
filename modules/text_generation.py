import os, json, random
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

def serialize_history(history):
    result = []
    for h in history:
        if hasattr(h, 'role') and hasattr(h, 'parts'):
            result.append({'role': h.role, 'parts': [{'text': str(p.text) if hasattr(p, 'text') else str(p)} for p in h.parts]})
        else:
            result.append(h)
    return result

def generate_gemini_quiz(topic):
    system_instruction = (
        f"You are an expert teacher. Generate exactly 10 multiple-choice questions about: '{topic}'. "
        f"Return ONLY valid JSON (no markdown, no extra text): "
        f'[{{"question":"...","options":{{"A":"...","B":"...","C":"...","D":"..."}},"answer":"A"}}]'
    )
    try:
        response = model.generate_content(system_instruction)
        text = response.text.strip()
        if '```json' in text: text = text.split('```json')[1].split('```')[0].strip()
        return json.loads(text)
    except Exception as e:
        err_msg = str(e)
        print(f"Gemini Quiz Error: {err_msg}")
        if "429" in err_msg or "quota" in err_msg.lower():
            return [
                {"question": f"Which of the following describes a core aspect of {topic}?", "options": {"A": "Option 1", "B": "Option 2", "C": "Correct Principle", "D": "None"}, "answer": "C"},
                {"question": f"True or False: {topic} is widely used in modern education.", "options": {"A": "True", "B": "False", "C": "Maybe", "D": "Not sure"}, "answer": "A"}
            ]
        return []

def generate_gemini_chat(message, history):
    system_instruction = (
        "You are Dronacharya, the legendary wise teacher from ancient India, now an AI tutor. "
        "Be patient, clear, encouraging. Use examples. Format responses in markdown. "
        "Never refuse a learning question."
    )
    chat = model.start_chat(history=history)
    try:
        response = chat.send_message(message)
        return response.text, serialize_history(chat.history)
    except Exception as e:
        print(f"Gemini Chat Error: {e}")
        return "I am currently unable to answer that. Please try again later.", history

def generate_tumtum_chat(message, history):
    chat = model.start_chat(history=history)
    try:
        response = chat.send_message(message)
        return response.text, serialize_history(chat.history)
    except Exception as e:
        err_msg = str(e)
        print(f"TumTum API Error: {err_msg}")
        return f"AI Assistant Error: {err_msg}", history

def generate_gemini_paper(topic, language):
    system_instruction = (
        f"You are an expert academic writer. Generate a comprehensive research paper about '{topic}' "
        f"written entirely in {language}. Include these exact markdown sections: "
        f"## Research Topic\n## Abstract\n## Introduction\n## Literature Review\n"
        f"## Methodology\n## Main Findings / Discussion\n## Conclusion\n## References\n"
        f"Under References, list exactly 12 realistic academic references. "
        f"Respond ONLY with markdown content. No preamble."
    )
    try:
        response = model.generate_content(system_instruction)
        if response.candidates and len(response.candidates) > 0:
            if response.candidates[0].finish_reason == 3:
                return "ERROR: Restricted by safety filters."
            return response.text
        return "ERROR: No response from AI."
    except Exception as e:
        err_msg = str(e)
        print(f"Gemini Research Error: {err_msg}")
        if "429" in err_msg or "quota" in err_msg.lower():
            refs = "\n".join([f"{i}. Expert, A. (202{random.randint(0,5)}). Research on {topic} Vol {i}." for i in range(1, 13)])
            return f"""# [DEMO MODE: Quota Exceeded] Research Paper: {topic}
## Abstract
This paper explores {topic}. Due to AI quota limits, this sample serves as a placeholder for testing.

## Introduction
The study of {topic} is crucial...

## Methodology
Structured analysis was conducted...

## Conclusion
Final results indicate clear trends...

## References
{refs}"""
        return f"ERROR: {err_msg}"

def generate_gemini_citation(source, style):
    try:
        response = model.generate_content(f"Generate a professional {style} citation for this source: {source}. Respond with only the citation.")
        return response.text.strip()
    except Exception as e:
        err_msg = str(e)
        print(f"Gemini Citation Error: {err_msg}")
        if "429" in err_msg or "quota" in err_msg.lower():
            # Demo fallback
            return f"{source} ({style} style). [Note: Quota Exceeded, using manual format]"
        return None

def generate_gemini_notes(topic):
    try:
        response = model.generate_content(f"Generate study notes for: {topic}")
        return response.text
    except Exception as e:
        print(f"Gemini Notes Error: {e}")
        return f"# Study Notes: {topic}\n(Error)"
