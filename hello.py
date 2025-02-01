import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import pandas as pd

def main():
    print("Hello from broadway-direct-bot!")

if __name__ == "__main__":
    driver = uc.Chrome(headless=False, use_subprocess=False)
    driver.get('https://lottery.broadwaydirect.com/')
    print('hello')
    
    trs = driver.find_elements(By.TAG_NAME, "tr")
    for tr in trs:
        # get element inside tr that contains "time" in class
        tds = tr.find_elements(By.TAG_NAME, "td")
        for td in tds:
            if "time" in td.get_attribute("class"):
                print(td.text)
    while True:
        continue

# url1 = 'https://lottery.broadwaydirect.com/'
# get all hrefs that contain 'https://lottery.broadwaydirect.com/show/' as the start of the href
# driver.switch_to.window(driver.window_handles[1])
df = pd.read_html(driver.page_source)[0]
df['Show Time']

