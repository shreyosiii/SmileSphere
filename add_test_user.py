from app import app, db, User
from werkzeug.security import generate_password_hash

# Create a test user
with app.app_context():
    # Check if test user already exists
    if not User.query.filter_by(username='test').first():
        test_user = User(
            username='test',
            email='test@example.com',
            password_hash=generate_password_hash('password'),
            smile_coins=100
        )
        db.session.add(test_user)
        db.session.commit()
        print("Test user created successfully!")
    else:
        print("Test user already exists.")