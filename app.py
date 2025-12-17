import requests
import os
import zipfile
from uuid import uuid4


def get_preview(query, limit):
    """Mengambil banyak gambar menggunakan API internal Pinterest"""
    # Gunakan API browser-side untuk hasil lebih banyak
    url = "https://www.pinterest.com/resource/BaseSearchResource/get/"

    params = {
        "source_url": f"/search/pins/?q={query}",
        "data": '{"options":{"isPrefetch":false,"query":"' + query + '","scope":"pins","no_fetch_context_on_resource":false},"context":{}}'
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
    }

    try:
        response = requests.get(
            url, params=params, headers=headers, timeout=15)
        if response.status_code != 200:
            return f"Error API: {response.status_code}"

        data = response.json()
        items = data.get('resource_response', {}).get(
            'data', {}).get('results', [])

        image_urls = []
        for item in items:
            # Mengambil resolusi tertinggi yang tersedia (originals atau 736x)
            images = item.get('images', {})
            img_url = images.get('orig', {}).get(
                'url') or images.get('736x', {}).get('url')
            if img_url:
                image_urls.append(img_url)

        return image_urls[:limit]

    except Exception as e:
        return f"Terjadi kesalahan teknis: {str(e)}"


def download_and_zip(urls, query):
    """Proses unduh langsung ke ZIP"""
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
