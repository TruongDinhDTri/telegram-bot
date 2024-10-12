
import json
import asyncio
import requests
import re
from datetime import datetime
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, PicklePersistence
from get_ip_info import *
from seleniumbase import Driver
import requests
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import certifi
import os
from concurrent.futures import ThreadPoolExecutor
from time import time, sleep
import json
import random   
from seleniumbase import Driver
import asyncio
from selenium.common.exceptions import TimeoutException

with open('general_data.json', 'r') as json_file: 
    data = json.load(json_file)

TOKEN = data['token']
CHAT_ID = data['chat_id']
active_users = data['active_users']
allowed_user_ids = set(data['allowed_user_ids'])
users_links_added = data["users_links_added"]
admin_ids = data['admin_id']
monitoring_state = data['monitoring_state']
os.environ['SSL_CERT_FILE'] = certifi.where()



with open('ip_list.json', 'r') as file:
    proxies = json.load(file)

# Add cookies => not to expired cookies session anymore
def get_iplogger_data(driver):
    combine_info_iplogger = ''
    try:        
        # Wait for the content to be present and visible
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.visitor-date'))
        )
        
        # Get page source and parse it with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Extract IP addresses and timestamps
        ip_dates = [div.text for div in soup.select('div.visitor-date div.ip-date')]
        ip_times = [div.text for div in soup.select('div.visitor-date .ip-time')]
        ip_address = [div.text for div in soup.select('div.visitor-ip div.ip-address')]
        ip_IPS = [div.text for div in soup.select('div.visitor-ip div.ip-text')]
        device = [div.text for div in soup.select('div.visitor-device div.platform')]
        user_agent = [div.text for div in soup.select('div.visitor-useragent div')]
        date_time = [f"{date} {time}" for date, time in zip(ip_dates, ip_times)]
        
        if not ip_address:
            ip_address = ["N/A"]
        if not ip_IPS:
            ip_IPS = ["N/A"]
        if not device:
            device = ["N/A"]
        if not user_agent:
            user_agent = ["N/A"]
        if not date_time:
            date_time = ["N/A"]
        

        combine_info_iplogger = (
            f"IP Address: {ip_address[0]}\n"
            f"Date and Time: {date_time[0]}\n"
            f"IP Provider: {ip_IPS[0]}\n"
            f"Victim Device: {device[0]}\n"
            f"User-Agent: {user_agent[0]}\n"
        )
        
        print("Đang tiếp tục giám sát...")
        return date_time, ip_address, combine_info_iplogger
    
    except Exception as e:
        print(f"An error occurred while getting iplogger data: {e}")
        return [], []

# ~ Prepared to bypass the CLOUDFLARE
def _get_with_cf_bypass(driver ,url: str) -> None:
    # open a new tab and navigate to the url
    driver.execute_script(f"window.open('{url}', '_blank');")
    # waiting CloudFlare to redirect to the real page, waiting for it to solved the captcha verify human
    sleep(6)
    # switch to the new tab
    driver.switch_to.window(driver.window_handles[1])
    
    
def get_custom_page_load_strategy(driver, url: str) -> None:
    _get_with_cf_bypass(driver ,url)

    start_time = time()
    while time() - start_time < 20:
        if driver.execute_script(
            "return document.readyState == 'complete' || document.readyState == 'interactive'"
        ):
            return

        sleep(1)

    raise TimeoutError()

async def get_element_value(driver, primary_selector: str, fallback_selector: str):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        primary_task = loop.run_in_executor(executor, wait_for_primary_element, driver, primary_selector)
        fallback_task = loop.run_in_executor(executor, wait_for_fallback_element, driver, fallback_selector)
        
        done, pending = await asyncio.wait(
            [primary_task, fallback_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        for task in pending:
            task.cancel()
        
        for task in done:
            result = task.result()
            if result:
                selector, value = result
                print(f"Notes from {selector}: {value}")
                return value
        
    return 'empty'

def wait_for_primary_element(driver, selector):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
        )
        return selector, element.get_attribute('value') if element else 'empty'
    except TimeoutException:
        return None

def wait_for_fallback_element(driver, selector):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
        )
        return selector, element.text if element else 'empty'
    except TimeoutException:
        return None


    except Exception as e:
        print(f"An error occurred: {e}")
        driver.save_screenshot('screenshot_headless.png')
        return 'empty'

    
