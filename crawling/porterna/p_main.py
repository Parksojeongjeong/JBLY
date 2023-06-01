import logging
import os
import re
import urllib.request
import ray
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


@ray.remote
def get_href_list(target_url):
    print(target_url[0])
    href_list = []
    for page_num in range(1, int(find_last_page(target_url[0])) + 1):
        header = {
            'Referrer': target_url[0] + str(page_num),
            'user-agent': user_agent
        }
        response = requests.get(target_url[0] + str(page_num), headers=header)
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

    print(len(href_list))
    return href_list

def get_all_href():
    urls = [
        ("https://porterna.com/product/list.html?cate_no=541&page=", product_types.OUTWEAR.name),
        ("https://porterna.com/product/list.html?cate_no=789&page=", product_types.TOP.name),
        ("https://porterna.com/product/list.html?cate_no=28&page=", product_types.BOTTOM.name),
        ("https://porterna.com/product/list.html?cate_no=44&page=", product_types.ACCESSORY.name),
        ("https://porterna.com/product/list.html?cate_no=79&page=", product_types.SHOES.name),
    ]

    href_lists = []
    for url in urls:
        each_url,item_type = url
        href_list_ref = get_href_list.remote(url) # 메시지
        href_lists.append(href_list_ref)# 리뫁, futurese담김. 결국 진짜 값은 없음.(약속된 객체들)
    href_lists = ray.get(href_lists) #메소드, 기다렷다가 받은 진짜 리스트들 담김 get(get은 퓨쳐에서 답 가져오는거임)
    print(href_lists)
    print(len(href_lists))

    return [href, item_type]

if __name__ == '__main__':
    get_all_href()