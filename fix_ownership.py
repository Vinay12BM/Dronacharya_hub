from app import create_app, db
from app.models import Note, Book, User

app = create_app()
with app.app_context():
    # Find the first user in the database (Your account)
    admin_user = User.query.first()
    
    if not admin_user:
        print("❌ No users found in database. Please register an account first!")
    else:
        print(f"🔗 Assigning ownership of all items to: {admin_user.email}")
        
        # Assign all ownerless notes
        notes_fixed = Note.query.filter(Note.user_id == None).update({Note.user_id: admin_user.id})
        
        # Assign all ownerless books
        books_fixed = Book.query.filter(Book.user_id == None).update({Book.user_id: admin_user.id})
        
        db.session.commit()
        print(f"✅ Success! {notes_fixed} Notes and {books_fixed} Books are now yours.")
        print("🚀 Refresh your browser and you will see the delete buttons.")
