import streamlit as st
import os
import time
import glob
from scraper_logic import get_preview, download_and_zip

# --- Konfigurasi Dasar ---
st.set_page_config(page_title="Pinterest Downloader Pro",
                   page_icon="📌", layout="wide")

# --- Fungsi Pembersihan (Cleanup) ---


def cleanup_old_files(directory="downloaded_images", max_age_seconds=3600):
    """Menghapus file ZIP yang lebih tua dari 1 jam untuk menghemat ruang"""
    if not os.path.exists(directory):
        return

    now = time.time()
    for f in glob.glob(os.path.join(directory, "*.zip")):
        if os.stat(f).st_mtime < now - max_age_seconds:
            try:
                os.remove(f)
            except:
                pass


# Jalankan pembersihan setiap kali aplikasi di-refresh
cleanup_old_files()

# --- CSS Kustom ---
st.markdown(
    """
    <style>
    /* Latar Belakang & Font */
    .stApp {
        background-color: #0f0f0f;
        color: #ffffff;
    }
    
    /* Animasi Fade-In */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    [data-testid="stVerticalBlock"] > div {
        animation: fadeInUp 0.6s ease-out;
    }

    /* Styling Gambar */
    [data-testid="stImage"] img {
        border-radius: 15px;
        height: 300px !important;
        object-fit: cover;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid #333;
    }

    [data-testid="stImage"] img:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 20px rgba(230, 0, 35, 0.3);
    }

    /* Styling Tombol Pinterest Red */
    div.stButton > button {
        background-color: #e60023;
        color: white;
        border-radius: 25px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: 0.3s;
    }

    div.stButton > button:hover {
        background-color: #ad001a;
        transform: translateY(-2px);
    }

    /* Checkbox styling */
    .stCheckbox {
        background: rgba(255,255,255,0.05);
        padding: 5px 10px;
        border-radius: 10px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
    }
    .sidebar-title {
        color: #e60023;
        font-weight: 800;
        font-size: 24px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- State Management ---
if "pins" not in st.session_state:
    st.session_state.pins = []
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
if "zip_ready" not in st.session_state:
    st.session_state.zip_ready = False
if "zip_filename" not in st.session_state:
    st.session_state.zip_filename = ""
if "selected_urls" not in st.session_state:
    st.session_state.selected_urls = []

# --- Sidebar ---
with st.sidebar:
    st.markdown('<p class="sidebar-title">📌 PINTEREST<br>SCRAPER</p>',
                unsafe_allow_html=True)
    st.write("---")

    query = st.text_input("Apa yang ingin Anda cari?",
                          placeholder="Contoh: Cyberpunk Architecture")
    limit = st.number_input("Jumlah limit gambar",
                            min_value=1, max_value=100, value=20)

    if st.button("Cari Gambar", use_container_width=True):
        if query:
            with st.spinner("Mengambil data dari Pinterest..."):
                res = get_preview(query, limit)
                if isinstance(res, list) and len(res) > 0:
                    st.session_state.pins = res
                    st.session_state.last_query = query
                    st.session_state.selected_urls = []  # Reset seleksi
                    st.session_state.zip_ready = False
                    st.rerun()
                else:
                    st.error("Tidak ditemukan gambar atau terjadi kesalahan.")
        else:
            st.warning("Masukkan kata kunci terlebih dahulu!")

# --- Konten Utama ---
if st.session_state.pins:
    # Header & Action Bar
    col_title, col_action = st.columns([2, 1])

    with col_title:
        st.markdown(f"### Hasil untuk: `{st.session_state.last_query}`")
        st.caption(f"Klik centang pada gambar yang ingin diunduh.")

    with col_action:
        selected_count = len(st.session_state.selected_urls)

        if st.session_state.zip_ready:
            zip_path = os.path.join(
                "downloaded_images", st.session_state.zip_filename)
            if os.path.exists(zip_path):
                with open(zip_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download ZIP Sekarang",
                        data=f,
                        file_name=st.session_state.zip_filename,
                        mime="application/zip",
                        use_container_width=True
                    )
                if st.button("🔄 Reset / Cari Lagi", use_container_width=True):
                    st.session_state.zip_ready = False
                    st.rerun()
        else:
            # Tombol ZIP hanya aktif jika ada yang dipilih
            btn_label = f"📦 ZIP {selected_count} Gambar" if selected_count > 0 else "📦 Pilih Gambar"
            if st.button(btn_label, use_container_width=True, disabled=(selected_count == 0)):
                with st.spinner("Sedang memproses ZIP..."):
                    filename = download_and_zip(
                        st.session_state.selected_urls, st.session_state.last_query)
                    st.session_state.zip_ready = True
                    st.session_state.zip_filename = filename
                    st.rerun()

    st.write("---")

    # Tampilan Grid
    rows = (len(st.session_state.pins) // 4) + 1
    for r in range(rows):
        cols = st.columns(4)
        for c in range(4):
            idx = r * 4 + c
            if idx < len(st.session_state.pins):
                url = st.session_state.pins[idx]
                with cols[c]:
                    st.image(url, use_container_width=True)
                    # Checkbox untuk memilih
                    is_selected = st.checkbox(
                        f"Pilih #{idx+1}", key=f"check_{idx}")

                    # Logika update seleksi
                    if is_selected:
                        if url not in st.session_state.selected_urls:
                            st.session_state.selected_urls.append(url)
                    else:
                        if url in st.session_state.selected_urls:
                            st.session_state.selected_urls.remove(url)

else:
    # Tampilan Awal (Kosong)
    st.write("")
    st.write("")
    st.markdown(
        """
        <div style="text-align: center;">
            <h1 style="font-size: 80px;">🖼️</h1>
            <h2>Siap untuk mencari inspirasi?</h2>
            <p style="color: #888;">Gunakan kolom pencarian di sebelah kiri untuk menemukan gambar Pinterest.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
