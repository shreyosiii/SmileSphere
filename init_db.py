import os
import sys
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app, db, User, Photo, Comment, Reaction, Reward, Redemption

def init_db():
    """Initialize the database with tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created.")

def add_sample_data():
    """Add sample data to the database for testing"""
    with app.app_context():
        # Check if data already exists
        if User.query.first() is not None:
            print("Sample data already exists. Skipping...")
            return
        
        # Create sample users
        users = [
            User(username="admin", email="admin@example.com", 
                 password_hash=generate_password_hash("password"), 
                 smile_coins=500, is_admin=True),
            User(username="john", email="john@example.com", 
                 password_hash=generate_password_hash("password"), 
                 smile_coins=350),
            User(username="sarah", email="sarah@example.com", 
                 password_hash=generate_password_hash("password"), 
                 smile_coins=420),
            User(username="mike", email="mike@example.com", 
                 password_hash=generate_password_hash("password"), 
                 smile_coins=280),
            User(username="emma", email="emma@example.com", 
                 password_hash=generate_password_hash("password"), 
                 smile_coins=150)
        ]
        
        for user in users:
            db.session.add(user)
        
        db.session.commit()
        print(f"Added {len(users)} sample users.")
        
        # Create sample photos
        # Note: In a real scenario, you would have actual image files
        # For this sample, we'll just create the database entries
        
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(app.static_folder, 'images', 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Sample photo filenames (these would be actual files in a real scenario)
        sample_filenames = [
            "user1_smile1.jpg", "user1_smile2.jpg", 
            "user2_smile1.jpg", "user3_smile1.jpg", 
            "user4_smile1.jpg", "user5_smile1.jpg"
        ]
        
        # Create empty placeholder files
        for filename in sample_filenames:
            file_path = os.path.join(uploads_dir, filename)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write("Placeholder for sample image")
        
        # Create photo records
        photos = []
        now = datetime.now()
        
        # Admin photos
        photos.append(Photo(
            user_id=1, 
            filename="user1_smile1.jpg", 
            smile_score=9, 
            public=True, 
            uploaded_at=now - timedelta(days=5)
        ))
        
        photos.append(Photo(
            user_id=1, 
            filename="user1_smile2.jpg", 
            smile_score=7, 
            public=True, 
            uploaded_at=now - timedelta(days=2)
        ))
        
        # John's photo
        photos.append(Photo(
            user_id=2, 
            filename="user2_smile1.jpg", 
            smile_score=8, 
            public=True, 
            uploaded_at=now - timedelta(days=3)
        ))
        
        # Sarah's photo
        photos.append(Photo(
            user_id=3, 
            filename="user3_smile1.jpg", 
            smile_score=10, 
            public=True, 
            uploaded_at=now - timedelta(days=1)
        ))
        
        # Mike's photo
        photos.append(Photo(
            user_id=4, 
            filename="user4_smile1.jpg", 
            smile_score=6, 
            public=False,  # Private photo
            uploaded_at=now - timedelta(days=4)
        ))
        
        # Emma's photo
        photos.append(Photo(
            user_id=5, 
            filename="user5_smile1.jpg", 
            smile_score=7, 
            public=True, 
            uploaded_at=now - timedelta(hours=12)
        ))
        
        for photo in photos:
            db.session.add(photo)
        
        db.session.commit()
        print(f"Added {len(photos)} sample photos.")
        
        # Add sample comments
        comments = [
            Comment(user_id=2, photo_id=1, content="Great smile!", created_at=now - timedelta(days=4, hours=12)),
            Comment(user_id=3, photo_id=1, content="You look so happy!", created_at=now - timedelta(days=4, hours=10)),
            Comment(user_id=1, photo_id=3, content="Nice one, John!", created_at=now - timedelta(days=2, hours=8)),
            Comment(user_id=5, photo_id=4, content="Perfect smile, Sarah!", created_at=now - timedelta(hours=20)),
            Comment(user_id=4, photo_id=6, content="Looking good, Emma!", created_at=now - timedelta(hours=6))
        ]
        
        for comment in comments:
            db.session.add(comment)
        
        db.session.commit()
        print(f"Added {len(comments)} sample comments.")
        
        # Add sample reactions (likes)
        reactions = []
        
        # Reactions for admin's first photo
        for user_id in range(2, 6):  # Users 2-5
            reactions.append(Reaction(user_id=user_id, photo_id=1))
        
        # Reactions for John's photo
        reactions.append(Reaction(user_id=1, photo_id=3))  # Admin likes
        reactions.append(Reaction(user_id=3, photo_id=3))  # Sarah likes
        
        # Reactions for Sarah's photo
        reactions.append(Reaction(user_id=1, photo_id=4))  # Admin likes
        reactions.append(Reaction(user_id=2, photo_id=4))  # John likes
        reactions.append(Reaction(user_id=5, photo_id=4))  # Emma likes
        
        # Reactions for Emma's photo
        reactions.append(Reaction(user_id=4, photo_id=6))  # Mike likes
        
        for reaction in reactions:
            db.session.add(reaction)
        
        db.session.commit()
        print(f"Added {len(reactions)} sample reactions.")
        
        # Add sample rewards
        rewards = [
            Reward(name="$5 Gift Card", description="Redeem for a $5 gift card to your favorite store.", cost=50, image="gift_card.jpg"),
            Reward(name="Premium Filter Pack", description="Unlock a pack of premium filters for your photos.", cost=30, image="filters.jpg"),
            Reward(name="Donation to Charity", description="We'll donate $10 to a charity of your choice.", cost=100, image="charity.jpg"),
            Reward(name="Custom Profile Badge", description="Get a special badge for your profile that shows your smile status.", cost=25, image="badge.jpg"),
            Reward(name="SmileSphere T-Shirt", description="Get a cool SmileSphere branded t-shirt delivered to your door.", cost=200, image="tshirt.jpg")
        ]
        
        for reward in rewards:
            db.session.add(reward)
        
        db.session.commit()
        print(f"Added {len(rewards)} sample rewards.")
        
        # Add sample redemptions
        redemptions = [
            Redemption(user_id=1, reward_id=1, status="completed", redeemed_at=now - timedelta(days=10)),
            Redemption(user_id=1, reward_id=4, status="completed", redeemed_at=now - timedelta(days=5)),
            Redemption(user_id=2, reward_id=2, status="completed", redeemed_at=now - timedelta(days=7)),
            Redemption(user_id=3, reward_id=1, status="pending", redeemed_at=now - timedelta(days=1)),
            Redemption(user_id=5, reward_id=4, status="pending", redeemed_at=now - timedelta(hours=5))
        ]
        
        for redemption in redemptions:
            db.session.add(redemption)
        
        db.session.commit()
        print(f"Added {len(redemptions)} sample redemptions.")
        
        print("Sample data added successfully!")

def main():
    """Main function to initialize database and optionally add sample data"""
    if len(sys.argv) > 1 and sys.argv[1] == "--with-sample-data":
        init_db()
        add_sample_data()
    else:
        init_db()
        print("To add sample data, run: python init_db.py --with-sample-data")

if __name__ == "__main__":
    main()
