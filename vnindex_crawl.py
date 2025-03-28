import os
import sys
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Setup Chrome options
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.binary_location = '/usr/bin/chromium-browser'

    # Initialize WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Scrape Data
def scrape_data():
    driver = setup_driver()
    data = []

    try:
        url = "https://cafef.vn/du-lieu/lich-su-giao-dich-symbol-vnindex/trang-1-0-tab-1.chn"
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        table = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="render-table-owner"]')))

        # Extract rows
        rows = table.find_elements(By.TAG_NAME, 'tr')

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) > 5:
                date = cells[0].text.strip()
                amount = cells[5].text.strip()
                data.append({'date': date, 'amount': amount})

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')

        return df

    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        driver.quit()

# Save data to CSV
def save_to_csv(df, file_path="output.csv"):
    if df is not None:
        df.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}")
    else:
        print("No data to save.")

# Main function to run script
def main():
    df = scrape_data()
    save_to_csv(df, "output.csv")

if __name__ == "__main__":
    main()
