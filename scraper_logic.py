import requests
import json
import os
import zipfile
from uuid import uuid4


def get_preview(query, limit):
    """Mengekstraksi URL gambar dari blok data JSON di dalam HTML"""
    url = f"https://www.pinterest.com/search/pins/?q={query.replace(' ', '%20')}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return f"Error: Pinterest menolak akses (Status {response.status_code})"

        # Mencari data JSON di dalam tag <script id="__PWS_DATA__">
        content = response.text
        start_marker = '<script id="__PWS_DATA__" type="application/json">'
        end_marker = '</script>'

        if start_marker in content:
            json_str = content.split(start_marker)[1].split(end_marker)[0]
            data = json.loads(json_str)

            # Menelusuri struktur JSON Pinterest yang kompleks
            pins = []
            try:
                # Mencari pin di dalam search results
                results = data['props']['initialReduxState']['pins']
                for pin_id in results:
                    pin_data = results[pin_id]
                    # Ambil resolusi original atau 736x
                    img_url = pin_data.get('images', {}).get(
                        'orig', {}).get('url')
                    if not img_url:
                        img_url = pin_data.get('images', {}).get(
                            '736x', {}).get('url')

                    if img_url and img_url not in pins:
                        pins.append(img_url)
            except KeyError:
                pass

            return pins[:limit]

        return "Gagal mengekstraksi data. Coba lagi dalam beberapa saat."

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