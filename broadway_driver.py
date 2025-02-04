import undetected_chromedriver as uc
# from selenium_recaptcha_solver import RecaptchaSolver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.chrome.options import Options
import dataclasses
from typing import List
import json
import time

# import elementnotfound exception
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

@dataclasses.dataclass
class Show:
    name: str
    href: str
    time: datetime
    day_of_week: str
    
@dataclasses.dataclass
class EntryOptions:
    first_name: str
    last_name: str
    ticket_qty: int
    email: str
    dob_month: str
    dob_day: str
    dob_year: str
    zipcode: str
    country: str

class BroadwayDriver():
    def __init__(self, config):
        options = Options()

        # test_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        # options.add_argument("--headless")  # Remove this if you want to see the browser (Headless makes the chromedriver not have a GUI)
        # options.add_argument("--window-size=1920,1080")
        # options.add_argument(f'--user-agent={test_ua}')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-extensions")
        self.driver = uc.Chrome(headless=False, use_subprocess=False, options=options)
        self.config = config
        # solver = RecaptchaSolver(driver=driver)


    # get all hrefs that contain https://lottery.broadwaydirect.com/show/
    def get_all_show_urls(self):
        self.driver.get('https://lottery.broadwaydirect.com/')
        shows = self.driver.find_elements(By.XPATH, '//a[contains(@href, "https://lottery.broadwaydirect.com/show/")]')
        show_hrefs = list(set([show.get_attribute('href') for show in shows]))
        show_names = [x.split('/show/')[-1].strip('/') for x in show_hrefs]
        # sort both lists by show_name
        show_names, show_hrefs = zip(*sorted(zip(show_names, show_hrefs)))
        return show_hrefs, show_names
        
    def _get_show_entries(self, show_href: str) -> List[Show]:
        self.driver.get(show_href)
        table = self.driver.find_element(By.TAG_NAME, "table")
        trs = table.find_elements(By.TAG_NAME, "tr")
        cur_url = self.driver.current_url
        cur_show = cur_url.split('/show/')[-1].strip('/')
        href_shows = []
        for tr in trs:
            show_href = None
            # get element inside tr that contains "time" in class
            tds = tr.find_elements(By.TAG_NAME, "td")
            for td in tds:
                if "time" in td.get_attribute("class"):
                    show_time = td.text.strip()
                    datetime_object = datetime.strptime(show_time, '%m/%d/%y %I:%M %p')
                    day_of_week = datetime_object.strftime('%A')
                    
                # check for href in td
                if td.find_elements(By.TAG_NAME, "a"):
                    show_href = td.find_element(By.TAG_NAME, "a").get_attribute("href")
            
            if show_href is None or 'enter-lottery' not in show_href:
                continue
        
            show = Show(cur_show, show_href, datetime_object, day_of_week)
            href_shows.append(show)
        return href_shows
    
    def get_show_times(self, show_hrefs) -> List[Show]:
        all_shows: List[Show] = []
        for show_href in show_hrefs:
            href_shows = self._get_show_entries(show_href)
            all_shows.extend(href_shows)
        return all_shows

    def _fill_entry(self, show_href, entry_options: EntryOptions):
        self.driver.get(show_href)
        # dlslot_name_first
        input_first_name = self.driver.find_element(By.ID, 'dlslot_name_first')
        # dlslot_name_last
        input_last_name = self.driver.find_element(By.ID, 'dlslot_name_last')
        # dlslot_ticket_qty
        select_ticket_qty = self.driver.find_element(By.ID, 'dlslot_ticket_qty')
        # dlslot_email
        input_email = self.driver.find_element(By.ID, 'dlslot_email')
        # dlslot_dob_month
        input_dob_month = self.driver.find_element(By.ID, 'dlslot_dob_month')
        # dlslot_dob_day
        input_dob_day = self.driver.find_element(By.ID, 'dlslot_dob_day')
        # dlslot_dob_year
        input_dob_year = self.driver.find_element(By.ID, 'dlslot_dob_year')
        # dlslot_zip
        input_zip = self.driver.find_element(By.ID, 'dlslot_zip')
        # dlslot_country
        select_country = self.driver.find_element(By.ID, 'dlslot_country')
        # <label for="dslot_agree">
        checkbox_agree = self.driver.find_element(By.XPATH, '//label[@for="dlslot_agree"]')

        input_first_name.send_keys("Jared")
        input_last_name.send_keys("Ucherek")
        select_ticket_qty.send_keys("2")
        input_email.send_keys("jared.ucherek@gmail.com")
        input_dob_month.send_keys("09")
        input_dob_day.send_keys("17")
        input_dob_year.send_keys("1996")
        input_zip.send_keys("11211")
        select_country.send_keys("USA")
        # scroll down all the way
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        checkbox_agree.click()
        
    def solve_capcha(self):
        pass
        
    def _accept_cookies(self):
        try:
            cookies_button = self.driver.find_element(By.XPATH, '//button[@onclick="CookieInformation.submitAllCategories();"]')
            cookies_button.click()
        except (NoSuchElementException, ElementNotInteractableException) as e:
            print(f'No cookies button found: {e.msg}')
        time.sleep(1)
        
    def _submit_entry(self):
        # btn btn-primary
        submit_button = self.driver.find_element(By.CLASS_NAME, 'btn-primary')
        time.sleep(1)
        submit_button.click()
        time.sleep(1)
        
    def run(self, all_shows: List[Show]):       
        if len(all_shows):
            self.driver.get(all_shows[0].href)
            time.sleep(2)
            self._accept_cookies()
     
        for email, options in self.config.items():
            print(f"Processing {options['first_name']}")
            
            options['shows'] = set(options['shows'])
            options['show_hours'] = set(options['show_hours'])
            options['show_days'] = set(options['show_days'])
            entry_options = EntryOptions(first_name=options['first_name'],
                                         last_name=options['last_name'],
                                         ticket_qty=options['ticket_qty'],
                                         email=options['email'],
                                         dob_month=options['birthday'].split('-')[0],
                                         dob_day=options['birthday'].split('-')[1],
                                         dob_year=options['birthday'].split('-')[2],
                                         zipcode=options['zipcode'],
                                         country=options['country'],
                                         )
            for show in all_shows:
                if show.name not in options['shows']:
                    print(f"Skipping {show.name}")
                    continue
                if show.time.hour not in options['show_hours'] or show.day_of_week not in options['show_days']:
                    print(f"Skipping {show.name} at {show.time} on {show.day_of_week}")
                    continue
                
                self._fill_entry(show.href, entry_options)
                self._submit_entry()
                # solve_capcha(driver)
                # submit
                print(f"Entered {show.name} at {show.time} on {show.day_of_week}")
                
    def close(self):
        self.driver.quit()
