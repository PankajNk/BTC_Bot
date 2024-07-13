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
        
        spot_row = [current_price] + spot_data_list
        print(spot_row)
        
        with open("spot_BTC_Real_Time_Update.csv", 'a', newline='') as csv_op:
            csvwriter = csv.writer(csv_op)
            csvwriter.writerow(spot_row)

        # Future Scrape
        future_url = "https://www.binance.com/en/futures/BTCUSDT"
        page.goto(future_url, wait_until="load")
        #print(page.content())

        #MainBTCUSDT data
        current_future_price = page.title().split('|')[:1]

        #rest columns 
        # main div 
        spot_data_list = page.wait_for_selector("div.default-market-list-container")
        # this catch the required data   
        value_elements = spot_data_list.query_selector_all("div.text-PrimaryText")

        # Extract text from the elements
        future_row = current_future_price + [el.inner_text().strip() for el in value_elements]
        
        # Print the values
        print(future_row)
        with open("Future_BTC_Real_Time_Update.csv", 'a', newline='') as csv_op:
            csvwriter = csv.writer(csv_op)
            csvwriter.writerow(future_row)
        
        browser.close()
        

def run_periodically():
    # Change cron variable to change Time Period (in seconds)
    cron = 10
    schedule.every(cron).seconds.do(job)

    # Loop to run the scheduler continuously
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    
    # Creating spot CSV
    spot_headers = ["lastPrice","24h Change","24h High","24h Low","24h Volume(BTC)","24h Volume(USDT)"]
    with open("spot_BTC_Real_Time_Update.csv", 'w', newline='') as csv_op:
        csvwriter = csv.writer(csv_op)
        csvwriter.writerow(spot_headers)

    future_headers = ["Mark","Index","Funding / Countdown","24h High","24h Low","24h Volume(BTC)","24h Volume(USDT)","Open Interest(USDT)"]
    with open("Future_BTC_Real_Time_Update.csv", 'w', newline='') as csv_op:
        csvwriter = csv.writer(csv_op)
        csvwriter.writerow(future_headers)    
            
    run_periodically()
