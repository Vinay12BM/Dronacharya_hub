from app import create_app, db
from sqlalchemy import text

def migrate_db():
    app = create_app()
    with app.app_context():
        print("Starting ownership migration...")
        try:
            with db.engine.connect() as conn:
                # Add user_id column to note table
                print("Step 1: Adding 'user_id' column to 'note' table...")
                try:
                    conn.execute(text("ALTER TABLE note ADD COLUMN user_id INTEGER REFERENCES \"user\"(id)"))
                    conn.commit()
                    print("Successfully added 'user_id' to 'note'.")
                except Exception as e:
                    print(f"Skipping Step 1: {e}")

                # Add user_id column to book table
                print("Step 2: Adding 'user_id' column to 'book' table...")
                try:
                    conn.execute(text("ALTER TABLE book ADD COLUMN user_id INTEGER REFERENCES \"user\"(id)"))
                    conn.commit()
                    print("Successfully added 'user_id' to 'book'.")
                except Exception as e:
                    print(f"Skipping Step 2: {e}")
                    
        except Exception as e:
            print(f"Migration error: {e}")
        
        print("Migration task completed.")

if __name__ == '__main__':
    migrate_db()
