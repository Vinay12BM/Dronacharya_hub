from app import create_app, db
from sqlalchemy import text

def migrate_db():
    app = create_app()
    with app.app_context():
        print("Starting Rewards Migration...")
        try:
            # We use db.create_all() but since tables might exist, 
            # we can also check/create specifically
            db.create_all()
            print("Successfully checked/created all tables (including user_coupon).")
        except Exception as e:
            print(f"Error during migration: {e}")
        
        print("Migration task completed.")

if __name__ == '__main__':
    migrate_db()
