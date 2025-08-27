# TODO: Fix Missing View Functions in SmileSphere App

## Current Issue
The application is failing with a template rendering error because the `base.html` template is checking for view functions that don't exist in `app.py`.

## Missing View Functions to Implement

### 1. leaderboard()
- **Purpose**: Display user rankings by smile coins
- **Template**: `templates/leaderboard.html`
- **Required Data**: List of users ordered by `smile_coins` descending
- **Implementation**: Query all users, order by smile_coins, pass to template

### 2. rewards()
- **Purpose**: Display available rewards for redemption
- **Template**: `templates/rewards.html`
- **Required Data**: List of available rewards from Reward model
- **Implementation**: Query all available rewards, pass to template

### 3. profile()
- **Purpose**: Show user profile with photos and redemption history
- **Template**: `templates/profile.html`
- **Required Data**: 
  - User's photos (already available via current_user.photos)
  - User's redemption history (Redemption model with reward relationship)
- **Implementation**: Query user's redemptions with reward details

### 4. redeem_reward()
- **Purpose**: Handle reward redemption requests
- **Template**: Referenced in `rewards.html` form action
- **Required**: POST method, deduct coins, create redemption record
- **Implementation**: Process form submission, validate coin balance, create redemption

## Steps Completed
- [x] Analyzed the error and identified missing view functions
- [x] Read all template files to understand data requirements
- [x] Created implementation plan

## Steps Remaining
- [ ] Implement leaderboard() function in app.py
- [ ] Implement rewards() function in app.py
- [ ] Implement profile() function in app.py
- [ ] Implement redeem_reward() function in app.py
- [ ] Test the application to ensure no more template errors
