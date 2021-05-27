import os
import time
import pandas as pd
import pytest

from operator import itemgetter
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


@pytest.mark.usefixtures("setup")
@pytest.mark.usefixtures("get_creds")
class TestStuff:
    def test_vendor(self):
        wait = WebDriverWait(self.driver, 10)

        self.driver.get('https://analytics.placer.ai/#!/pages/signin')
        self.driver.find_element_by_id('input_2').send_keys(self.creds['user'])
        self.driver.find_element_by_id('input_3').send_keys(self.creds['password'])
        self.driver.find_element_by_css_selector('button[type="submit"]').click()

        search_bar: WebElement = wait.until(ec.visibility_of_element_located((By.ID, 'venue-search-input-1')))
        search_bar.clear()
        search_bar.send_keys('Victoria Gardens')
        search_bar.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
        result: WebElement = wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, 'button[aria-label^="Victoria Gardens"]')))
        result.click()
        open_report_button: WebElement = wait.until(ec.visibility_of_element_located((By.CLASS_NAME, 'explore-action-button')))
        open_report_button.click()
        assert '59fed3731b5c0a1702be81bf' in self.driver.current_url

        rows: list[WebElement] = wait.until(ec.visibility_of_all_elements_located((By.CLASS_NAME, 'pl-row')))
        victoria_visits_text = rows[0].find_elements_by_class_name('pl-cell')[2].text
        terra_vista_visits_text = rows[1].find_elements_by_class_name('pl-cell')[2].text

        def convert_string_to_number(string: str) -> int:
            number = float(string[:-1])
            if string[-1] == 'M':
                return int(number * 1000000)
            elif string[-1] == 'K':
                return int(number * 1000)
            else:
                return int(number)

        victoria_visits = convert_string_to_number(victoria_visits_text)
        terra_vista_visits = convert_string_to_number(terra_vista_visits_text)
        if victoria_visits > terra_vista_visits:
            print('victoria wins')
        elif terra_vista_visits > victoria_visits:
            print('terra vista wins')
        else:
            print('its a tie yo')

        metrics_component = self.driver.find_element_by_class_name('overview-metrics-component')
        self.driver.execute_script("arguments[0].scrollIntoView();", metrics_component)
        switch_button = self.driver.find_elements_by_class_name('switch-block')[1]
        switch_button.click()
        visit_trend_download_button: WebElement = self.driver.find_elements_by_class_name('basic-graph-dropdown-button')[0]
        visit_trend_download_button.click()
        visit_trend_download_csv_button: WebElement = wait.until(ec.visibility_of_element_located((By.CLASS_NAME, 'pl-download-csv-button')))
        visit_trend_download_csv_button.click()
        time.sleep(1)
        download_file_name = os.listdir('downloads')[0]
        csvFilePath = f'./downloads/{download_file_name}'
        df = pd.read_csv(csvFilePath, skiprows=1)
        list_of_rows = []
        for row in df.values:
            list_of_rows.append(
                {
                    'date': row[0],
                    'visits': row[1]
                }
            )
        print('max visits: ' + str(max(list_of_rows, key=itemgetter('visits'))))

    @pytest.mark.usefixtures("setup")
    def test_hourly_visits(self):
        wait = WebDriverWait(self.driver, 10)
        self.driver.get('https://www.google.com/maps/place/Victoria+Gardens/@34.1114122,-117.5323513,15z/data=!4m5!3m4!1s0x0:0xd0f441fb7cc773eb!8m2!3d34.1114122!4d-117.5323513')
        self.driver.find_element_by_class_name('LJKBpe-Tswv1b-hour-text').click()


        hours_list = wait.until(ec.presence_of_all_elements_located((By.CLASS_NAME,'y0skZc-oKdM2c')))


        hour_range: str = [hour.text for hour in hours_list if 'Tuesday' in hour.text][0]

        hour_range_list = hour_range.replace("\n", "").replace("Tuesday", "").strip().split('–')

        self.driver.get('https://analytics.placer.ai/#!/admin/insights/complexes/59fed3731b5c0a1702be81bf/overview?competitor=%5B%5D&filter=%5B%7B%22date%22:%7B%22key%22:%222021-04-01%22,%22name%22:%22April+2021%22,%22end%22:%222021-04-30%22,%22start%22:%222021-04-01%22,%22chosenLabel%22:%22April+2021%22%7D,%22attributes%22:%5B%22all%22,%5B%22in%22,%22days_of_week%22,%5B3%5D%5D%5D%7D%5D')
        self.driver.find_element_by_id('input_2').send_keys(self.creds['user'])
        self.driver.find_element_by_id('input_3').send_keys(self.creds['password'])
        self.driver.find_element_by_css_selector('button[type="submit"]').click()
        hourly_visit_trend_download_button: WebElement = wait.until(ec.presence_of_all_elements_located((By.CLASS_NAME, 'basic-graph-dropdown-button')))[1]
        hourly_visit_trend_download_button.click()
        hourly_visit_trend_download_csv_button: WebElement = wait.until(ec.presence_of_all_elements_located((By.CLASS_NAME, 'pl-download-csv-button')))[1]
        hourly_visit_trend_download_csv_button.click()
        time.sleep(1)
        download_file_name = os.listdir('downloads')[0]
        csvFilePath = f'./downloads/{download_file_name}'
        df = pd.read_csv(csvFilePath, skiprows=1)
        list_of_rows = []
        for row in df.values:
            hour = row[0].replace(':00 ', '')
            if '10' not in hour:
                hour = hour.replace('0', '')
            list_of_rows.append(
                {
                    'hour': hour,
                    'visits': row[1]
                }
            )
        in_range = False
        for row in list_of_rows:
            if row['hour'] == hour_range_list[0]:
                in_range = True
            elif row['hour'] == hour_range_list[1]:
                in_range = False
            if in_range:
                if row['visits'] > 0:
                    print(f"{row['hour']} has visitors! hurray!")
                else:
                    print(f"no visitors at {row['hour']} - open hours! oh nooo!!!")
            else:
                if row['visits'] == 0:
                    print(f"{row['hour']} has no visitors! hurray!")
                else:
                    print(f"visitors at {row['hour']} - closed hours! oh nooo!!!")

