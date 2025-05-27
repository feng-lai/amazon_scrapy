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

# 输入的商品链接
product_link = 'https://www.amazon.com/GNEPH-Seamless-Underwear-Invisible-8026-L2Flower-M/dp/B09JBM9X15/ref=sr_1_6?dib=eyJ2IjoiMSJ9.u_mnlj2Bpkm7k1ZBZy8H8Ozl7zw97sNJOcrYcC7lqUTkTCjFxmH46uZdVeJA1pG__CRNW6iwkbuouo5ko6E8biI_C_jj7MjE3C1xZp1d1NY.xtbK4Nz_D-yPqNzlAxwsLaiScKeuAzoIOMn5B9ACpY4&dib_tag=se&m=A3E1929Y5GMA9F&marketplaceID=ATVPDKIKX0DER&qid=1732001628&s=merchant-items&sr=1-6'

# 访问商品页面
driver.get(product_link)
time.sleep(3)

# 获取页面HTML内容
text = driver.page_source
# 解析HTML
tree = etree.HTML(text)

# XPath表达式//*[@id="corePrice_desktop"]/div/table/tbody/tr/td[2]/span[1]/span[1]/span[2]
title_xpath = '//*[@id="productTitle"]/text()'
price_xpath = '//*[@id="corePrice_desktop"]/div/table/tbody/tr/td[2]/span[1]/span[1]/text()'
alternative_price_xpath = '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[1]/text()'
alternative_price_xpath_2 = '//*[@id="corePrice_desktop"]/div/table/tbody/tr/td[2]/span[1]/span[1]/span[2]/text()'

# 抓取数据
title = tree.xpath(title_xpath)
price = tree.xpath(price_xpath)

# 如果原始XPath没有找到价格，则尝试备用XPath
if not price:
    price = tree.xpath(alternative_price_xpath)
    if not price:
        price = tree.xpath(alternative_price_xpath_2)
    
# 清洗价格数据，仅保留数字部分
cleaned_price = price[0].strip().replace('$', '') if price else ''
# 输出结果以检查
print("Title:", title[0].strip() if title else "No title found")
print("Cleaned Price:", cleaned_price)

# 构建商品信息字典
product_info = {
    'price': cleaned_price,
    'itm_name': title[0].strip(),
    'cat_id': "2",  # 根据实际情况填写
    's_id': "2",  # 根据实际情况填写
    'link': product_link
}

# 抓取图片
images = []

# 主图
main_image = tree.xpath('//*[@id="landingImage"]/@src')
if main_image:
    images.append(main_image[0])
else:
    images.append('')

# 查找所有额外图片按钮
image_buttons = tree.xpath('//*[@id="altImages"]/ul/li')
if image_buttons:
    for idx, button in enumerate(image_buttons):
        # 构建完整的XPath表达式
        image_option_xpath = f'//*[@id="altImages"]/ul/li[{idx + 1}]/span'
        
        # 检查元素是否存在
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

description = ""
try:
    # 等待描述元素加载
    description_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='aplus']/div"))
    )
    time.sleep(3)
    
    # 检查描述元素是否存在
    if description_div:
        # 获取前七个 div 元素
        description_divs = driver.find_elements(By.XPATH, "//*[@id='aplus']/div/div[position() <= 7]")
        
        # 合并前七个 div 的内容
        combined_description_html = ''.join(div.get_attribute('outerHTML') for div in description_divs)
        
        # 使用 BeautifulSoup 处理合并后的 HTML
        soup = BeautifulSoup(combined_description_html, 'html.parser')
        
        # 删除所有包含 "video" 类或样式的 div 标签
        for div_tag in soup.find_all('div', class_=lambda x: x and 'video' in x if x else False):
            div_tag.decompose()
        
        # 删除所有 script 标签
        for script_tag in soup.find_all('script'):
            script_tag.decompose()
        
        # 获取更新后的 HTML 结构
        description = str(soup)
    else:
        description = ""
        print("描述元素未找到，设置描述为空")
except (NoSuchElementException, TimeoutException):
    description = ""
    print("未能提取到描述，设置描述为空")
    
# 抓取选项
attr = []

# 抓取颜色选项
color_buttons = tree.xpath('//*[@id="variation_color_name"]/ul/li')
if color_buttons:
    color_attr = {'name': 'color', 'value': []}
    existing_colors = set()  # 用于存储已存在的颜色名称
    for idx, button in enumerate(color_buttons):
        # 构建完整的XPath表达式
        color_option_xpath = f'//*[@id="variation_color_name"]/ul/li[{idx + 1}]'
        
        # 检查元素是否存在
        try:
            color_button = driver.find_element(By.XPATH, color_option_xpath)
            color_button.click()
            time.sleep(3)
            driver.refresh()
            # 等待页面刷新完成
            time.sleep(5)
            
            # 重新获取页面HTML内容
            detail_text = driver.page_source
            detail_tree = etree.HTML(detail_text)
            
            # 提取当前选项名和图片
            color_name = detail_tree.xpath('//*[@id="variation_color_name"]/div/span/text()')[0].strip()
            color_img = detail_tree.xpath('//*[@id="landingImage"]/@src')[0]
            if color_name not in existing_colors:
                if color_name:
                    color_attr['value'].append({'v': color_name, 'img': color_img})
                    existing_colors.add(color_name)
                    print(f"已提取颜色：{color_name}")
                else:
                    print(f"颜色 {color_name} 已存在，跳过")
        except Exception as e:
            print(f"处理颜色选项时出错: {e}")
    
    # 如果颜色列表不为空，则添加到属性列表中
    if color_attr['value']:
        attr.append(color_attr)
else:
    print("未找到颜色选项")

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
        default_sizes = ["Small", "Medium", "Large", "X-Large"]
        default_size_attr = {'name': 'size', 'value': [{'v': size.lower(), 'img': ""} for size in default_sizes]}
        attr.append(default_size_attr)
except Exception as e:
    print(f"处理尺寸选项时出错")
    # 如果无法处理尺寸选项，则设置默认尺寸
    default_sizes = ["Small", "Medium", "Large", "X-Large"]
    default_size_attr = {'name': 'size', 'value': [{'v': size.lower(), 'img': ""} for size in default_sizes]}
    attr.append(default_size_attr)

# 更新商品信息
product_info.update({
    'img1': images[0],
    'img2': images[1],
    'img3': images[2],
    'img4': images[3],
    'img5': images[4],
    'img6': images[5],
    'img7': images[6],
    'img8': images[7],
    'itm_dsc': description,
    'attr': attr,
})

# 将数据转换为JSON格式并保存
output_dir = './output'
os.makedirs(output_dir, exist_ok=True)
json_file_path = os.path.join(output_dir, 'product_info.json')
with open(json_file_path, 'w', encoding='utf-8') as f:
    json.dump([product_info], f, ensure_ascii=False, indent=4)
print(f"产品信息已保存到 '{json_file_path}'")

# 关闭浏览器
driver.quit()