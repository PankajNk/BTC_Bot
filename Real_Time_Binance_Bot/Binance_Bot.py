import gspread
from google.oauth2.service_account import Credentials
import schedule
import time
import csv
import numpy as np
from playwright.sync_api import sync_playwright
import os
from spot_future_data import spot_future_data

# Google Sheets setup
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("Real_Time_Binance_Bot/sheet_credentials.json", scopes=scopes)
client = gspread.authorize(creds)
sheet_id = "1_DXmHi5dFlKQTFYq979PITfYxq7jIQisA7GF_Mk3s5Q"
# sheet_id = input("Enter Sheet ID: ")
workbook = client.open_by_key(sheet_id)

worksheet_titles = [sheet.title for sheet in workbook.worksheets()]

if "Spot Data" not in worksheet_titles:
    spot_headers = ["lastPrice","24h Change","24h High","24h Low","24h Volume(BTC)","24h Volume(USDT)"]
    spot_worksheet = workbook.add_worksheet(title="Spot Data", rows="1000", cols="20")
    spot_worksheet.append_row(spot_headers)

    future_headers = ["Mark","Index","Funding / Countdown","24h High","24h Low","24h Volume(BTC)","24h Volume(USDT)","Open Interest(USDT)"]
    future_worksheet = workbook.add_worksheet(title="Future Data", rows="1000", cols="20")
    future_worksheet.append_row(future_headers)
else:
    spot_worksheet = workbook.worksheet("Spot Data")
    future_worksheet = workbook.worksheet("Future Data")

def job():
    print("Running job...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        spot_row, future_row = spot_future_data(page)
      
        spot_worksheet.append_row(spot_row)
        future_worksheet.append_row(future_row)

        worksheet_titles = [sheet.title.split('_')[-1] for sheet in workbook.worksheets()]
        if 'Sheet1' in worksheet_titles:
            sheet1 = workbook.worksheet("Sheet1")
            workbook.del_worksheet(sheet1)

        # options scraping
        binance_url = "https://www.binance.com/en/eoptions/BTCUSDT"
        page.goto(binance_url, wait_until="load")

        time.sleep(4)
        next_five_dates_btns = page.locator("(//div[@class='css-j8ru5z'])[position() <= 5]")

        if worksheet_titles[2:] != next_five_dates_btns.all_text_contents():
            worksheets = workbook.worksheets()

            # Delete all worksheets
            for worksheet in worksheets:
                if worksheet.title not in ["Spot Data", "Future Data"]:
                    workbook.del_worksheet(worksheet)
        
        for i in range(next_five_dates_btns.count()):
            tab_text = next_five_dates_btns.nth(i).inner_text().strip()
            next_five_dates_btns.nth(i).click()

            print("--Left Side Table--")
            page.wait_for_selector("//div[@class='in-the-money call-row css-tb8ein' or @class='call-row css-tb8ein']")
            left_rows = page.locator("//div[@class='in-the-money call-row css-tb8ein' or @class='call-row css-tb8ein']")
            
            left_row_data_final = []
            for i in range(left_rows.count()):
                left_row = left_rows.nth(i)
                left_row_data = left_row.locator("//div[@class='css-mr03qh']/descendant::span[1]").all_text_contents()
                left_row_data_filtered = [item for item in left_row_data if '%' not in item]
                left_row_data_final.append(left_row_data_filtered)

            np_left_row_data = np.array(left_row_data_final)
            print(np_left_row_data, len(np_left_row_data))

            print("\n--Middle Side Table--")
            middle_rows_ele = page.locator("//div[@class='css-kfl4vl']").all_text_contents()
            middle_rows = np.array(middle_rows_ele).reshape(len(middle_rows_ele), 1)
            print(middle_rows, len(middle_rows))

            print("\n--Right Side Table--")
            page.wait_for_selector("//div[@class='in-the-money put-row css-tb8ein' or @class='put-row css-tb8ein']")
            right_rows = page.locator("//div[@class='in-the-money put-row css-tb8ein' or @class='put-row css-tb8ein']")
            
            right_row_data_final = []
            for i in range(right_rows.count()):
                right_row = right_rows.nth(i)
                right_row_data = right_row.locator("//div[@class='css-mr03qh']/descendant::span[1]").all_text_contents()
                right_row_data_filtered = [item for item in right_row_data if '%' not in item]
                right_row_data_final.append(right_row_data_filtered)

            np_right_row_data = np.array(right_row_data_final)
            print(np_right_row_data, len(np_right_row_data))
            
            stacked_array = np.concatenate((np_left_row_data, middle_rows, np_right_row_data), axis=1)
            print(stacked_array, len(stacked_array))

            sheet_name = f"options_{tab_text}"

            try: 
                if tab_text not in worksheet_titles:
                    worksheet = workbook.add_worksheet(title=sheet_name, rows="1000", cols="20")
                else:
                    worksheet = workbook.worksheet(sheet_name)

                worksheet.clear()
                time.sleep(10)
                headers = ['Call_Open (USDT)', 'Call_Delta', 'Call_Bid Size', 'Call_Bid/IV', 'Call_Mark/IV', 'Call_Ask/IV', 'Call_Ask Size',
                           'Call_Position', 'Strike', 'Put_Position', 'Put_Bid Size', 'Put_Bid/IV', 'Put_Mark/IV', 'Put_Ask/IV',
                           'Put_Ask Size', 'Put_Delta', 'Put_Open (USDT)']
                worksheet.append_row(headers)
                # Convert the numpy array to a list of lists
                data_to_append = stacked_array.tolist()
                # Append all rows at once
                worksheet.append_rows(data_to_append)

            except gspread.exceptions.WorksheetNotFound:
                pass                    

        browser.close()

def run_periodically():
    cron = 3
    schedule.every(cron).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_periodically()