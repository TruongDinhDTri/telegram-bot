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



IPLOGGER_LINK = 'https://iplogger.org/logger/'
os.environ['SSL_CERT_FILE'] = certifi.where()
invalid_ip = False

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
        user_agent = [div.text for div in soup.select('div.visitor-usergent div')]
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
            f"IP Provider: {ip_IPS[0]}"
            f"Victim Device: {device[0]}"
            f"User-Agent: {user_agent[0]}"
            f"Date-Time: {date_time[0]}"
        )
        
        print(date_time, ip_address)
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
    
    # Format date_time and ip_address for better readability
    date_time_str = ', '.join(date_time) if isinstance(date_time, list) else str(date_time)
    ip_address_str = ', '.join(ip_address) if isinstance(ip_address, list) else str(ip_address)

    print("Notes:", notes)
    print("Date and Time:", date_time_str)
    print("IP Address:", ip_address_str)
    return notes, date_time, ip_address, combine_info_iplogger





def get_ip_info(ip_address):
    # Base URL for ipinfo.io API
    random_proxy = random.choice(proxies) 
    print('IP address: ', ip_address)
    url = f"https://ipinfo.io/widget/demo/{ip_address}"

    try:
        response = requests.get(url, proxies={'http:': random_proxy, 'https:': random_proxy})
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

        
        print('combine string: ', combined_info_string)
        return response.status_code, combined_info_string
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None, 'HTTP Error'
    
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the API request
        print(f"Error fetching IP information: {e}")
        return None, 'Error feting IP Infomation'

if __name__ == '__main__':
    driver = Driver(headless=True, uc=True)
    get_full_info_iplogger(driver, '')

