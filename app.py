import streamlit as st
import os
from scraper_logic import get_preview, download_and_zip

# --- CONFIG ---
st.set_page_config(page_title="PinSave Pro", page_icon="📌", layout="wide")

# CSS untuk tampilan rapi
st.markdown("""
    <style>
    .stApp { background-color: #111; color: white; }
    [data-testid="stImage"] img { border-radius: 12px; height: 350px !important; object-fit: cover; border: 1px solid #333; }
    div.stButton > button { background-color: #e60023; color: white; border-radius: 20px; font-weight: bold; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- STATE ---
if "pins" not in st.session_state:
    st.session_state.pins = []
if "selected" not in st.session_state:
    st.session_state.selected = set()
if "zip_file" not in st.session_state:
    st.session_state.zip_file = ""

# --- SIDEBAR ---
with st.sidebar:
    st.title("📌 PinSave")
    query = st.text_input(
        "Cari Sesuatu", placeholder="Contoh: Wallpaper Aesthetic")
    limit = st.number_input("Jumlah", 1, 100, 20)

    if st.button("Cari Sekarang", width="stretch"):
        if query:
            with st.spinner("Mengambil data dari Pinterest..."):
                res = get_preview(query, limit)
                if isinstance(res, list) and len(res) > 0:
                    st.session_state.pins = res
                    st.session_state.selected = set()
                    st.session_state.zip_file = ""
                    st.rerun()
                else:
                    st.error(
                        "Gagal mendapatkan gambar. Pinterest mungkin membatasi akses.")

# --- MAIN ---
if st.session_state.pins:
    col_t, col_b = st.columns([3, 1])
    with col_t:
        st.subheader(f"Hasil untuk: {query}")
    with col_b:
        if st.session_state.zip_file:
            path = os.path.join("downloaded_images", st.session_state.zip_file)
            with open(path, "rb") as f:
                st.download_button("⬇️ DOWNLOAD ZIP", f,
                                   st.session_state.zip_file, width="stretch")
        else:
            if st.button(f"📦 ZIP ({len(st.session_state.selected)})", width="stretch", disabled=not st.session_state.selected):
                fname = download_and_zip(
                    list(st.session_state.selected), query)
                st.session_state.zip_file = fname
                st.rerun()

    st.divider()
    cols = st.columns(4)
    for i, url in enumerate(st.session_state.pins):
        with cols[i % 4]:
            st.image(url, width="stretch")
            # Logika seleksi yang lebih stabil
            if st.checkbox(f"Pilih #{i+1}", key=f"chk_{url}"):
                st.session_state.selected.add(url)
            else:
                st.session_state.selected.discard(url)
else:
    st.info("Gunakan sidebar untuk mencari gambar.")
