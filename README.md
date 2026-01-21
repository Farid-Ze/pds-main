# COVID-19 Dashboard Indonesia

Aplikasi **Streamlit** untuk analisis data COVID-19 Indonesia dengan data dari **disease.sh API**.

## Quickstart

1) Install dependencies:
```bash
pip install -r config/requirements.txt
```

2) Jalankan aplikasi:
```bash
streamlit run src/app.py
```

Aplikasi akan terbuka di browser pada `http://localhost:8501`

## Fitur

- **Dashboard Utama** - Overview statistik COVID-19
- **Visualisasi COVID-19** - Charts trend kasus, kematian, recovery
- **Analisis GIS** - Peta sebaran per provinsi (simulasi)
- **Statistik Data** - CFR, R0, rolling averages
- **Database COVID-19** - Tabel data dengan filter dan export
- **Trend Vaksinasi** - Data vaksinasi Indonesia
- **Kalkulator Risiko** - CFR, R0, herd immunity calculator

## Data Source

Data diambil dari [disease.sh API](https://disease.sh/):
- Data current: `/v3/covid-19/countries/indonesia`
- Data historis: `/v3/covid-19/historical/indonesia`

**Catatan**: Data per provinsi adalah simulasi untuk tujuan edukasi.

## Dokumentasi

Lihat `docs/README.md` untuk dokumentasi lengkap.
