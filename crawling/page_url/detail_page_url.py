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
import ray

urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context

ray.init()
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

@ray.remote
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

urls = [
    ("https://porterna.com/product/list.html?cate_no=541&page=", product_types.OUTWEAR.name),
    ("https://porterna.com/product/list.html?cate_no=789&page=", product_types.TOP.name),
    ("https://porterna.com/product/list.html?cate_no=28&page=", product_types.BOTTOM.name),
    ("https://porterna.com/product/list.html?cate_no=44&page=", product_types.ACCESSORY.name),
    ("https://porterna.com/product/list.html?cate_no=79&page=", product_types.SHOES.name),
]

result_ids = []
for url in urls:
    for page_num in range(1, 6):  # 1 ~ 5 페이지를 크롤링
        result_ids.append(detail_url_scraper.remote(url[0], page_num, url[1]))
start_time = time.time()
results = ray.get(result_ids)
end_time = time.time()

elapsed_time = end_time - start_time
print("Elapsed Time: ", elapsed_time, "seconds")

total_href_list = []
for href_list in results:
    total_href_list += href_list

print("상품개수: ", len(total_href_list))