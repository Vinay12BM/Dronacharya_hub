from app import create_app

# Entry point for production servers (Render/Gunicorn)
app = create_app()

if __name__ == "__main__":
    app.run()
