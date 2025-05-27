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
driver.get('https://www.amazon.com/s?me=A1E0YVIEEE0AQG&marketplaceID=ATVPDKIKX0DER')
time.sleep(3)

# 准备存储数据的列表
final_product_info_list = []
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

    # 获取页面HTML内容
    text = driver.page_source
    # 解析HTML
    tree = etree.HTML(text)

    # XPath表达式
    titles_xpath = '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[position()>1 and position()<last()]/div/div/span/div/div/div/div[2]/div/div/div[1]/h2/a/span/text()'
    prices_xpath = '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[position()>1 and position()<last()]/div/div/span/div/div/div/div[2]/div/div/div[3]/div[1]/div/div[1]/div/div[1]/a/span/span[1]/text()'
    links_xpath = '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[position()>1 and position()<last()]/div/div/span/div/div/div/div[2]/div/div/div[1]/h2/a/@href'
    
    # 抓取数据
    titles = tree.xpath(titles_xpath)
    prices = tree.xpath(prices_xpath)
    product_links = ['https://www.amazon.com' + link for link in tree.xpath(links_xpath)]
    
    # 清洗价格数据，仅保留数字部分
    cleaned_prices = [price.strip().replace('$', '') for price in prices]

    # 确保所有列表长度一致
    min_length = min(len(titles), len(cleaned_prices), len(product_links))
    a = 1
    # 对每个商品链接进行详细信息爬取
    for j in tqdm(range(min_length), desc=f'正在爬取Best Sellers in Women\'s Fashion Hoodies & Sweatshirts第{a}页'):
        title = titles[j].strip()
        price = cleaned_prices[j]
        product_link = product_links[j]
        a = a + 1

        # 过滤掉包含 product-reviews 的链接
        if 'product-reviews' in product_link:
            continue

        # 检查链接是否已存在
        if product_link in unique_links:
            continue
        unique_links.add(product_link)

        # 获取页面HTML内容
        driver.get(product_link)
        driver.implicitly_wait(2)
        detail_text = driver.page_source
        # 解析HTML
        detail_tree = etree.HTML(detail_text)

        # 抓取图片
        images = []

        # 主图
        main_image = detail_tree.xpath('//*[@id="landingImage"]/@src')
        if main_image:
            images.append(main_image[0])
        else:
            images.append('')

        # 查找所有额外图片按钮
        image_buttons = detail_tree.xpath('//*[@id="altImages"]/ul/li')
        if image_buttons:
            for idx, button in enumerate(image_buttons):
                # 构建完整的XPath表达式
                image_option_xpath = f'//*[@id="altImages"]/ul/li[{idx + 1}]'
                
                # 获取按钮的class属性值
                class_value = button.get('class')
                
                # 如果不是视频按钮，则点击
                if 'videoThumbnail' not in class_value:
                    try:
                        # 使用 WebDriver 的 find_element 方法来定位元素，这样可以直接操作
                        image_button_element = driver.find_element(By.XPATH, image_option_xpath)
                        image_button_element.click()
                        time.sleep(3)  # 等待图片加载
                        
                        # 重新获取页面HTML内容
                        detail_text = driver.page_source
                        detail_tree = etree.HTML(detail_text)
                        
                        dynamic_images = detail_tree.xpath('//img[@class="a-dynamic-image"]/@src')
                        for img_src in dynamic_images[:7]:  # 只取前7个，因为主图已经算一个
                            if img_src not in images:  # 检查图片是否已经存在于列表中
                                images.append(img_src)
                                print(img_src)
                    except Exception:
                        print("没有这个图片选项")
        else:
            print("没有找到额外图片按钮")

        # 确保有至少8张图片，如果没有则用空字符串填充
        images.extend([''] * (8 - len(images)))
        
        # 提取描述
        description = ""
        try:
            # 尝试从第一个位置提取描述
            description_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='aplus']/div"))
            )
            time.sleep(3)  # 等待页面加载
        
            # 如果找到描述元素，则继续处理
            if description_div:
                # 获取前七个 div 元素
                description_divs = driver.find_elements(By.XPATH, "//*[@id='aplus']/div/div[position() <= 7]")
        
                # 合并前七个 div 的内容
                combined_description_html = ''.join(div.get_attribute('outerHTML') for div in description_divs)
        
                # 使用 BeautifulSoup 处理合并后的 HTML
                soup = BeautifulSoup(combined_description_html, 'html.parser')
        
                # 清理 HTML 内容
                for tag in soup.find_all(['div', 'script'], class_=lambda x: x and 'video' in x if x else False):
                    tag.decompose()
        
                # 获取清理后的 HTML 结构
                description = str(soup)
                print("找到有效的描述")
        
        except (NoSuchElementException, TimeoutException):
            try:
                # 如果第一个位置没有找到，尝试从第二个位置提取描述
                description_divs = driver.find_elements(By.XPATH, "//*[@id='productDescription_feature_div']//div[position() <= 7]")
        
                # 如果找到描述元素，则继续处理
                if description_divs:
                    # 合并前七个 div 的内容
                    combined_description_html = ''.join(div.get_attribute('outerHTML') for div in description_divs)
        
                    # 使用 BeautifulSoup 处理合并后的 HTML
                    soup = BeautifulSoup(combined_description_html, 'html.parser')
        
                    # 清理 HTML 内容
                    for tag in soup.find_all(['div', 'script'], class_=lambda x: x and 'video' in x if x else False):
                        tag.decompose()
        
                    # 获取清理后的 HTML 结构
                    description = str(soup)
                    print("找到备用的描述")
                else:
                    print("未找到有效的描述元素")
            except Exception:
                print("处理备用选项时发生错误")
        
        if not description:
            print("未能提取到描述，设置描述为空")
        
        # 抓取选项
        attr = []
        
        # 抓取颜色选项
        color_buttons_container = driver.find_elements(By.XPATH, '//*[@id="variation_color_name"]/ul/li')
        
        if color_buttons_container:
            color_attr = {'name': 'color', 'value': []}
            existing_colors = set()  # 用于存储已存在的颜色名称
            
            for idx, button in enumerate(color_buttons_container):
                try:
                    # 构建完整的XPath表达式
                    color_option_xpath = f'//*[@id="color_name_{idx}"]'
                    
                    # 检查元素是否存在
                    color_button = driver.find_element(By.XPATH, color_option_xpath)
                    color_button.click()
                    time.sleep(5)
                    driver.refresh()
                    # 等待页面刷新完成
                    time.sleep(3)
                    
                    # 重新获取页面HTML内容
                    detail_text = driver.page_source
                    detail_tree = etree.HTML(detail_text)
                    
                    # 提取当前选项名和图片
                    color_name = detail_tree.xpath('//*[@id="variation_color_name"]/div/span/text()')[0].strip()
                    color_img = detail_tree.xpath('//*[@id="landingImage"]/@src')[0]
                    
                    if color_name and color_name not in existing_colors:
                        color_attr['value'].append({'v': color_name, 'img': color_img})
                        existing_colors.add(color_name)
                        print(f"已提取颜色：{color_name}")
                    else:
                        print(f"颜色 {color_name} 已存在，跳过")
                except Exception:
                    print("处理颜色选项时出错")          
            attr.append(color_attr)
            
        # 抓取尺寸选项
        # 先滚动页面，确保所有元素都加载完毕
        driver.execute_script("window.scrollTo(0, 500);")
        driver.implicitly_wait(2)
    
        # 抓取尺寸选项
        try:
            # 找到尺寸选择器并点击
            size_selector = driver.find_element(By.CSS_SELECTOR, 'span.a-button-text.a-declarative[data-csa-c-content-id="dropdown_selected_size_name"]')
            size_selector.click()
            driver.implicitly_wait(2)
        
            # 等待下拉菜单加载
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.a-popover-inner ul.a-nostyle'))
            )
            
            # 重新获取页面HTML内容
            detail_text = driver.page_source
            detail_tree = etree.HTML(detail_text)
        
            # 获取下拉菜单中的所有尺寸选项
            size_options = driver.find_elements(By.CSS_SELECTOR, '.a-popover-inner ul.a-nostyle li.a-dropdown-item')
            if size_options:
                size_attr = {'name': 'size', 'value': []}
                existing_sizes = set()  # 用于存储已存在的尺寸名称
        
                for option in size_options:
                    size_name = option.find_element(By.CSS_SELECTOR, 'a.a-dropdown-link').text.strip()
                    if size_name == "Select":
                        continue  # 跳过值为 "Select" 的选项
                    if size_name in existing_sizes:
                        print(f"尺寸 {size_name} 已存在，跳过")
                        continue
        
                    # 添加到尺寸选项列表中
                    size_attr['value'].append({'v': size_name, 'img': ''})
                    existing_sizes.add(size_name)
                    print(f"已提取尺寸：{size_name}")
        
                # 添加尺寸选项到属性列表
                attr.append(size_attr)
            else:
                print("未找到尺寸选项")
        except Exception:
            print("处理尺寸选项时出错")
        
        # 如果无法处理尺寸选项，则设置默认尺寸
        #default_sizes = ["Small", "Medium", "Large", "X-Large"]
        #default_size_attr = {'name': 'size', 'value': [{'v': size.lower(), 'img': ""} for size in default_sizes]}
        #attr.append(default_size_attr)


        # 只有当属性列表不为空时才添加到最终列表中
        #if attr:
        if description:
            updated_product_info = {
                'price': price,
                'itm_name': title,                     
                'img1': images[0],
                'img2': images[1],
                'img3': images[2],
                'img4': images[3],
                'img5': images[4],
                'img6': images[5],
                'img7': images[6],
                'img8': images[7],
                'itm_dsc': description,
                'cat_id': "2",  # 根据实际情况填写
                's_id': "2",  # 根据实际情况填写
                'attr': attr,
            }
            final_product_info_list.append(updated_product_info)

# 将数据转换为JSON格式并保存
if final_product_info_list:
    output_dir = './output'
    os.makedirs(output_dir, exist_ok=True)
    json_file_path = os.path.join(output_dir, 'product_info.json')
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(final_product_info_list, f, ensure_ascii=False, indent=4)
    print(f"产品信息已保存到 '{json_file_path}'")

# 关闭浏览器
driver.quit()