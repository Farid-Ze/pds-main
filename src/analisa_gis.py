"""Analisis GIS COVID-19.

Menampilkan peta Indonesia dengan data per provinsi:
- Scatter map dengan warna berdasarkan tingkat kasus
- Tooltip informasi detail
- Toggle untuk berbagai metrik

CATATAN: Data per provinsi adalah SIMULASI untuk tujuan edukasi.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import utils
import ui


def tampilkan_analisa_gis(df_province: pd.DataFrame):
    """Tampilkan halaman analisis GIS."""
    
    st.title("Analisis GIS COVID-19")
    st.markdown("Peta sebaran COVID-19 per provinsi di Indonesia.")
    
    # Warning tentang data simulasi
    ui.warning_callout(
        "Data per provinsi adalah **SIMULASI** untuk tujuan demonstrasi dan edukasi. "
        "Data riil per provinsi tidak tersedia dari API publik.",
        icon="⚠️"
    )
    
    if df_province.empty:
        st.warning("Data provinsi tidak tersedia.")
        return
    
    st.divider()
    
    # --- Controls ---
    col1, col2 = st.columns([0.7, 0.3])
    
    with col1:
        metric = st.radio(
            "Metrik yang Ditampilkan",
            options=["Kasus", "Kasus_per_100K", "Kematian", "Aktif"],
            format_func=lambda x: {
                "Kasus": "Total Kasus",
                "Kasus_per_100K": "Kasus per 100K Penduduk",
                "Kematian": "Total Kematian",
                "Aktif": "Kasus Aktif",
            }.get(x, x),
            horizontal=True,
            key="gis_metric"
        )
    
    with col2:
        basemap_style = st.selectbox(
            "Gaya Peta",
            options=["open-street-map", "carto-positron", "carto-darkmatter"],
            format_func=lambda x: {
                "open-street-map": "OpenStreetMap",
                "carto-positron": "Terang",
                "carto-darkmatter": "Gelap",
            }.get(x, x),
            key="gis_basemap"
        )
    
    st.divider()
    
    # --- Map ---
    st.subheader("Peta Sebaran COVID-19")
    
    # Prepare hover text
    df_province["hover_text"] = df_province.apply(
        lambda row: (
            f"<b>{row['Provinsi']}</b><br>"
            f"Kasus: {utils.format_number(row['Kasus'])}<br>"
            f"Kematian: {utils.format_number(row['Kematian'])}<br>"
            f"Sembuh: {utils.format_number(row['Sembuh'])}<br>"
            f"Aktif: {utils.format_number(row['Aktif'])}<br>"
            f"Kasus/100K: {row['Kasus_per_100K']}"
        ),
        axis=1
    )
    
    # Size based on metric
    size_col = metric if metric in df_province.columns else "Kasus"
    max_val = df_province[size_col].max()
    df_province["size"] = (df_province[size_col] / max_val * 50).clip(lower=10)
    
    # Color scale
    color_scale = "Reds" if metric in ["Kematian", "Aktif"] else "Purples"
    
    fig = px.scatter_mapbox(
        df_province,
        lat="lat",
        lon="lon",
        size="size",
        color=metric,
        hover_name="Provinsi",
        hover_data={
            "Kasus": True,
            "Kematian": True,
            "Sembuh": True,
            "Aktif": True,
            "Kasus_per_100K": True,
            "lat": False,
            "lon": False,
            "size": False,
        },
        color_continuous_scale=color_scale,
        zoom=4,
        center={"lat": -2.5, "lon": 118},
        mapbox_style=basemap_style,
        title=f"Sebaran {metric.replace('_', ' ')} per Provinsi",
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=600,
    )
    
    st.plotly_chart(fig, **ui.kw_plotly_chart())
    
    st.divider()
    
    # --- Ranking Table ---
    st.subheader("Ranking Provinsi")
    
    # Sort by selected metric
    df_sorted = df_province.sort_values(metric, ascending=False).reset_index(drop=True)
    df_sorted.index = df_sorted.index + 1  # 1-indexed ranking
    
    # Display top 10
    display_cols = ["Provinsi", "Kasus", "Kematian", "Sembuh", "Aktif", "Kasus_per_100K"]
    df_display = df_sorted[display_cols].head(10)
    
    # Format numbers
    for col in ["Kasus", "Kematian", "Sembuh", "Aktif"]:
        df_display[col] = df_display[col].apply(utils.format_number)
    
    st.dataframe(df_display, use_container_width=True)
    
    st.caption("Menampilkan 10 provinsi teratas berdasarkan metrik yang dipilih.")
    
    st.divider()
    
    # --- Bar Chart Comparison ---
    st.subheader("Perbandingan Antar Provinsi")
    
    fig_bar = px.bar(
        df_sorted.head(15),
        x="Provinsi",
        y=metric,
        title=f"Top 15 Provinsi berdasarkan {metric.replace('_', ' ')}",
        color=metric,
        color_continuous_scale=color_scale,
    )
    
    fig_bar.update_layout(
        xaxis_tickangle=-45,
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False,
    )
    
    st.plotly_chart(fig_bar, **ui.kw_plotly_chart())
