# Panduan Deployment Aplikasi COVID-19 Dashboard

Aplikasi ini dibangun menggunakan **Streamlit** (Python). Karena GitHub Pages hanya mendukung situs web statis (HTML/CSS/JS), aplikasi ini **tidak dapat berjalan di GitHub Pages**.

Solusi terbaik dan gratis adalah menggunakan **Streamlit Community Cloud**.

## Langkah-langkah Deployment ke Streamlit Community Cloud

1.  **Buka Streamlit Community Cloud**
    *   Kunjungi [share.streamlit.io](https://share.streamlit.io/)
    *   Klik "Sign up" atau "Log in" (gunakan akun GitHub Anda).

2.  **Buat Aplikasi Baru**
    *   Klik tombol **"New app"** di pojok kanan atas.
    *   Pilih opsi **"Paste GitHub URL"** atau pilih dari daftar repository.
    *   Jika memilih dari daftar:
        *   **Repository**: `Farid-Ze/pds-main`
        *   **Branch**: `main`
        *   **Main file path**: `src/app.py`
            *   *Penting: Jangan lupa mengubah ini dari default `streamlit_app.py` menjadi `src/app.py` karena file utama aplikasi Anda berada di dalam folder `src`.*

3.  **Konfigurasi Advanced (Opsional)**
    *   Jika aplikasi Anda membutuhkan konfigurasi khusus (seperti yang ada di `.env`), klik **"Advanced settings..."**.
    *   Namun, berdasarkan `.env.example`, konfigurasi saat ini bersifat opsional sehingga Anda bisa langsung melanjutkan.

4.  **Deploy!**
    *   Klik tombol **"Deploy!"**.
    *   Tunggu beberapa menit hingga proses instalasi (`pip install -r requirements.txt`) selesai.
    *   Aplikasi Anda akan aktif di URL seperti `https://pds-main-farid-ze.streamlit.app/`.

## Mengapa GitHub Pages Tidak Bisa?

GitHub Pages hanya menyajikan file statis. Streamlit adalah aplikasi Python yang membutuhkan server untuk menjalankan kode Python di belakang layar. Streamlit Cloud menyediakan server ini secara gratis untuk proyek open-source di GitHub.
