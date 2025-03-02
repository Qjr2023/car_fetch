from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time
import pickle

# open a browser
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # not open browser
service = Service("/usr/local/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

# open Facebook
driver.get('https://www.facebook.com/')
time.sleep(3)

# import cookies
cookies = pickle.load(open("cookies.pkl", "rb"))
for cookie in cookies:
    driver.add_cookie(cookie)

# refresh the page
driver.refresh()
time.sleep(3)

# fetch data
search_url = "https://www.facebook.com/marketplace?query=Toyota"
driver.get(search_url)
time.sleep(5)


# roll down the page
for _ in range(3):
    driver.execute_script("window.scrollBy(0,1000)")
    time.sleep(2)

# use BeautifulSoup to parse the page
soup = BeautifulSoup(driver.page_source, 'html.parser')
items = soup.find_all('div', {'class': 'x1i10hfl'})  # find all items

# extract data
data = []
for item in items:
    title = item.find('span', {'class': 'x1lliihq'}).get_text() if item.find('span', {'class': 'x1lliihq'}) else "N/A"
    price = item.find('span', {'class': 'x193iq5w'}).get_text() if item.find('span', {'class': 'x193iq5w'}) else "N/A"
    link = item.find('a', href=True)['href'] if item.find('a', href=True) else "N/A"
    data.append([title, price, link])

# save data to csv
df = pd.DataFrame(data, columns=['Title', 'Price', 'Link'])
df.to_csv('data.csv', index=False)

print("Data saved to marketplace_data.csv")

# close the browser
driver.quit()



