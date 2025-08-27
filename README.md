# SmileSphere

SmileSphere is a web application that incentivizes users to share smiling photos. The application uses AI to analyze uploaded or captured smiling photos and awards "Smile Coins" based on the detected smile quality.

## Features

- **User Authentication:** Secure user registration and login functionalities.
- **Photo Submission:** Upload existing smiling photos or capture new ones directly within the application.
- **AI-Powered Smile Analysis:** AI model detects and quantifies smile quality, assigning Smile Coins accordingly.
- **Smile Coin Wallet:** Track accumulated Smile Coins in a personal wallet.
- **Leaderboard:** Global leaderboard showcasing users with the highest Smile Coin balances.
- **Community Features:** Photo sharing, comments, and reactions to foster user interaction.
- **Reward Redemption System:** Exchange accumulated Smile Coins for various rewards.

## Technology Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **Database:** SQLite (SQLAlchemy ORM)
- **Authentication:** Flask-Login
- **Image Processing:** OpenCV, face-recognition

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/smilesphere.git
   cd smilesphere
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
For models go to this link: https://drive.google.com/drive/folders/1LxAti19dPcLMaoPCaS7jcMjT2QJmFSaN?usp=drive_link
4. Initialize the database:
   ```
   flask init-db
   ```

5. (Optional) Add sample data for testing:
   ```
   flask seed-db
   ```

6. Run the application:
   ```
   flask run
   ```

7. Open your web browser and navigate to `http://127.0.0.1:5000`

## Project Structure

```
smilesphere/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── instance/              # Instance-specific data (database)
├── static/                # Static files (CSS, JS, images)
│   ├── css/               # CSS stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Image files
│       └── uploads/       # User uploaded photos
└── templates/             # HTML templates
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Face recognition libraries and AI models used for smile detection
- Flask and its extensions for web development
- The open-source community for various tools and libraries used in this project
