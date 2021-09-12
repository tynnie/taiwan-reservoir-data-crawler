import logging
import os
from time import sleep
from datetime import timezone, datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# path setting
dir_path = os.path.dirname(os.path.realpath(__file__))
directory = ['/output/', '/log/']
for d in directory:
    if not os.path.exists(dir_path + d):
        os.makedirs(dir_path + d)

# webdriver setting
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# datetime setting
local_tz = timezone(timedelta(hours=+8))


def get_time_record():
    time_record = datetime.now().astimezone(local_tz).strftime('%Y%m%dT%H%M')
    return time_record


def get_yesterday_date():
    yesterday = datetime.now().astimezone(local_tz) - timedelta(1)
    date = yesterday.strftime('%Y%m%d')
    return date


def add_logger(timestamp):
    logging.captureWarnings(True)
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(message)s]')
    logging.Formatter.converter = lambda *args: datetime.now(
        tz=local_tz).timetuple()
    my_logger = logging.getLogger('my_logger')
    my_logger.setLevel(logging.INFO)

    # file handler: 設定 logger 儲存的檔案格式
    filename = '/log/{}.log'.format(timestamp)
    file_handler = logging.FileHandler(dir_path + filename, 'w', 'utf-8')
    file_handler.setFormatter(formatter)
    my_logger.addHandler(file_handler)

    # console handler: 設定 logger 將訊息丟到 console 的格式
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    my_logger.addHandler(console_handler)

    return my_logger


def setup_driver(link):
    driver = webdriver.Chrome(executable_path='/Users/tynnie/Documents/chromedriver', chrome_options=chrome_options)
    # driver = webdriver.Chrome(executable_path="the_path_to_your_driver", chrome_options=chrome_options)
    driver.get(link)

    return driver


def record_time_parser(record_time):
    if len(record_time) > 1:
        parsed = '-'.join([record_time.split('(')[0][:4],
                           record_time.split('(')[0][4:6],
                           record_time.split('(')[0][6:]])
        return parsed


def combine_data(data, column):
    data.columns = column[:-1]
    df = data.drop(['統計時間', '與昨日水位差(公尺)'], axis=1)
    df = df.replace(r'\s+|%|％|-+', '', regex=True)
    df['水情時間'] = (df['水情時間']
                  .astype(str)
                  .apply(lambda x: record_time_parser(x)))

    df.columns = ['ReservoirName', 'EffectiveCapacity', 'CatchmentAreaRainfall',
                  'InflowVolume', 'OutflowTotal', 'RecordTime', 'WaterLevel',
                  'EffectiveWaterStorageCapacity', 'WaterStorageRate']

    df_meta = pd.read_csv('meta.csv')
    df_meta = df_meta[['Application', 'Area', 'Location', 'ReservoirName', 'Type', 'Year']]

    df = df.merge(df_meta, on='ReservoirName', how='left')
    return df


def save_data(data, column, date):
    df_data = combine_data(data, column)
    file_path = dir_path + '/output/reservoir_{}.csv'.format(date)
    df_data.to_csv(file_path, index=False)


def data_crawler(driver):
    date = get_yesterday_date()
    year = int(date[:4])
    month = int(date[4:6])
    day = int(date[6:])

    try:

        element = driver.find_element_by_xpath("/html/body/form/div[3]/div[1]/select[1]/option[2]").click()
        sleep(1)

        select = Select(driver.find_element_by_id("ctl00_cphMain_ucDate_cboYear"))
        select.select_by_value('{}'.format(year))
        sleep(1)

        select = Select(driver.find_element_by_id("ctl00_cphMain_ucDate_cboMonth"))
        select.select_by_value('{}'.format(month))
        sleep(1)

        select = Select(driver.find_element_by_id("ctl00_cphMain_ucDate_cboDay"))
        select.select_by_value('{}'.format(day))
        sleep(1)

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,
                                                                    '//*[@id="ctl00_cphMain_btnQuery"]'))).click()

        res = driver.page_source
        df = pd.read_html(res, flavor='html5lib')[0]
        columns = [i[1] for i in list(df.columns)]
        df.columns = columns
        df = df.iloc[:-1, :-1]

        save_data(df, columns, date)
        driver.quit()

    except StaleElementReferenceException as e:
        pass

    except Exception as e:
        raise e


if __name__ == '__main__':
    timestamp = get_time_record()
    logger = add_logger(timestamp)
    logger.info('Start')
    try:
        url = 'https://fhy.wra.gov.tw/ReservoirPage_2011/StorageCapacity.aspx'
        web_driver = setup_driver(url)

        # fetch data
        data_crawler(web_driver)
        web_driver.quit()

    except Exception as e:
        logger.exception("Runtime Error Message:")

    logger.info("Done!")
