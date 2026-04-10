from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
driver.get("https://mollymax.co.uk")

time.sleep(5)  # đợi load JS

items = driver.find_elements(By.CSS_SELECTOR, ".book_item")

for item in items:
    print(item.text)

driver.quit()