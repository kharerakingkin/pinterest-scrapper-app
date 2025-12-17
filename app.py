import streamlit as st
import os
import time
import glob
# Pastikan file scraper_logic.py ada di folder yang sama
try:
    from scraper_logic import get_preview, download_and_zip
except ImportError:
    st.error(
        "File 'scraper_logic.py' tidak ditemukan. Pastikan file tersebut ada di GitHub Anda.")

# --- CONFIG ---
st.set_page_config(page_title="PinSave - Pinterest Downloader",
                   page_icon="📌", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0f0f0f; color: white; }
    [data-testid="stImage"] img {
        border-radius: 15px; height: 300px !important; 
        object-fit: cover; transition: 0.3s; border: 1px solid #333;
    }
    div.stButton > button {
        background-color: #e60023; color: white; border-radius: 25px;
        font-weight: bold; width: 100%; border: none; height: 45px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if "pins" not in st.session_state:
    st.session_state.pins = []
if "selected" not in st.session_state:
    st.session_state.selected = []
if "zip_file" not in st.session_state:
    st.session_state.zip_file = ""

# --- SIDEBAR ---
with st.sidebar:
    st.title("📌 PinScrap")
    query = st.text_input(
        "Cari Inspirasi", placeholder="Misal: Coffee Aesthetic")
    limit = st.number_input("Batas Jumlah Gambar",
                            min_value=1, max_value=100, value=30)

    # Update: Menggunakan width='stretch' sesuai peringatan terbaru
    if st.button("Cari Sekarang", width='stretch'):
        if query:
            with st.spinner("Sedang mencari..."):
                res = get_preview(query, limit)
                if isinstance(res, list) and len(res) > 0:
                    st.session_state.pins = res
                    st.session_state.selected = []
                    st.session_state.zip_file = ""
                    st.rerun()
                else:
                    st.error("Gagal mengambil gambar.")

# --- KONTEN UTAMA ---
if st.session_state.pins:
    col_info, col_action = st.columns([3, 1])

    with col_info:
        st.subheader(f"Hasil: `{query if query else 'Pencarian'}`")

    with col_action:
        if st.session_state.zip_file:
            path = os.path.join("downloaded_images", st.session_state.zip_file)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    # Update: Menggunakan width='stretch'
                    st.download_button(
                        "⬇️ DOWNLOAD ZIP", f, st.session_state.zip_file, width='stretch')
        else:
            txt = f"📦 BUAT ZIP ({len(st.session_state.selected)})"
            if st.button(txt, disabled=len(st.session_state.selected) == 0, width='stretch'):
                zip_name = download_and_zip(st.session_state.selected, query)
                st.session_state.zip_file = zip_name
                st.rerun()

    st.write("---")
    cols = st.columns(4)
    for i, url in enumerate(st.session_state.pins):
        with cols[i % 4]:
            # Update: Menggunakan width='stretch' untuk gambar
            st.image(url, width='stretch')
            is_sel = st.checkbox(f"Pilih #{i+1}", key=f"p_{i}")
            if is_sel:
                if url not in st.session_state.selected:
                    st.session_state.selected.append(url)
            else:
                if url in st.session_state.selected:
                    st.session_state.selected.remove(url)
