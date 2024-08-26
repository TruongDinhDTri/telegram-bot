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
from undetected_chromedriver.options import ChromeOptions
from undetected_chromedriver import Chrome
from selenium_stealth import stealth



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
                                    "/addlinks - Add new links to monitoring \n"
                                    "/help - Show this help message\n"
                                    "/monitorlinks - Monitor stored links\n"
                                    "/view - View stored and monitoring links\n"
                                    "/deletelink - Delete specific links\n"
                                    "/deleteall - Delete all links\n"
                                    "/authenticate [OTP] - to authenticate your credentials\n"
                                    "/info - to show info for your personal account\n")
    



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
    # ~ User first time come in they neither in the active_users or in inactive_users
    if is_new_user(user_id): 
        await update.message.reply_text("Please authenticate using /authenticate [OTP]")
        return 
    # ~ User not in active_users but IN inactive_users => They're expired
    elif not is_authenticated(user_id):
        await update.message.reply_text("Your session expired! Please use /start to begin or /authenticate to log in again.")
        return
    else:
        await update.message.reply_text("Please paste you link");
        return ADD_LINKS

# ~ 🐥 STORE LINK HANDLE ADDLINKS
async def handle_addlinks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    link = update.message.text.strip()

    valid_url_pattern = re.compile(r'^https://iplogger\.org/logger/[a-zA-Z0-9]*/?')

    try:
        if user_id not in users_links_added:
            print('ADD LINKS: USER NOT IN ADD LINKS: ')
            users_links_added[user_id] = {}
            users_links_added[user_id]["stored_links"] = []
            users_links_added[user_id]["monitoring_links"] = []
        if link in users_links_added[user_id]["stored_links"]:
            print('link already in')
            await update.message.reply_text('Link already in the database, thanks')
            return ConversationHandler.END
        if valid_url_pattern.match(link):
            print('add links here')
            users_links_added[user_id]["stored_links"].append(link)
            await update.message.reply_text(f'New link {link} added, If you want to add another link, use /addlinks again.')
            save_data()
            return ConversationHandler.END
        else: 
            await update.message.reply_text("Invalid link! Please provide a link in the format https://iplogger.org/logger/xxxxxx. Please /addlinks again")
            return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(f"Something went wrong! Failed to add link: {str(e)}. Please try again.")
        return ConversationHandler.END




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

    # Stop the current monitoring if active
    if user_id in monitoring_stop_events:
        monitoring_stop_events[user_id].set()
        monitoring_threads[user_id].join()

        del monitoring_stop_events[user_id]
        del monitoring_threads[user_id]
        
        monitoring_state[user_id] = False

    # Clear all stored links
    users_links_added[user_id]['stored_links'] = []

    # Save the updated data
    save_data()

    # Notify the user
    return await update.message.reply_text("All your links have been deleted, and monitoring has been stopped.")
    


        


# ~ If delete from 'links': delete in links will also be delete from 'monitoring_links"
# ~ If delete from 'monitoring_links': delete only in the 'monitoring_links'
async def delete_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    
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
    
    if not links:
        await update.message.reply_text("You don't have any links to delete.")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "Here are your links: \n" + 
        "\n".join([f"{i+1} 🪩 {item}" for i, item in enumerate(links)]) + 
        "\n\nPlease choose the number of the link you want to delete, or type 'cancel' to exit."
    )
    
    return DELETE_SPECIFIC_LINK


async def delete_link_by_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text.strip()
    
    if text.lower() == 'cancel':
        await update.message.reply_text("Link deletion cancelled.")
        return ConversationHandler.END
    
    try:
        link_number = int(text) - 1  # Convert to zero-based index
        links = users_links_added[user_id]["stored_links"]

        if 0 <= link_number < len(links):
            deleted_link = links.pop(link_number)  # Remove the link from 'links'
            await update.message.reply_text(f"Link deleted: {deleted_link}")
            save_data()

            # Stop the current monitoring
            if user_id in monitoring_stop_events:
                monitoring_stop_events[user_id].set()
                monitoring_threads[user_id].join()

                del monitoring_stop_events[user_id]
                del monitoring_threads[user_id]
                save_data()
                
            await update.message.reply_text("Link deletion successful")

            # Re-monitor if there are still links and monitoring is active
            if links and monitoring_state.get(user_id, False):
                await update.message.reply_text("Re-starting monitoring for remaining links.")
            
                
                stop_event = threading.Event()
                monitoring_stop_events[user_id] = stop_event
                monitoring_threads[user_id] = threading.Thread(target=monitor_iplogger, args=(user_id, users_links_added[user_id]['stored_links'], stop_event, 5),)
                
                
                monitoring_threads[user_id].start()
                monitoring_state[user_id] = True
                save_data()
            return ConversationHandler.END
        else:
            await update.message.reply_text("Invalid link number. Please try again.")
            return DELETE_SPECIFIC_LINK
    
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return DELETE_SPECIFIC_LINK





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
        users_links_added[user_id] = {}
        users_links_added[user_id]["stored_links"] = []
        return await update.message.reply_text("You have no links stored. Please add some links first.")
    
    formatted_items = [f'Link {i + 1}: {item}' for i, item in enumerate(users_links_added[user_id]['stored_links'])]
    response = '\n'.join(formatted_items)
    
    stop_event = threading.Event()
    monitoring_stop_events[user_id] = stop_event
    
    
    monitor_thread = threading.Thread(target=monitor_iplogger, args=(user_id, users_links_added[user_id]['stored_links'], stop_event, 5), daemon=True)
    monitoring_threads[user_id] = monitor_thread
    monitor_thread.start()
    
    
    monitoring_state[user_id] = True
    save_data()

    
    return await update.message.reply_text(f'Here are the monitoring links:\n{response}\n')

