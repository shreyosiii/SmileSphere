import random
from datetime import datetime, date

class SmileTipsGenerator:
    """Generate personalized smile tips based on smile scores and user behavior"""
    
    def __init__(self):
        self.tips_database = {
            'low_score': [
                "Try relaxing your face muscles and think of something that makes you genuinely happy!",
                "Practice your smile in front of a mirror - a natural smile shows teeth and reaches your eyes!",
                "Take a deep breath and smile slowly - it often looks more natural than a quick grin.",
                "Remember to engage your eyes when smiling - a genuine smile creates crow's feet!",
                "Try slightly tilting your head - it can make your smile appear more friendly and approachable."
            ],
            'medium_score': [
                "Great smile! Try showing a bit more teeth for an even brighter expression.",
                "Your smile is looking good! Focus on making it symmetrical for maximum impact.",
                "Nice work! Try holding your smile for a few seconds longer to capture the perfect moment.",
                "You're getting there! A slight squint of the eyes can make your smile more genuine.",
                "Good progress! Try different angles - sometimes a 3/4 view works better than straight on."
            ],
            'high_score': [
                "Fantastic smile! Your happiness is contagious - keep spreading those positive vibes!",
                "Perfect smile! You've mastered the art of genuine, warm expression.",
                "Amazing! Your smile could light up any room - keep being your wonderful self!",
                "Incredible smile! You radiate positivity and joy - never stop smiling!",
                "Outstanding! Your smile is absolutely radiant - you're a natural at this!"
            ],
            'streak_motivation': [
                "You're on fire! Keep the streak going - every smile counts!",
                "Incredible dedication! Your consistency is inspiring others to smile more!",
                "Amazing streak! You're building a habit that will brighten your days!",
                "Fantastic commitment! Your daily smiles are making the world happier!",
                "Outstanding streak! You're becoming a smile champion!"
            ]
        }
    
    def get_smile_tip(self, smile_score, current_streak=0):
        """Generate a personalized smile tip based on score and streak"""
        
        # Determine score category
        if smile_score <= 3:
            category = 'low_score'
        elif smile_score <= 7:
            category = 'medium_score'
        else:
            category = 'high_score'
        
        # Get base tip
        tip = random.choice(self.tips_database[category])
        
        # Add streak motivation if user has a good streak
        if current_streak >= 3:
            streak_tip = random.choice(self.tips_database['streak_motivation'])
            return f"{tip} {streak_tip}"
        
        return tip
    
    def calculate_streak_update(self, user, current_date=None):
        """Calculate streak updates for a user"""
        if current_date is None:
            current_date = date.today()
        
        # Check if this is a new day upload
        if user.last_upload_date is None:
            # First upload ever
            user.current_streak = 1
            user.longest_streak = max(user.longest_streak, 1)
        else:
            days_since_last = (current_date - user.last_upload_date).days
            
            if days_since_last == 0:
                # Same day upload - no streak change
                pass
            elif days_since_last == 1:
                # Consecutive day - increase streak
                user.current_streak += 1
                user.longest_streak = max(user.longest_streak, user.current_streak)
            else:
                # Streak broken - reset to 1
                user.current_streak = 1
                user.longest_streak = max(user.longest_streak, 1)
        
        user.last_upload_date = current_date
        return user.current_streak, user.longest_streak

    def get_streak_message(self, current_streak, longest_streak):
        """Generate a motivational message based on streak status"""
        if current_streak == 0:
            return "Start your smile streak today!"
        elif current_streak == 1:
            return "Day 1! You're on your way to building a smile habit!"
        elif current_streak < 7:
            return f"Great job! {current_streak} days in a row - keep it up!"
        elif current_streak < 30:
            return f"Amazing! {current_streak} days streak - you're becoming a smile champion!"
        else:
            return f"Incredible! {current_streak} days streak - you're a true smile master!"
