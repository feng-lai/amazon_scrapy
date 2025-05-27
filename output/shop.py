import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from lxml import etree
from tqdm import tqdm
from bs4 import BeautifulSoup
import time
import pandas as pd

# 获取当前日期
day_date = datetime.now().strftime("%Y-%m-%d")

# 初始化浏览器对象（使用Edge）
options = Options()
# options.add_argument("headless")  # 无头模式
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument('--disable-blink-features=AutomationControlled')  # 规避检测
options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 规避检测

driver = webdriver.Edge(options=options)

# 访问亚马逊榜单页面
driver.get('https://www.amazon.com/Best-Sellers-Clothing-Shoes-Jewelry-Womens-Fashion-Hoodies-Sweatshirts/zgbs/fashion/1258603011/ref=zg_bs_pg_2_fashion?_encoding=UTF8&pg=2')
time.sleep(3)
# 准备存储数据的列表
product_info_list = []
unique_links = set()  # 用于存储唯一的产品链接

# 定义循环次数，抓取前两页的数据
for i in range(1, 2):
    # 等待页面加载
    driver.implicitly_wait(2)
    # 滚动页面以加载更多数据
    driver.execute_script("window.scrollTo(0, 3000);")
    driver.implicitly_wait(4)
    driver.execute_script("window.scrollTo(3000, 4070);")
    driver.implicitly_wait(4)
    time.sleep(4)
    driver.execute_script("window.scrollTo(0, 1070);")
    driver.implicitly_wait(4)
    driver.execute_script("window.scrollTo(0, 1070);")
    driver.implicitly_wait(4)
    driver.execute_script("window.scrollTo(0, 1070);")
    driver.implicitly_wait(4)
    time.sleep(4)

    # 获取页面HTML内容
    text = driver.page_source
    # 解析HTML
    tree = etree.HTML(text)

    product_links_page = tree.xpath('//div[@id="gridItemRoot"]//div/a/@href')

# 对每个商品链接进行详细信息爬取
for product_link in tqdm(unique_links, desc='正在爬取商品详情'):
    try:
        # 获取页面HTML内容
        driver.get(product_link)
        driver.implicitly_wait(2)
        
        # 找到并点击卖家信息按钮
        seller_profile_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="sellerProfileTriggerId"]'))
        )
        seller_profile_button.click()

        # 获取卖家页面链接
        seller_page_url = driver.current_url

        # 点击评论时间周期下拉菜单
        rating_time_periods_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="seller-rating-time-periods"]/span'))
        )
        rating_time_periods_button.click()

        # 收集不同时间段的评论数
        rating_periods = ['1 month', '3 months', '12 months', 'Lifetime']
        rating_counts = {}
        for period in rating_periods:
            option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//a[text()="{period}"]'))
            )
            option.click()
            rating_count_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="rating-thirty-num"]/span[1]'))
            )
            rating_counts[period] = rating_count_element.text
        
        # 向下滚动页面
        driver.execute_script("window.scrollTo(0, 300);")
        
        # 收集卖家描述
        description_elements = driver.find_elements(By.XPATH, '//*[@id="page-section-detail-seller-info"]/div/div/div/div[position() > 3]')
        description = ' '.join([element.text for element in description_elements])
        
        # 存储数据
        product_info_list.append({
            'seller_name': driver.find_element(By.XPATH, '//*[@id="seller-name"]').text,
            'seller_link': seller_page_url,
            '1month_rating': rating_counts['1 month'],
            '3months_rating': rating_counts['3 months'],
            '12months_rating': rating_counts['12 months'],
            'lifetime_rating': rating_counts['Lifetime'],
            'description': description
        })
    except Exception as e:
        print(f"Error processing {product_link}: {e}")

# 将结果保存到CSV文件
df = pd.DataFrame(product_info_list)
df.to_csv(f'amazon_product_details_{day_date}.csv', index=False, encoding='utf-8-sig')

# 关闭浏览器
driver.quit()