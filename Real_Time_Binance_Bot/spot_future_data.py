import time

def spot_future_data(page, CRYPTO_NAME):
        # spot scraping
        binance_url = f"https://www.binance.com/en/trade/{CRYPTO_NAME}?_from=markets&type=spot"
        page.goto(binance_url, wait_until="load")
        
        current_price = page.wait_for_selector("//div[@class='subPrice']").text_content()
        
        page.wait_for_selector("//div[@class='tickerPriceText']")
        spot_data_list = page.locator("//div[@class='tickerPriceText']").all_text_contents()
        
        spot_row = [current_price] + spot_data_list
        print(f"\033[1;34mLatest Spot data: {spot_row}\033[0m")        

        # Future Scrape
        future_url = f"https://www.binance.com/en/futures/{CRYPTO_NAME}"
        page.goto(future_url, wait_until="load")

        #MainBTCUSDT data
        current_future_price = page.title().split('|')[:1]

        #rest columns 
        # main div 
        spot_data_list = page.wait_for_selector("div.default-market-list-container")
        # this catch the required data   
        value_elements = spot_data_list.query_selector_all("div.text-PrimaryText")

        # Extract text from the elements
        future_row = current_future_price + [el.inner_text().strip() for el in value_elements]
     
        print(f"\033[1;35mLatest Future Data: {future_row}\033[0m")        

        
        return (spot_row, future_row)
        
