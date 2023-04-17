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

path_folder_outwear = 'D:\\Jblyoutwear\\'
path_folder_top = 'D:\\Jblytop\\'
path_folder_bottom = 'D:\\Jblybottom\\'
path_folder_acc = 'D:\\Jblyacc\\'
path_folder_shoes = 'D:\\Jblyshoes\\'

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


def detail_url_scraper(target_url, page_num):
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
    start_time = time.time()
    target_url = "https://porterna.com/product/list.html?cate_no=79&page="
    last_page = int(find_last_page(target_url))
    href_list = []
    with concurrent.futures.ThreadPoolExecutor() as executor: # 쓰레드 풀 생성
        future_to_url = {executor.submit(detail_url_scraper, target_url, page_num): page_num for page_num in range(1, last_page+1)}
        for future in concurrent.futures.as_completed(future_to_url):
            page_num = future_to_url[future]
            try:
                href_set = future.result()
                href_list += list(href_set)
            except Exception as e:
                logging.exception(e)
    print("상품 개수:",len(href_list))
    print(f"{time.time() - start_time} sec")


def porterna_img_downloader(target_url, item_type):
    href_list = detail_url_scraper(target_url)
    for href in href_list:
        detail_url = main_url + str(href)
        detail_header = {
            'Referrer': detail_url,
            'user-agent': user_agent
        }
        detail_response = requests.get(detail_url, headers=detail_header)
        b_soup = BeautifulSoup(detail_response.text, 'html.parser')
        detail_html = b_soup.find(id="big-image").find_all("img")
        link_img = []
        url = 'https:'
        for img in detail_html:
            link_img.append(url + img['src'])
            for link in link_img:
                if item_type == product_types.OUTWEAR.name:
                    with urllib.request.urlopen(link) as response:
                        data = response.read()
                        md5hash = hashlib.md5(data).hexdigest()
                        md5hash = md5hash + ".jpg"
                        with open(path_folder_outwear + md5hash, 'wb') as f:
                            f.write(data)

                elif item_type == product_types.TOP.name:
                    with urllib.request.urlopen(link) as response:
                        data = response.read()
                        md5hash = hashlib.md5(data).hexdigest()
                        md5hash = md5hash + ".jpg"
                        with open(path_folder_top + md5hash, 'wb') as f:
                            f.write(data)
                elif item_type == product_types.BOTTOM.name:
                    with urllib.request.urlopen(link) as response:
                        data = response.read()
                        md5hash = hashlib.md5(data).hexdigest()
                        md5hash = md5hash + ".jpg"
                        with open(path_folder_bottom + md5hash, 'wb') as f:
                            f.write(data)

                elif item_type == product_types.ACCESSORY.name:
                    with urllib.request.urlopen(link) as response:
                        data = response.read()
                        md5hash = hashlib.md5(data).hexdigest()
                        md5hash = md5hash + ".jpg"
                        with open(path_folder_acc + md5hash, 'wb') as f:
                            f.write(data)

                else:
                    with urllib.request.urlopen(link) as response:
                        data = response.read()
                        md5hash = hashlib.md5(data).hexdigest()
                        md5hash = md5hash + ".jpg"
                        with open(path_folder_shoes + md5hash, 'wb') as f:
                            f.write(data)

    return None
