import os
import json
import time
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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

    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Authenticate Google Sheets API
def authenticate_google_sheets():
    try:
        creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        if not creds_json:
            raise ValueError("Google Sheets credentials not found in environment variables.")

        creds_dict = json.loads(creds_json)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"Google Sheets authentication failed: {e}")
        return None

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
                data.append({
                    'date': cells[0].text.strip(),
                    'closing_price': cells[1].text.strip(),
                    'adjusted_price': cells[2].text.strip(),
                    'change': cells[3].text.strip(),
                    'order_matching_volume': cells[4].text.strip(),
                    'order_matching_value': cells[5].text.strip(),
                    'block_trade_volume': cells[6].text.strip(),
                    'block_trade_value': cells[7].text.strip(),
                    'opening_price': cells[8].text.strip(),
                    'lowest_price': cells[9].text.strip(),
                    'highest_price': cells[10].text.strip()
                })

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
        df.sort_values(by='date', ascending=False, inplace=True)
        df["date"] = df["date"].astype(str)
        # df["amount"] = df["amount"].replace(",", "", regex=True).astype(float)

        return df

    except Exception as e:
        print(f"Error during scraping: {e}")
        return None
    finally:
        driver.quit()

# Save data to Google Sheets (Replace Data)
def save_to_google_sheets(df, sheet_name="VNIndex_Data"):
    if df is not None:
        try:
            client = authenticate_google_sheets()
            if client is None:
                print("Google Sheets client authentication failed.")
                return

            sheet = client.open("VNIndex_Data").worksheet("crawl_data")

            # Clear old data before adding new data
            sheet.clear()
            sheet.append_rows([df.columns.tolist()] + df.values.tolist())

            print(f"Data replaced successfully in Google Sheets: {sheet_name}")

        except Exception as e:
            print(f"Failed to save data to Google Sheets: {e}")

    else:
        print("No data to save.")

# Main function
def main():
    df = scrape_data()
    save_to_google_sheets(df)

if __name__ == "__main__":
    main()
