import pandas as pd
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webhook import send_message
import time
import csv
import os.path

item_ls = []
item_url_ls=[]
txt_cache_path = "media/csv/cache.txt"

def browser_setup(chromedriver_path):
    """Browser setup function"""
    #Configure the browser
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    #Start browser
    service = webdriver.ChromeService(executable_path=chromedriver_path)
    browser = webdriver.Chrome(service=service, options=options)
    browser.implicitly_wait(3)
    return browser


def get_url(KEYWORD , browser):
    #Display items
    #print(f"DEBUG: get_url HIT")
    url = 'https://jp.mercari.com/search?keyword=' + KEYWORD + '&status=on_sale'
    browser.get(url)
    browser.implicitly_wait(5)
    wait = WebDriverWait(browser, 10)
    #Get the URL of the product detail page
    item_box = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#item-grid > ul > li')))
    #print(f"DEBUG: results page loaded")
    for item_elem in item_box:
        #print(f"DEBUG: Getting item page url")
        #Check if this is a listing element
        href_check = item_elem.get_attribute('innerHTML').find('href')
        #print(f"DEBUG: href_check = {href_check}")
        if href_check >= 0:
            item_urls = item_elem.find_elements(By.CSS_SELECTOR, 'a')     
            if item_urls:
                for item_url in item_urls:
                    item_url_ls.append(item_url.get_attribute('href'))
                    print(f"DEBUG: Got {item_url.get_attribute('href')}, adding to list")
    #print(f"DEBUG: Got {len(item_url_ls)} urls")

def is_contained(target_str, search_str):
    """
    Function to determine if target_str contains search_str
    """
    if target_str.find(search_str) >= 0:
        return True
    else:
        return False
    
def df_to_csv_local_url(df: pd.DataFrame , output_csv_path: str = "output.csv"):
    """ Function to generate a URL to download a table of data frame type in csv format """
    # Generate csv & save on local directory (if "path_or_buf" is specified, return value is "None")
    pd.set_option('display.max_colwidth', 5000)
    df.to_csv(path_or_buf=output_csv_path, mode='a' ,index=False, header=False, encoding='utf-8-sig')
    print(f"DEBUG: csv saved")

def load_txt_cache(file):
    with open(file,  newline ='') as f:
        read_sites = [line.rstrip() for line in f]
    return read_sites

def save_txt_cache(file, urls):
    with open(file,"a") as fp:
        for line in urls:
            fp.write(line)
            fp.write('\n')

def page_mercari_com(browser):
    wait = WebDriverWait(browser, 10)
    #Product Name
    item_name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#item-info > section:nth-child(1) > div.mer-spacing-b-12'))).text
    # Product Description
    item_ex = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#item-info > section:nth-child(2) > div:nth-child(2)'))).text
    # Price
    item_price = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#item-info [data-testid="price"] > span:last-child'))).text
    return item_name , item_ex , item_price


def page_mercari_shop_com(browser):
    wait = WebDriverWait(browser, 10)
    # Brand Name
    item_name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))).text
    # Product Description
    item_ex = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#product-info > section:nth-child(2) > div:nth-child(2)'))).text
    # Price
    item_price = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#product-info [data-testid="product-price"] > span:last-child'))).text
    return item_name , item_ex , item_price


def get_data(browser, names):
    #Get detailed product information
    #count = 0
    read_sites = load_txt_cache(txt_cache_path)
    #print(f"DEBUG: got {read_sites} in cache")
    #st.write(f"Getting : {getting_count} items \n")
    print(f'Found {len(item_url_ls)} items')
    for item_url in item_url_ls:
        if not item_url in read_sites:
            browser.get(item_url)
            time.sleep(3)
           # Get product name ~ image URL
            if is_contained(item_url, "shop"):  # When the product detail page is mercari-shops.com
                item_name , item_ex , item_price = page_mercari_shop_com(browser)
            else:  # When the product detail page is mercari.com
                item_name , item_ex , item_price = page_mercari_com(browser)
                item_price = item_price.replace(",","").replace('"','')
                print(f"Getting {item_name}")
            #Parse the title to avoid false positives    
            title_check = [name for name in names if(name in item_name)]
            if title_check:
                data = {
                    'Name':item_name,
                    'Price':item_price,
                    'URL':item_url,
                }
                send_message(data)
                item_ls.append(data)
            read_sites.append(item_url)
            
        else:
            print("Already read this url, skipping")        
    save_txt_cache(txt_cache_path, read_sites)




def main():
    # main variables
    chromedriver_path =  "/usr/bin/chromedriver"
    output_csv_path = "media/csv/output.csv"
    KEYWORDS = ['初音ミク　どでか','初音ミク メガジャンボ寝そべりぬいぐるみ', '初音ミク 特大寝そべりぬいぐるみ'] # Search keywords
    NAMES = ['ミク　どでか','ミク寝そべり','初音ミク','ミクプライズ'] # Any of the words MUST be in the title 
    for key in KEYWORDS:
        print("DEBUG: Setting up WebDriver")
        browser = browser_setup(chromedriver_path)
        print(f"DEBUG: getting {key} urls")
        get_url(key , browser)
        a = get_data(browser, NAMES)
        print(f"DEBUG: Saving to csv")
        pd.set_option('display.max_colwidth', 5000)
        df = pd.DataFrame(item_ls)
        df_to_csv_local_url(df , output_csv_path)


if __name__ == '__main__':
        main()
