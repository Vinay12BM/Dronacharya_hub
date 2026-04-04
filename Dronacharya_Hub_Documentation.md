# 📘 Dronacharya Hub: Complete System Documentation

## 1. Technology Stack Overview
The platform is built using a modern, scalable stack designed for high performance and AI integration.

- **Backend Framework**: Flask (Python)
- **Frontend UI**: HTML5, Jinja2, Tailwind CSS
- **Database Persistence**: PostgreSQL (via Supabase)
- **Object-Relational Mapper (ORM)**: SQLAlchemy
- **Intelligence Engine**: Google Gemini AI
- **Cloud Asset Storage**: Supabase Storage
- **Production Web Server**: Gunicorn (WSGI)

## 2. Extensions & Libraries (Requirements)
Detailed list of installed dependencies and their specific purposes:

- **Flask-Login**: Manages session security and user authentication states.
- **google-generativeai**: Enables advanced natural language processing for the AI Tutor.
- **supabase**: Python client for cloud database and file bucket interactions.
- **gtts (Google Text-to-Speech)**: Converts text responses into spoken audio.
- **yt-dlp**: Specialized library for fetching educational video metadata from YouTube.
- **python-docx**: Library for creating Word documents automatically.
- **Flask-Migrate**: Synchronizes database schema changes.
- **python-dotenv**: Manages sensitive API keys and configuration.

## 3. System Design & Architecture
The system follows a modular "Blueprint Pattern" to keep features isolated and stable.

- **Tutor**: AI-driven learning and real-time interaction.
- **Research**: Advanced document creation and academic analysis.
- **Books**: Geolocation-aware marketplace for book sharing/selling.
- **Scholarships**: Database for tracking financial aid opportunities.
- **Notes**: Central repository for students to upload and share study materials.
- **Games**: Educational puzzles (Sudoku, Crossmath, etc.).

## 4. Algorithms Used in the System
Core logic and mathematical formulas powering the platform:

- **Haversine Formula**: Calculates the physical distance between users and booksellers using GPS latitude/longitude.
- **LLM Inference**: The "brain" of the AI, providing contextual answers and summaries via the Gemini model.
- **Password Hashing (PBKDF2)**: Secure cryptographic encryption for protecting user credentials.
- **Timsort**: Python's optimized sorting algorithm used for ranking nearby books by distance.
- **UUID Generation**: Generates 128-bit unique IDs to prevent file naming conflicts.

## 5. Request Handling & Lifecycle
How the system processes one user interaction from start to finish:

1. **Worker Layer**: Gunicorn receives the internet request and routes it to the application.
2. **Logic Controller**: Flask Blueprints match the URL to the correct module (e.g., /notes).
3. **Security Check**: Middleware verifies the user's login session and permissions via Flask-Login.
4. **Data Integration**: The app fetches records from PostgreSQL or calls the Gemini AI API for text generation.
5. **Template Engine**: Jinja2 combines data with HTML layouts to create the final webpage.
