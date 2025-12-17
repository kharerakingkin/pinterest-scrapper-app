import requests
import re
import os
import zipfile
from uuid import uuid4


def get_preview(query, limit):
    """Mencari URL gambar secara global di seluruh kode sumber Pinterest"""
    # Gunakan URL mobile atau desktop secara bergantian jika masih gagal
    url = f"https://www.pinterest.com/search/pins/?q={query.replace(' ', '%20')}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return f"Pinterest memblokir akses (Status {response.status_code})"

        html_content = response.text

        # Mencari semua link yang mengarah ke i.pinimg.com (server gambar Pinterest)
        # Kami mencari format originals, 736x, dan 474x
        img_patterns = [
            r'https://i\.pinimg\.com/originals/[a-zA-Z0-9/_\-]+\.(?:jpg|png|webp)',
            r'https://i\.pinimg\.com/736x/[a-zA-Z0-9/_\-]+\.(?:jpg|png|webp)'
        ]

        all_found = []
        for pattern in img_patterns:
            matches = re.findall(pattern, html_content)
            all_found.extend(matches)

        # Membersihkan duplikat dan menghapus gambar profil (biasanya berukuran kecil/khusus)
        unique_images = []
        for link in all_found:
            if link not in unique_images and "user" not in link.lower():
                unique_images.append(link)

        return unique_images[:limit]

    except Exception as e:
        return f"Error: {str(e)}"


def download_and_zip(urls, query):
    if not os.path.exists("downloaded_images"):
        os.makedirs("downloaded_images")

    zip_filename = f"{query.replace(' ', '_')}_{uuid4().hex[:6]}.zip"
    zip_path = os.path.join("downloaded_images", zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for i, url in enumerate(urls):
            try:
                # Kadang URL mengandung karakter backslash dari JSON, kita bersihkan
                clean_url = url.replace('\\', '')
                res = requests.get(clean_url, timeout=10)
                if res.status_code == 200:
                    ext = clean_url.split('.')[-1].split('?')[0]
                    zip_file.writestr(f"pin_{i+1}.{ext}", res.content)
            except:
                continue
    return zip_filename
