
from pickle import TRUE
from typing import Final
import threading
from threading import Thread
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, ConversationHandler, PicklePersistence
import time
import requests
from bs4 import BeautifulSoup


TOKEN: Final = ''
CHAT_ID: Final = '1700028265'
BOT_USERNAME: Final = '@wizSIZ_bot'
IPLOGGER_LINK: Final = 'https://iplogger.org/logger/'
ADD_LINKS = 1
MONITORING_LINKS = 1
CHOSEN_LINK_ALREADY = False

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
# update: represents the incoming update from telegram API 
    await update.message.reply_text("Hello! Thanks for chatting with me! I am Wiganz Bot!")
    
# * 🌅 HELP Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Here are the available commands: \n"
                                    "/start - start the bot \n"
                                    "/addlinks - Add new links \n"
                                    "/help - Show this helo message")
    
# * 🌅 CUSTOM Command
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command")
    
    

# * 🌅 ADDLinks Command
async def addlinks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please paste your links here one at a time");
    return ADD_LINKS


# ~ 🐥 STORE LINK
async def store_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id: int = update.message.from_user.id
    link: str = update.message.text
    
    # store the linkk in the user's context 
    if user_id not in context.user_data:
        context.user_data[user_id] = {
            'links': [],
            'monitoring_links': []
        }
    context.user_data[user_id]['links'].append(link)
    
    await update.message.reply_text('Linked add, You can add another one or type /done when you are finish')
    return ADD_LINKS



# * 🌊 MONITORING Command

async def monitoringlinks_command(update:Update, context: ContextTypes.DEFAULT_TYPE):
    user_id: int = update.message.from_user.id

    # Ensure that the user data exists and is initialized
    if user_id not in context.user_data or 'links' not in context.user_data[user_id]:
        await update.message.reply_text("You have no links stored. Please add some links first.")
        return ConversationHandler.END
    
    links = context.user_data[user_id]['links']
    formatted_links = '\n'.join([f"{i + 1}. {link}" for i, link in enumerate(links)])

    await update.message.reply_text(
        f"Please choose which links below you want to monitor\n{formatted_links}\n"
    )
    return MONITORING_LINKS


# ~ 🌋 CHOOSING LINKS TO MONITORING 
async def choose_links(update:Update, context: ContextTypes.DEFAULT_TYPE):
    global CHOSEN_LINK_ALREADY
    user_id: int = update.message.from_user.id
    position: str = update.message.text
    # Ensure position is a valid integer
    try:
        position_index = int(position) - 1  # Convert input to zero-based index
    except ValueError:
        await update.message.reply_text("Please enter a valid number corresponding to the link.")
        return MONITORING_LINKS
    
        # Ensure that the user data exists and is initialized
    if 'links' not in context.user_data[user_id] or len(context.user_data[user_id]['links']) == 0:
        await update.message.reply_text("No links available to choose from.")
        return MONITORING_LINKS
    
        # Ensure the position is within the valid range
    if position_index < 0 or position_index >= len(context.user_data[user_id]['links']):
        await update.message.reply_text("Invalid choice. Please choose a valid link number.")
        return MONITORING_LINKS
    
    CHOSEN_LINK_ALREADY = True
    chosen_link = context.user_data[user_id]['links'][position_index]
    # Initialize the monitoring_links list if it doesn't exist
    if 'monitoring_links' not in context.user_data[user_id]:
        context.user_data[user_id]['monitoring_links'] = []
    if chosen_link not in context.user_data[user_id]['monitoring_links']:
        context.user_data[user_id]['monitoring_links'].append(chosen_link)
    
    await update.message.reply_text(f'Chosen link {chosen_link} successfully. You can choose another link to monitor or type /done when you are finished.')
    return MONITORING_LINKS


# * 🌅 DONE Command
async def done(update: Update, context: CallbackContext):
    user_id: int = update.message.from_user.id
    global CHOSEN_LINK_ALREADY
    response = ""

    if CHOSEN_LINK_ALREADY:
        if 'monitoring_links' in context.user_data[user_id]:
            formatted_items = [f'Link {i + 1}: {item}' for i, item in enumerate(context.user_data[user_id]['monitoring_links'])]
            response = '\n'.join(formatted_items)
        # Call the monitor_iplogger function in a separate task
        asyncio.create_task(monitor_iplogger(context.user_data[user_id]['monitoring_links'], 5))
        await update.message.reply_text(
            f'Here are the monitoring links:\n{response}\n'
        )
        print('Monitoring Links:', context.user_data[user_id]['monitoring_links'])
        CHOSEN_LINK_ALREADY = False
        return ConversationHandler.END
    
    if 'links' in context.user_data[user_id]:
        formatted_items = [f'Link {i + 1}: {item}' for i, item in enumerate(context.user_data[user_id]['links'])]
        response = '\n'.join(formatted_items)
    await update.message.reply_text(
        "Thanks for your work 🐥 All links have been saved\n 😽"
        f'Here are your links 👇🏻 \n{response}\n'
    )
    
    print("User data: ", context.user_data[user_id]);
    return ConversationHandler.END;




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
    
    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME,'').strip()
            response: str = handle_response(new_text)
            
        else: 
            return 
    else: 
        response: str = handle_response(text)
    print('Bot:' , response)
    
    await update.message.reply_text(response)
    
    