async def get_full_info_iplogger(driver, url: str):
    # Run the blocking function in a separate thread
    return await asyncio.to_thread(_get_full_info_iplogger, driver, url)

def _get_full_info_iplogger(driver, url: str):
    get_custom_page_load_strategy(driver, url)

    notes = asyncio.run(get_element_value(driver, 'div.notes input', '.link-info-row:last-child div:last-child'))

    date_time, ip_address, combine_info_iplogger = get_iplogger_data(driver)
    
    return notes, date_time, ip_address, combine_info_iplogger





def get_ip_info(ip_address):
    # Base URL for ipinfo.io API
    random_proxy = random.choice(proxies) 
    print('IP address: ', ip_address)
    url = f"https://ipinfo.io/widget/demo/{ip_address}"

    try:
        response = requests.get(url, proxies={'http': random_proxy, 'https': random_proxy})
        print('Using proxies to get CARRIER: ', random_proxy)
        
        # Check if the response status code is 400
        if response.status_code == 400:
            return response.status_code, "Error: Invalid IP address format. Please enter a valid IP address."
        
        response.raise_for_status()
        
        ip_data = response.json()
        ip_info = {
            "IP Address": ip_data.get("data", {}).get("ip", "N/A"),
            "City": ip_data.get("data", {}).get("city", "N/A"),
            "Region": ip_data.get("data", {}).get("region", "N/A"),
            "Country": ip_data.get("data", {}).get("country", "N/A"),
            "Location": ip_data.get("data", {}).get("loc", "N/A"),
            "Organization": ip_data.get("data", {}).get("org", "N/A"),
            "Postal Code": ip_data.get("data", {}).get("postal", "N/A"),
            "Timezone": ip_data.get("data", {}).get("timezone", "N/A"),
            "ASN": ip_data.get("data", {}).get("asn", {}).get("asn", "N/A"),
            "ASN Name": ip_data.get("data", {}).get("asn", {}).get("name", "N/A"),
            "ASN Domain": ip_data.get("data", {}).get("asn", {}).get("domain", "N/A"),
            "ASN Route": ip_data.get("data", {}).get("asn", {}).get("route", "N/A"),
            "ASN Type": ip_data.get("data", {}).get("asn", {}).get("type", "N/A"),
            "Company Name": ip_data.get("data", {}).get("company", {}).get("name", "N/A"),
            "Company Domain": ip_data.get("data", {}).get("company", {}).get("domain", "N/A"),
            "Company Type": ip_data.get("data", {}).get("company", {}).get("type", "N/A"),
            "Carrier Name": ip_data.get("data", {}).get("carrier", {}).get("name", "N/A"),
            "MCC": ip_data.get("data", {}).get("carrier", {}).get("mcc", "N/A"),
            "MNC": ip_data.get("data", {}).get("carrier", {}).get("mnc", "N/A"),
            "VPN": ip_data.get("data", {}).get("privacy", {}).get("vpn", "N/A"),
            "Proxy": ip_data.get("data", {}).get("privacy", {}).get("proxy", "N/A"),
            "Tor": ip_data.get("data", {}).get("privacy", {}).get("tor", "N/A"),
            "Relay": ip_data.get("data", {}).get("privacy", {}).get("relay", "N/A"),
            "Hosting": ip_data.get("data", {}).get("privacy", {}).get("hosting", "N/A"),
            "Service": ip_data.get("data", {}).get("privacy", {}).get("service", "N/A"),
            "Abuse Contact Name": ip_data.get("data", {}).get("abuse", {}).get("name", "N/A"),
            "Abuse Contact Email": ip_data.get("data", {}).get("abuse", {}).get("email", "N/A"),
            "Abuse Contact Phone": ip_data.get("data", {}).get("abuse", {}).get("phone", "N/A"),
            "Abuse Network": ip_data.get("data", {}).get("abuse", {}).get("network", "N/A"),
        }

        combined_info_string = (
            f"IP Address: {ip_info['IP Address']}\n"
            f"City: {ip_info['City']}\n"
            f"Region: {ip_info['Region']}\n"
            f"Country: {ip_info['Country']}\n"
            f"Location: {ip_info['Location']}\n"
            f"Organization: {ip_info['Organization']}\n"
            f"Postal Code: {ip_info['Postal Code']}\n"
            f"Timezone: {ip_info['Timezone']}\n"
            "\n------------ASN DETIALS--------------\n"
            f"ASN: {ip_info['ASN']}\n"
            f"ASN Name: {ip_info['ASN Name']}\n"
            f"ASN Domain: {ip_info['ASN Domain']}\n"
            f"ASN Route: {ip_info['ASN Route']}\n"
            f"ASN Type: {ip_info['ASN Type']}\n"
            "\n------------COMPANY DETAIL-----------\n"
            f"Company Name: {ip_info['Company Name']}\n"
            f"Company Domain: {ip_info['Company Domain']}\n"
            f"Company Type: {ip_info['Company Type']}\n"
            "\n------------CARRIER DETAIL-----------\n"
            f"Carrier Name: {ip_info['Carrier Name']}\n"
            f"MCC: {ip_info['MCC']}\n"
            f"MNC: {ip_info['MNC']}\n"
            "\n------------PRIVACY------------------\n"
            f"VPN: {ip_info['VPN']}\n"
            f"Proxy: {ip_info['Proxy']}\n"
            f"Tor: {ip_info['Tor']}\n"
            f"Relay: {ip_info['Relay']}\n"
            f"Hosting: {ip_info['Hosting']}\n"
            f"Service: {ip_info['Service']}\n"
            "\n------------ABUSE CONTACT-------------\n"
            f"Abuse Contact Name: {ip_info['Abuse Contact Name']}\n"
            f"Abuse Contact Email: {ip_info['Abuse Contact Email']}\n"
            f"Abuse Contact Phone: {ip_info['Abuse Contact Phone']}\n"
            f"Abuse Network: {ip_info['Abuse Network']}\n"
        )
        return response.status_code, combined_info_string
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None, 'HTTP Error'
    
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the API request
        print(f"Error fetching IP information: {e}")
        return None, 'Error feting IP Infomation'

