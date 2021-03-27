import os
import re
import time
import getpass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

## configs
SEP = os.path.sep
DATA_FOLDER = 'C:\\Users\\mou\\stock-selector'
if os.name != 'nt':
    DATA_FOLDER = '/Users/{}/stock-selector'.format(getpass.getuser())

URL_LIST_FILE = '{}{}{}'.format(DATA_FOLDER, SEP, 'dog_health_chk.txt')
OUTPUT_TXT = 'dog_filter.txt'
FORCE_PRINT_OUT = ['SPY', 'IVV', 'VTI', 'VOO', 'QQQ', 'AGG', 'VTV', 'BND', 'VUG', 'IWM', 'IJR', 'IWF', 'IJH', 'VIG',
                   'IWD', 'VO', 'VB', 'LQD', 'VCIT', 'VGT', 'VCSH', 'XLK', 'XLF', 'ITOT', 'VNQ']
with open('{}'.format(URL_LIST_FILE)) as f:
    content = f.readlines()
urls = [x.strip() for x in content]

## loading chrome driver
## download from https://chromedriver.storage.googleapis.com/index.html?path=89.0.4389.23/
webdriver_path = 'C:\\Users\\mou\\Downloads\\chromedriver.exe'
webdriver_path = '/Users/{}/Downloads/chromedriver'.format(getpass.getuser())
driver = webdriver.Chrome(webdriver_path)

## waiting log in, after you login, press enter in the terminal
driver.get(urls[0])
input('press enter to proceed...')

## clear output file
with open('{}{}{}'.format(DATA_FOLDER, SEP, OUTPUT_TXT), 'w') as f_out:
    f_out.write('')

## loop scan
with open('{}{}{}'.format(DATA_FOLDER, SEP, OUTPUT_TXT), 'a') as f_out:
    for url in urls:
        ticker = re.findall('analysis/(.*?)/', url)[0]
        if ticker in FORCE_PRINT_OUT:
            f_out.write(ticker + '\n')
            continue
        driver.get(url)
        invalid_stock_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[2]/div/div[2]/div/div/div[2]/div/h2'))
        )
        time.sleep(1)
        if invalid_stock_element and not invalid_stock_element.is_displayed():
            if '不適用' in driver.page_source:
                time.sleep(5)
                continue
            try:
                element = WebDriverWait(driver, 60).until(
                    EC.visibility_of_element_located((By.XPATH,
                                                      "/html/body/div[2]/div/div[2]/div/div/div[3]/div[2]/div[2]/div[1]/div[2]/div[1]/div[2]/span[1]"))
                )
                non_landmine_score = int(driver.find_elements_by_xpath(
                    '/html/body/div[2]/div/div[2]/div/div/div[3]/div[2]/div[2]/div[1]/div[2]/div[1]/div[2]/span[1]')[
                                             0].text)
                saving_stock_score = int(driver.find_elements_by_xpath(
                    '/html/body/div[2]/div/div[2]/div/div/div[3]/div[2]/div[2]/div[2]/div[2]/div[1]/div[2]/span[1]')[
                                             0].text)
                growing_stock_score = int(driver.find_elements_by_xpath(
                    '/html/body/div[2]/div/div[2]/div/div/div[3]/div[2]/div[2]/div[3]/div[2]/div[1]/div[2]/span[1]')[
                                              0].text)
                cheap_stock_score = int(driver.find_elements_by_xpath(
                    '/html/body/div[2]/div/div[2]/div/div/div[3]/div[2]/div[2]/div[4]/div[2]/div[1]/div[2]/span[1]')[
                                            0].text)
                print(ticker, non_landmine_score, saving_stock_score, growing_stock_score, cheap_stock_score)
                sum = non_landmine_score + saving_stock_score + growing_stock_score + cheap_stock_score

                if (sum >= 8 and (saving_stock_score != 0 or growing_stock_score != 0)):
                    f_out.write(url + '\n')
            except Exception as e:
                print(e)
        time.sleep(5)
