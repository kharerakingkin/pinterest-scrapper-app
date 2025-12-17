import os
import time
import requests
import zipfile
from uuid import uuid4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def get_preview(query, limit=20):
    """Menggunakan Selenium untuk men-scroll Pinterest dan mengambil URL gambar"""
    chrome_options = Options()
    # Jalankan tanpa membuka jendela browser
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Inisialisasi Driver
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=chrome_options)

    urls = []
    try:
        search_url = f"https://www.pinterest.com/search/pins/?q={query.replace(' ', '%20')}"
        driver.get(search_url)
        time.sleep(5)  # Tunggu loading awal

        last_height = driver.execute_script(
            "return document.body.scrollHeight")

        while len(urls) < limit:
            # Ambil semua tag gambar
            img_elements = driver.find_elements(By.TAG_NAME, "img")
            for img in img_elements:
                src = img.get_attribute("src")
                if src and "i.pinimg.com" in src:
                    # Ubah ke resolusi tinggi
                    high_res = src.replace(
                        "236x", "736x").replace("474x", "736x")
                    if high_res not in urls:
                        urls.append(high_res)
                if len(urls) >= limit:
                    break

            # Scroll ke bawah untuk memicu lazy loading
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    except Exception as e:
        print(f"Error Selenium: {e}")
    finally:
        driver.quit()

    return urls


def download_and_zip(urls, query):
    """Mengunduh gambar pilihan ke dalam file ZIP"""
    folder_name = "downloaded_images"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    zip_filename = f"{query.replace(' ', '_')}_{uuid4().hex[:6]}.zip"
    zip_path = os.path.join(folder_name, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for i, url in enumerate(urls):
            try:
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    ext = url.split('.')[-1].split('?')[0]
                    zip_file.writestr(f"pin_{i+1}.{ext}", res.content)
            except:
                continue

    return zip_filename
