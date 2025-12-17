import requests
import re
import os
import zipfile
from uuid import uuid4


def get_preview(query, limit):
    """Mencari URL gambar secara paksa di seluruh kode sumber Pinterest"""
    url = f"https://www.pinterest.com/search/pins/?q={query.replace(' ', '%20')}"

    # User-Agent yang sangat spesifik agar dikira browser manusia
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return f"Pinterest memblokir akses server (Status {response.status_code})"

        html_content = response.text

        # Pola untuk mencari link gambar Pinterest (resolusi 736x atau originals)
        # Pinterest menyimpan link ini dalam format string tersembunyi
        patterns = [
            r'https://i\.pinimg\.com/originals/[a-zA-Z0-9/_\-]+\.(?:jpg|png|webp)',
            r'https://i\.pinimg\.com/736x/[a-zA-Z0-9/_\-]+\.(?:jpg|png|webp)'
        ]

        all_matches = []
        for pattern in patterns:
            matches = re.findall(pattern, html_content)
            all_matches.extend(matches)

        # Bersihkan hasil (hapus duplikat dan bersihkan karakter escape jika ada)
        unique_urls = []
        for url_match in all_matches:
            # Menghapus backslash dari JSON
            clean_url = url_match.replace('\\', '')
            if clean_url not in unique_urls:
                unique_urls.append(clean_url)

        if not unique_urls:
            return "Tidak ada gambar ditemukan. Coba gunakan kata kunci dalam Bahasa Inggris (misal: 'Minimalist Interior')."

        return unique_urls[:limit]

    except Exception as e:
        return f"Terjadi kesalahan: {str(e)}"


def download_and_zip(urls, query):
    if not os.path.exists("downloaded_images"):
        os.makedirs("downloaded_images")

    zip_filename = f"{query.replace(' ', '_')}_{uuid4().hex[:6]}.zip"
    zip_path = os.path.join("downloaded_images", zip_filename)

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
