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
from typing import Dict, List

urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context

ray.init(num_cpus=4)
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
def detail_url_scraper(target_url, item_type)-> Dict[str, List[str]]:
    href_dict = {}
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
    # href_dict +=
    href_list += list(href_set)
    href_dict = dict.fromkeys(item_type, href_list)
    print(href_dict)

def detail_url_scraper(target_url):
    href_list = []
    for page_num in range(1, int(find_last_page(target_url)) + 1):
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
def detail_url_scraper(target_url) -> Dict[str, List[str]]:
    response = requests.get(target_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    detail_urls = {}
    item_types = soup.select('.inner > h4')
    for item_type in item_types:
        hrefs = [a['href'] for a in item_type.find_next('ul').find_all('a')]
        detail_urls[item_type.text] = hrefs

    return detail_urls
# @ray.remote
# def porterna_img_downloader(target_url, item_type):
#     href_list = detail_url_scraper.remote(target_url, item_type)
#     for href in href_list:
#         detail_url = main_url + str(href)
#         detail_header = {
#             'Referrer': detail_url,
#             'user-agent': user_agent
#         }
#         detail_response = requests.get(detail_url, headers=detail_header)
#         b_soup = BeautifulSoup(detail_response.text, 'html.parser')
#         detail_html = b_soup.find(id="big-image").find_all("img")


if __name__ == "__main__":
    urls = [
        ("https://porterna.com/product/list.html?cate_no=541&page=", product_types.OUTWEAR.name),
        ("https://porterna.com/product/list.html?cate_no=789&page=", product_types.TOP.name),
        ("https://porterna.com/product/list.html?cate_no=28&page=", product_types.BOTTOM.name),
        ("https://porterna.com/product/list.html?cate_no=44&page=", product_types.ACCESSORY.name),
        ("https://porterna.com/product/list.html?cate_no=79&page=", product_types.SHOES.name),
    ]
    start_time = time.time()
    results = []
    for url in urls:
        target_url, item_type = url
        last_page = find_last_page(target_url)
        hrefs = []
        futures = []
        for page_num in range(1, int(last_page)+1):
            future = detail_url_scraper.remote(target_url, item_type)
            futures.append(future)
        hrefs = ray.get(futures)
        hrefs = [href for href_list in hrefs for href in href_list]
        results.append(hrefs)

    total_href_list = []
    for href_list in results:
        total_href_list += href_list
    print(time.time() - start_time)
    # print("상품개수:", len(total_href_list))
    # img_url = []
    # for href in href_list:
    #     future =porterna_img_downloader.remote(target_url, item_type)



