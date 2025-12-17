import streamlit as st
import os
import sys

# Menambahkan folder saat ini ke path agar modul lokal terbaca
sys.path.append(os.path.dirname(__file__))

try:
    from scraper_logic import get_preview, download_and_zip
except ImportError as e:
    st.error(f"Gagal mengimpor file: {e}")
    st.stop()

st.set_page_config(page_title="PinSave Pro - Local Mode",
                   page_icon="📌", layout="wide")

# UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #0f0f0f; color: white; }
    [data-testid="stImage"] img { border-radius: 15px; height: 350px !important; object-fit: cover; }
    .stButton>button { background-color: #e60023; color: white; border-radius: 20px; width: 100%; }
    </style>
""", unsafe_allow_html=True)

if "pins" not in st.session_state:
    st.session_state.pins = []
if "selected" not in st.session_state:
    st.session_state.selected = set()
if "zip_ready" not in st.session_state:
    st.session_state.zip_ready = ""

with st.sidebar:
    st.title("📌 PinSave Hybrid")
    query = st.text_input("Cari Inspirasi")
    limit = st.number_input("Limit Gambar", 1, 100, 20)

    if st.button("Cari Sekarang"):
        if query:
            with st.spinner("Browser sedang men-scroll Pinterest..."):
                res = get_preview(query, limit)
                if res:
                    st.session_state.pins = res
                    st.session_state.selected = set()
                    st.session_state.zip_ready = ""
                    st.rerun()
                else:
                    st.error("Tidak ditemukan gambar.")

if st.session_state.pins:
    col_t, col_b = st.columns([3, 1])
    with col_t:
        st.subheader(f"Hasil: {query}")
    with col_b:
        if st.session_state.zip_ready:
            with open(os.path.join("downloaded_images", st.session_state.zip_ready), "rb") as f:
                st.download_button("⬇️ DOWNLOAD ZIP", f,
                                   st.session_state.zip_ready)
        else:
            if st.button(f"📦 ZIP ({len(st.session_state.selected)})", disabled=not st.session_state.selected):
                fname = download_and_zip(
                    list(st.session_state.selected), query)
                st.session_state.zip_ready = fname
                st.rerun()

    st.divider()
    grid = st.columns(4)
    for i, url in enumerate(st.session_state.pins):
        with grid[i % 4]:
            st.image(url)
            if st.checkbox(f"Pilih #{i+1}", key=f"p_{i}"):
                st.session_state.selected.add(url)
            else:
                st.session_state.selected.discard(url)
