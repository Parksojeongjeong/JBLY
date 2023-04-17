import logging
import re
import urllib.request
from bs4 import BeautifulSoup
import requests
from common.ProductTypes import product_types
import urllib3
import ssl
import hashlib
import time
import concurrent.futures


urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context


main_url = "https://porterna.com"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"


def find_last_page(target_url):
    pattern = r'<li class="xans-record-"><a class="other" href="\?cate_no=\d+&amp;page=(\d+)">'
    header = {
        'Referrer': main_url,
        'user-agent': user_agent
    }
    response = requests.get(target_url, headers=header)
    soup = BeautifulSoup(response.text, 'html.parser')
    find_li = soup.find('div', 'xans-element- xans-product xans-product-normalpaging paging')
    find_li = find_li.find_all('li')
    find_li = list(map(str, find_li))
    string = str(find_li[-1])
    match = re.search(pattern, string)
    number = match.group(1)
    return number


def detail_url_scraper(target_url, page_num, item_type):
    href_list = []
    header = {
        'Referrer': target_url + str(page_num),
        'user-agent': user_agent
    }
    response = requests.get(target_url + str(page_num), headers=header)
    soup = BeautifulSoup(response.text, 'html.parser')
    soup = soup.find_all('ul', {'class': 'thumbnail'})
    href_set = set()
    for ul_tag in soup:
        a_tags = ul_tag.find_all('a')
        for a_tag in a_tags:
            href = a_tag.get('href')
            if href is not None:
                href_set.add(href)
    href_list += list(href_set)
    return href_list


if __name__ == "__main__":
    urls = [
        ("https://porterna.com/product/list.html?cate_no=541&page=", product_types.OUTWEAR.name),
        ("https://porterna.com/product/list.html?cate_no=789&page=", product_types.TOP.name),
        ("https://porterna.com/product/list.html?cate_no=28&page=", product_types.BOTTOM.name),
        ("https://porterna.com/product/list.html?cate_no=44&page=", product_types.ACCESSORY.name),
        ("https://porterna.com/product/list.html?cate_no=79&page=", product_types.SHOES.name),
    ]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        start_time = time.time()
        futures = []
        for url, item_type in urls:
            last_page = int(find_last_page(url))
            for page_num in range(1, last_page+1):
                futures.append(executor.submit(detail_url_scraper, url, page_num, item_type))
        href_list = []
        for future in concurrent.futures.as_completed(futures):
            try:
                href_set = future.result()
                href_list += list(href_set)
            except Exception as e:
                logging.exception(e)
    print("상품 개수:", len(href_list))
    print(f"{time.time() - start_time} sec")
