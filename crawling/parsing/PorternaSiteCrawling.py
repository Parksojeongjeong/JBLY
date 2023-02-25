from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import ssl


ssl._create_default_https_context = ssl._create_unverified_context


def getTotalProducts():
    driver = webdriver.Chrome()

    shopId = 1
    storeName = "porterna"
    result = [] # storeName, itemName, getUrl, getPrice, itemType, shopId
    urls = []
    urls.append(("https://porterna.com/product/list.html?cate_no=541", "outwear")) # outwear
    urls.append(("https://porterna.com/product/list.html?cate_no=789", "top")) # top
    urls.append(("https://porterna.com/product/list.html?cate_no=28", "pants")) # pants
    urls.append(("https://porterna.com/product/list.html?cate_no=44", "accessory")) # acc
    urls.append(("https://porterna.com/product/list.html?cate_no=79", "shoes")) # shoes

    for url in urls:
        eachUrl, itemType = url
        driver.get(eachUrl)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        datas = soup.find("ul", "thumbnail").find_all("li", recursive=False)
        datas = list(map(str, datas))

        for data in datas:
            itemInfoGather = []
            eachData = BeautifulSoup(data, 'html.parser')
            getImageUrl = eachData.find('img')['src']
            imageUrl = 'https:' + getImageUrl

            getItemName = eachData.find('p', {'class': 'name'})
            itemName = getItemName.text

            getPrice = eachData.find('div', {'class': 'price1'})
            price = getPrice.text

            itemInfoGather.append(storeName)
            itemInfoGather.append(itemName)
            itemInfoGather.append(imageUrl)
            itemInfoGather.append(int(price))
            itemInfoGather.append(itemType)
            itemInfoGather.append(shopId)
            copyItemInfo = itemInfoGather.copy()
            result.append(copyItemInfo)
            itemInfoGather.clear()

        # page 이동
        element = driver.find_element(by=By.XPATH, value='//*[@id="contents"]/div[2]/div[4]/a[2]')
        time.sleep(5)

        if element.is_displayed() and element.is_enabled():
            try:
                driver.execute_script("arguments[0].click();", element)
            except:
                pass
        if driver.current_url.endswith("#none"):
            continue

    driver.close()
    return result
