import time
import pickle
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Chrome driver setup with options
options = Options()
options.add_argument('--start-maximized')
options.add_argument('--disable-notifications')
options.add_argument('--no-sandbox') 
options.add_argument('--disable-dev-shm-usage')
# options.add_argument('--headless')  # Run in headless mode
service = Service("/usr/local/bin/chromedriver")
browser = webdriver.Chrome(service=service, options=options)
# Load cookies to maintain session
browser.get('https://www.facebook.com/')
time.sleep(3)
try:
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        browser.add_cookie(cookie)
    browser.refresh()
    time.sleep(2)
    if "Log In" in browser.page_source:
        logging.error("Cookies might be expired or not valid. Please re-login and update cookies.")
        browser.quit()
        exit()
except Exception as e:
    logging.error(f"Error loading cookies: {e}")

# Define the brands and base URL
# brands = [
#     "Toyota", "Honda", "Ford", "Chevrolet", "Nissan", 
#     "BMW", "Mercedes-Benz", "Tesla", "Volkswagen", "Subaru", 
#     "Hyundai", "Kia", "Jeep", "Audi", "Ram", 
#     "GMC", "Mazda", "Lexus", "Buick", "Chrysler"
# ]
brand = "Honda"
min_price = 5000
max_price = 100000
days_listed = 1
min_year = 2000
max_mileage = 200000
filtered_urls = []

# for brand in brands:
#     base_url = f"https://www.facebook.com/marketplace/search?minPrice={min_price}&maxPrice={max_price}&daysSinceListed={days_listed}&maxMileage={max_mileage}&minYear={min_year}&sortBy=creation_time_descend&query={brand}&exact=false"
#     browser.get(base_url)
#     time.sleep(5)

#     # Infinite scroll to load more items
#     scroll_count = 0
#     last_height = browser.execute_script("return document.body.scrollHeight")
#     while scroll_count < 100:
#         browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(5)
#         new_height = browser.execute_script("return document.body.scrollHeight")
#         if new_height == last_height:
#             logging.info("Reached the bottom of the page.")
#             break
#         last_height = new_height
#         scroll_count += 1

#     # Parse page source with BeautifulSoup
#     page_source = browser.page_source
#     soup = BeautifulSoup(page_source, 'html.parser')
#     urls_div = soup.find_all('a', role='link')
#     urls_list = [url.get('href') for url in urls_div if url.get('href')]
#     for url in urls_list:
#         if url.startswith('/marketplace/item/'):
#             filtered_urls.append("https://www.facebook.com" + url.split('?')[0]) 

base_url = f"https://www.facebook.com/marketplace/vancouver/search?minPrice={min_price}&maxPrice={max_price}&daysSinceListed={days_listed}&maxMileage={max_mileage}&minYear={min_year}&sortBy=creation_time_descend&query={brand}&exact=false&radius_km=100"
browser.get(base_url)
time.sleep(5)

# Infinite scroll to load more items
scroll_count = 0
last_height = browser.execute_script("return document.body.scrollHeight")
while scroll_count < 50:
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    new_height = browser.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        logging.info("Reached the bottom of the page.")
        break
    last_height = new_height
    scroll_count += 1

# Parse page source with BeautifulSoup
page_source = browser.page_source
soup = BeautifulSoup(page_source, 'html.parser')
urls_div = soup.find_all('a', role='link')
urls_list = [url.get('href') for url in urls_div if url.get('href')]
for url in urls_list:
    if url.startswith('/marketplace/item/'):
        filtered_urls.append("https://www.facebook.com" + url.split('?')[0]) 

valid_urls = []
for url in filtered_urls:
    browser.get(url)
    time.sleep(3)
    if "查看更多" in browser.page_source:
        view_more_button = browser.find_element(By.XPATH, "//span[text()='查看更多']")
        view_more_button.click()
        time.sleep(5)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    # Find all seller description sections
    seller_desc_sections = soup.find_all('span', {'class': 'x193iq5w xeuugli x13faqbe x1vvkbs xlh3980 xvmahel x1n0sxbx x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u'})  
    # seller_desc_sections
    keywords = ['rebuild', '#', 'lease', 'stock', 'dealer', 'dealership', 'wholesale', 'wholesaler', 'wholesaling', 'wholesales', 'wholesaled', 'doc', 'financing', 'financed', 'finance', 'finances', 'financer', 'financers', 'financier', 'financiers', 'financiers']

    # Check if any of the seller description sections contain any of the keywords
    for seller_desc_section in seller_desc_sections:
        # Get the text of the seller description section
        seller_desc = seller_desc_section.get_text(strip=True)
        # Check if any of the keywords are in the seller description
        if any(keyword.lower() in seller_desc.lower() for keyword in keywords):
            break
    else:
        valid_urls.append(url)

browser.quit()

csv_file = "valid_urls.csv"

# Write the filtered URLs to the CSV file
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write the header (optional)
    writer.writerow(["URL"])
    
    # Write each URL to the file
    for url in valid_urls:
        writer.writerow([url])

logging.info(f"Filtered URLs have been saved to {csv_file}")