def save_data():
    with open('general_data.json', 'w') as json_file:
        data['active_users'] = active_users
        data['allowed_user_ids'] = list(allowed_user_ids)
        data['users_links_added'] = users_links_added
        data['monitoring_state'] = monitoring_state
        json.dump(data, json_file, indent=4)
        
VIEW_LINK = 1
monitoring_tasks = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_name = update.message.from_user.username
    full_name = update.message.from_user.full_name
    if user_id not in active_users:
        active_users[user_id] = {'user_name': user_name, 'full_name': full_name}
        save_data()
    return await update.message.reply_text(f"✋🏻 Xin chào {user_name}!\nSử dụng lệnh /help để xem hướng dẫn!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    bot = context.bot
    if user_id not in allowed_user_ids:
        return await update.message.reply_text('⚠️ Bạn không có quyền sử dụng lệnh này!')
    user_commands = {
        "/start": "Khởi động BOT",
        "/help": "Hướng dẫn sử dụng BOT",
        "/info": "Kiểm tra thông tin người dùng",
        "/view": "Xem tất cả liên kết đã thêm",                                   
        "/add [link]": "Thêm link để giám sát",
        "/on [Stt_link]": "Bắt đầu giám sát liên kết đã chọn theo số thứ tự trong danh sách",
        "/off": "Dừng giám sát liên kết",
        "/delete [Stt_link|all]": "Xóa một hoặc tất cả các liên kết",
        "/ipinfo [ip]": "Lấy thông tin IP"
    }
    command_list = [BotCommand(command=cmd.split()[0], description=desc) for cmd, desc in user_commands.items()]
    await bot.set_my_commands(command_list)
    if user_id in admin_ids:
        admin_commands = {
            "/users": "Hiển thị danh sách người dùng trực tuyến",
            "/allow [userID]": "Thêm người dùng vào danh sách cho phép sử dụng BOT",
            "/remove": "Xóa người dùng khỏi danh sách cho phép sử dụng BOT"
        }
        user_commands.update(admin_commands)
    help_text = '\n'.join([f"{cmd}: {desc}" for cmd, desc in user_commands.items()])
    return await update.message.reply_text(f'📄 Danh sách lệnh với BOT:\n{help_text}')

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in allowed_user_ids:
        return await update.message.reply_text('⚠️ Bạn không có quyền sử dụng lệnh này!')
    user_info = f"ℹ️ Thông tin người dùng:\n"
    user_info += f"👤 Full Name: {update.message.from_user.full_name}\n"
    user_info += f"🆔 UserID: {user_id}\n"
    user_info += f"📛 Username: @{update.message.from_user.username}\n"
    return await update.message.reply_text(user_info)


async def view_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    response = ''
    if user_id not in allowed_user_ids:
        return await update.message.reply_text('⚠️ Bạn không có quyền sử dụng lệnh này!')  
    else: 
        if user_id not in users_links_added:
            users_links_added[user_id] = {}
            users_links_added[user_id]["stored_links"] = []
            users_links_added[user_id]["monitoring_links"] = []
        if ('stored_links' not in users_links_added[user_id] or not users_links_added[user_id]['stored_links']):
            await update.message.reply_text("⚠️ Danh sách trống! Sử dụng lệnh /add [link] để thêm liên kết mới.")
            return VIEW_LINK
        if 'stored_links' in users_links_added[user_id] and len(users_links_added[user_id]['stored_links']) >= 0:
            response = "\n--DANH SÁCH LIÊN KẾT ĐÃ LƯU--\n" + "\n".join([f"{i+1}. Liên kết {item[0]}. \n   Tên liên kết: {item[1]}" for i, item in enumerate(users_links_added[user_id]['stored_links'])])
        await update.message.reply_text(response)  
        return VIEW_LINK
    
async def addlinks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    args = context.args
    if user_id not in allowed_user_ids:
        return await update.message.reply_text('⚠️ Bạn không có quyền sử dụng lệnh này!')
    if len(args) != 1:
        return await update.message.reply_text("⚠️ Vui lòng cung cấp liên kết hợp lệ! Cú pháp: /add [link].")
    link = args[0].strip()
    valid_url_pattern = re.compile(r'^https://iplogger\.org/logger/[a-zA-Z0-9]*/?')
    try:
        if user_id not in users_links_added:
            users_links_added[user_id] = {
                "stored_links": [],
                "monitoring_links": []
            }
        if any(link == l for l, _ in users_links_added.get(user_id, {}).get('stored_links', []) ):
            return await update.message.reply_text("⚠️ Liên kết đã có trong danh sách!")
        if valid_url_pattern.match(link):
            users_links_added[user_id]["stored_links"].append((link, 'Đang lấy dữ liệu notes, vui lòng chờ....'))
            save_data()
            await update.message.reply_text(f'✅ Liên kết mới {link} đã được thêm thành công!')
            
            asyncio.create_task(process_link_background(user_id, link))
        else:
            return await update.message.reply_text("⚠️ Liên kết không hợp lệ!\nSử dụng /add [link] để thêm liên kết hợp lệ theo định dạng https://iplogger.org/logger/xxxxxx.")
    except Exception as e:
        return await update.message.reply_text(f"⚠️ Không thể thêm liên kết: {str(e)}! Vui lòng thử lại.")

async def process_link_background(user_id: str, link: str):
    # Initialize WebDriver here (you'll need to adjust this for your setup)
    driver = Driver(headless=True, uc=True)

    try:
        get_custom_page_load_strategy(driver, link)
        
        notes = await get_element_value(driver, 'div.notes input', '.link-info-row:last-child div:last-child')
        
        # Update the user's stored link with the notes
        if user_id in users_links_added:
            users_links_added[user_id]["stored_links"] = [
                (l, notes) if l == link else (l, s)
                for l, s in users_links_added[user_id]["stored_links"]
            ]
            save_data()
        
    finally:
        driver.quit()


async def on_monitor_command(update:Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in allowed_user_ids:
        return await update.message.reply_text('⚠️ Bạn không có quyền sử dụng lệnh này!') 
    if user_id not in users_links_added or 'stored_links' not in users_links_added[user_id] or len(users_links_added[user_id]['stored_links']) == 0:
        users_links_added[user_id] = {"stored_links": [], "monitoring_links": []}
        return await update.message.reply_text("⚠️ Bạn chưa có liên kết nào được lưu trữ! Sử dụng lệnh /add [link] để thêm liên kết trước.")
    try:
        index = int(context.args[0]) - 1
    except (IndexError, ValueError):
        return await update.message.reply_text("⚠️ Vui lòng theo cú pháp /on [Stt_link] để giám sát liên kết đã chọn!")
    if index < 0 or index >= len(users_links_added[user_id]['stored_links']):
        return await update.message.reply_text("⚠️ Chỉ số vượt quá phạm vi! Vui lòng cung cấp chỉ số hợp lệ.")
    link = users_links_added[user_id]["stored_links"][index][0]   
    if user_id not in monitoring_tasks:
        monitoring_tasks[user_id] = {}       
    if link in monitoring_tasks[user_id]:
        return await update.message.reply_text(f"✅ Liên kết: {link} hiện đang được giám sát!")
    await update.message.reply_text("⏳ Đang chuẩn bị giám sát, vui lòng chờ...")
    user_name = update.message.from_user.username
    full_name = update.message.from_user.full_name
    if user_id not in active_users:
        active_users[user_id] = {'user_name': user_name, 'full_name': full_name}
        save_data()
    async def start_monitoring():
        while True:
            await monitor_iplogger(user_id, link, interval=5)
    task = asyncio.create_task(start_monitoring())
    monitoring_tasks[user_id][link] = task
    if link not in users_links_added[user_id]["monitoring_links"]:
        users_links_added[user_id]["monitoring_links"].append(link)
    monitoring_state[user_id] = True
    save_data()
    return await update.message.reply_text(f'✅ Đã bắt đầu giám sát liên kết:\n {index + 1}: {link}')

async def off_monitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in allowed_user_ids:
        return await update.message.reply_text('⚠️ Bạn không có quyền sử dụng lệnh này!') 
    if user_id not in monitoring_tasks or not monitoring_tasks[user_id]:
        return await update.message.reply_text("⚠️ Bạn không có liên kết nào đang giám sát!")
    tasks = monitoring_tasks[user_id].values()
    for task in tasks:
        task.cancel()  
    done, pending = await asyncio.wait(tasks, timeout=3, return_when=asyncio.ALL_COMPLETED)
    for task in pending:
        task.cancel()
    del monitoring_tasks[user_id]
    users_links_added[user_id]["monitoring_links"] = []
    monitoring_state[user_id] = False
    save_data()
    return await update.message.reply_text("✅ Đã dừng việc giám sát thành công!")


async def delete_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    args = context.args
    if user_id not in allowed_user_ids:
        return await update.message.reply_text('⚠️ Bạn không có quyền sử dụng lệnh này!')
    if user_id not in users_links_added:
        users_links_added[user_id] = {"stored_links": [], "monitoring_links": []}
    links = users_links_added[user_id]["stored_links"]
    if user_id in monitoring_state and monitoring_state[user_id]:
        await update.message.reply_text("⚠️ Sử dụng lệnh /off để dừng giám sát trước khi xóa liên kết!")
        return
    if len(args) == 1 and args[0].strip().lower() == 'all':
        if not links:
            return await update.message.reply_text("⚠️ Bạn không có liên kết nào để xóa!")
        users_links_added[user_id]['stored_links'] = []
        users_links_added[user_id]['monitoring_links'] = []
        save_data()
        return await update.message.reply_text("✅ Đã xóa tất cả liên kết!")
    if len(args) != 1:
        return await update.message.reply_text("⚠️ Sử dụng lệnh /delete [Stt_link|all] để xóa liên kết trong danh sách!")
    try:
        link_number = int(args[0]) - 1
        if 0 <= link_number < len(links):
            deleted_link = links.pop(link_number)
            if deleted_link[0] in users_links_added[user_id]["monitoring_links"]:
                users_links_added[user_id]["monitoring_links"].remove(deleted_link)
            save_data()
            return await update.message.reply_text(f"✅ Liên kết: {deleted_link[0]} đã được xóa!")
        else:
            return await update.message.reply_text("⚠️ Số thứ tự liên kết không hợp lệ! Vui lòng thử lại!")
    except ValueError:
        return await update.message.reply_text("⚠️ Vui lòng nhập một số hợp lệ!")

def startup_monitoring():
    print("Đang khởi động lại việc giám sát cho người dùng...")
    for user_id, state in monitoring_state.items():
        if state:
            if user_id in users_links_added and 'monitoring_links' in users_links_added[user_id]:
                links = users_links_added[user_id]['monitoring_links']
                for link in links:
                    if link not in monitoring_tasks.get(user_id, {}):
                        task = asyncio.create_task(monitor_iplogger(user_id, link, interval=5))
                        monitoring_tasks.setdefault(user_id, {})[link] = task
    save_data()
    
async def ipinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in allowed_user_ids:
        return await update.message.reply_text('⚠️ Bạn không có quyền sử dụng lệnh này!')
    args = context.args
    if len(args) != 1:
        await update.message.reply_text("⚠️ Vui lòng sử dụng lệnh /ipinfo [ip] để lấy thông tin IP!")
        return
    status_code, result = get_ip_info(str(args[0]))
    if status_code == 400:
        return await update.message.reply_text('⚠️ Địa chỉ IP không hợp lệ, vui lòng thử lại!')
    if status_code == 200:
        return await asyncio.to_thread(auto_sent_message, TOKEN, user_id, result)

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in admin_ids:
        return await update.message.reply_text('⚠️ Bạn không có quyền sử dụng lệnh này!')
    active_and_allowed_users = [
        user_id for user_id in active_users 
        if user_id in allowed_user_ids
    ]
    if not active_and_allowed_users:
        return await update.message.reply_text("⚠️ Không có người dùng nào đang hoạt động!")
    response = "📋 Danh sách người dùng đang hoạt động:\n\n"
    for user_id in active_and_allowed_users:
        user_info = active_users[user_id]
        response += f"👤 Full Name: {user_info['full_name']}\n"
        response += f"🆔 UserID: {user_id}\n"
        response += f"📛 Username: @{user_info['user_name']}\n"
        response += "\n"
    return await update.message.reply_text(response)

async def allow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    args = context.args
    if user_id not in admin_ids:
        return await update.message.reply_text("⚠️ Bạn không có quyền thực hiện lệnh này!")
    if len(args) != 1:
        return await update.message.reply_text("⚠️ Sử dụng lệnh /allow [userID] để cho phép userID sử dụng BOT!")
    new_user_id = args[0].strip()
    if not new_user_id.isdigit():
        return await update.message.reply_text("⚠️ UserID không hợp lệ! Vui lòng thử lại.")
    if new_user_id in allowed_user_ids:
        return await update.message.reply_text("⚠️ UserID đã có trong danh sách cho phép!")
    allowed_user_ids.add(new_user_id)
    save_data()
    return await update.message.reply_text(f"✅ UserID {new_user_id} đã được thêm vào danh sách cho phép!")

async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    args = context.args
    if user_id not in admin_ids:
        return await update.message.reply_text("⚠️ Bạn không có quyền thực hiện lệnh này!")
    if len(args) != 1:
        return await update.message.reply_text("⚠️ Sử dụng lệnh /remove [userID|all] để xóa người dùng khỏi danh sách cho phép!")
    option = args[0].strip()
    if option == "all":
        allowed_user_ids.clear()
        save_data()
        return await update.message.reply_text("✅ Đã xóa tất cả userID khỏi danh sách cho phép!")
    if not option.isdigit():
        return await update.message.reply_text("⚠️ UserID không hợp lệ! Vui lòng nhập 'userID' hoặc 'all'!")
    if option in allowed_user_ids:
        allowed_user_ids.remove(option)
        save_data()
        return await update.message.reply_text(f"✅ UserID {option} đã được xóa khỏi danh sách cho phép!")
    else:
        return await update.message.reply_text(f"⚠️ UserID {option} không có trong danh sách cho phép!")

def handle_response(text: str) -> str:
    processed: str = text.lower();
    if 'hello' in processed:
        return 'Hey there!'
    if 'how are you' in processed: 
        return "I am good"
    return "⚠️ Tôi không hiểu! Hãy thao tác lại!"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text    
    response: str = handle_response(text)
    await update.message.reply_text(response)
    
async def error(update: Update, context:ContextTypes.DEFAULT_TYPE):
    if isinstance(context.error, (ConnectionError, TimeoutError)):
        print("Phát hiện lỗi kết nối. Đang khởi động lại bot...")
        await restart_bot()
    else:
        print("Lỗi không được xử lý. Không thực hiện hành động nào.")

async def restart_bot():
    global app
    app.stop()
    print("Đang khởi động lại bot...")
    await asyncio.sleep(5)
    main()

def auto_sent_message(token, user_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": user_id,
        "text": message
    }
    try: 
        response = requests.get(url, data = payload)
        response.raise_for_status()
        return 'Tin nhắn đã được gửi thành công!'
    except requests.exceptions.RequestException as e:
        return f'Không thể gửi tin nhắn với lỗi: {e}'
    
async def monitor_iplogger(user_id, link, interval=5):
    last_data = {}
    while True:
        code = link.rstrip('/').split('/')[-1]
        try:
            driver = Driver(headless=True, uc=True)
            notes, date_time, _ , combine_info_iplogger = await get_full_info_iplogger(driver, link)
            driver.quit()
        except Exception as e:
            print(f"Đã xảy ra lỗi khi lấy thông tin đầy đủ: {e}")
            await asyncio.sleep(interval)
            continue
        if last_data.get(code) != date_time and len(date_time) != 0:
            print("Đã phát hiện dữ liệu mới!")
            await asyncio.to_thread(auto_sent_message, TOKEN, user_id,
                                    f'\nTên liên kết: "{notes}"\n'+
                                    f'Liên kết: {link} \n\n' +
                                    combine_info_iplogger)
            last_data[code] = date_time
        else:
            print(f"Không có dữ liệu mới!")
        await asyncio.sleep(interval)

def main():
    print('Starting Bot...')
    global app
    persistence = PicklePersistence(filepath='bot_data_testing')
    app = Application.builder().token(TOKEN).persistence(persistence).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('info', info_command))
    app.add_handler(CommandHandler('view', view_command))
    app.add_handler(CommandHandler('add', addlinks_command))
    app.add_handler(CommandHandler('on', on_monitor_command))
    app.add_handler(CommandHandler('off', off_monitor_command))
    app.add_handler(CommandHandler('delete', delete_link))
    app.add_handler(CommandHandler('ipinfo', ipinfo_command))
    app.add_handler(CommandHandler('users', users_command))
    app.add_handler(CommandHandler("allow", allow_command))
    app.add_handler(CommandHandler("remove", remove_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)
    print('Polling...')
    app.run_polling(poll_interval=4)

if __name__ == '__main__':
    main()
