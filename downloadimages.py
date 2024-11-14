import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image  # Optional: To display images

# Search query and number of images to download
query1 = "antelope"  # Change this to whatever you want to search for
query2 = "rabbit"  # Change this to whatever you want to search for
num_images = 10  # Number of images to download

# Minimum size of image to be downloaded (in bytes)
min_size = 2000

# Setup folder to save images
saved_folder = 'images'
if not os.path.exists(saved_folder):
    os.makedirs(saved_folder)
if not os.path.exists(saved_folder + f'/{query}'):
    os.makedirs(saved_folder + f'/{query}')

# Set up the Chrome WebDriver using webdriver-manager
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode (no browser window will open)
options.add_argument("--incognito")  # Use incognito mode
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def download_images(query, num_images):
    search_url = f"https://www.google.com/search?hl=en&tbm=isch&q={query}"

    # Open Google Images and perform the search
    driver.get(search_url)
    
    # Wait until the page is fully loaded
    wait = WebDriverWait(driver, 30)  # Increased wait time
    try:
        # Wait for image elements to load (broader selector)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img")))
    except Exception as e:
        print(f"Error or Timeout while waiting for images: {e}")
        driver.quit()
        return

    # Scroll to the bottom of the page to load more images
    last_height = driver.execute_script("return document.body.scrollHeight")
    images = set()  # Use a set to avoid duplicate URLs
    count = 0
    
    while count < num_images:
        # Scroll the page to load images
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for images to load
        
        # Get the updated list of image elements
        img_elements = driver.find_elements(By.CSS_SELECTOR, "img")
        
        # Extract image URLs from the 'src' or 'data-src' attributes
        for img in img_elements:
            try:
                # Sometimes the images might be in the 'data-src' attribute, not 'src'
                src = img.get_attribute("data-src") or img.get_attribute("src")
                if src:
                    images.add(src)
            except Exception as e:
                print(f"Error extracting image source: {e}")

        # If we've loaded all available images, break
        if len(images) >= num_images:
            break

        # Check for scroll height again and stop if we've reached the bottom of the page
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Download the images
    print(f"Found {len(images)} images. Starting to download...")

    # Image numbering starts from 1, and only increases for valid images
    image_number = 1

    for i, img_url in enumerate(images):
        if image_number > num_images:
            break
        try:
            # Download the image
            response = requests.get(img_url, stream=True)
            image_path = os.path.join(saved_folder + f'/{query}', f"{query}_{image_number}.jpg")

            # Save the image to the folder
            with open(image_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    if chunk:
                        f.write(chunk)
            print(f"Downloaded image {image_number}")

            # Get the size of the image in bytes
            image_size = os.path.getsize(image_path)
            print(f"Image {image_number} size: {image_size} bytes")

            # Only keep the image if its size is greater than the threshold (1000 bytes)
            if image_size < min_size:
                os.remove(image_path)  # Delete the image if it's too small
                print(f"Image {image_number} is too small. Skipping...")
            else:
                # Increment the image number if the image is valid
                image_number += 1

            # Optional: Display the image using PIL (Python Imaging Library)
            # Uncomment this if you want to display the images
            # image = Image.open(image_path)
            # image.show()

        except Exception as e:
            print(f"Error downloading image {image_number}:")

    # Close the WebDriver
    driver.quit()

# Run the function to download images
download_images(query1, num_images)
download_images(query2, num_images)
