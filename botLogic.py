from typing import Final
import time
import telegram
import threading
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, ConversationHandler, PicklePersistence
import requests
import re
from get_ip_info import *
from authenticate import *
# from undetected_chromedriver.options import ChromeOptions
# from undetected_chromedriver import Chrome
from seleniumbase import Driver



TOKEN: Final = data['token']  # token of your bot
CHAT_ID: Final = data['chat_id']  # your bot chat id
ADD_LINKS = 1
MONITORING_LINKS = 1
CHOOSE_DELETE_ALL_LIST = 1
CHOOSE_DELETE_LIST, DELETE_SPECIFIC_LINK = range(2)
VIEW_LINK = 1

# Flags to track state
CHOSEN_LINK_ALREADY = False
ADD_LINK_ALREADY = False
monitoring_threads = {}
monitoring_stop_events = {}
monitoring_tasks = {}

'''
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
..................................................:-+********+=:....................................
..............................................:=#*=:...........-*#=:................................
............................................-#+...........::::::::.*#:..............................
..........................................-#-.:::::::::::::::::::::::+*:............................
........................................:+*:::::::::::::::::::::::::::-#:...........................
........................................+=.::::::::::::::::::::::::::::-#:..........................
.......................................+*:::::::::::::::::::::::::::::--=+..........................
......................................:#:::::::::::::::*++%*::::::::::***#..........................
......................................-*::::::::::::::-##*%%+:::::::::*%##***=:.....................
......................................=+:::::::::::::::#%%%%=:::::::-*##=-====*+....................
......................................=+::::::::::::::::=#*-:::::=#+======++++=#:...................
...........................-***#+:....-#:::::::::::::::::::::-+#*======+*+++++=#:...................
.........................:*=.:::-#:...:*=::::::::::::::::-*#+=======+**+++++++#-....................
........................:#-::::::-#-...:#-::::::::::::::-#===+==+##*+++++++##=......................
........................+=:::-----:=*#*++#=::::::::::::--#*==++##*+++++++++#=.......................
.......................:#:::::::::::::::::+*---:::::------=*##*+===++**+++=*+.......................
......................:*=:::::::::::::::::::++------------------=*###***##+:........................
......................+=::::::::::::::::::::-------------------=+*##-...............................
.....................=*:::--::::::::::::::::::----------------------=#+:............................
....................:#-:=*--+#+--:::---===--:::::---------------------=#-...........................
....................=+:-#::::...-==-::.....-*#-::::::----------------:::#-..........................
....................#-:+*:::::::::......::::::=*:::::::::::::---::::::::-#:.........................
...................:#-:*#-:::::::::::::::::::::=*::::::::::::::::::::::::+*.........................
...................:#-:#=+-:::::::::::::::::::::*=::::::::::::::::::::::::#:........................
...................:#--#=::=-:::::::::::::::::::=+::::::::::::::::::::::::#:........................
....................*=-+*:::::::::::::::::::::::=*::::::::::::::::::::::::#:........................
....................-*--*=:::::::::::::::::::::-*+:::::::::::::::::::::::=#:........................
....................:*=--#=:::::::::::::::::::--#--:::::::::::::::::::::-*+.........................
.....................:#=--**-:::::::::::::::---#=---:::::::::::::::::---=#..........................
......................:#=--=**---::::::::----+#=-----------------------=#:..........................
........................+*----+#*+=-------=*#=------------------------=#:...........................
......................::::**------=+*###*=--------------------------=#+:::..........................
.....................:::::::=#*-----------------------------------+#+::::::.........................
.....................::::::::::=*#*=-------------------------=+**+-::::::::.........................
......................:::::::::::::-=**##**+++======++**###*+-::::::::::::..........................
........................::::::::::::::::::::::::::::::::::::::::::::::::............................
...........................::::::::::::::::::::::::::::::::::::::::::...............................
.................................::::::::::::::::::::::::::::::.....................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
'''
#* 🌅 START Command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_name = update.message.from_user.username  # Get the username
    
    if user_id in active_users:
        await update.message.reply_text(f"Hi! {user_name} You're already authenticated. Enjoy our service!")
    else:
        await update.message.reply_text("Please authenticate using /authenticate [OTP]")
    
    
