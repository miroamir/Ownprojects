import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin

def extract_subcategory_links(driver, category_url):
    try:
        driver.get(category_url)

        category_grid = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.CategoryGrid-root-2G6"))
        )

        subcategory_links = category_grid.find_elements(By.TAG_NAME, "a")
        subcategory_hrefs = [link.get_attribute("href") for link in subcategory_links]
        print("Subcategory Links:", subcategory_hrefs)

        return subcategory_hrefs

    except Exception as e:
        print(f"An error occurred while extracting subcategory links for {category_url}: {e}")
        print("Page HTML content:", driver.page_source)
        return []

def extract_product_data(driver, category_url, csv_writer, processed_links):
    try:
        subcategory_hrefs = extract_subcategory_links(driver, category_url)

        for subcategory_href in subcategory_hrefs:
            if subcategory_href not in processed_links:
                process_product_link(driver, subcategory_href, category_url, csv_writer)
                processed_links.add(subcategory_href)

    except Exception as e:
        print(f"An error occurred while processing category {category_url}: {e}")
        import traceback
        traceback.print_exc()

def process_product_link(driver, link, category_url, csv_writer):
    base_url = 'https://www.selcobw.com'
    full_url = urljoin(base_url, link)

    print(f"Processing link: {full_url}")

    try:
        driver.get(full_url)

        print("Waiting for the page to load...")
        WebDriverWait(driver, 20).until(
            lambda x: x.execute_script("return document.readyState === 'complete'")
        )
        print("Page loaded, continuing...")

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        subcategories = soup.find_all('a', class_='SideNav-sideNavLink-RDv')

        if subcategories:
            for subcategory in subcategories:
                subcategory_link = subcategory['href']
                process_product_link(driver, subcategory_link, category_url, csv_writer)
        else:
            product_items = soup.find_all('a', class_='ProductListItem-link-3ot')

            data = []
            category = category_url.split('/')[-1]
            counter = 0

            for product_item in product_items:
                counter += 1
                print(counter)
                extract_and_append_product_data(product_item, category, data)

            data.sort(key=lambda x: (x[0], x[1]))

            csv_writer.writerows(data)

            driver.back()
            time.sleep(2)

    except Exception as e:
        print(f"An error occurred while processing link {full_url}: {e}")
        import traceback
        traceback.print_exc()

    print(f"Finished processing link: {full_url}")

def extract_and_append_product_data(product_item, category, data):
    product_name = product_item.text.strip()
    print(product_name)
    product_url = 'https://www.selcobw.com' + product_item['href']

    price_div = product_item.find_next('div', class_='PriceBox-root-RD8')
    price_ex_vat_span = price_div.select_one('.PriceBox-itemExVat-skf span')

    subcategory_div = product_item.find_previous('div', class_='TwoCol-hasLeft-3uX ul li:nth-child(3)')

    price_ex_vat_text = (
        price_ex_vat_span.find_next('span').text.strip()
        if 'From' in price_ex_vat_span.text.strip()
        else price_ex_vat_span.text.strip()
    )
    price_ex_vat = (
        f'From {price_ex_vat_text}'
        if 'From' in price_ex_vat_span.text.strip()
        else price_ex_vat_text
    )

    price_inc_vat_span = price_div.select_one('.PriceBox-itemIncVat-vQr span:not(.PriceBox-priceFrom-RU4)')
    price_inc_vat = price_inc_vat_span.text.strip() if price_inc_vat_span else ' '

    image_url = product_item.find_previous('img', class_='ProductListItem-image-SKe')['src']

    subcategory = subcategory_div.text.strip() if subcategory_div else ' '

    data.append([category, subcategory, product_name, price_ex_vat, price_inc_vat, image_url, product_url])

