from flask import render_template, request, jsonify
from . import games_bp
from modules.text_generation import generate_chess_move, generate_crossmath_puzzle

@games_bp.route('/')
def index():
    return render_template('games/index.html')

@games_bp.route('/word-search')
def word_search():
    return render_template('games/word_search.html')

@games_bp.route('/chess')
def chess():
    return render_template('games/chess.html')

@games_bp.route('/chess-move', methods=['POST'])
def chess_move_bot():
    data = request.json
    fen = data.get('fen')
    if not fen:
        return jsonify({"error": "No FEN provided"}), 400
    
    move = generate_chess_move(fen)
    return jsonify({"move": move})

@games_bp.route('/crossmath')
def crossmath():
    return render_template('games/crossmath.html')

@games_bp.route('/crossmath-gen')
def crossmath_gen():
    puzzle = generate_crossmath_puzzle()
    return jsonify(puzzle)

@games_bp.route('/skills')
def skills():
    return render_template('games/skills.html')

@games_bp.route('/baby-puzzles')
def baby_puzzles():
    return render_template('games/baby_puzzles.html')