# * 🌅 HELP Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if is_new_user(user_id): 
        await update.message.reply_text("Please authenticate using /authenticate [OTP]")
        return 
    # ~ User not in active_users but IN inactive_users => They're expired
    elif not is_authenticated(user_id):
        await update.message.reply_text("Your session expired! Please use /start to begin or /authenticate to log in again.")
        return
    else:
        await update.message.reply_text("Hello! Here are the available commands: \n"
                                    "/start - start the bot \n"
                                    "/help - Show this help message\n"
                                    "/authenticate [OTP] - to authenticate your credentials\n"
                                    "/add - Add new links to monitoring. Syntax: /add [your_link] \n"
                                    "/on - Start monitor links. Syntaxt: /on [link_number]\n"
                                    "/off - Stop monitor links\n"
                                    "/view - View all your links\n"
                                    "/delete - Delete specific links. Syntaxt: /delete [link_number]\n"
                                    "/deleteall - Delete all links\n"
                                    "/info - Show your personal info\n"
                                    # "/users - Show all active users [admin only]\n"
                                    # "/logout [user_id] - Log out a users [admin only]\n"
                                    # "/logoutall - Log out all users [admin only]\n"
                                    )
    



async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_name = update.message.from_user.username  # Get the username
    
    if is_new_user(user_id): 
        await update.message.reply_text("Please authenticate using /authenticate [OTP]")
        return 
    elif not is_authenticated(user_id):
        await update.message.reply_text("Your session expired! Please use /start to begin or /authenticate to log in again.")
        return
    
    if user_id in active_users:
        time_left = active_users[user_id]['expired_time'] - time.time()
        logged_time = int(active_users[user_id]['logged_time'])
        # Call the nested helper function to calculate the time
        dt_object = datetime.fromtimestamp(logged_time)
        formatted_date_time = dt_object.strftime("%d/%m/%Y %H:%M:%S %p")
        def calculate_time_left(time_seconds):
            hours = int(time_seconds // 3600)
            minutes = int((time_seconds % 3600) // 60)
            seconds = int(time_seconds % 60)
            return f"{hours} hours, {minutes} minutes, {seconds} seconds"
        time_formatted = calculate_time_left(time_left)
        await update.message.reply_text(f"👤 User {user_name}\n"
                                        "\n"
                                        f"\n Logged Time {formatted_date_time}"
                                        "\n"
                                        f"Time left: {time_formatted}")

    
    
    
# * 🌅 ADDLinks Command
async def addlinks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    args = context.args  # Get command arguments
    
    # ~ User first time come in they neither in the active_users or in inactive_users
    if is_new_user(user_id): 
        await update.message.reply_text("Please authenticate using /authenticate [OTP]")
        return 
    # ~ User not in active_users but IN inactive_users => They're expired
    elif not is_authenticated(user_id):
        await update.message.reply_text("Your session expired! Please use /start to begin or /authenticate to log in again.")
        return
    # Check if an argument was provided
    if len(args) != 1:
        return await update.message.reply_text("Please provide a single valid link. Usage: /add [link]")
    
    link = args[0].strip()
    
    valid_url_pattern = re.compile(r'^https://iplogger\.org/logger/[a-zA-Z0-9]*/?')
    
    try:
        if user_id not in users_links_added:
            users_links_added[user_id] = {
                "stored_links": [],
                "monitoring_links": []
            }
        
        if link in users_links_added[user_id]["stored_links"]:
            return await update.message.reply_text("Link already in the database, thanks.")
    
        if valid_url_pattern.match(link):
            users_links_added[user_id]["stored_links"].append(link)
            save_data()
            return await update.message.reply_text(f'New link {link} added. If you want to add another link, use /add [link] again.')
        else:
            return await update.message.reply_text("Invalid link! Please provide a valid link in the format https://iplogger.org/logger/xxxxxx. Use /add [link]")
    except Exception as e:
        return await update.message.reply_text(f"Something went wrong! Failed to add link: {str(e)}. Please try again.")


# * 🌅 VIEWS Command
async def view_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    response = ''
    # ~ User first time come in they neither in the active_users or in inactive_users
    if is_new_user(user_id): 
        await update.message.reply_text("Please authenticate using /authenticate [OTP]")
        return 
    # ~ User not in active_users but IN inactive_users => They're expired
    elif not is_authenticated(user_id):
        await update.message.reply_text("Your session expired! Please use /start to begin or /authenticate to log in again.")
        return    
    else: 
        if user_id not in users_links_added:
            users_links_added[user_id] = {}
            users_links_added[user_id]["stored_links"] = []
            users_links_added[user_id]["monitoring_links"] = []
        # Prompt the user to choose which list to view
        if ('stored_links' not in users_links_added[user_id] or not users_links_added[user_id]['stored_links']):
            await update.message.reply_text("Please add some links before viewing them!")
            return VIEW_LINK
        if 'stored_links' in users_links_added[user_id] and len(users_links_added[user_id]['stored_links']) >= 0:
            print('theeree stored linkks??')
            response = "\n--STORED LINKS--\n" + "\n".join([f"{i+1} 👉🏻 {item}" for i, item in enumerate(users_links_added[user_id]['stored_links'])])
        
        await update.message.reply_text(response)
            
        return VIEW_LINK


async def delete_all_links_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    # Check if the user is new or has an expired session
    if is_new_user(user_id): 
        await update.message.reply_text("Please authenticate using /authenticate [OTP]")
        return 
    
    if not is_authenticated(user_id):
        await update.message.reply_text("Your session expired! Please use /start to begin or /authenticate to log in again.")
        return
    
    # Ensure user data is initialized
    if user_id not in users_links_added:
        users_links_added[user_id] = {}

    # Check if there are any links to delete
    if 'stored_links' not in users_links_added[user_id] or not users_links_added[user_id]['stored_links']:
        return await update.message.reply_text("You don't have any links to delete.")


    if user_id in monitoring_state and monitoring_state[user_id]:
        return await update.message.reply_text("Please stop monitoring first by using /off before deleting links.")

    # Clear all stored links
    users_links_added[user_id]['stored_links'] = []

    # Save the updated data
    save_data()

    # Notify the user
    return await update.message.reply_text("All your links have been deleted, and monitoring has been stopped.")
    


async def delete_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    args = context.args  # Get command arguments
    
    if is_new_user(user_id): 
        await update.message.reply_text("Please authenticate using /authenticate [OTP]")
        return 
    # ~ User not in active_users but IN inactive_users => They're expired
    elif not is_authenticated(user_id):
        await update.message.reply_text("Your session expired! Please use /start to begin or /authenticate to log in again.")
        return
    
    if user_id not in users_links_added:
        users_links_added[user_id] = {}
        users_links_added[user_id]["stored_links"] = []
        users_links_added[user_id]["monitoring_links"] = []
    
    links = users_links_added[user_id]["stored_links"]
    
    # Check if monitoring is active
    if user_id in monitoring_state and monitoring_state[user_id]:
        await update.message.reply_text("Please stop monitoring first using /off before deleting any links.")
        return
    
    
    if not links:
        await update.message.reply_text("You don't have any links to delete.")
        return
    
        # Check if an argument was provided
    if len(args) != 1:
        await update.message.reply_text("Please provide a single number to delete. Usage: /delete [number]")
        return
    
    try:
        link_number = int(args[0]) - 1  # Convert to zero-based index

        if 0 <= link_number < len(links):
            deleted_link = links.pop(link_number)  # Remove the link from 'links'
            
            # Also remove the link from 'monitoring_links' if it exists there
            if deleted_link in users_links_added[user_id]["monitoring_links"]:
                users_links_added[user_id]["monitoring_links"].remove(deleted_link)

            save_data()
            return await update.message.reply_text(f"Link deleted: {deleted_link}")
        else:
            await update.message.reply_text("Invalid link number. Please try again.")
            return
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return



async def on_monitor_command(update:Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    if is_new_user(user_id): 
        await update.message.reply_text("Please authenticate using /authenticate [OTP]")
        return 
    # ~ User not in active_users but IN inactive_users => They're expired
    elif not is_authenticated(user_id):
        await update.message.reply_text("Your session expired! Please use /start to begin or /authenticate to log in again.")
        return
    
    # Ensure that the user data exists and is initialized    
    if user_id not in users_links_added or 'stored_links' not in users_links_added[user_id] or len(users_links_added[user_id]['stored_links']) == 0:
        users_links_added[user_id] = {"stored_links": [], "monitoring_links": []}
        return await update.message.reply_text("You have no links stored. Please add some links first.")
    
    try:
        index = int(context.args[0]) - 1
    except (IndexError, ValueError):
        return await update.message.reply_text("Please provide a valid link index (e.g., /on 1).")

    if index < 0 or index >= len(users_links_added[user_id]['stored_links']):
        return await update.message.reply_text("Index out of range. Please provide a valid index.")

    link = users_links_added[user_id]["stored_links"][index]
    
    
    if user_id not in monitoring_tasks:
        monitoring_tasks[user_id] = {}
        
    if link in monitoring_tasks[user_id]:
        return await update.message.reply_text(f"Already monitoring link: {link}")
    
    async def start_monitoring():
        while True:
            await monitor_iplogger(user_id, link, interval=5)
    
    task = asyncio.create_task(start_monitoring())
    monitoring_tasks[user_id][link] = task
    
    if link not in users_links_added[user_id]["monitoring_links"]:
        users_links_added[user_id]["monitoring_links"].append(link)
    
    
    formatted_items = [f'Link {i + 1}: {item}' for i, item in enumerate(users_links_added[user_id]['stored_links'])]
    response = '\n'.join(formatted_items)


    monitoring_state[user_id] = True
    save_data()

    return await update.message.reply_text(f'Started monitoring link {index + 1}: {link}\n\nAll stored links:\n{response}')


async def off_monitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    
    if is_new_user(user_id): 
        await update.message.reply_text("Please authenticate using /authenticate [OTP]")
        return 
    # ~ User not in active_users but IN inactive_users => They're expired
    elif not is_authenticated(user_id):
        await update.message.reply_text("Your session expired! Please use /start to begin or /authenticate to log in again.")
        return


    tasks = monitoring_tasks[user_id].values()
    
    for task in tasks:
        task.cancel()
        
    # Wait for tasks to properly cancel
    done, pending = await asyncio.wait(tasks, timeout=3, return_when=asyncio.ALL_COMPLETED)
    
    
    for task in pending:
        task.cancel()
    
    # Clear the user's monitoring tasks
    del monitoring_tasks[user_id]
    users_links_added[user_id]["monitoring_links"] = []
    monitoring_state[user_id] = False
    save_data()

    return await update.message.reply_text("Monitoring stopped successfully.")
    
    
    

def startup_monitoring():
    print("Restarting monitoring for users...")
    for user_id, state in monitoring_state.items():
        if state:
            # Ensure user has monitoring links
            if user_id in users_links_added and 'monitoring_links' in users_links_added[user_id]:
                links = users_links_added[user_id]['monitoring_links']
                
                # Create a task for each link
                for link in links:
                    if link not in monitoring_tasks.get(user_id, {}):
                        task = asyncio.create_task(monitor_iplogger(user_id, link, interval=5))
                        monitoring_tasks.setdefault(user_id, {})[link] = task

    save_data()

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    # Check if the user is the admin
    if user_id != admin_id:
        await update.message.reply_text("You do not have permission to use this command.")
        return

    response = ''
    print('active user: ', active_users)

    # Admin can view even if there are no active users
    response = "Active Users List:\n"
    if not active_users:
        response += 'There\'s no user online at the moment'
    else:
        for user_id, user_infos in active_users.items():
            response += f"\n User ID: {user_id} \n"
            logged_time = datetime.fromtimestamp(int(user_infos.get('logged_time', 0))).strftime("%d/%m/%Y %H:%M:%S %p")
            expired_time = datetime.fromtimestamp(int(user_infos.get('expired_time', 0))).strftime("%d/%m/%Y %H:%M:%S %p")
            response += f"----LOGGED TIME: {logged_time}\n"  # Display Logged Time
            response += f"----EXPIRED TIME: {expired_time}\n"  # Display Expire Time
            response += f"----USERNAME: {user_infos.get('user_name', 'N/A')}\n\n"  # Display Username

    await update.message.reply_text(response)
    
async def logout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    # Check if the user is the admin
    if user_id != admin_id:
        await update.message.reply_text("You do not have permission to use this command.")
        return

    # Check if exactly one user ID is provided
    if len(context.args) != 1:
        await update.message.reply_text("Please provide exactly one user ID to log out, e.g., /logout [user_id].")
        return

    target_user_id = context.args[0]  # Get the user ID from the command arguments

    # Check if the target user is in active_users
    if str(target_user_id) not in active_users:
        await update.message.reply_text(f'User ID {target_user_id} is not currently logged in.')
        return

    # Remove the user from active_users and inactive_users
    if str(target_user_id) in active_users:
        del active_users[target_user_id]
        inactive_user_ids.add(target_user_id)  # Optionally add to inactive users if needed

    # Save the updated active_users to the JSON file
    save_data()  # Call your existing save_data function

    await update.message.reply_text(f'User ID {target_user_id} has been logged out successfully.')

    
async def logoutall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    # Check if the user is the admin
    if user_id != admin_id:
        await update.message.reply_text("You do not have permission to use this command.")
        return
    if not active_users:
        await update.message.reply_text('There\'s no user online at the moment to logout')
        return 

    clear_data()  # This function should clear the active_users
    await update.message.reply_text('\nLogout all users completed\n')

    



# todo 💬 HANDLE MESSAGE 
def handle_response(text: str) -> str:
    processed: str = text.lower();
    if 'hello' in processed:
        return 'Hey there!'
    if 'how are you' in processed: 
        return "I am good"
    return "I do not understand what you wrote..."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text    
    
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}" ')
    response: str = handle_response(text)
    print('Bot:' , response)
    
    await update.message.reply_text(response)
    
    
async def error(update: Update, context:ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused an error {context.error}')
    


# ! 🌅 AUTOSENT MESSAGE Command
def auto_sent_message(token, user_id, message):
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": user_id,
        "text": message
    }
    
    try: 
        response = requests.get(url, data = payload)
        # Raise an exception if the status was not successful
        response.raise_for_status()
        
        return 'Message Sent Successfully'
    except requests.exceptions.RequestException as e:
        return f'Failed to sent the message with Exception: {e}'
    
    
async def monitor_iplogger(user_id, link, interval=5):
    last_data = {}
    
    while True:
        code = link.rstrip('/').split('/')[-1]
        try:
            driver = Driver(headless=True, uc=True)
            notes, date_time, ip_address_details = await get_full_info_iplogger(driver, link)
            driver.quit()
        except Exception as e:
            print(f"An error occurred while getting full info: {e}")
            # Optionally, add a delay before retrying
            await asyncio.sleep(interval)
            continue
        
        if last_data.get(code) != date_time and len(date_time) != 0:
            print('dateTime: ', date_time)
            print('time: ', last_data.get(code))
            print(f'------------------------\nMonitoring {link}')
            print("New data detected!")
            combined_info_string = get_ip_info(date_time, ip_address_details)
            await asyncio.to_thread(auto_sent_message, TOKEN, user_id,
                                    f'\nNOTES: {notes}\n'+
                                    f'\nLink URL: {link} \n' +
                                    combined_info_string)
            last_data[code] = date_time
        else:
            print(f"No new data for {link}..................")
            print(last_data)
        
        print('going to sleep now')
        await asyncio.sleep(interval)
        print('Done sleeping')




if __name__ == '__main__':
    print('Starting Bot...')
    
    clear_data()
    persistence = PicklePersistence(filepath='bot_data_testing')
    
    # Build application with job queue
    app = Application.builder().token(TOKEN).persistence(persistence).build()
    
    # Add handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('add', addlinks_command))
    app.add_handler(CommandHandler('delete', delete_link))
    app.add_handler(CommandHandler('deleteall', delete_all_links_command))
    app.add_handler(CommandHandler('authenticate', authenticate_command))
    app.add_handler(CommandHandler('info', info_command))
    app.add_handler(CommandHandler('view', view_command))
    app.add_handler(CommandHandler('users', users_command))
    app.add_handler(CommandHandler('logoutall', logoutall_command))
    app.add_handler(CommandHandler('logout', logout_command))
    app.add_handler(CommandHandler('on', on_monitor_command))
    app.add_handler(CommandHandler('off', off_monitor_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)

    # Run startup_monitoring asynchronously
    # startup_monitoring()

    # Start polling
    print('Polling...')
    app.run_polling(poll_interval=4)





    
