"""Dashboard Utama COVID-19.

Menampilkan overview statistik COVID-19 Indonesia:
- Metric cards (Total Kasus, Kematian, Sembuh, Aktif)
- Mini chart trend
- Feature cards navigasi
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

import utils
import ui


def tampilkan_dashboard_utama(current_stats: dict, df_historical: pd.DataFrame):
    """Tampilkan dashboard utama COVID-19."""
    
    st.title("Dashboard COVID-19 Indonesia")
    st.markdown("Analisis data COVID-19 Indonesia dengan data dari **disease.sh API**.")
    
    # Info jika menggunakan fallback data
    if current_stats.get("is_fallback"):
        ui.warning_callout(
            "Menggunakan data terakhir yang tersimpan. API mungkin sedang tidak tersedia.",
            icon="⚠️"
        )
    
    st.divider()
    
    # --- Metric Cards ---
    st.subheader("Statistik Terkini")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Kasus",
            value=utils.format_number(current_stats.get("cases", 0)),
            help="Total kasus terkonfirmasi COVID-19"
        )
    
    with col2:
        st.metric(
            label="Total Kematian",
            value=utils.format_number(current_stats.get("deaths", 0)),
            help="Total kematian akibat COVID-19"
        )
    
    with col3:
        st.metric(
            label="Total Sembuh",
            value=utils.format_number(current_stats.get("recovered", 0)),
            help="Total pasien yang sembuh"
        )
    
    with col4:
        st.metric(
            label="Kasus Aktif",
            value=utils.format_number(current_stats.get("active", 0)),
            help="Kasus yang masih aktif"
        )
    
    st.divider()
    
    # --- Key Metrics ---
    st.subheader("Metrik Kunci")
    
    col1, col2, col3, col4 = st.columns(4)
    
    cases = current_stats.get("cases", 0)
    deaths = current_stats.get("deaths", 0)
    recovered = current_stats.get("recovered", 0)
    
    cfr = utils.calculate_cfr(deaths, cases)
    recovery_rate = utils.calculate_recovery_rate(recovered, cases)
    
    with col1:
        st.metric(
            label="Case Fatality Rate",
            value=utils.format_percentage(cfr),
            help="Persentase kematian terhadap total kasus"
        )
    
    with col2:
        st.metric(
            label="Recovery Rate",
            value=utils.format_percentage(recovery_rate),
            help="Persentase kesembuhan terhadap total kasus"
        )
    
    with col3:
        st.metric(
            label="Kasus/1 Juta",
            value=utils.format_number(current_stats.get("cases_per_million", 0)),
            help="Kasus per 1 juta penduduk"
        )
    
    with col4:
        st.metric(
            label="Total Tes",
            value=utils.format_number(current_stats.get("tests", 0)),
            help="Total tes PCR yang dilakukan"
        )
    
    st.divider()
    
    # --- Trend Chart (30 hari terakhir) ---
    st.subheader("Trend 30 Hari Terakhir")
    
    if not df_historical.empty and len(df_historical) >= 30:
        df_recent = df_historical.tail(30).copy()
        
        # Chart kasus baru harian
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df_recent["Tanggal"],
            y=df_recent["Kasus_Baru"],
            name="Kasus Baru",
            marker_color="rgba(124, 58, 237, 0.7)",
        ))
        
        # Rolling average
        df_recent["Rolling_7"] = df_recent["Kasus_Baru"].rolling(window=7, min_periods=1).mean()
        
        fig.add_trace(go.Scatter(
            x=df_recent["Tanggal"],
            y=df_recent["Rolling_7"],
            name="Rata-rata 7 Hari",
            line=dict(color="rgba(220, 38, 38, 0.9)", width=2),
        ))
        
        fig.update_layout(
            title="Kasus Baru Harian",
            xaxis_title="Tanggal",
            yaxis_title="Jumlah Kasus",
            hovermode="x unified",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=40, b=0),
        )
        
        st.plotly_chart(fig, **ui.kw_plotly_chart())
    else:
        st.info("Data historis tidak tersedia atau tidak cukup untuk menampilkan trend.")
    
    st.divider()
    
    # --- Feature Cards ---
    st.subheader("Eksplorasi Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Visualisasi")
        st.markdown("Lihat grafik trend kasus, kematian, dan kesembuhan dari waktu ke waktu.")
        if ui.button("Buka Visualisasi", key="nav_visualisasi"):
            ui.request_navigation("Visualisasi COVID-19")
            st.rerun()
    
    with col2:
        st.markdown("### 🗺️ Analisis GIS")
        st.markdown("Lihat peta sebaran COVID-19 per provinsi di Indonesia.")
        if ui.button("Buka Peta", key="nav_gis"):
            ui.request_navigation("Analisis GIS")
            st.rerun()
    
    with col3:
        st.markdown("### 📈 Statistik")
        st.markdown("Analisis statistik lengkap termasuk peak, tren, dan distribusi.")
        if ui.button("Buka Statistik", key="nav_statistik"):
            ui.request_navigation("Statistik Data")
            st.rerun()
    
    # Footer info
    st.divider()
    
    updated = current_stats.get("updated")
    if updated:
        st.caption(f"Data terakhir diperbarui: {updated}")
    
    st.caption("Sumber data: disease.sh API | Data untuk tujuan edukasi")
