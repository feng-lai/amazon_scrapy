import os
import re
import requests
import pandas as pd
from tqdm import tqdm
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# 配置
url = 'https://img.maiiepay.com/globalmai/upload'
headers = {}  # 不需要设置Content-Type，因为我们将使用multipart/form-data

# 创建本地图片目录
os.makedirs('./local_images', exist_ok=True)

# 读取JSON文件
df = pd.read_json('product_info.json')

# 定义函数来下载图片
def download_image(url, local_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_path, 'wb') as file:
            file.write(response.content)
        return True
    else:
        print(f"Failed to download image from {url}")
        return False

# 定义函数来上传图片
def upload_image(file_path):
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, files=files)
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and 'src' in result['data'] and 'img' in result['data']:
                return result['data']['src'], result['data']['img']
            else:
                print(f"Unexpected response from server: {response.text}")
                return None, None
        else:
            print(f"Failed to upload image from {file_path}")
            return None, None

# 定义函数来处理商品详情中的图片链接
def process_item_description(description):
    # 使用正则表达式提取图片链接
    img_pattern = re.compile(r"https?://[^\s]+?\.(?:png|jpg|gif|css|svg)")
    ban = ["pixel", "inlinePlayer"]
    img_urls = img_pattern.findall(description)
    
    # 打印提取的图片链接
    print(f"Extracted image URLs: {img_urls}")

    # 过滤图片链接
    filtered = [img_url for img_url in img_urls if not any(keyword in img_url for keyword in ban) and not img_url.endswith(('.css', '.svg'))]

    # 删除特定的 CSS 样式
    description = description.replace("font-family:Amazon Ember!important;", "")
    description = description.replace("font-family:Amazon Ember;", "")
    description = description.replace("data-src", "src")
    description = description.replace("padding-left", "")
    
    


    href_pattern = re.compile(r'href="[^"]+"')
    description = href_pattern.sub('', description)
    
    # 替换图片链接
    for img_url in img_urls:
        # 如果链接是无效的或包含禁止的关键词，或者是.css或.svg文件，则删除它
        if not urlparse(img_url).scheme or any(keyword in img_url for keyword in ban) or img_url.endswith(('.css', '.svg')):
            print(f"Removing invalid or banned URL: {img_url}")
            description = description.replace(img_url, "")
        elif img_url in filtered:
            # 下载图片
            local_image_path = os.path.join('./local_images', os.path.basename(img_url))
            if download_image(img_url, local_image_path):
                # 上传图片
                new_img_url, _ = upload_image(local_image_path)
                if new_img_url:
                    # 替换原链接
                    description = description.replace(img_url, new_img_url)
                    print(f"Updated image in description: {new_img_url}")

    return description

# 处理每一条记录
for index, row in tqdm(df.iterrows(), total=len(df), desc='Processing images'):
    # 处理 img1 到 img8
    for img_col in [f'img{i}' for i in range(1, 9)]:
        img_url = row[img_col]
        if img_url and img_url != '':
            # 将转义的 \ 转换为普通 /
            img_url = img_url.replace('\\/', '/')
            if not urlparse(img_url).scheme:
                print(f"Invalid URL: {img_url}")
                continue
            # 下载图片
            local_image_path = os.path.join('./local_images', os.path.basename(img_url))
            if download_image(img_url, local_image_path):
                # 上传图片
                _, new_img_url = upload_image(local_image_path)
                if new_img_url:
                    df.at[index, img_col] = new_img_url
                    print(f"Updated {img_col} for row {index}: {new_img_url}")

    # 处理 attr 中的颜色选项图片链接
    if 'attr' in row and isinstance(row['attr'], list):
        for attr in row['attr']:
            if attr.get('name') == 'color' and 'value' in attr and isinstance(attr['value'], list):
                for color_option in attr['value']:
                    if 'img' in color_option and color_option['img']:
                        img_url = color_option['img']
                        if img_url and img_url != '':
                            # 将转义的 \ 转换为普通 /
                            img_url = img_url.replace('\\/', '/')
                            if not urlparse(img_url).scheme:
                                print(f"Invalid URL: {img_url}")
                                continue
                            # 下载图片
                            local_image_path = os.path.join('./local_images', os.path.basename(img_url))
                            if download_image(img_url, local_image_path):
                                # 上传图片
                                _, new_img_url = upload_image(local_image_path)
                                if new_img_url:
                                    color_option['img'] = new_img_url
                                    print(f"Updated color option image for row {index}: {new_img_url}")

    # 处理商品详情中的图片链接
    if 'itm_dsc' in row and row['itm_dsc']:
        updated_description = process_item_description(row['itm_dsc'])
        df.at[index, 'itm_dsc'] = updated_description

# 保存更新后的JSON文件
df.to_json('updated_product_info.json', orient='records')
print(f"Updated JSON file saved to {'updated_product_info.json'}")