import streamlit as st
import os
from scraper_logic import get_preview, download_and_zip

st.set_page_config(page_title="Office PinSave", page_icon="📌", layout="wide")

# Tema Profesional
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { background-color: #e60023; color: white; border-radius: 8px; font-weight: bold; border:none; }
    [data-testid="stImage"] img { border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

if "pins" not in st.session_state:
    st.session_state.pins = []
if "selected" not in st.session_state:
    st.session_state.selected = set()
if "zip_file" not in st.session_state:
    st.session_state.zip_file = ""

# Sidebar
with st.sidebar:
    st.title("📌 Office Scrapper")
    st.info("Gunakan aplikasi ini untuk riset desain tim.")
    search_q = st.text_input("Cari Inspirasi")
    limit = st.number_input("Jumlah Gambar", 5, 100, 20)

    if st.button("Cari Sekarang", use_container_width=True):
        if search_q:
            with st.spinner("Mengambil data..."):
                res = get_preview(search_q, limit)
                if isinstance(res, list):
                    st.session_state.pins = res
                    st.session_state.selected = set()
                    st.session_state.zip_file = ""
                    st.rerun()
                else:
                    st.error(res)

# Main Dashboard
if st.session_state.pins:
    c1, c2 = st.columns([3, 1])
    with c1:
        st.subheader(f"Hasil Riset: {search_q}")
    with c2:
        if st.session_state.zip_file:
            with open(os.path.join("downloaded_images", st.session_state.zip_file), "rb") as f:
                st.download_button("⬇️ DOWNLOAD SEMUA (ZIP)", f,
                                   st.session_state.zip_file, use_container_width=True)
        else:
            if st.button(f"📦 Buat ZIP ({len(st.session_state.selected)})", disabled=not st.session_state.selected, use_container_width=True):
                fname = download_and_zip(
                    list(st.session_state.selected), search_q)
                st.session_state.zip_file = fname
                st.rerun()

    st.divider()
    grid = st.columns(4)
    for i, url in enumerate(st.session_state.pins):
        with grid[i % 4]:
            st.image(url)
            if st.checkbox("Pilih", key=f"sel_{url}"):
                st.session_state.selected.add(url)
            else:
                st.session_state.selected.discard(url)
else:
    st.write("### 👋 Selamat datang! Masukkan kata kunci di kiri.")
