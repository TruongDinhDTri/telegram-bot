import pyotp
import time
import asyncio
from threading import Timer
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, PicklePersistence



with open('general_data.json', 'r') as json_file: 
    data = json.load(json_file)

TOKEN = data['token']  # token of your bot
CHAT_ID = data['chat_id']  # your bot chat id
otp_secret = data['otp_secret']  # Google Authenticator secret key
active_users = data['active_users']
inactive_user_ids = set(data['inactive_user_ids'])
users_links_added = data["users_links_added"]
inactive_time = data['inactive_time']
admin_id = data['admin_id']
monitoring_state = data['monitoring_state']



# Generate the OTP object
totp = pyotp.TOTP(otp_secret)


# Function to save active_users back to the JSON file
def save_data():
    with open('general_data.json', 'w') as json_file:
        data['active_users'] = active_users  # Update active_users in the data dictionary
        data['inactive_user_ids'] = list(inactive_user_ids)
        data['users_links_added'] = users_links_added
        data['monitoring_state'] = monitoring_state
        json.dump(data, json_file, indent=4)  # Save the updated data
        
# Function to clear active_users and update JSON
def clear_data():
    global active_users  # Declare it as a global variable
    active_users.clear()  # Clear the active_users dictionary
    data['active_users'] = {}  # Clear active_users in the data dictionary as well
    with open('general_data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)  # Save the updated data
        
def is_authenticated(user_id):
    # ~ Because if the user first time speak to the bot then they won't be in neither active_users or inactive_users
    # ~ This is use to know which user's session is expired
    return user_id in active_users and user_id not in inactive_user_ids

def is_new_user(user_id):
    return user_id not in active_users and user_id not in inactive_user_ids

async def authenticate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_name = update.message.from_user.username  # Get the username
    if user_id in active_users:
        await update.message.reply_text("You've already authenticated, feel free to enjoy")
        return 
    if len(context.args) == 1:
        user_otp = context.args[0]
        if totp.verify(user_otp):
            await update.message.reply_text(f"Authenticated Successfully! Welcome {user_name} Please enjoy our services")
            if user_id not in active_users:
                active_users[user_id] = {}
            active_users[user_id]['logged_time'] = time.time() 
            active_users[user_id]['expired_time'] = time.time() + inactive_time # 60 seconds starting from now 
            active_users[user_id]['user_name'] = user_name
            if user_id in inactive_user_ids:
                inactive_user_ids.discard(user_id)
            # * I think here you can start another thread to run the count down in the background.
            save_data()  # Save the updated active_users to JSON
            start_log_out(user_id, update)
        else: 
            await update.message.reply_text("Invalid OTP! Please try again!")
    else: 
        await update.message.reply_text("Usage: /authenticate [OTP]")

def start_log_out(user_id, update):
    user_id = str(update.message.from_user.id)
    async def log_user():
        if user_id in active_users and time.time() > active_users[user_id]['expired_time']:
            del active_users[user_id]
            inactive_user_ids.add(user_id)
            save_data()  # Save the updated active_users to JSON
            await update.message.reply_text("Session expired. Please authenticate again or /start to start the conversation again")
    
    async def schedule_logout():
        await asyncio.sleep(inactive_time)  # 20 seconds delay
        await log_user()

    # Schedule the logout after 20 seconds
    asyncio.create_task(schedule_logout())


if __name__ == '__main__':
    print('Starting Bot...')
    persistence = PicklePersistence(filepath='bot_data_testing')
    app = Application.builder().token(TOKEN).persistence(persistence).build()
    app.add_handler(CommandHandler('authenticate', authenticate_command))
    
    print('Polling...')
    app.run_polling(poll_interval=4)
