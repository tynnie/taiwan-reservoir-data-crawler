import logging
import os
import requests
from datetime import timezone, datetime, timedelta
import pandas as pd
from bs4 import BeautifulSoup


# path setting
dir_path = os.path.dirname(os.path.realpath(__file__))
directory = ['/output/', '/log/']
for d in directory:
    if not os.path.exists(dir_path + d):
        os.makedirs(dir_path + d)


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

    df_meta = pd.read_csv(dir_path + '/meta.csv')
    df_meta = df_meta.drop_duplicates(subset=['ReservoirName'], keep="last")
    df_meta = df_meta[['Application', 'Area', 'Location', 'ReservoirName', 'Type', 'Year']]

    df = df.merge(df_meta, on='ReservoirName', how='left')
    return df


def save_data(data, column, date):
    df_data = combine_data(data, column)
    file_path = dir_path + '/output/reservoir_{}.csv'.format(date)
    df_data.to_csv(file_path, index=False)


def data_crawler(link):
    date = get_yesterday_date()
    year = int(date[:4])
    month = int(date[4:6])
    day = int(date[6:])
    s = requests.Session()

    payload = {'ctl00$ctl02': 'ctl00$cphMain$ctl00|ctl00$cphMain$cboSearch',
               'ctl00$cphMain$cboSearch': '所有水庫',
               'ctl00$cphMain$ucDate$cboYear': year,
               'ctl00$cphMain$ucDate$cboMonth': month,
               'ctl00$cphMain$ucDate$cboDay': day,
               '__EVENTTARGET': 'ctl00$cphMain$btnQuery',
               '__EVENTARGUMENT': '',
               '__LASTFOCUS': '',
               '__ASYNCPOST': True}

    try:
        res = s.get(link)
        soup = BeautifulSoup(res.content, 'lxml')
        payload['__VIEWSTATE'] = soup.select_one('#__VIEWSTATE')['value']
        payload['__VIEWSTATEGENERATOR'] = soup.select_one('#__VIEWSTATEGENERATOR')['value']
        payload['ctl00_ctl02_HiddenField'] = soup.select_one('#ctl00_ctl02_HiddenField')['value']
        fetch = s.post(link, data=payload, allow_redirects=True)
        df = pd.read_html(fetch.text, flavor='html5lib')[0]
        columns = [i[1] for i in list(df.columns)]
        df.columns = columns
        df = df.iloc[:-1, :-1]

        save_data(df, columns, date)

    except Exception as e:
        raise e


if __name__ == '__main__':
    timestamp = get_time_record()
    logger = add_logger(timestamp)
    logger.info('Start')
    try:
        url = 'https://fhy.wra.gov.tw/ReservoirPage_2011/StorageCapacity.aspx'

        # fetch data
        data_crawler(url)

    except Exception as e:
        logger.exception("Runtime Error Message:")

    logger.info("Done!")
