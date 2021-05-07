from time import sleep
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def setup_driver(link):
    driver = webdriver.Firefox(executable_path="the_path_to_your_driver")
    # driver = webdriver.Chrome(executable_path="the_path_to_your_driver")
    driver.get(link)

    return driver


def data_crawler(driver):
    columns = []
    data = []

    element = driver.find_element_by_xpath("/html/body/form/div[3]/div[1]/select[1]/option[2]").click()

    for y in range(2010, 2022):
        select = Select(driver.find_element_by_id("ctl00_cphMain_ucDate_cboYear"))
        select.select_by_value('{}'.format(y))

        for m in range(1, 13):
            select = Select(driver.find_element_by_id("ctl00_cphMain_ucDate_cboMonth"))
            select.select_by_value('{}'.format(m))

            for d in range(1, 32):
                try:
                    select = Select(driver.find_element_by_id("ctl00_cphMain_ucDate_cboDay"))
                    select.select_by_value('{}'.format(d))
                    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,
                                                                                '//*[@id="ctl00_cphMain_btnQuery"]'))).click()

                    res = driver.page_source
                    df = pd.read_html(res)[0]
                    columns = [i[1] for i in list(df.columns)]
                    df.columns = columns
                    data.append(df.iloc[:-1, :-1])
                    sleep(0.75)

                except StaleElementReferenceException:
                    pass

    return data, columns


def save_data(d, column):
    df_data = pd.concat(d)
    df_data.columns = column[:-1]
    df_data.to_csv("reservoir_history_data.csv", index=False)


if __name__ == '__main__':
    url = "https://fhy.wra.gov.tw/ReservoirPage_2011/StorageCapacity.aspx"
    web_driver = setup_driver(url)
    all_data = data_crawler(web_driver)
    save_data(all_data[0], all_data[1])
    web_driver.quit()
