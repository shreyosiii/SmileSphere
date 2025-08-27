from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smilesphere.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure instance directory exists
os.makedirs('instance', exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

# Create all tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")