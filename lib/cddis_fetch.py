import datetime
import subprocess
import sys
import tempfile
from pathlib import Path

import chromedriver_autoinstaller
import requests
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

IONEX_BASE_URL = 'https://cddis.nasa.gov/archive/gnss/products/ionex/'


def fetch_latest_ionex(username: str, password: str):
    now = datetime.date.today()
    url = IONEX_BASE_URL + str(now.year)

    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Login
    username_field = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "username")))
    username_field.clear()
    username_field.send_keys(username)
    password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
    password_field.clear()
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)

    # Wait until we're redirected to the right page.
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "parDirTextContainer")))

    # Get the days in the year.
    day_elements = driver.find_elements(By.XPATH, '//div[@class="archiveDir"]/div[@class="archiveDirTextContainer"]/a[@class="archiveDirText"]')
    day_urls = [element.get_attribute('href') for element in day_elements]

    # Load the latest day.
    driver.get(day_urls[-1])

    # Find our file.
    file_elements = driver.find_elements(By.XPATH, '//a[@class="archiveItemText"]')
    file_urls = [element.get_attribute('href') for element in file_elements]
    found_url = None
    for u in file_urls:
        parts = u.split('/')
        if parts[-1].startswith('c2pg'):
            found_url = u
            break
    if found_url is None:
        print('Did not find c2pg')
        sys.exit(1)

    # Download our file.
    auth_cookie = None
    for cookie in driver.get_cookies():
        if cookie['name'] == 'ProxyAuth':
            auth_cookie = cookie['value']
            break
    if auth_cookie is None:
        print('Did not find ProxyAuth cookie')
        sys.exit(1)

    driver.close()
    del driver

    # Download data.
    zip_data_r = requests.get(found_url, cookies={'ProxyAuth': auth_cookie})
    zip_data_r.raise_for_status()

    # Read data.
    tmp_file = tempfile.NamedTemporaryFile()
    tmp_file.write(zip_data_r.content)
    tmp_dir = tempfile.TemporaryDirectory()
    subprocess.run(["7z", "e", tmp_file.name, f"-o{tmp_dir.name}"], check=True, stdout=subprocess.PIPE)
    p = Path(tmp_dir.name)
    target_file = list(p.iterdir())[-1]
    data = target_file.read_text()
    return data
