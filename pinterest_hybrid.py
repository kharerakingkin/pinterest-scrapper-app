import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def get_pinterest_images(query, limit=20):
    print(f"🔍 Mencari inspirasi untuk: {query}...")

    # 1. KONFIGURASI BROWSER (CHROME)
    chrome_options = Options()
    # Hapus baris di bawah jika ingin melihat browser bekerja secara visual
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=chrome_options)

    urls = []
    try:
        search_url = f"https://www.pinterest.com/search/pins/?q={query.replace(' ', '%20')}"
        driver.get(search_url)
        time.sleep(5)  # Tunggu halaman loading awal

        # 2. LOGIKA SCROLLING (Agar gambar muncul banyak)
        last_height = driver.execute_script(
            "return document.body.scrollHeight")
        while len(urls) < limit:
            # Ambil semua elemen gambar
            img_elements = driver.find_elements(By.TAG_NAME, "img")
            for img in img_elements:
                src = img.get_attribute("src")
                if src and "i.pinimg.com" in src:
                    # Ubah URL ke kualitas original (736x atau originals)
                    high_res = src.replace(
                        "236x", "736x").replace("474x", "736x")
                    if high_res not in urls:
                        urls.append(high_res)

                if len(urls) >= limit:
                    break

            # Scroll ke bawah untuk memicu lazy loading
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Tunggu gambar baru dimuat

            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break  # Berhenti jika sudah tidak ada gambar baru
            last_height = new_height

    finally:
        driver.quit()

    return urls


def download_images(image_list, folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    print(f"📥 Mengunduh {len(image_list)} gambar ke folder '{folder_name}'...")
    for i, url in enumerate(image_list):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(f"{folder_name}/pin_{i+1}.jpg", "wb") as f:
                    f.write(response.content)
        except Exception as e:
            print(f"❌ Gagal unduh gambar {i+1}: {e}")


# --- JALANKAN PROGRAM ---
if __name__ == "__main__":
    keyword = input("Masukkan kata kunci pencarian: ")
    jumlah = int(input("Berapa banyak gambar yang ingin diambil? "))

    hasil_urls = get_pinterest_images(keyword, jumlah)

    if hasil_urls:
        download_images(hasil_urls, f"hasil_{keyword}")
        print("✅ Selesai! Cek folder hasil pencarian Anda.")
    else:
        print("❌ Tidak ada gambar yang ditemukan.")
