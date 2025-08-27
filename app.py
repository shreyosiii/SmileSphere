from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
import uuid
from datetime import datetime, date

# ------------------ APP CONFIG ------------------ #
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-smilesphere')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smilesphere.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload (kept consistent with messages)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ------------------ EXTENSIONS ------------------ #
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ------------------ MODELS ------------------ #
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    smile_coins = db.Column(db.Integer, default=0)
    photos = db.relationship('Photo', backref='user', lazy=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_upload_date = db.Column(db.Date)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    smile_score = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    public = db.Column(db.Boolean, default=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reaction_type = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255))
    available = db.Column(db.Boolean, default=True)


class Redemption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey('reward.id'), nullable=False)
    redeemed_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------ ROUTES ------------------ #
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')

        if not username or not email or not password:
            flash('All fields are required.')
            return redirect(url_for('register'))

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists.')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    photos = Photo.query.filter_by(user_id=current_user.id).order_by(Photo.uploaded_at.desc()).all()
    return render_template('dashboard.html', photos=photos)

# ---- SINGLE, CANONICAL PHOTO DETAIL ROUTE ----
# Use endpoint 'show_photo' to match templates; function name also 'show_photo' to avoid collisions.
@app.route('/photo/<int:photo_id>')
def view_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    comments = Comment.query.filter_by(photo_id=photo_id).order_by(Comment.created_at.desc()).all()
    return render_template('photo.html', photo=photo, comments=comments)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'photo' not in request.files and 'photo' not in request.form:
            flash('No photo provided.')
            return redirect(request.url)

        file_path = None

        # Case 1: Base64 capture (e.g., from webcam)
        if 'photo' in request.form and request.form.get('photo', '').startswith('data:image'):
            import base64, re
            img_data = re.sub(r'^data:image/\w+;base64,', '', request.form['photo'])
            image_bytes = base64.b64decode(img_data)
            filename = f"{uuid.uuid4()}.png"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(file_path, 'wb') as f:
                f.write(image_bytes)

        # Case 2: File upload
        else:
            file = request.files.get('photo')
            if not file or file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

        # Run smile detector
        from smile_detector import SmileDetector
        detector = SmileDetector()
        result = detector.analyze_image(file_path)
        smile_score = int(result.get('score', 0))

        new_photo = Photo(
            filename=os.path.basename(file_path),
            smile_score=smile_score,
            user_id=current_user.id,
            public=bool(request.form.get('public'))
        )
        db.session.add(new_photo)
        current_user.smile_coins = (current_user.smile_coins or 0) + smile_score
        db.session.commit()

        flash(f'Photo uploaded! You earned {smile_score} Smile Coins!')
        return redirect(url_for('dashboard'))

    return render_template('upload.html')

# photo deletion route
@app.route('/photo/<int:photo_id>/delete', methods=['POST'])
@login_required
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)

    # Ensure only owner or admin can delete
    if photo.user_id != current_user.id and not current_user.is_admin:
        flash("You don't have permission to delete this photo.")
        return redirect(url_for('dashboard'))

    # Delete image file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Deduct Smile Coins (optional)
    current_user.smile_coins -= photo.smile_score
    if current_user.smile_coins < 0:
        current_user.smile_coins = 0

    # Delete DB record
    db.session.delete(photo)
    db.session.commit()

    flash("Photo deleted successfully.")
    return redirect(url_for('dashboard'))

# ✅ Community route to show all public photos
@app.route('/community')
@login_required
def community():
    photos = Photo.query.filter_by(public=True).order_by(Photo.uploaded_at.desc()).all()
    return render_template('community.html', photos=photos)

@app.route('/leaderboard')
def leaderboard():
    users = User.query.order_by(User.smile_coins.desc()).all()
    return render_template('leaderboard.html', users=users)

@app.route('/rewards')
def rewards():
    available_rewards = Reward.query.filter_by(available=True).order_by(Reward.id).all()
    return render_template('rewards.html', rewards=available_rewards)

@app.route('/profile')
@login_required
def profile():
    photos = current_user.photos
    redemptions = Redemption.query.filter_by(user_id=current_user.id).join(Reward).all()
    return render_template('profile.html', photos=photos, redemptions=redemptions)

