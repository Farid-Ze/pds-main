"""
COVID-19 Dashboard Indonesia
============================
Aplikasi Streamlit untuk analisis data COVID-19 Indonesia.
Data diambil dari disease.sh API.
"""

import streamlit as st
import sys
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Load environment variables dari .env
try:
    from dotenv import load_dotenv
    load_dotenv(str(Path(__file__).resolve().parents[1] / ".env"))
except Exception:
    pass

# Add src directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modul-modul yang telah dipisah
import utils
import styles
import ui
import api_client
import dashboard_utama
import visualisasi_covid
import analisa_gis
import statistik_data
import database_covid
import trend_vaksinasi
import kalkulator_risiko

# Konfigurasi halaman
st.set_page_config(
    page_title="COVID-19 Dashboard Indonesia",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data(ttl=60 * 60, show_spinner=False)
def _load_historical_cached():
    """Load data historis dengan cache untuk mengurangi latency & rerun."""
    return api_client.get_historical_df()


@st.cache_data(ttl=60 * 5, show_spinner=False)
def _load_current_cached():
    """Load data current dengan cache 5 menit."""
    return api_client.get_current_stats()


@st.cache_data(ttl=60 * 60, show_spinner=False)
def _load_province_cached():
    """Load data provinsi (simulasi) dengan cache."""
    stats = _load_current_cached()
    total_cases = stats.get("cases", 6800000)
    return api_client.generate_province_simulation(total_cases)


def main():
    """
    Fungsi utama aplikasi Streamlit
    """
    # Deep-link: izinkan URL mengatur halaman yang aktif (sekali per session)
    ui.sync_state_from_url(
        "app",
        keys=["app_page"],
    )

    # Theme: gunakan fitur bawaan Streamlit (Choose app theme).
    st.markdown(styles.get_custom_css(), unsafe_allow_html=True)

    st.sidebar.title("COVID-19 Indonesia")
    st.sidebar.caption("Dashboard analisis data COVID-19 Indonesia dengan data dari disease.sh API.")

    # --- Navigasi terkelompok (HCI: information architecture lebih jelas) ---
    pages_by_group = {
        "Data COVID-19": [
            "Dashboard Utama",
            "Visualisasi COVID-19",
            "Analisis GIS",
            "Statistik Data",
            "Database COVID-19",
        ],
        "Vaksinasi": [
            "Trend Vaksinasi",
        ],
        "Alat": [
            "Kalkulator Risiko",
        ],
    }

    # --- Navigasi aman ---
    pending_page = st.session_state.pop("_app_page_pending", None)
    if isinstance(pending_page, str) and pending_page.strip():
        wanted = pending_page.strip()
        all_pages = {p for group_pages in pages_by_group.values() for p in group_pages}
        if wanted in all_pages:
            st.session_state["app_page"] = wanted

    # Sinkronkan group default dari page aktif
    current_page = st.session_state.get("app_page")
    current_group = None
    for g, opts in pages_by_group.items():
        if current_page in opts:
            current_group = g
            break
    if current_group is None:
        current_group = "Data COVID-19"

    # Pastikan state nav_group valid
    try:
        if st.session_state.get("nav_group") not in pages_by_group:
            st.session_state["nav_group"] = current_group
    except Exception:
        st.session_state["nav_group"] = current_group

    nav_group = st.sidebar.selectbox(
        "Kategori",
        options=list(pages_by_group.keys()),
        index=list(pages_by_group.keys()).index(current_group),
        key="nav_group",
    )

    if not isinstance(nav_group, str):
        nav_group = current_group

    # Pastikan app_page valid terhadap group yang dipilih
    if st.session_state.get("app_page") not in pages_by_group[nav_group]:
        st.session_state["app_page"] = pages_by_group[nav_group][0]

    current_in_group = st.session_state.get("app_page")
    if not isinstance(current_in_group, str):
        current_in_group = pages_by_group[nav_group][0]
    try:
        nav_index = pages_by_group[nav_group].index(current_in_group)
    except Exception:
        nav_index = 0

    halaman = st.sidebar.radio(
        "Navigasi",
        pages_by_group[nav_group],
        index=nav_index,
        key="app_page",
    )

    # Load data dengan spinner
    with st.spinner("Memuat data COVID-19..."):
        df_historical = _load_historical_cached()
        current_stats = _load_current_cached()
        df_province = _load_province_cached()

    # Routing ke halaman yang sesuai
    if halaman == "Dashboard Utama":
        dashboard_utama.tampilkan_dashboard_utama(current_stats, df_historical)

    elif halaman == "Visualisasi COVID-19":
        visualisasi_covid.tampilkan_visualisasi_covid(df_historical)

    elif halaman == "Analisis GIS":
        analisa_gis.tampilkan_analisa_gis(df_province)

    elif halaman == "Statistik Data":
        statistik_data.tampilkan_statistik_data(df_historical, current_stats)

    elif halaman == "Database COVID-19":
        database_covid.tampilkan_database_covid(df_historical)

    elif halaman == "Trend Vaksinasi":
        trend_vaksinasi.tampilkan_trend_vaksinasi()

    elif halaman == "Kalkulator Risiko":
        kalkulator_risiko.tampilkan_kalkulator_risiko(current_stats)


if __name__ == "__main__":
    main()
