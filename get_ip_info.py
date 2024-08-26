import requests
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from undetected_chromedriver.options import ChromeOptions
import certifi
import os
from undetected_chromedriver import Chrome
from time import time, sleep
import json
import random


IPLOGGER_LINK = 'https://iplogger.org/logger/'
os.environ['SSL_CERT_FILE'] = certifi.where()


with open('ip_list.json', 'r') as file:
    proxies = json.load(file)


# def get_valid_proxy(proxies: list) -> str:
#     """Select a valid proxy from the list."""
#     if not proxies:
#         raise ValueError("Proxy list is empty.")
    
#     while proxies:
#         random.shuffle(proxies)
#         proxy = random.choice(proxies)  # Pick a random proxy
#         if is_proxy_valid(proxy):
#             return proxy
        
#         proxies.remove(proxy)  # Remove invalid proxy
        
#         if not proxies:
#             break  # Exit if no proxies are left to check
    
#     raise ValueError("No valid proxies found.")

# def is_proxy_valid(proxy: str) -> bool:
#     """Check if the proxy is valid."""
#     try:
#         # Define a test URL (this should be something lightweight and reliable)
#         test_url = 'https://httpbin.org/ip'
        
#         # Define the proxy configuration for requests
#         proxy_dict = {
#             'http': f"http://{proxy}",
#             'https': f"https://{proxy}",
#         }
        
#         response = requests.get(test_url, proxies=proxy_dict, timeout=5)
#         # If the request is successful and the status code is 200, consider the proxy valid
#         return response.status_code == 200
#     except requests.RequestException:
#         return False


# try:
#     random_proxy = get_valid_proxy(proxies)
#     print(f"Selected valid proxy: {random_proxy}")
# except ValueError as e:
#     print(e)


random_proxy = random.choice(proxies)




# Add cookies => not to expired cookies session anymore
def get_iplogger_data(code, cookies):
    # Form data
    
    # print('code passsing in: ', code)
    payload = {
        'interval': 'all',
        'filters': '',
        'page': '1',
        'sort': 'created',
        'order': 'desc',
        'code': {code}
    }
    
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'cookie': cookies,
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

    try:
            # Perform the POST request
            
            response = requests.post(IPLOGGER_LINK, headers=headers, data=payload, proxies={'http:': random_proxy, 'https:': random_proxy})
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            print('Using proxies to get iplogger: ', random_proxy)
            # Process the response
            json_data_ips = response.json().get('content', [])
            if not json_data_ips:
                print("No IP data found.")
                return [], []

            # Combine the HTML content
            converted = ''.join(json_data_ips)

            # Parse the page using Beautiful Soup
            soup = BeautifulSoup(converted, 'html.parser')
            ip_dates = [div.text for div in soup.select('div.visitor-date div.ip-date')]
            ip_times = [div.text for div in soup.select('div.visitor-date .ip-time')]
            ip_address = [div.text for div in soup.select('div.visitor-ip div.ip-address')]
            date_time = [f"{date} {time}" for date, time in zip(ip_dates, ip_times)]
            print(date_time, ip_address)
            return date_time, ip_address
        
    except requests.exceptions.RequestException as e:
            # Handle any request exceptions (e.g., connection error, timeout, HTTP error)
            print(f"An error occurred while fetching IP logger data: {e}")
            return [], []

# ~ Prepared to bypass the CLOUDFLARE
def _get_with_cf_bypass(driver: Chrome ,url: str) -> None:
    # open a new tab and navigate to the url
    driver.execute_script(f"window.open('{url}', '_blank');")
    # waiting CloudFlare to redirect to the real page, waiting for it to solved the captcha verify human
    sleep(6)
    # switch to the new tab
    driver.switch_to.window(driver.window_handles[1])
    
    
def get_custom_page_load_strategy(driver: Chrome, url: str) -> None:
    _get_with_cf_bypass(driver ,url)

    start_time = time()
    while time() - start_time < 20:
        if driver.execute_script(
            "return document.readyState == 'complete' || document.readyState == 'interactive'"
        ):
            return

        sleep(1)

    raise TimeoutError()

def get_element_value(driver: Chrome, selector: str):
    print("getting into")
    try: 
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
        )
        cookies = driver.get_cookies()
        cookie_header = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        notes = element.get_attribute('value') if element else 'empty'
        print("notes: ", notes)
        return notes, cookie_header
    
    except Exception as e:
        print(f"An error occurred: -------------------- {e}")
        return ""
    
def get_full_info_iplogger(driver: Chrome, url: str, code):

    get_custom_page_load_strategy(driver, url)

    notes, cookie_header = get_element_value(driver, 'div.notes input')

    date_time, ip_address = get_iplogger_data(code, cookie_header)
    
        # Format date_time and ip_address for better readability
    date_time_str = ', '.join(date_time) if isinstance(date_time, list) else str(date_time)
    ip_address_str = ', '.join(ip_address) if isinstance(ip_address, list) else str(ip_address)

    driver.quit()

    # Print and return results
    print("Notes:", notes)
    print("Date and Time:", date_time_str)
    print("IP Address:", ip_address_str)
    return notes, date_time, ip_address


    
    
    



def get_ip_info(date_time, ip_address_details):
    # Base URL for ipinfo.io API 
    ip_address = ip_address_details[0]
    print('IP address: ', ip_address)
    url = f"https://ipinfo.io/widget/demo/{ip_address}"

    try:
        # Send GET request to ipinfo.io API
        response = requests.get(url, proxies={'http:': random_proxy, 'https:': random_proxy})
        
        print('Using proxies to get CARRIER: ', random_proxy)
        
        
        # Raise an exception if the request was unsuccessful
        response.raise_for_status()
        
        # Parse the JSON response
        ip_data = response.json()
        
        print('data: ', ip_data, type(ip_data))
        
        # Extract relevant information
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

        
        # Get additional data from iplogger
        # date_time, ip_address_details = get_full_info_iplogger(code)

        # Format the combined information as a single string
        combined_info_string = (
            f"Logged IP Address: {ip_address_details[0]}\n"
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
            f"Date and Time: {date_time[0]}\n"
        )

        
        print('combine string: ', combined_info_string)
        return combined_info_string
    
    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the API request
        print(f"Error fetching IP information: {e}")
        return None

if __name__ == '__main__':
    chrome_options = ChromeOptions()
    chrome_options.page_load_strategy = 'none' # disable page load strategy
    chrome_options.add_argument('--headless')  # Enable headless mode
    driver = Chrome(options = chrome_options)
    get_full_info_iplogger(driver, '','')