@app.route('/redeem_reward/<int:reward_id>', methods=['POST'])
@login_required
def redeem_reward(reward_id):
    reward = Reward.query.get_or_404(reward_id)

    if not reward.available:
        flash('This reward is no longer available.')
        return redirect(url_for('rewards'))

    if (current_user.smile_coins or 0) < reward.cost:
        flash(f'You need {reward.cost - (current_user.smile_coins or 0)} more Smile Coins to redeem this reward.')
        return redirect(url_for('rewards'))

    current_user.smile_coins -= reward.cost
    redemption = Redemption(user_id=current_user.id, reward_id=reward.id, status='pending')
    db.session.add(redemption)
    db.session.commit()

    flash(f'Successfully redeemed {reward.name}! Your redemption is pending approval.')
    return redirect(url_for('rewards'))

@app.route('/photo/<int:photo_id>/reaction', methods=['POST'])
@login_required
def add_reaction(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    reaction_type = request.form.get('reaction_type', 'like')

    # Toggle same reaction; remove any other reaction first
    existing_reaction = Reaction.query.filter_by(
        user_id=current_user.id,
        photo_id=photo_id,
        reaction_type=reaction_type
    ).first()

    if existing_reaction:
        db.session.delete(existing_reaction)
        db.session.commit()
        flash('Reaction removed.')
    else:
        Reaction.query.filter_by(user_id=current_user.id, photo_id=photo_id).delete()
        db.session.add(Reaction(user_id=current_user.id, photo_id=photo_id, reaction_type=reaction_type))
        db.session.commit()
    flash('Reaction added!')

    return redirect(url_for('view_photo', photo_id=photo_id))

@app.route('/photo/<int:photo_id>/comment', methods=['POST'])
@login_required
def add_comment(photo_id):
    Photo.query.get_or_404(photo_id)
    content = (request.form.get('content') or '').strip()

    if not content:
        flash('Comment cannot be empty.')
        return redirect(url_for('view_photo', photo_id=photo_id))

    db.session.add(Comment(user_id=current_user.id, photo_id=photo_id, content=content))
    db.session.commit()

    flash('Comment added successfully!')
    return redirect(url_for('view_photo', photo_id=photo_id))

# ------------------ ERROR HANDLERS & CONTEXT ------------------ #
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash("File is too large! Max 50MB allowed.")
    return redirect(request.url)

@app.context_processor
def inject_current_app():
    return dict(current_app=current_app)

# ------------------ DB Commands ------------------ #
@app.cli.command('init-db')
def init_db_command():
    db.create_all()
    print('Initialized the database.')

@app.cli.command('seed-db')
def seed_db_command():
    rewards_data = [
        ("Fastrack SmartWatch", "Smartwatch with fitness tracking", 1000, "gift1.jpg"),
        ("ASUS Laptop", "High-performance laptop for work and gaming", 5000, "gift2.jpg"),
        ("Nike Shoes", "Comfortable running shoes", 1200, "gift3.jpg"),
        ("iPhone 15", "Latest Apple smartphone", 7000, "gift4.jpg"),
        ("Bluetooth Speaker", "Portable high-bass speaker", 900, "gift5.jpg"),
        ("Amazon Voucher", "₹125 Amazon gift voucher", 2000, "gift6.jpg"),
        ("Smart TV", "42-inch LED Smart TV", 6000, "gift7.jpg"),
        ("Backpack", "Durable laptop backpack", 700, "gift8.jpg"),
        ("Fitness Band", "Track steps, heart rate, sleep", 1500, "gift9.jpg"),
        ("Headphone", "Wireless noise-cancelling headphones", 800, "gift10.jpg"),
    ]

    for name, description, cost, image in rewards_data:
        reward = Reward(name=name, description=description, cost=cost, image=image)
        db.session.add(reward)

    db.session.commit()
    print("🎁 Rewards added successfully!")

# ------------------ MAIN ------------------ #
if __name__ == '__main__':
    app.run(debug=True)
