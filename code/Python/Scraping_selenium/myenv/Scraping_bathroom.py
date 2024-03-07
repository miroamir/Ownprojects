import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

def scrape_product_data(driver, url, subcategory_link, data):
    subcategory_name = subcategory_link.text.strip()

    try:
        subcategory_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, subcategory_link.text))
        )
        subcategory_element.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'ProductListItem-link-3ot'))
        )
    except Exception as e:
        print(f"Error clicking on subcategory link '{subcategory_name}': {e}")
        return

    try:
        subcategory_element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, subcategory_link.text))
        )
        subcategory_element.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'ProductListItem-link-3ot'))
        )
    except TimeoutException:
        print(f"Timeout waiting for subcategory page to load for '{subcategory_name}'")
        return
    except Exception as e:
        print(f"Error clicking on subcategory link '{subcategory_name}': {e}")
        return

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    product_items = soup.find_all('a', class_='ProductListItem-link-3ot')

    for product_item in product_items:
        try:
            product_name_element = product_item.find('div', class_='ProductListItem-title-1g7')
            if not product_name_element:
                print(f"Error: Product name not found in {subcategory_name}")
                continue

            product_name = product_name_element.text.strip()
            product_url = urljoin(url, product_item['href'])

            price_div = product_item.find_next('div', class_='PriceBox-root-RD8')
            price_ex_vat_span = price_div.select_one('.PriceBox-itemExVat-skf span')
            price_ex_vat_text = (
                price_ex_vat_span.find_next('span').text.strip()
                if 'From' in price_ex_vat_span.text.strip()
                else price_ex_vat_span.text.strip()
            )
            price_ex_vat = f'From {price_ex_vat_text}' if 'From' in price_ex_vat_span.text.strip() else price_ex_vat_text

            price_inc_vat_span = price_div.select_one('.PriceBox-itemIncVat-vQr span:not(.PriceBox-priceFrom-RU4)')
            price_inc_vat = price_inc_vat_span.text.strip() if price_inc_vat_span else ' '

            image_url = product_item.find('img', class_='ProductListItem-image-SKe')['src']

            print(f"Debug: Subcategory: {subcategory_name}")
            print(f"Debug: Product Name: {product_name}")
            print(f"Debug: Price (Ex VAT): {price_ex_vat}")
            print(f"Debug: Price (Inc VAT): {price_inc_vat}")
            print(f"Debug: Image URL: {image_url}")
            print(f"Debug: Product URL: {product_url}")
            print("----------------------")

            data.append([subcategory_name, product_name, price_ex_vat, price_inc_vat, image_url, product_url])
        except AttributeError as e:
            print(f'Error: {e}')
            print(f'Information not available for a product in {subcategory_name}.')

def save_to_csv(data, csv_file_path, header):
    try:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(header)
            csv_writer.writerows(data)
        print(f'Data saved to {csv_file_path}')
    except Exception as e:
        print(f'Error saving data to CSV: {e}')

if __name__ == "__main__":
    chrome_driver_path = 'chromedriver-linux64/chromedriver'
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service)

    base_url = 'https://www.selcobw.com/products/bathrooms'
    driver.get(base_url)

    subcategory_links = driver.find_elements(By.CLASS_NAME, 'CategoryGrid-titleLink-1ZJ')

    data = []
    header = ['Subcategory', 'Product Name', 'Price (Ex VAT)', 'Price (Inc VAT)', 'Image URL', 'Product URL']

    for subcategory_link in subcategory_links:
        try:
            scrape_product_data(driver, base_url, subcategory_link, data)
        except Exception as e:
            print(f'Error processing subcategory link: {e}')

    save_to_csv(data, 'output.csv', header)

    driver.quit()
