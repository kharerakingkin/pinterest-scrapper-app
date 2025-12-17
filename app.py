import streamlit as st
import os
import time
import glob
from scraper_logic import get_preview, download_and_zip

# --- Konfigurasi Dasar ---
st.set_page_config(page_title="Pinterest Downloader Pro",
                   page_icon="📌", layout="wide")

# --- Fungsi Pembersihan ---


def cleanup_old_files(directory="downloaded_images", max_age_seconds=3600):
    if not os.path.exists(directory):
        os.makedirs(directory)
        return
    now = time.time()
    for f in glob.glob(os.path.join(directory, "*.zip")):
        if os.stat(f).st_mtime < now - max_age_seconds:
            try:
                os.remove(f)
            except:
                pass


cleanup_old_files()

# --- CSS Modern ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    [data-testid="stImage"] img {
        border-radius: 12px; height: 280px !important; 
        object-fit: cover; transition: 0.3s; border: 1px solid #333;
    }
    [data-testid="stImage"] img:hover { transform: scale(1.03); border-color: #e60023; }
    div.stButton > button {
        background-color: #e60023; color: white; border-radius: 20px;
        font-weight: bold; width: 100%; border: none;
    }
    div.stButton > button:hover { background-color: #ad001a; border: none; color: white; }
    .sidebar-title { color: #e60023; font-weight: 800; font-size: 22px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- State Management ---
for key in ["pins", "last_query", "zip_ready", "zip_filename", "selected_urls"]:
    if key not in st.session_state:
        st.session_state[key] = [] if "urls" in key or "pins" in key else ""
if "zip_ready" not in st.session_state:
    st.session_state.zip_ready = False

# --- Sidebar ---
with st.sidebar:
    st.markdown('<p class="sidebar-title">📌 PINTEREST SCRAPER</p>',
                unsafe_allow_html=True)
    query = st.text_input("Cari Inspirasi", placeholder="Ketik sesuatu...")
    limit = st.number_input("Jumlah Gambar", 1, 100, 20)

    if st.button("Cari Sekarang"):
        if query:
            with st.spinner("Mencari..."):
                res = get_preview(query, limit)
                if isinstance(res, list) and len(res) > 0:
                    st.session_state.pins = res
                    st.session_state.last_query = query
                    st.session_state.selected_urls = []
                    st.session_state.zip_ready = False
                    st.rerun()
                else:
                    st.error(
                        f"Gagal: {res if isinstance(res, str) else 'Data kosong'}")
        else:
            st.warning("Isi kata kunci!")

# --- Konten Utama ---
if st.session_state.pins:
    col_t, col_b = st.columns([3, 1])
    with col_t:
        st.markdown(f"### Hasil untuk: `{st.session_state.last_query}`")
    with col_b:
        count = len(st.session_state.selected_urls)
        if st.session_state.zip_ready:
            zip_p = os.path.join("downloaded_images",
                                 st.session_state.zip_filename)
            if os.path.exists(zip_p):
                with open(zip_p, "rb") as f:
                    st.download_button(
                        "⬇️ Download ZIP", f, st.session_state.zip_filename, "application/zip")
                if st.button("🔄 Cari Lagi"):
                    st.session_state.zip_ready = False
                    st.rerun()
        else:
            if st.button(f"📦 ZIP {count} Gambar", disabled=(count == 0)):
                with st.spinner("Zipping..."):
                    fname = download_and_zip(
                        st.session_state.selected_urls, st.session_state.last_query)
                    st.session_state.zip_ready = True
                    st.session_state.zip_filename = fname
                    st.rerun()

    st.divider()
    cols = st.columns(4)
    for idx, url in enumerate(st.session_state.pins):
        with cols[idx % 4]:
            st.image(url, use_container_width=True)
            if st.checkbox(f"Pilih #{idx+1}", key=f"c_{idx}"):
                if url not in st.session_state.selected_urls:
                    st.session_state.selected_urls.append(url)
            else:
                if url in st.session_state.selected_urls:
                    st.session_state.selected_urls.remove(url)
else:
    st.markdown("<br><br><div style='text-align: center'><h1>🔍</h1><h3>Cari gambar di sidebar untuk memulai</h3></div>", unsafe_allow_html=True)
