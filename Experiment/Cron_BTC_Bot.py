import schedule
import time
import schedule
import csv
from playwright.sync_api import sync_playwright

def job():
    print("Running job...")
    # Your method's logic here
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        binance_url = "https://www.binance.com/en/trade/BTC_USDT?_from=markets&type=spot"
        page.goto(binance_url, wait_until="load")
        
        current_price = page.wait_for_selector("//div[@class='subPrice']").text_content()
        
        page.wait_for_selector("//div[@class='tickerPriceText']")
        spot_data_list = page.locator("//div[@class='tickerPriceText']").all_text_contents()
        
        row = [current_price] + spot_data_list
        print(row)
        
        with open("BTC_Real_Time_Update.csv", 'a', newline='') as csv_op:
            csvwriter = csv.writer(csv_op)
            csvwriter.writerow(row)
        
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
    headers = ["lastPrice","24h Change","24h High","24h Low","24h Volume(BTC)","24h Volume(USDT)"]
    with open("BTC_Real_Time_Update.csv", 'w', newline='') as csv_op:
        csvwriter = csv.writer(csv_op)
        csvwriter.writerow(headers)
            
    run_periodically()
