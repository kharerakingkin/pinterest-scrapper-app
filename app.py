import streamlit as st
import os
import time
import glob
from scraper_logic import get_preview, download_and_zip

# --- CONFIG ---
st.set_page_config(page_title="PinSave - Pinterest Downloader",
                   page_icon="📌", layout="wide")

# --- CLEANUP (Menghapus file ZIP lama setiap kali aplikasi dijalankan) ---


def cleanup():
    path = "downloaded_images"
    if os.path.exists(path):
        for f in glob.glob(os.path.join(path, "*.zip")):
            # Hapus jika file lebih tua dari 1 jam
            if time.time() - os.path.getmtime(f) > 3600:
                try:
                    os.remove(f)
                except:
                    pass


cleanup()

# --- CUSTOM CSS (Tema Dark Pinterest) ---
st.markdown("""
    <style>
    .stApp { background-color: #0f0f0f; color: white; }
    [data-testid="stImage"] img {
        border-radius: 15px; height: 300px !important; 
        object-fit: cover; transition: 0.3s ease; border: 1px solid #333;
    }
    [data-testid="stImage"] img:hover { 
        transform: scale(1.02); 
        border-color: #e60023; 
        box-shadow: 0 10px 20px rgba(230, 0, 35, 0.2);
    }
    div.stButton > button {
        background-color: #e60023; color: white; border-radius: 25px;
        font-weight: bold; width: 100%; border: none; height: 45px;
    }
    div.stButton > button:hover { background-color: #ad001a; color: white; border: none; }
    .sidebar-title { color: #e60023; font-weight: 800; font-size: 24px; text-align: center; }
    .stCheckbox { background: rgba(255,255,255,0.05); padding: 8px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE (Penyimpanan Data Sesi) ---
if "pins" not in st.session_state:
    st.session_state.pins = []
if "selected" not in st.session_state:
    st.session_state.selected = []
if "zip_file" not in st.session_state:
    st.session_state.zip_file = ""

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<p class="sidebar-title">📌 PinSave</p>',
                unsafe_allow_html=True)
    st.write("---")
    query = st.text_input(
        "Cari Inspirasi", placeholder="Misal: Minimalist Interior")
    # Menggunakan number_input sebagai pengganti slide
    limit = st.number_input("Batas Jumlah Gambar",
                            min_value=1, max_value=100, value=30)

    if st.button("Cari Sekarang"):
        if query:
            with st.spinner("Sedang mencari..."):
                res = get_preview(query, limit)
                if isinstance(res, list) and len(res) > 0:
                    st.session_state.pins = res
                    st.session_state.selected = []  # Reset pilihan setiap cari baru
                    st.session_state.zip_file = ""
                    st.rerun()
                else:
                    st.error("Gagal mengambil gambar. Coba kata kunci lain.")
        else:
            st.warning("Masukkan kata kunci!")

# --- KONTEN UTAMA ---
if st.session_state.pins:
    col_info, col_action = st.columns([3, 1])

    with col_info:
        st.markdown(f"### Hasil: `{query if query else 'Pencarian'}`")
        st.write(f"Terpilih: **{len(st.session_state.selected)}** gambar")

    with col_action:
        # Logika tombol ZIP dan Download
        if st.session_state.zip_file:
            path = os.path.join("downloaded_images", st.session_state.zip_file)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    st.download_button(
                        "⬇️ DOWNLOAD ZIP", f, st.session_state.zip_file, use_container_width=True)
                if st.button("🔄 Cari Baru"):
                    st.session_state.zip_file = ""
                    st.rerun()
        else:
            txt = f"📦 BUAT ZIP ({len(st.session_state.selected)})"
            if st.button(txt, disabled=len(st.session_state.selected) == 0):
                with st.spinner("Mengompres file..."):
                    zip_name = download_and_zip(
                        st.session_state.selected, query)
                    st.session_state.zip_file = zip_name
                    st.rerun()

    st.write("---")

    # GRID GAMBAR 4 KOLOM
    cols = st.columns(4)
    for i, url in enumerate(st.session_state.pins):
        with cols[i % 4]:
            st.image(url, use_container_width=True)
            # Checkbox untuk memilih gambar mana yang mau di-ZIP
            is_sel = st.checkbox(f"Pilih #{i+1}", key=f"p_{i}")
            if is_sel:
                if url not in st.session_state.selected:
                    st.session_state.selected.append(url)
            else:
                if url in st.session_state.selected:
                    st.session_state.selected.remove(url)
else:
    # Tampilan awal saat belum mencari
    st.markdown("<br><br><div style='text-align: center'><h1>📌</h1><h2>Siap mencari inspirasi?</h2><p>Masukkan kata kunci di sidebar sebelah kiri.</p></div>", unsafe_allow_html=True)
