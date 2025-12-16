import streamlit as st
import os
from scraper_logic import get_preview, download_and_zip

# --- Setup Dasar & Tema ---
st.set_page_config(page_title="Pinterest Downloader", page_icon="📌", layout="wide")

# CSS Kustom untuk Animasi Smoot & UI Rapi
st.markdown(
    """
    <style>
    /* 1. LATAR BELAKANG APLIKASI */
    .stApp {
        background-color: #00000;
        background-attachment: fixed;
    }
    
    /* 2. Animasi Fade-In & Slide-Up untuk Kontainer */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Terapkan animasi pada setiap kolom gambar */
    [data-testid="stVerticalBlock"] > div {
        animation: fadeInUp 0.6s ease-out;
    }

    /* 3. Styling Grid Gambar */
    [data-testid="stImage"] img {
        border-radius: 12px;
        height: 250px !important;
        object-fit: cover;
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease; /* Transisi halus saat hover */
    }

    /* Efek Zoom Halus saat Mouse di atas Gambar */
    [data-testid="stImage"] img:hover {
        transform: scale(1.03);
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
        cursor: pointer;
    }

    /* 4. Styling Tombol (Pinterest Red) */
    div.stButton > button {
        background-color: #e60023;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        height: 45px;
        width: 100%;
        transition: background-color 0.3s ease;
    }

    div.stButton > button:hover {
        background-color: #ad001a;
        border: none;
        color: white;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #000000;
    }
    
    .sidebar-title {
        color: #e60023;
        font-weight: 800;
        font-size: 20px;
        margin-bottom: 20px;
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

# --- Sidebar ---
with st.sidebar:
    st.markdown(
        '<p class="sidebar-title">📌 Pinterest Scrapper</p>', unsafe_allow_html=True
    )
    st.write("Temukan inspirasi dan unduh koleksinya secara instan.")
    st.write("---")

    query = st.text_input("Kata Kunci", placeholder="Ketik topik di sini...")
    limit = st.number_input("Jumlah Gambar", min_value=1, value=20, step=1)

    if st.button("Cari Referensi"):
        if query:
            st.session_state.zip_ready = False
            st.session_state.zip_filename = ""

            with st.spinner("Sedang mencari gambar..."):
                res = get_preview(query, limit)
                if isinstance(res, list):
                    st.session_state.pins = res
                    st.session_state.last_query = query
                    st.rerun()
                else:
                    st.error("Gagal mengambil gambar.")
        else:
            st.warning("Silakan isi kata kunci!")

# --- Konten Utama ---
if st.session_state.pins:
    # Header Hasil
    head_col, action_col = st.columns([3, 1.2])

    with head_col:
        st.write(
            f"Menampilkan **{len(st.session_state.pins)}** hasil untuk: **{st.session_state.last_query}**"
        )

    with action_col:
        button_placeholder = st.empty()

        if st.session_state.zip_ready:
            zip_path = os.path.join("downloaded_images", st.session_state.zip_filename)
            if os.path.exists(zip_path):
                with open(zip_path, "rb") as f:
                    button_placeholder.download_button(
                        label="⬇️ Download File ZIP",
                        data=f,
                        file_name=st.session_state.zip_filename,
                        mime="application/zip",
                        use_container_width=True,
                    )
        else:
            if button_placeholder.button("📦 Buat File ZIP", use_container_width=True):
                with st.spinner("Mengompres file..."):
                    filename = download_and_zip(
                        st.session_state.pins, st.session_state.last_query
                    )
                    st.session_state.zip_ready = True
                    st.session_state.zip_filename = filename
                    st.rerun()

    st.write("---")

    # Grid Gambar dengan Animasi Per Kolom
    cols = st.columns(4)
    for i, url in enumerate(st.session_state.pins):
        with cols[i % 4]:
            # Container div tambahan untuk membantu animasi (opsional dalam Streamlit)
            st.image(url, use_container_width=True)
            st.caption(f"Ref #{i+1}")

else:
    st.write("### 👋 Cari Aja Pake ini")
    st.info("Masukkan kata kunci di sidebar untuk memuat preview gambar.")
    st.write("---")