def main():
    chrome_path = 'chromedriver-linux64/chromedriver'
    service = Service(executable_path=chrome_path)
    chrome_options = webdriver.ChromeOptions()

    csv_file_path = 'product_data.csv'

    categories = ['https://www.selcobw.com/products/bathrooms', 'https://www.selcobw.com/products/kitchens', 'https://www.selcobw.com/products/flooring-tiling', 'https://www.selcobw.com/products/flooring-tiling/tiling', 'https://www.selcobw.com/products/flooring-tiling/tile-adhesives-grouts', 'https://www.selcobw.com/products/flooring-tiling/floor-levelling-compounds', 'https://www.selcobw.com/products/flooring-tiling/flooring-adhesives', 'https://www.selcobw.com/products/building-materials/bricks-blocks', 'https://www.selcobw.com/products/building-materials/aggregates', 'https://www.selcobw.com/products/roofing', 'https://www.selcobw.com/products/plaster-drylining', 'https://www.selcobw.com/products/insulation', 'https://www.selcobw.com/products/plastics-drainage', 'https://www.selcobw.com/products/building-materials/cement', 'https://www.selcobw.com/products/building-materials/builders-metalwork', 'https://www.selcobw.com/products/building-materials/lintels', 'https://www.selcobw.com/products/building-materials/cladding', 'https://www.selcobw.com/products/building-materials/weather-waterproofing', 'https://www.selcobw.com/products/building-materials/render', 'https://www.selcobw.com/products/building-materials/floor-levelling-compounds', 'https://www.selcobw.com/products/building-materials/building-sealants', 'https://www.selcobw.com/products/timber-mdf-sheet-materials/treated-timber', 'https://www.selcobw.com/products/timber-mdf-sheet-materials/sheet-materials', 'https://www.selcobw.com/products/timber-mdf-sheet-materials/sawn-timber', 'https://www.selcobw.com/products/doors-windows-stairs', 'https://www.selcobw.com/products/timber-mdf-sheet-materials/planed-timber', 'https://www.selcobw.com/products/timber-mdf-sheet-materials/skirting-architrave', 'https://www.selcobw.com/products/timber-mdf-sheet-materials/cls-timber', 'https://www.selcobw.com/products/timber-mdf-sheet-materials/cladding', 'https://www.selcobw.com/products/timber-mdf-sheet-materials/timber-boards', 'https://www.selcobw.com/products/timber-mdf-sheet-materials/mouldings', 'https://www.selcobw.com/products/timber-mdf-sheet-materials/floorboards', 'https://www.selcobw.com/products/timber-mdf-sheet-materials/melamine-faced-chipboard', 'https://www.selcobw.com/products/timber-mdf-sheet-materials/window-board', 'https://www.selcobw.com/products/timber-mdf-sheet-materials/wall-panelling', 'https://www.selcobw.com/products/landscaping-fencing/fencing',
                  'https://www.selcobw.com/products/landscaping-fencing/paving', 'https://www.selcobw.com/products/landscaping-fencing/decking', 'https://www.selcobw.com/products/landscaping-fencing/aggregates', 'https://www.selcobw.com/products/landscaping-fencing/sleepers-boards', 'https://www.selcobw.com/products/landscaping-fencing/driveways', 'https://www.selcobw.com/products/plastics-drainage/drainage', 'https://www.selcobw.com/products/landscaping-fencing/groundwork-landscaping', 'https://www.selcobw.com/products/landscaping-fencing/artificial-grass', 'https://www.selcobw.com/products/landscaping-fencing/landscaping-fabrics', 'https://www.selcobw.com/products/landscaping-fencing/walling', 'https://www.selcobw.com/products/landscaping-fencing/paving-care', 'https://www.selcobw.com/products/landscaping-fencing/wood-care', 'https://www.selcobw.com/products/landscaping-fencing/commercial-paving', 'https://www.selcobw.com/products/landscaping-fencing/external-lighting',
                  'https://www.selcobw.com/products/plumbing-heating/wastes-pipework', 'https://www.selcobw.com/products/plumbing-heating/heating', 'https://www.selcobw.com/products/plumbing-heating/plumbing', 'https://www.selcobw.com/products/plumbing-heating/copper-pipe-fittings', 'https://www.selcobw.com/products/plumbing-heating/taps', 'https://www.selcobw.com/products/plumbing-heating/vents-ducting', 'https://www.selcobw.com/products/plumbing-heating/plumbing-tools', 'https://www.selcobw.com/products/safety-wear-clothing', 'https://www.selcobw.com/products/hand-power-tools/power-tools', 'https://www.selcobw.com/products/hand-power-tools/hand-tools', 'https://www.selcobw.com/products/builders-equipment-cleaning', 'https://www.selcobw.com/products/hand-power-tools/power-tool-accessories', 'https://www.selcobw.com/products/hand-power-tools/tool-storage', 'https://www.selcobw.com/products/painting-decorating/paint', 'https://www.selcobw.com/products/painting-decorating/decorators-tools', 'https://www.selcobw.com/products/painting-decorating/wood-care', 'https://www.selcobw.com/products/painting-decorating/protection', 'https://www.selcobw.com/products/painting-decorating/fillers', 'https://www.selcobw.com/products/painting-decorating/wallpaper', 'https://www.selcobw.com/products/painting-decorating/sand-paper-abrasives', 'https://www.selcobw.com/products/painting-decorating/masking-tapes', 'https://www.selcobw.com/products/painting-decorating/paint-remover-brush-cleaner', 'https://www.selcobw.com/products/painting-decorating/cleaning-solutions',
                  'https://www.selcobw.com/products/electrical-lighting-ventilation', 'https://www.selcobw.com/products/electrical-lighting-ventilation/lighting', 'https://www.selcobw.com/products/electrical-lighting-ventilation/ventilation', 'https://www.selcobw.com/products/door-furniture-ironmongery-locks/door-furniture', 'https://www.selcobw.com/products/door-furniture-ironmongery-locks/ironmongery', 'https://www.selcobw.com/products/door-furniture-ironmongery-locks/security', 'https://www.selcobw.com/products/door-furniture-ironmongery-locks/hinges', 'https://www.selcobw.com/products/screws-nails-fixings/screws', 'https://www.selcobw.com/products/sealants-adhesives', 'https://www.selcobw.com/products/screws-nails-fixings/fixings', 'https://www.selcobw.com/products/screws-nails-fixings/nails-pins']

    with open(csv_file_path, 'a+', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)

        driver = webdriver.Chrome(service=service, options=chrome_options)

        processed_links = set()

        for category_url in categories:
            extract_product_data(driver, category_url, csv_writer, processed_links)

        driver.quit()

if __name__ == "__main__":
    main()