async def error(update: Update, context:ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused an error {context.error}')
    


# ! 🌅 AUTOSENT MESSAGE Command
def auto_sent_message(token, chat_id, message):
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    
    try: 
        response = requests.get(url, data = payload)
        # Raise an exception if the status was not successful
        response.raise_for_status()
        
        return 'Message Sent Successfully'
    except requests.exceptions.RequestException as e:
        return f'Failed to sent the message with Exception: {e}'




"""
 .--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--. 
/ .. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \
\ \/\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ \/ /
 \/ /`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'\/ / 
 / /\                                                                                / /\ 
/ /\ \   ___                              _   _                        _            / /\ \
\ \/ /  (  _`\                           ( )_( )                    _ ( )_          \ \/ /
 \/ /   | |_) )  _ _ _ __  ___    __     | ,_) |__     __       ___(_)| ,_)   __     \/ / 
 / /\   | ,__/'/'_` | '__)',__) /'__`\   | | |  _ `\ /'__`\   /',__) || |   /'__`\   / /\ 
/ /\ \  | |   ( (_| | |  \__, \(  ___/   | |_| | | |(  ___/   \__, \ || |_ (  ___/  / /\ \
\ \/ /  (_)   `\__,_|_)  (____/`\____)   `\__|_) (_)`\____)   (____(_)`\__)`\____)  \ \/ /
 \/ /                                                                                \/ / 
 / /\.--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--./ /\ 
/ /\ \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \/\ \
\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `' /
 `--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--' 
"""

def get_iplogger_data(code):
    # Form data
    
    print('code passsing in: ', code)
    payload = {
        'interval': 'all',
        'filters': '',
        'page': '1',
        'sort': 'created',
        'order': 'desc',
        'code': {code}
    }

    # Headers (excluding Content-Type and content-length)
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'cookie': f'_lang=us; _autolang=us; cookies-consent=1721871352; confirmation=Sp67xpXBHZeY226232386sRM; cf_clearance=mKy_IeL4t9gkR.RgTYOfI3jZXlpaSx_0dOUpIcGNjKg-1722676948-1.0.1.1-NTXTjfJEdf.M5J8EmuPlBHdxpIIAfkS1kdzFU.ddpckN8mrWIMGr35wc5HmiFVZxPd.e21zbLVahX.yzUJVu7A; _gid=GA1.2.297228745.1722676948; _gat_gtag_UA_67516667_1=1; cursor=EA0V13j7X6C4p8m672q2N731evRXoOjf; __gads=ID=274ad628c2d89cb5:T=1721871346:RT=1722684676:S=ALNI_MY4Ws2UkMN7nX07T9D-9-5sMwXiQg; __gpi=UID=00000ea5712e9c18:T=1721871346:RT=1722684676:S=ALNI_MbmhnCSq0-U4GUQ4xsC4I0Bt3XJug; __eoi=ID=0577e04acefdaa6d:T=1721871346:RT=1722684676:S=AA-AfjbdAs_F3_y6Jht5js18ETY4; loggers=UnZ3TDRLRGlMMENa; turnback=logger%2F{code}%2F; FCNEC=%5B%5B%22AKsRol9Gz6cyUpHs4bBmnyUjrwY1o7DDPzhgwqkXRf3GHuMpVpvgYIKXkGEMHP90RQGzmEVkthvAaFgl2GRMaDl2BTwKTBWDR_pVeFsiBv-Jflastj9-GQYAJalWqDjXsE6bxbrl50iOObwXE0wzi1vvimD70mproA%3D%3D%22%5D%5D; integrity=XaMEUk0wsSjoLjltL1HfhVv5; _ga_7FSG7D195N=GS1.1.1722683685.11.1.1722684719.9.0.0; _ga=GA1.2.2040753983.1721871345; 37852530250738181=3; _autolang=us; _lang=us; clhf03028ja=14.241.246.5; cursor=EA0V13j7X6C4p8m672q2N731evRXoOjf',
        'origin': 'https://iplogger.org',
        'priority': 'u=1, i',
        'referer': 'https://iplogger.org/logger/{code}/',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    # Perform the POST request
    response = requests.post(IPLOGGER_LINK, headers=headers, data=payload)
    json_data_ips = response.json()['content']
    # Combine those html 
    converted = ''.join(json_data_ips)
    # Parse the page using Beautiful Soup
    soup = BeautifulSoup(converted, 'html.parser')
    ip_dates = [div.text for div in soup.select('div.visitor-date div.ip-date')]
    ip_times = [div.text for div in soup.select('div.visitor-date .ip-time')]
    ip_address = [div.text for div in soup.select('div.visitor-ip div.ip-address')]
    date_time = [x + " " +  y for x in ip_dates for y in ip_times]
    print('date_time: ',date_time, "  ", "ip_address", ip_address )
    return date_time, ip_address



def get_ip_info(ip_address):
    # Base URL for ipinfo.io API
    url = f"https://ipinfo.io/{ip_address}/json"

    try:
        # Send GET request to ipinfo.io API
        response = requests.get(url)
        
        # Raise an exception if the request was unsuccessful
        response.raise_for_status()
        
        # Parse the JSON response
        ip_data = response.json()
        
        # Extract relevant information
        ip_info = {
            "IP Address": ip_data.get("ip", "N/A"),
            "City": ip_data.get("city", "N/A"),
            "Region": ip_data.get("region", "N/A"),
            "Country": ip_data.get("country", "N/A"),
            "Location": ip_data.get("loc", "N/A"),
            "Organization": ip_data.get("org", "N/A"),
            "Postal Code": ip_data.get("postal", "N/A"),
            "Timezone": ip_data.get("timezone", "N/A")
        }
        # Format the information as a single string
        ip_info_string = (
            f"IP Address: {ip_info['IP Address']}\n"
            f"City: {ip_info['City']}\n"
            f"Region: {ip_info['Region']}\n"
            f"Country: {ip_info['Country']}\n"
            f"Location: {ip_info['Location']}\n"
            f"Organization: {ip_info['Organization']}\n"
            f"Postal Code: {ip_info['Postal Code']}\n"
            f"Timezone: {ip_info['Timezone']}\n"
        )

        return ip_info_string
    
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the API request
        print(f"Error fetching IP information: {e}")
        return None

    
def monitor_iplogger(monitoring_links,interval = 5):
    last_data = {}
    while True:
        for link in monitoring_links:
            #Extract code from url
            code = link.rstrip('/').split('/')[-1]
            current_data, ip_address = get_iplogger_data(code)
            if last_data.get(code) != current_data:
                print(f'------------------------\nMonitoring {link}')
                print("New data detected!")
                print("New Dates and Times:", current_data[-1])
                print("IP Addresses:", ip_address[-1])
                new_info = get_ip_info(ip_address[-1])
                auto_sent_message(TOKEN, CHAT_ID, 
                                f'New info for the link: {link} \n' +  new_info)
                last_data[code] = current_data
            else:
                print(f"No new data for {link}..................")
        time.sleep(interval)

if __name__ == '__main__':
    print('Starting Bot...')
    # monitor_iplogger(['https://iplogger.org/logger/q4yL4EDH6l7L/'], 5)
    # get_iplogger_data('q4yL4EDH6l7L')
    
    #Create persistence object
    persistence = PicklePersistence(filepath='bot_data')
    app = Application.builder().token(TOKEN).persistence(persistence).build()
    
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    # Add conversation handler for /addlinks command
    addlinks_handler = ConversationHandler(
        entry_points=[CommandHandler('addlinks', addlinks_command)],
        states={
            ADD_LINKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, store_links)],
        },
        fallbacks=[CommandHandler('done', done)],
    )
    app.add_handler(addlinks_handler)
    
    # Add conversation handler for /monitoringlinks command
    monitoringlinks_handler = ConversationHandler(
        entry_points=[CommandHandler('monitoringlinks', monitoringlinks_command)],
        states={
            MONITORING_LINKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_links)],
        },
        fallbacks=[CommandHandler('done', done)],
    )
    app.add_handler(monitoringlinks_handler)
    
    
    #Message 

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #Errors 
    app.add_error_handler(error)
    
    # Poll the bot 
    print('Polling...')
    app.run_polling(poll_interval=4)
    