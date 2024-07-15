import schedule
import time
import schedule
import csv
import numpy as np
from playwright.sync_api import sync_playwright
import os

with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        binance_url = "https://www.binance.com/en/eoptions/BTCUSDT"
        page.goto(binance_url, wait_until="load")

        time.sleep(8)
        # Performing click Actions on Individual Dates
        next_five_dates_btns = page.locator("(//div[@class='css-j8ru5z'])[position() <= 5]")
        print("\n\n")
        print(next_five_dates_btns.count())
        print("\n")
        for i in range(next_five_dates_btns.count()):
            tab_text = next_five_dates_btns.nth(i).inner_text().strip()
            next_five_dates_btns.nth(i).click()
            print(tab_text)
            

            print("--Left Side Table--")
            page.wait_for_selector("//div[@class='in-the-money call-row css-tb8ein' or @class='call-row css-tb8ein']")
            left_rows = page.locator("//div[@class='in-the-money call-row css-tb8ein' or @class='call-row css-tb8ein']")

            left_row_data_final = []
            for i in range(left_rows.count()):
                left_row = left_rows.nth(i)
                left_row_data = left_row.locator("//div[@class='css-mr03qh']/descendant::span[1]").all_text_contents()
                left_row_data_filtered = [item for item in left_row_data if '%' not in item]
                print(left_row_data_filtered, len(left_row_data_filtered))
                left_row_data_final.append(left_row_data_filtered)

            filename = f"{tab_text}_BTC_Options_Real_Time.csv"
            # with open(filename, 'a', newline='') as csvfile:
            # csvwriter = csv.writer(csvfile)
            # csvwriter.writerows(stacked_array) 
            file_exists = os.path.exists(filename)

            with open(filename, 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                if not file_exists:
                    csvwriter.writerow(['Open (USDT)', 'Delta', 'Bid Size', 'Bid/IV', 'Mark/IV', 'Ask/IV', 'Ask Size',
        'Position'])
                csvwriter.writerows(left_row_data_final) 