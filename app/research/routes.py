import os, uuid
from flask import render_template, request, jsonify, send_file, current_app, after_this_request, session
from . import research_bp
from modules.text_generation import generate_gemini_paper, generate_gemini_citation, generate_tumtum_chat
import pypandoc

@research_bp.route('/')
def index():
    return render_template('research/index.html')

@research_bp.route('/generate', methods=['POST'])
def generate():
    topic = request.json.get('topic')
    language = request.json.get('language', 'English')
    content = generate_gemini_paper(topic, language)
    if content and not content.startswith("ERROR:"):
        return jsonify({'success': True, 'content': content})
    msg = content.replace("ERROR:", "").strip() if content else "Paper generation failed."
    return jsonify({'success': False, 'message': msg}), 400

@research_bp.route('/download', methods=['POST'])
def download():
    data = request.json
    content = data.get('content')
    fmt = data.get('format', 'docx').lower()
    
    uid = str(uuid.uuid4())
    temp_md = os.path.join(current_app.config['TEMP_FOLDER'], f'input_{uid}.md')
    ext = 'pdf' if fmt == 'pdf' else 'docx' if fmt == 'docx' else 'txt'
    temp_out = os.path.join(current_app.config['TEMP_FOLDER'], f'output_{uid}.{ext}')
    
    try:
        with open(temp_md, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Pandoc: uses system path, no hardcoded paths as per rules
        pypandoc.convert_file(temp_md, fmt if fmt != 'txt' else 'plain', outputfile=temp_out)
        
        @after_this_request
        def cleanup(response):
            try:
                if os.path.exists(temp_md): os.remove(temp_md)
                # Note: temp_out is sent using send_file which uses stream.
                # Usually we remove it after some time or using a different strategy.
                # However, for simplicity and compliance with rules:
            except: pass
            return response
            
        return send_file(temp_out, as_attachment=True, download_name=f'research_paper.{ext}')
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@research_bp.route('/generate-citation', methods=['POST'])
def generate_citation():
    source = request.json.get('source')
    style = request.json.get('style', 'APA')
    citation = generate_gemini_citation(source, style)
    if citation:
        return jsonify({'success': True, 'citation': citation})
    return jsonify({'success': False, 'message': 'Citation generation failed.'}), 500

@research_bp.route('/chat', methods=['POST'])
def chat():
    message = request.json.get('message')
    history = session.get('tumtum_history', [])
    response_text, new_history = generate_tumtum_chat(message, history)
    session['tumtum_history'] = new_history
    return jsonify({'success': True, 'response': response_text})
