import requests
import json
import os
import zipfile
from uuid import uuid4


def get_preview(query, limit):
    """Mencari gambar via Pinterest Internal Data (Tanpa Selenium)"""
    # Mencoba akses via URL pencarian dengan User-Agent modern
    url = f"https://www.pinterest.com/search/pins/?q={query.replace(' ', '%20')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return f"Pinterest Error (Status {response.status_code})"

        # Ekstraksi JSON dari tag script __PWS_DATA__
        content = response.text
        start_marker = '<script id="__PWS_DATA__" type="application/json">'
        end_marker = '</script>'

        if start_marker in content:
            json_str = content.split(start_marker)[1].split(end_marker)[0]
            data = json.loads(json_str)

            pins_data = data.get('props', {}).get(
                'initialReduxState', {}).get('pins', {})

            image_urls = []
            for pin_id in pins_data:
                images = pins_data[pin_id].get('images', {})
                # Utamakan resolusi original atau 736x
                img_url = images.get('orig', {}).get(
                    'url') or images.get('736x', {}).get('url')
                if img_url and img_url not in image_urls:
                    image_urls.append(img_url)

            if not image_urls:
                return "Tidak ada gambar ditemukan. Pinterest mungkin memperbarui sistemnya."

            return image_urls[:limit]

        return "Gagal mengekstraksi data. Coba lagi atau ganti kata kunci."

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
