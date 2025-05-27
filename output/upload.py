import requests
import json
import time

url = 'https://img.maiiepay.com/pro_save'
headers = {'Content-Type': 'application/json'}

# 读取JSON文件
with open('updated_product_info.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 遍历每个产品信息并发送POST请求
for index, product in enumerate(data):
    # 构建要上传的JSON数据
    payload = {
        "price": product.get("price", ""),
        "itm_name": product.get("itm_name", ""),
        "img1": product.get("img1", ""),
        "img2": product.get("img2", ""),
        "img3": product.get("img3", ""),
        "img4": product.get("img4", ""),
        "img5": product.get("img5", ""),
        "img6": product.get("img6", ""),
        "img7": product.get("img7", ""),
        "img8": product.get("img8", ""),
        "itm_dsc": product.get("itm_dsc", ""),
        "cat_id": "2",
        "s_id": "2",
        "attr": product.get("attr", [])
    }
    
    # 发送POST请求
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"第 {index + 1} 个项目上传成功:")
            print(response.json())
        else:
            print(f"第 {index + 1} 个项目上传失败:")
            print(response.json())
            # 检查响应中的错误信息
            error_response = response.json()
            if 'error' in error_response:
                print(f"错误信息: {error_response['error']}")
            else:
                print(f"未知错误: {response.text}")
    except Exception as e:
        print(f"第 {index + 1} 个项目上传时发生异常: {str(e)}")
    
    # 添加延时，防止API请求频率过高
    time.sleep(1)