import csv

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep

chrome_driver_location = "C:/Users/student/Downloads/chromedriver_win32"

options = webdriver.ChromeOptions()

# options.add_argument('headless')
# options.add_argument('window-size=1920x1080')
# options.add_argument("disable-gpu")
# driver = webdriver.Chrome(chrome_driver_location+"/chromedriver", chrome_options=options)

driver = webdriver.Chrome(chrome_driver_location+"/chromedriver")

url_by_plus_event = "http://cu.bgfretail.com/event/plus.do?category=event&depth2=1&sf=N"
url_by_add_event = "http://cu.bgfretail.com/event/present.do?category=event&depth2=5&sf=N"
url_by_pb_goods = "http://cu.bgfretail.com/product/pb.do?category=product&sf=N"

goods_list = []

#driver와 실제 코드는 따로 작동한다. >>> 특히

def make_file(fileName, case):
    with open("C:/Users/student/Desktop/CU/"+fileName,"w", encoding='UTF-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for good in goods_list:
            if case=="plus":
                csv_writer.writerow([good[0], int(good[1].replace(',','')), good[2]])
        print('file making complete')

def load_more_in_plus_event():
    driver.get(url_by_plus_event)
    driver.implicitly_wait(2)
    for i in range(0,20):
        element_by_more = driver.find_element(By.XPATH, "//div[@class='prodListWrap']/div[@class='prodListBtn']/div[@class='prodListBtn-w']/a")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        element_by_more.send_keys(Keys.ENTER)
        driver.implicitly_wait(2)
    sleep(30)

def crawling_in_pb_goods(html_list):
    for html_each in html_list:
        soup = BeautifulSoup(html_each, "html.parser")
        for ul_list in soup.find('div', class_='prodListWrap').findChildren('ul', recursive=False):
            for li_list in ul_list.findChildren('li', recursive=False):
                inner_list = ['PB_PB' if html_each==html_list[0] else 'PB_diff',
                              li_list.find('p', class_='prodName').get_text(),
                              li_list.find('p', class_='prodPrice').find('span').get_text()]
                goods_list.append(inner_list)

def get_pb_goods():
    driver.get(url_by_pb_goods)
    driver.implicitly_wait(2)
    btn_by_differ_goods = driver.find_element(By.XPATH, "//div[@class='depth3 mb40']/ul[@class='cardInfo']/li[@class='cardInfo_02']/a")

    def load_more_in_pb_goods(maxLoop):
        for i in range(0,maxLoop):
            element_by_more = driver.find_element(By.XPATH, "//div[@class='prodListWrap']/div[@class='prodListBtn']/div[@class='prodListBtn-w']/a")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            element_by_more.send_keys(Keys.ENTER)
            driver.implicitly_wait(2)
        sleep(int(maxLoop*2.5))

    load_more_in_pb_goods(7)
    html1 = driver.page_source

    sleep(2)

    btn_by_differ_goods.send_keys(Keys.ENTER)
    driver.implicitly_wait(2)

    load_more_in_pb_goods(20)
    html2 = driver.page_source

    return [html1,html2]

def crawling_in_plus_event():
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    for ul_list in soup.find('div',class_='prodListWrap').findChildren('ul',recursive=False):
        for li_list in ul_list.findChildren('li',recursive=False):
            inner_list=[li_list.find('p',class_='prodName').get_text(), li_list.find('p',class_='prodPrice').find('span').get_text(), li_list.find('li').get_text()]
            goods_list.append(inner_list)

def crawling_in_add_event():
    driver.get(url_by_add_event)
    driver.implicitly_wait(2)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    for wrap_list in soup.find('div', class_='presentListWrap').find_all('div',class_='presentListBox'):
        set_good = [];
        main_good = wrap_list.find('div', class_='presentList-w')
        main_list = [main_good.find('p',class_='prodName').find('a').get_text(), main_good.find('p',class_='prodPrice').find('span').get_text()]
        gift_good = wrap_list.find('div', class_='presentList-e')
        gift_list = [gift_good.find('p',class_='prodName').find('a').get_text(), gift_good.find('p',class_='prodPrice').get_text()]
        goods_list.append(main_list+gift_list)

## 1+1/2+1/3+1상품 목록
load_more_in_plus_event()
crawling_in_plus_event()
make_file("plus_event_list.csv", "plus")

## 증정상품 목록
#crawling_in_add_event()
# print(goods_list)
# print(len(goods_list))

## pb상품 목록
# crawling_in_pb_goods(get_pb_goods())
# print(goods_list)
# print(len(goods_list))