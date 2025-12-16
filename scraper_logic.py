import time, requests, os, zipfile, shutil, urllib.parse, re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor


def get_preview(query, max_images):
    search_query_encoded = urllib.parse.quote_plus(query)
    query_url = f"https://id.pinterest.com/search/pins/?q={search_query_encoded}"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(query_url)
        time.sleep(5)

        image_urls = set()
        for _ in range(10):
            imgs = driver.find_elements(By.TAG_NAME, "img")
            for img in imgs:
                src = img.get_attribute("src")
                if src and "236x" in src:
                    image_urls.add(src)
                if len(image_urls) >= max_images:
                    break

            driver.execute_script("window.scrollBy(0, 1500);")
            time.sleep(1.5)
            if len(image_urls) >= max_images:
                break

        driver.quit()
        return list(image_urls)[:max_images]
    except Exception as e:
        if "driver" in locals():
            driver.quit()
        return f"Error: {str(e)}"


def download_and_zip(image_urls, query):
    safe_name = (
        re.sub(r'[\\/*?:"<>|]', "", query)[:30].strip().replace(" ", "_").lower()
    )
    if not safe_name:
        safe_name = "pins"

    save_folder = os.path.join("downloaded_images", safe_name)
    os.makedirs(save_folder, exist_ok=True)

    def fetch(idx_url):
        idx, url = idx_url
        orig = url.replace("236x", "originals")
        try:
            r = requests.get(orig, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code != 200:
                r = requests.get(url, timeout=10)
            with open(os.path.join(save_folder, f"pin_{idx+1}.jpg"), "wb") as f:
                f.write(r.content)
        except:
            pass

    with ThreadPoolExecutor(max_workers=10) as ex:
        list(ex.map(fetch, enumerate(image_urls)))

    zip_name = f"{safe_name}.zip"
    zip_path = os.path.join("downloaded_images", zip_name)
    with zipfile.ZipFile(zip_path, "w") as z:
        for f in os.listdir(save_folder):
            z.write(os.path.join(save_folder, f), f)

    shutil.rmtree(save_folder)
    return zip_name
