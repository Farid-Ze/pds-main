# COVID-19 Dashboard Indonesia - Dokumentasi

Aplikasi Streamlit untuk analisis data COVID-19 Indonesia dengan struktur modular yang terorganisir.

## 🚀 Cara Menjalankan

### 1. Install Dependencies
```bash
pip install -r config/requirements.txt
```

### 2. Jalankan Aplikasi
```bash
streamlit run src/app.py
```

Aplikasi akan otomatis terbuka di browser Anda pada `http://localhost:8501`

## 📁 Struktur Proyek

```
pds-covid/
├── src/                          # Source code utama
│   ├── __init__.py              # Python package init
│   ├── app.py                   # Main application dengan routing
│   ├── api_client.py            # Fetch data dari disease.sh API
│   ├── utils.py                 # Fungsi utility (data processing)
│   ├── styles.py                # CSS styling netral
│   ├── ui.py                    # UI helpers
│   ├── dashboard_utama.py       # Modul Dashboard Utama
│   ├── visualisasi_covid.py     # Modul Visualisasi Data
│   ├── analisa_gis.py           # Modul Analisis GIS/Peta
│   ├── statistik_data.py        # Modul Statistik Lengkap
│   ├── database_covid.py        # Modul Database & Filter
│   ├── trend_vaksinasi.py       # Modul Trend Vaksinasi
│   └── kalkulator_risiko.py     # Modul Kalkulator Risiko
├── config/                       # Configuration files
│   └── requirements.txt         # Dependencies Python
├── docs/                         # Documentation
│   └── README.md                # Dokumentasi ini
├── .env.example                  # Environment variable example
├── .gitignore                    # Git ignore rules
└── README.md                     # Quick start
```

## 🎯 Fitur Utama

### 1. Dashboard Utama
- Overview statistik COVID-19 Indonesia
- Metric cards: Total Kasus, Kematian, Sembuh, Aktif
- Key metrics: CFR, Recovery Rate, Kasus per 1 Juta
- Trend 30 hari terakhir
- Feature cards navigasi

### 2. Visualisasi COVID-19
- **Trend Kumulatif**: Line chart kasus, kematian, sembuh
- **Kasus Harian**: Bar chart dengan rolling average
- **Perbandingan**: Area chart stacked
- **Distribusi**: Histogram dan box plot
- Filter berdasarkan rentang tanggal

### 3. Analisis GIS
- Peta Indonesia dengan Plotly Scatter Map
- Warna marker berdasarkan tingkat kasus
- Tooltip informasi detail per provinsi
- Toggle metrik: Total Kasus, Kasus per 100K, Kematian, Aktif
- Ranking provinsi dan bar chart perbandingan
- **Catatan**: Data provinsi adalah SIMULASI

### 4. Statistik Data
- Case Fatality Rate (CFR)
- Estimasi R0 (Basic Reproduction Number)
- Peak analysis (tanggal puncak kasus)
- Statistik deskriptif lengkap
- Histogram dan box plot distribusi
- Rolling average dengan window kustom

### 5. Database COVID-19
- Tabel data historis lengkap
- Filter berdasarkan tanggal dan tahun
- Export data ke CSV
- Quick stats untuk periode terpilih

### 6. Trend Vaksinasi
- Total dosis vaksin
- Persentase populasi tervaksinasi
- Chart kumulatif dan harian
- Progress bars per dosis
- Ringkasan bulanan

### 7. Kalkulator Risiko
- **CFR Calculator**: Hitung Case Fatality Rate
- **R0 & Herd Immunity**: Hitung threshold herd immunity
- **Proyeksi Kasus**: Simulasi pertumbuhan eksponensial

## 📊 Sumber Data

### API Utama
Data diambil dari [disease.sh API](https://disease.sh/):
- Current stats: `https://disease.sh/v3/covid-19/countries/indonesia`
- Historical data: `https://disease.sh/v3/covid-19/historical/indonesia?lastdays=all`
- Vaccine data: `https://disease.sh/v3/covid-19/vaccine/coverage/countries/indonesia`

### Fallback
Jika API tidak tersedia, aplikasi menggunakan sample data yang di-generate.

### Data Provinsi
Data per provinsi adalah **SIMULASI** untuk tujuan demonstrasi. 
Data riil per provinsi tidak tersedia dari API publik.

## 🎨 Desain & Tema

### Theme mengikuti Streamlit
Aplikasi menggunakan fitur bawaan Streamlit **Settings → Choose app theme** (Light/Dark/Custom).

### Responsive Design
- Mobile friendly
- Konsisten di semua halaman
- Smooth hover effects dan transitions

## 🔧 Teknologi

- **Backend**: Python 3.8+
- **Frontend**: Streamlit >= 1.29.0
- **Visualisasi**: Plotly >= 5.17.0
- **Data Processing**: Pandas, NumPy
- **HTTP Client**: Requests
- **Styling**: Custom CSS dengan Google Fonts

## 🏗️ Arsitektur Modular

### Keuntungan Struktur Modular
- **Maintainability**: Setiap halaman terisolasi
- **Scalability**: Mudah menambah fitur baru
- **Team Development**: Banyak developer bisa kerja simultan
- **Reusability**: Functions dapat di-reuse

### Modul-Modul
- **`api_client.py`**: Fetch data dari API, fallback handling
- **`utils.py`**: Kalkulasi statistik, formatting
- **`styles.py`**: Centralized CSS styling
- **`ui.py`**: UI helpers, state management
- **Page Modules**: Setiap halaman dalam file terpisah

## 🔧 Troubleshooting

### Error koneksi API
- Pastikan koneksi internet stabil
- Aplikasi akan menggunakan fallback data jika API gagal

### Error dependencies
- Jalankan `pip install -r config/requirements.txt`
- Pastikan menggunakan Python 3.8+

### Import errors
- Pastikan menjalankan dari root directory
- Gunakan `streamlit run src/app.py`

### Peta tidak muncul
- Pastikan koneksi internet stabil
- Coba refresh browser

## 📚 Referensi

- [disease.sh API Documentation](https://disease.sh/docs/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Python Documentation](https://plotly.com/python/)

---

**Dikembangkan untuk Tugas Besar PSD dengan struktur modular Streamlit**
