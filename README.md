# Amazon Scraping Project Documentation

## Project Overview

This project is designed to scrape product information from Amazon, process the data, and upload it to a specified server. It includes multiple Python scripts for different functionalities such as data scraping, image processing, and data uploading. The project utilizes Selenium for web automation and BeautifulSoup for HTML parsing.

## File Descriptions

### change.py

- **Purpose**: Downloads images from specified URLs, uploads them to a server, and updates the JSON file with new image URLs.
- **Functions**:
  - Downloads images from given URLs.
  - Uploads images to a server and retrieves new URLs.
  - Updates the product information JSON file with new image URLs.
- **Dependencies**: `requests`, `pandas`, `tqdm`, `BeautifulSoup`, `os`.

### extract.py

- **Purpose**: Extracts image links from a JSON file and saves them to a text file.
- **Functions**:
  - Reads a JSON file containing product information.
  - Extracts image URLs using regular expressions.
  - Filters out unwanted URLs based on specified keywords.
  - Saves the extracted URLs to a text file.
- **Dependencies**: `json`, `re`, `os`.

### product_info.json & updated_product_info.json

- **Content**: JSON files containing product information including price, name, images, description, and attributes.
- **Structure**:
  - `price`: Product price.
  - `itm_name`: Product name.
  - `img1`-`img8`: Product image URLs.
  - `itm_dsc`: Product description in HTML format.
  - `cat_id` & `s_id`: Category and store IDs.
  - `attr`: Product attributes such as color and size options.

### shop.py

- **Purpose**: Scrapes product details from Amazon's best seller page.
- **Functions**:
  - Navigates to Amazon's best seller page.
  - Extracts product links, prices, and titles.
  - Collects detailed information including seller profile, ratings, and description.
  - Saves the data to a CSV file.
- **Dependencies**: `selenium`, `webdriver_manager`, `pandas`, `time`, `os`.

### upload.py

- **Purpose**: Uploads product information from a JSON file to a server.
- **Functions**:
  - Reads the product information JSON file.
  - Sends POST requests to the server with the product data.
  - Handles responses and errors during the upload process.
- **Dependencies**: `requests`, `json`, `time`.

### size_and_color.py & amazon_item.py & amazon_shop.py & amz.py & bag.py & no_color.py

- **Purpose**: These scripts are variations of scraping scripts designed to extract product information from different Amazon pages.
- **Common Functions**:
  - Extract product title, price, images, description, and attributes.
  - Handle color and size variations.
  - Save the extracted data to a JSON file.
- **Dependencies**: `selenium`, `webdriver_manager`, `lxml`, `BeautifulSoup`, `time`, `os`, `json`, `tqdm`.

## Deployment and Running Instructions

### Environment Setup

1. **Python Installation**: Ensure Python 3.x is installed on your system.
2. **Package Installation**: Install the required packages using pip:
   ```bash
   pip install requests pandas tqdm beautifulsoup4 selenium lxml
   ```
3. **WebDriver Setup**: Download the appropriate WebDriver for your browser (e.g., EdgeDriver for Microsoft Edge) and ensure it's in your system PATH.

### Running the Scripts

#### change.py

1. Place the script in the directory containing `product_info.json`.
2. Run the script:
   ```bash
   python change.py
   ```
3. The script will create an `updated_product_info.json` file with new image URLs.

#### extract.py

1. Place the script in the directory containing the JSON file to extract links from.
2. Run the script:
   ```bash
   python extract.py
   ```
3. Specify the input JSON file and output text file as command-line arguments.

#### shop.py

1. Update the target URL in the script if necessary.
2. Run the script:
   ```bash
   python shop.py
   ```
3. The script will generate a CSV file with the scraped data.

#### upload.py

1. Ensure the `updated_product_info.json` file is in the same directory.
2. Update the upload URL and headers in the script if necessary.
3. Run the script:
   ```bash
   python upload.py
   ```

#### Other Scraping Scripts (size_and_color.py, amazon_item.py, etc.)

1. Update the target product link in the script.
2. Run the script:
   ```bash
   python script_name.py
   ```
3. The script will generate a JSON file with the scraped product information.

## Notes

- Some scripts use hard-coded URLs and XPaths which may need to be updated if the target website structure changes.
- The scripts assume that the necessary browsers and drivers are installed and configured properly.
- Be mindful of Amazon's terms of service and robots.txt when scraping data.
- Handle the data responsibly and in compliance with applicable laws and regulations.

