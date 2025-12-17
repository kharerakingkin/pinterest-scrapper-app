import requests
import os
import zipfile
import re
from uuid import uuid4


def get_preview(query, limit):
    """Mengambil URL gambar dari Pinterest menggunakan pencarian publik"""
    # Header untuk mengelabui Pinterest agar menganggap kita browser asli
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.pinterest.com/"
    }

    search_url = f"https://www.pinterest.com/search/pins/?q={query.replace(' ', '%20')}"

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"Error: Status {response.status_code}"

        # Mencari URL gambar beresolusi tinggi menggunakan Regex
        # Pinterest menyimpan data gambar dalam format JSON di dalam HTML
        html = response.text
        image_urls = re.findall(
            r'https://i\.pinimg\.com/originals/[a-z0-9/]+\.(?:jpg|png|webp)', html)

        # Jika tidak ketemu originals, coba cari yang resolusi 736x
        if not image_urls:
            image_urls = re.findall(
                r'https://i\.pinimg\.com/736x/[a-z0-9/]+\.(?:jpg|png|webp)', html)

        # Menghapus duplikat dan membatasi jumlah
        unique_urls = list(dict.fromkeys(image_urls))
        return unique_urls[:limit]

    except Exception as e:
        return f"Terjadi kesalahan: {str(e)}"


def download_and_zip(urls, query):
    """Mengunduh gambar yang dipilih dan mengompresnya ke dalam ZIP"""
    folder_name = "downloaded_images"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    zip_id = f"{query.replace(' ', '_')}_{uuid4().hex[:6]}.zip"
    zip_path = os.path.join(folder_name, zip_id)

    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for i, url in enumerate(urls):
            try:
                img_data = requests.get(url, timeout=10).content
                ext = url.split('.')[-1]
                filename = f"image_{i+1}.{ext}"

                # Simpan sementara dan masukkan ke ZIP
                temp_path = os.path.join(folder_name, filename)
                with open(temp_path, 'wb') as f:
                    f.write(img_data)

                zip_file.write(temp_path, filename)
                os.remove(temp_path)  # Hapus file mentah setelah masuk ZIP
            except:
                continue

    return zip_id
