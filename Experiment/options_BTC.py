import schedule
import time
import schedule
import csv
import numpy as np
from playwright.sync_api import sync_playwright
import gspread
from google.oauth2.service_account import Credentials

def job():
    print("Running job...")
    # Your method's logic here
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        binance_url = "https://www.binance.com/en/eoptions/BTCUSDT"
        page.goto(binance_url, wait_until="load")

        time.sleep(4)
        # Performing click Actions on Individual Dates
        # next_five_dates_btns = page.locator("(//div[@class='css-j8ru5z'])[position() <= 5]")
        # for i in range(next_five_dates_btns.count()):
        #     next_five_dates_btns.nth(i).click()

        # Left side table
        print("--Left Side Table--")
        page.wait_for_selector("//div[@class='in-the-money call-row css-tb8ein' or @class='call-row css-tb8ein']")
        left_rows = page.locator("//div[@class='in-the-money call-row css-tb8ein' or @class='call-row css-tb8ein']")
        
        left_row_data_final = []
        for i in range(left_rows.count()):
            left_row = left_rows.nth(i)
            left_row_data = left_row.locator("//div[@class='css-mr03qh']/descendant::span[1]").all_text_contents()
            left_row_data_filtered = [item for item in left_row_data if '%' not in item]
            # print(left_row_data_filtered, len(left_row_data_filtered))
            left_row_data_final.append(left_row_data_filtered)

        np_left_row_data = np.array(left_row_data_final)
        print(np_left_row_data, len(np_left_row_data))

        # middle strike
        print("\n--Middle Side Table--")
        middle_rows_ele = page.locator("//div[@class='css-kfl4vl']").all_text_contents()
        middle_rows = np.array(middle_rows_ele).reshape(len(middle_rows_ele), 1)
        print(middle_rows, len(middle_rows))

        # Right side table
        print("\n--Right Side Table--")
        page.wait_for_selector("//div[@class='in-the-money put-row css-tb8ein' or @class='put-row css-tb8ein']")
        right_rows = page.locator("//div[@class='in-the-money put-row css-tb8ein' or @class='put-row css-tb8ein']")
        
        right_row_data_final = []
        for i in range(right_rows.count()):
            right_row = right_rows.nth(i)
            right_row_data = right_row.locator("//div[@class='css-mr03qh']/descendant::span[1]").all_text_contents()
            right_row_data_filtered = [item for item in right_row_data if '%' not in item]
            # print(right_row_data_filtered, len(right_row_data_filtered))
            right_row_data_final.append(right_row_data_filtered)

        np_right_row_data = np.array(right_row_data_final)
        print(np_right_row_data, len(np_right_row_data))
        
        stacked_array =  np.concatenate((np_left_row_data, middle_rows, np_right_row_data), axis=1)
        
        print(stacked_array, len(stacked_array))

        # Save stacked_array to CSV
        with open("options_BTC_Real_Time_Update.csv", 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(stacked_array)     

        browser.close()


def run_periodically():
    # Change cron variable to change Time Period (in seconds)
    cron = 3
    schedule.every(cron).seconds.do(job)

    # Loop to run the scheduler continuously
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Creating CSV File
    top_headers = ['Calls'] + ['' for i in range(8)] + ['Puts',]
    
    headers = [
        'Open (USDT)', 'Delta', 'Bid Size', 'Bid/IV', 'Mark/IV', 'Ask/IV', 'Ask Size',
        'Position', 'Strike', 'Position', 'Bid Size', 'Bid/IV', 'Mark/IV', 'Ask/IV',
        'Ask Size', 'Delta', 'Open (USDT)',
    ]

    with open("options_BTC_Real_Time_Update.csv", 'w', newline='') as csv_op:
        csvwriter = csv.writer(csv_op)
        csvwriter.writerow(top_headers)
        csvwriter.writerow(headers)
            
    run_periodically()
