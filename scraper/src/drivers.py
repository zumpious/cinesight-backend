import threading

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from src.params import HEADLESS

# Headless Options
headless_mode = Options()
headless_mode.add_argument('--headless')
headless_mode.add_argument('--disable-gpu')

thread_local = threading.local()


def get_webdriver():
    if not hasattr(thread_local, 'webdriver'):
        print(f"Create Driver for Thread {threading.get_ident()}")
        thread_local.webdriver = webdriver.Firefox(options=headless_mode if HEADLESS else None)
    # print(f"Return Driver for Thread {threading.get_ident()}")
    return thread_local.webdriver


def close_webdriver():
    if hasattr(thread_local, 'webdriver'):
        print(f"Close Driver for Thread {threading.get_ident()}")
        thread_local.webdriver.quit()
        del thread_local.webdriver
