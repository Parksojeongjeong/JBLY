import hashlib
import urllib.request
import ray

urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context

path_folder_outwear = 'D:\\Jblyoutwear\\'
path_folder_top = 'D:\\Jblytop\\'
path_folder_bottom = 'D:\\Jblybottom\\'
path_folder_acc = 'D:\\Jblyacc\\'
path_folder_shoes = 'D:\\Jblyshoes\\'

main_url = "https://porterna.com"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"


@ray.remote
def download_images(href_list, item_type):
    link_img = []
    url = 'https:'
    for href in href_list:
        detail_url = main_url + str(href)
        detail_header = {
            'Referrer': detail_url,
            'user-agent': user_agent
        }
        detail_response = requests.get(detail_url, headers=detail_header)
        b_soup = BeautifulSoup(detail_response.text, 'html.parser')
        detail_html = b_soup.find(id="big-image").find_all("img")
        for img in detail_html:
            link_img.append(url + img['src'])

    downloaded_images = []
    for link in link_img:
        with urllib.request.urlopen(link) as response:
            data = response.read()
            md5hash = hashlib.md5(data).hexdigest() + ".jpg"
            downloaded_images.append((md5hash, data))

    if item_type == product_types.OUTWEAR.name:
        for md5hash, data in downloaded_images:
            with open(path_folder_outwear + md5hash, 'wb') as f:
                f.write(data)

# Parallel execution using Ray
href_list_refs = []
for url in urls:
    href_list_ref = get_href_list.remote(url)
    href_list_refs.append(href_list_ref)

href_lists = ray.get(href_list_refs)

# Crawling detail pages and downloading images in parallel
ray_tasks = []
for href_list, url, item_type in zip(href_lists, urls, product_types):
    ray_task = download_images.remote(href_list, url[0], item_type)
    ray_tasks.append(ray_task)

ray.get(ray_tasks)

if __name__ == '__main__':
    ray.init()

    urls = [
        ("https://porterna.com/product/list.html?cate_no=541&page=", product_types.OUTWEAR.name),
        ("https://porterna.com/product/list.html?cate_no=789&page=", product_types.TOP.name),
        ("https://porterna.com/product/list.html?cate_no=28&page=", product_types.BOTTOM.name),
        ("https://porterna.com/product/list.html?cate_no=44&page=", product_types.ACCESSORY.name),
        ("https://porterna.com/product/list.html?cate_no=79&page=", product_types.SHOES.name),
    ]
    href_lists = []
    start_time = time.time()
    for url in urls:
        each_url,item_type = url
