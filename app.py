import streamlit as st
import os
from scraper_logic import get_preview, download_and_zip

st.set_page_config(page_title="PinSave Pro", page_icon="📌", layout="wide")

# UI Fix
st.markdown("""
    <style>
    .stApp { background-color: #0e0e0e; color: white; }
    [data-testid="stImage"] img { border-radius: 12px; border: 1px solid #444; object-fit: cover; height: 350px !important; width: 100%; }
    .stButton>button { background-color: #e60023; color: white; border-radius: 20px; font-weight: bold; width: 100%; border:none; }
    </style>
""", unsafe_allow_html=True)

if "pins" not in st.session_state:
    st.session_state.pins = []
if "selected" not in st.session_state:
    st.session_state.selected = set()
if "zip_name" not in st.session_state:
    st.session_state.zip_name = ""

with st.sidebar:
    st.title("📌 PinSave")
    q = st.text_input("Cari")
    num = st.number_input("Limit", 1, 100, 30)
    if st.button("Cari Sekarang"):
        if q:
            with st.spinner("Searching..."):
                res = get_preview(q, num)
                if isinstance(res, list) and len(res) > 0:
                    st.session_state.pins = res
                    st.session_state.selected = set()
                    st.session_state.zip_name = ""
                    st.rerun()
                else:
                    st.error("Hasil masih kosong. Pinterest memblokir IP server.")

if st.session_state.pins:
    c1, c2 = st.columns([3, 1])
    with c1:
        st.subheader(f"Hasil: {q}")
    with c2:
        if st.session_state.zip_name:
            with open(os.path.join("downloaded_images", st.session_state.zip_name), "rb") as f:
                st.download_button("⬇️ Download ZIP", f,
                                   st.session_state.zip_name)
        else:
            if st.button(f"📦 ZIP ({len(st.session_state.selected)})", disabled=not st.session_state.selected):
                fname = download_and_zip(list(st.session_state.selected), q)
                st.session_state.zip_name = fname
                st.rerun()

    st.divider()
    grid = st.columns(4)
    for i, url in enumerate(st.session_state.pins):
        with grid[i % 4]:
            # Bersihkan URL untuk display
            st.image(url.replace('\\', ''))
            if st.checkbox("Pilih", key=f"s_{i}"):
                st.session_state.selected.add(url)
            else:
                st.session_state.selected.discard(url)
