import streamlit as st
import os
from scraper_logic import get_preview, download_and_zip

st.set_page_config(page_title="PinSave Pro", page_icon="📌", layout="wide")

# UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #0e0e0e; color: white; }
    [data-testid="stImage"] img { border-radius: 15px; border: 1px solid #444; object-fit: cover; height: 320px !important; }
    .stButton>button { background-color: #e60023; color: white; border-radius: 20px; font-weight: bold; width: 100%; border:none; }
    .stButton>button:hover { background-color: #ad001a; border:none; color:white; }
    </style>
""", unsafe_allow_html=True)

# State Management
if "pins" not in st.session_state:
    st.session_state.pins = []
if "selected" not in st.session_state:
    st.session_state.selected = set()
if "zip_ready" not in st.session_state:
    st.session_state.zip_ready = ""

# Sidebar
with st.sidebar:
    st.title("📌 PinSave")
    search_query = st.text_input(
        "Kata Kunci", placeholder="Contoh: Aesthetic Room")
    num_images = st.number_input("Jumlah", 1, 100, 20)

    if st.button("Cari"):
        if search_query:
            with st.spinner("Mengambil gambar..."):
                results = get_preview(search_query, num_images)
                if isinstance(results, list) and len(results) > 0:
                    st.session_state.pins = results
                    st.session_state.selected = set()
                    st.session_state.zip_ready = ""
                    st.rerun()
                else:
                    st.error(results if isinstance(
                        results, str) else "Hasil kosong.")

# Main UI
if st.session_state.pins:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Hasil: {search_query}")
    with col2:
        if st.session_state.zip_ready:
            with open(os.path.join("downloaded_images", st.session_state.zip_ready), "rb") as f:
                st.download_button("⬇️ Download ZIP", f,
                                   st.session_state.zip_ready)
            if st.button("🔄 Reset"):
                st.session_state.zip_ready = ""
                st.rerun()
        else:
            if st.button(f"📦 ZIP ({len(st.session_state.selected)})", disabled=not st.session_state.selected):
                fname = download_and_zip(
                    list(st.session_state.selected), search_query)
                st.session_state.zip_ready = fname
                st.rerun()

    st.divider()
    grid = st.columns(4)
    for i, url in enumerate(st.session_state.pins):
        with grid[i % 4]:
            st.image(url)
            if st.checkbox("Pilih", key=f"select_{url}"):
                st.session_state.selected.add(url)
            else:
                st.session_state.selected.discard(url)
else:
    st.info("Silakan masukkan kata kunci di sidebar.")
