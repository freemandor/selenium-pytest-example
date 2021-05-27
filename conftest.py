import os
import pytest

from selenium import webdriver
from selenium.webdriver.android.webdriver import WebDriver


@pytest.fixture(scope="function")
def setup(request):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    DOWNLOAD_PATH = os.path.abspath("downloads")
    print("initiating chrome driver")
    chrome_options = webdriver.ChromeOptions()
    prefs = {'download.default_directory': DOWNLOAD_PATH}
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument("--lang=en-GB")
    driver: WebDriver = webdriver.Chrome('./drivers/chromedriver', options=chrome_options)
    driver.maximize_window()
    request.cls.driver = driver

    yield driver
    driver.close()
    list_of_files = os.listdir('downloads')
    for file in list_of_files:
        os.remove(os.path.join(DOWNLOAD_PATH, file))


@pytest.fixture(scope="class")
def get_creds(request):
    creds = {
        "user": os.environ.get('USER'),
        "password": os.environ.get('PASSWORD')
    }
    request.cls.creds = creds
    return creds
