import requests
import re
import os
import zipfile
from uuid import uuid4


def get_preview(query, limit):
    """Mengambil banyak URL gambar dengan pola Regex yang luas"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://www.pinterest.com/"
    }

    # Format URL pencarian agar hasil lebih maksimal
    search_url = f"https://www.pinterest.com/search/pins/?q={query.replace(' ', '%20')}&rs=typed"

    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        if response.status_code != 200:
            return f"Error: Pinterest menolak akses (Status {response.status_code})"

        html = response.text

        # Mencari semua pola URL gambar Pinterest (Original, 736x, 474x)
        patterns = [
            r'https://i\.pinimg\.com/originals/[a-z0-9/]+\.(?:jpg|png|webp)',
            r'https://i\.pinimg\.com/736x/[a-z0-9/]+\.(?:jpg|png|webp)',
            r'https://i\.pinimg\.com/474x/[a-z0-9/]+\.(?:jpg|png|webp)'
        ]

        found_urls = []
        for pattern in patterns:
            found_urls.extend(re.findall(pattern, html))

        # Menghapus duplikat sambil menjaga urutan asli
        unique_urls = []
        for url in found_urls:
            if url not in unique_urls:
                unique_urls.append(url)

        # Cadangan jika pola spesifik gagal
        if not unique_urls:
            unique_urls = re.findall(
                r'https://i\.pinimg\.com/[a-z0-9//]+\.jpg', html)

        return unique_urls[:limit]

    except Exception as e:
        return f"Terjadi kesalahan: {str(e)}"


def download_and_zip(urls, query):
    """Proses unduh gambar langsung ke memori ZIP tanpa menyimpan file sampah"""
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
                    ext = url.split('.')[-1]
                    # Membersihkan parameter URL jika ada (seperti .jpg?v=123)
                    ext = ext.split('?')[0]
                    img_name = f"pin_{i+1}.{ext}"
                    zip_file.writestr(img_name, res.content)
            except:
                continue

    return zip_filename
