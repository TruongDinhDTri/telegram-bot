from time import time, sleep
from undetected_chromedriver.options import ChromeOptions
from undetected_chromedriver import Chrome
import certifi
import os

os.environ['SSL_CERT_FILE'] = certifi.where()

def _get_with_cf_bypass(driver: Chrome ,url: str) -> None:
    # open a new tab and navigate to the url
    driver.execute_script(f"window.open('{url}', '_blank');")
    # waiting CloudFlare to redirect to the real page, waiting for it to solved the captcha verify human
    sleep(5)
    # switch to the new tab
    driver.switch_to.window(driver.window_handles[1]) 

def get_custom_page_load_strategy(driver: Chrome, url: str) -> None:
    _get_with_cf_bypass(driver ,url)

    start_time = time()
    while time() - start_time < 10:
        if driver.execute_script(
            "return document.readyState == 'complete' || document.readyState == 'interactive'"
        ):
            return

        sleep(1)

    raise TimeoutError()

chrome_options = ChromeOptions()
chrome_options.page_load_strategy = 'none' # disable page load strategy

driver = Chrome(options = chrome_options)

get_custom_page_load_strategy(driver, '')
