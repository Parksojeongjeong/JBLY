import ray
import urllib.request
import hashlib
from bs4 import BeautifulSoup
import requests
from porterna.detail_page_url import detail_url_scraper
import urllib3
import ssl

ray.init()

urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context

# path_folder_outwear = 'D:\\Jblyoutwear\\'
# path_folder_top = 'D:\\Jblytop\\'
# path_folder_bottom = 'D:\\Jblybottom\\'
# path_folder_acc = 'D:\\Jblyacc\\'
# path_folder_shoes = 'D:\\Jblyshoes\\'

main_url = "https://porterna.com"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"

@ray.remote
def crawl_detail_page_and_download_images(href):
    detail_url = main_url + str(href)
    detail_header = {
        'Referrer': detail_url,
        'user-agent': user_agent
    }
    detail_response = requests.get(detail_url, headers=detail_header)
    b_soup = BeautifulSoup(detail_response.text, 'html.parser')
    detail_html = b_soup.find(id="big-image").find_all("img")


# @ray.remote
# def download_images(link_img, item_type):
#     for link in link_img:
#         with urllib.request.urlopen(link) as response:
#             data = response.read()
#             md5hash = hashlib.md5(data).hexdigest()
#             md5hash = md5hash + ".jpg"
#             if item_type == ProductType.OUTWEAR:
#                 with open(path_folder_outwear + md5hash, 'wb') as f:
#                     f.write(data)
#             elif item_type == ProductType.TOP:
#                 with open(path_folder_top + md5hash, 'wb') as f:
#                     f.write(data)
#             elif item_type == ProductType.BOTTOM:
#                 with open(path_folder_bottom + md5hash, 'wb') as f:
#                     f.write(data)
#             elif item_type == ProductType.ACCESSORY:
#                 with open(path_folder_acc + md5hash, 'wb') as f:
#                     f.write(data)
#             else:
#                 with open(path_folder_shoes + md5hash, 'wb') as f:
#                     f.write(data)
#
#
# @ray.remote
# def porterna_img_downloader(target_url, item_type):
#     href_list = detail_url_scraper(target_url)
#     for href in href_list:
#         detail_url = main_url + str(href)
#         detail_header = {
#             'Referrer': detail_url,
#             'user-agent': user_agent
#         }
#         detail_response = requests.get(detail_url, headers=detail_header)
#         b_soup = BeautifulSoup(detail_response.text, 'html.parser')
#         detail_html = b_soup.find(id="big-image").find_all("img")
#         link_img = []
#         url = 'https:'
#         for img in detail_html:
#             link_img.append(url + img['src'])
#         for link in link_img:
#             download_images.remote(link, item_type)
#
#
# def parallel_porterna_img_downloader():
#     urls = [
#         ("https://porterna.com/product/list.html?cate_no=541&page=", product_types.OUTWEAR.name),
#         ("https://porterna.com/product/list.html?cate_no=789&page=", product_types.TOP.name),
#         ("https://porterna.com/product/list.html?cate_no=28&page=", product_types.BOTTOM.name),
#         ("https://porterna.com/product/list.html?cate_no=44&page=", product_types.ACCESSORY.name),
#         ("https://porterna.com/product/list.html?cate_no=79&page=", product_types.SHOES.name),
#     ]
#     futures = []
#     for url in urls:
#         target_url, item_type = url
#         future = porterna_img_downloader.remote(target_url, item_type)
#         futures.append(future)
#     ray.get(futures)