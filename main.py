import logging
import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.firefox.options import Options

LOGGER.setLevel(logging.WARNING)

from global_platform import GLOBAL_PLATFORM

DOWNLOAD_DIR_PATH = r'C:\Users\ivans\Downloads\test_folder'

service = Service(executable_path=r"F:\firefoxdriver\geckodriver.exe")

formatter = logging.Formatter('%(name)s: [%(levelname)s] [%(asctime)s] %(message)s')
current_date = datetime(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)

options = Options()
options.page_load_strategy = "eager"
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("browser.download.dir", DOWNLOAD_DIR_PATH)
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")

driver = webdriver.Firefox(service=service, options=options)

parser = GLOBAL_PLATFORM(driver)
docs = parser.content()

print(*docs, sep='\n\r\n')
