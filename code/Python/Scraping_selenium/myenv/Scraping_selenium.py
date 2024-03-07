from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService

# Set the path to your chromedriver executable
chrome_driver_path = 'chromedriver-linux64/chromedriver'

# Start the WebDriver
chrome_service = ChromeService(chrome_driver_path)
driver = webdriver.Chrome(service=chrome_service)

# Navigate to the website
url = 'https://www.selcobw.com'
driver.get(url)

# Extract all the links
links = driver.find_elements_by_tag_name('a')

# Print the links
for link in links:
    href = link.get_attribute('href')
    if href:
        print(href)

# Close the WebDriver
driver.quit()
