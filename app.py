import streamlit as st
import os
import time
import glob
from scraper_logic import get_preview, download_and_zip

# --- CONFIG ---
st.set_page_config(page_title="PinSave - Pinterest Downloader",
                   page_icon="📌", layout="wide")

# --- CLEANUP OLD ZIPS ---


def cleanup():
    path = "downloaded_images"
    if os.path.exists(path):
        for f in glob.glob(os.path.join(path, "*.zip")):
            if time.time() - os.path.getmtime(f) > 3600:  # Hapus jika > 1 jam
                os.remove(f)


cleanup()

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    [data-testid="stImage"] img {
        border-radius: 15px; height: 320px !important; 
        object-fit: cover; transition: 0.4s; border: 1px solid #333;
    }
    [data-testid="stImage"] img:hover { transform: scale(1.02); border-color: #e60023; }
    div.stButton > button {
        background-color: #e60023; color: white; border-radius: 30px;
        font-weight: bold; width: 100%; border: none; height: 50px;
    }
    div.stButton > button:hover { background-color: #ad001a; color: white; }
    .stCheckbox { background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; }
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
    st.title("📌 PinSave")
    query = st.text_input("Cari Gambar", placeholder="Misal: Coffee Aesthetic")
    limit = st.slider("Jumlah Maksimal", 5, 100, 30)

    if st.button("Cari Gambar"):
        if query:
            with st.spinner("Mencari inspirasi..."):
                res = get_preview(query, limit)
                if isinstance(res, list) and len(res) > 0:
                    st.session_state.pins = res
                    st.session_state.selected = []
                    st.session_state.zip_file = ""
                    st.rerun()
                else:
                    st.error("Tidak ditemukan hasil. Coba kata kunci lain.")
        else:
            st.warning("Masukkan teks pencarian!")

# --- MAIN CONTENT ---
if st.session_state.pins:
    col_head, col_btn = st.columns([3, 1])

    with col_head:
        st.subheader(f"Hasil untuk: {query if query else 'Pencarian'}")
        st.write(f"Terpilih: **{len(st.session_state.selected)}** gambar")

    with col_btn:
        if st.session_state.zip_file:
            path = os.path.join("downloaded_images", st.session_state.zip_file)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    st.download_button(
                        "⬇️ DOWNLOAD ZIP", f, st.session_state.zip_file, use_container_width=True)
                if st.button("🔄 Reset"):
                    st.session_state.zip_file = ""
                    st.rerun()
        else:
            btn_txt = f"📦 BUAT ZIP ({len(st.session_state.selected)})"
            if st.button(btn_txt, disabled=len(st.session_state.selected) == 0):
                with st.spinner("Mengompres..."):
                    zip_name = download_and_zip(
                        st.session_state.selected, query)
                    st.session_state.zip_file = zip_name
                    st.rerun()

    st.divider()

    # GRID DISPLAY
    cols = st.columns(4)
    for i, url in enumerate(st.session_state.pins):
        with cols[i % 4]:
            st.image(url, use_container_width=True)
            # Sync selection
            is_sel = st.checkbox(f"Pilih #{i+1}", key=f"pin_{i}")
            if is_sel:
                if url not in st.session_state.selected:
                    st.session_state.selected.append(url)
            else:
                if url in st.session_state.selected:
                    st.session_state.selected.remove(url)
else:
    st.markdown("<br><br><center><h1>🔍</h1><h3>Gunakan sidebar untuk mencari gambar</h3></center>",
                unsafe_allow_html=True)