async def off_monitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    
    if is_new_user(user_id): 
        await update.message.reply_text("Please authenticate using /authenticate [OTP]")
        return 
    # ~ User not in active_users but IN inactive_users => They're expired
    elif not is_authenticated(user_id):
        await update.message.reply_text("Your session expired! Please use /start to begin or /authenticate to log in again.")
        return

    if user_id in monitoring_stop_events:
        monitoring_stop_events[user_id].set()
        monitoring_threads[user_id].join()

        del monitoring_stop_events[user_id]
        del monitoring_threads[user_id]
        
        monitoring_state[user_id] = False
        save_data()

        return await update.message.reply_text("Monitoring stopped successfully.")
    else:
        return await update.message.reply_text("No active monitoring session found.")
    
    
    

def startup_monitoring():
    print("Restarting monitoring for users...")
    for user_id, state in monitoring_state.items():
        if state:
            stop_event = threading.Event()
            monitoring_stop_events[user_id] = stop_event
            
            monitor_thread = threading.Thread(
                target=monitor_iplogger,
                args=(user_id, users_links_added[user_id]['stored_links'], stop_event, 5),
                daemon=True
            )
            monitoring_threads[user_id] = monitor_thread
            monitor_thread.start()

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
    
    
def monitor_iplogger(user_id, monitoring_links, stop_event, interval = 5):
    last_data = {}
    while not stop_event.is_set():
        for link in monitoring_links:
            code = link.rstrip('/').split('/')[-1]
            chrome_options = ChromeOptions()
            chrome_options.page_load_strategy = 'none'
            chrome_options.add_argument('--headless')
            driver = Chrome(options=chrome_options, service_args=['--verbose'])
            print(f'Using random proxies for monitoring: {random_proxy}')
            try:
                notes, date_time, ip_address_details = get_full_info_iplogger(driver, link, code)
            except Exception as e:
                print(f"An error occurred while getting full info: {e}")
            if last_data.get(code) != date_time and len(date_time) != 0:
                    print('dateTime: ', date_time)
                    print('time: ', last_data.get(code) )
                    print(f'------------------------\nMonitoring {link}')
                    print("New data detected!")
                    combined_info_string = get_ip_info(date_time, ip_address_details)
                    auto_sent_message(TOKEN, user_id,
                                    f'\nNOTES: {notes}\n'+
                                    f'\nLink URL: {link} \n' +
                                    combined_info_string)
                    last_data[code] = date_time
            else:
                print(f"No new data for {link}..................")
                print(last_data)
        time.sleep(interval)
    print(f"Monitoring stopped for user {user_id}.")


if __name__ == '__main__':
    print('Starting Bot...')
    
    
    clear_data()
    persistence = PicklePersistence(filepath='bot_data_testing')
    
    # Build application with job queue
    app = Application.builder().token(TOKEN).persistence(persistence).build()
    
    # Add handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('deleteall', delete_all_links_command))
    app.add_handler(CommandHandler('authenticate', authenticate_command))
    app.add_handler(CommandHandler('info', info_command))
    app.add_handler(CommandHandler('view', view_command))
    app.add_handler(CommandHandler('users', users_command))
    app.add_handler(CommandHandler('logoutall', logoutall_command))
    app.add_handler(CommandHandler('logout', logout_command))
    app.add_handler(CommandHandler('on', on_monitor_command))
    app.add_handler(CommandHandler('off', off_monitor_command))

    # Add conversation handlers
    addlinks_handler = ConversationHandler(
        entry_points=[CommandHandler('add', addlinks_command)],
        states={ADD_LINKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_addlinks)]},
        fallbacks=[]
    )
    app.add_handler(addlinks_handler)

    delete_links_handler = ConversationHandler(
        entry_points=[CommandHandler('delete', delete_link)],
        states={DELETE_SPECIFIC_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_link_by_number)]},
        fallbacks=[]
    )
    app.add_handler(delete_links_handler)

    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)

    # Start monitoring on startup
    # Run startup_monitoring asynchronously
    startup_monitoring()

    # Start polling
    print('Polling...')
    app.run_polling(poll_interval=4)





    
