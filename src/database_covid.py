"""Database COVID-19.

Menampilkan tabel data lengkap dengan:
- Filter tanggal
- Export ke CSV
- Pagination untuk dataset besar
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

import utils
import ui


def tampilkan_database_covid(df: pd.DataFrame):
    """Tampilkan halaman database COVID-19."""
    
    st.title("Database COVID-19")
    st.markdown("Tabel data lengkap COVID-19 Indonesia dengan filter dan export.")
    
    if df.empty:
        st.warning("Data tidak tersedia.")
        return
    
    st.divider()
    
    # --- Filter Section ---
    st.subheader("Filter Data")
    
    col1, col2, col3 = st.columns(3)
    
    min_date = df["Tanggal"].min().date()
    max_date = df["Tanggal"].max().date()
    
    with col1:
        start_date = st.date_input(
            "Tanggal Mulai",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            key="db_start_date"
        )
    
    with col2:
        end_date = st.date_input(
            "Tanggal Akhir",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key="db_end_date"
        )
    
    with col3:
        # Filter by year
        years = sorted(df["Tanggal"].dt.year.unique())
        selected_year = st.selectbox(
            "Tahun (opsional)",
            options=["Semua"] + [str(y) for y in years],
            key="db_year"
        )
    
    # Apply filters
    df_filtered = utils.filter_by_date_range(df, start_date, end_date)
    
    if selected_year != "Semua":
        df_filtered = df_filtered[df_filtered["Tanggal"].dt.year == int(selected_year)]
    
    # Active filters display
    active_filters = {
        "Mulai": start_date.strftime("%d/%m/%Y") if start_date != min_date else None,
        "Akhir": end_date.strftime("%d/%m/%Y") if end_date != max_date else None,
        "Tahun": selected_year if selected_year != "Semua" else None,
    }
    
    ui.active_filters_bar(
        title="Filter aktif",
        items=active_filters,
        reset_keys=["db_start_date", "db_end_date", "db_year"],
    )
    
    st.divider()
    
    # --- Data Info ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Baris", utils.format_number(len(df_filtered)))
    
    with col2:
        if not df_filtered.empty:
            st.metric(
                "Rentang Tanggal",
                f"{df_filtered['Tanggal'].min().strftime('%d/%m/%Y')} - {df_filtered['Tanggal'].max().strftime('%d/%m/%Y')}"
            )
    
    with col3:
        if not df_filtered.empty:
            st.metric(
                "Total Kasus (periode)",
                utils.format_number(df_filtered["Kasus_Baru"].sum())
            )
    
    st.divider()
    
    # --- Data Table ---
    st.subheader("Tabel Data")
    
    if df_filtered.empty:
        st.info("Tidak ada data untuk filter yang dipilih.")
        return
    
    # Prepare display dataframe
    df_display = df_filtered.copy()
    df_display["Tanggal"] = df_display["Tanggal"].dt.strftime("%d/%m/%Y")
    
    # Reorder columns
    display_cols = ["Tanggal", "Kasus", "Kematian", "Sembuh", "Kasus_Baru", "Kematian_Baru"]
    df_display = df_display[display_cols]
    
    # Rename for display
    df_display.columns = ["Tanggal", "Kasus Kumulatif", "Kematian Kumulatif", "Sembuh Kumulatif", "Kasus Baru", "Kematian Baru"]
    
    # Show dataframe
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=500,
    )
    
    st.divider()
    
    # --- Export Section ---
    st.subheader("Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV Export
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"covid19_indonesia_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="download_csv"
        )
    
    with col2:
        st.caption(
            f"Export {len(df_display):,} baris data. "
            f"File akan berisi data sesuai filter yang dipilih."
        )
    
    st.divider()
    
    # --- Quick Stats ---
    st.subheader("Statistik Cepat (Periode Terpilih)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Rata-rata Kasus/Hari",
            utils.format_number(df_filtered["Kasus_Baru"].mean())
        )
    
    with col2:
        st.metric(
            "Maks Kasus/Hari",
            utils.format_number(df_filtered["Kasus_Baru"].max())
        )
    
    with col3:
        st.metric(
            "Rata-rata Kematian/Hari",
            utils.format_number(df_filtered["Kematian_Baru"].mean())
        )
    
    with col4:
        st.metric(
            "Total Kematian (periode)",
            utils.format_number(df_filtered["Kematian_Baru"].sum())
        )
