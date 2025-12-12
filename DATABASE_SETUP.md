# Database Setup Guide

## Overview
Proyek ini sekarang terhubung dengan database PostgreSQL. Semua data (kecuali `raw-all-komoditas`) akan dimuat dari database.

## Konfigurasi Database

Database connection string sudah dikonfigurasi di `database.py`:
```
```

## Instalasi Dependencies

Jalankan perintah berikut untuk menginstall dependencies baru:
```bash
pip install -r requirements.txt
```

Atau install manual:
```bash
pip install flask-sqlalchemy==3.0.5 sqlalchemy==2.0.23 psycopg2-binary==2.9.9
```

## Mapping Tabel Database

Pastikan nama tabel di database sesuai dengan yang digunakan di aplikasi. Berikut mapping yang digunakan:

### 1. Perbankan Summary
- **Tabel**: `kinerja_perbankan`
- **Kolom yang diperlukan**:
  - `negara`, `provinsi`, `tahun`, `bulan`
  - `total_aset`, `giro`, `tabungan`, `deposito`, `total_dpk`
  - `modal_kerja`, `investasi`, `konsumsi`, `total_kredit`
  - `nominal_npl_gross`, `rasio_npl_gross`, `nominal_npl_net`, `rasio_npl_net`
  - `loan_to_deposit_ratio_ldr`

### 2. Perbankan Jenis Usaha (UMKM)
- **Tabel**: `jenis_usaha`
- **Kolom yang diperlukan**:
  - `provinsi`, `tahun`, `bulan`, `jenis`
  - `nominal_kredit`, `nominal_npl`, `nominal_npl_net`
  - `jumlah_rekening_umkm`

### 3. Perbankan Per Daerah (Konvensional/Syariah)
- **Tabel**: `daerah_perbankan`
- **Kolom yang diperlukan**:
  - `provinsi`, `kab_kota`, `tahun`, `bulan`
  - `jenis_bank`, `skema`
  - `aset`, `kredit`, `dpk`, `npl`

### 4. Asuransi
- **Tabel**: `asuransi`
- **Kolom yang diperlukan**:
  - `provinsi`, `kabupaten`, `periode`, `tahun`, `jenis`
  - `premi`, `klaim`
  - `jumlah_peserta_premi`, `jumlah_peserta_klaim`
  - `jumlah_polis_premi`, `jumlah_polis_klaim`

### 5. Dana Pensiun
- **Tabel**: `dana_pensiun`
- **Kolom yang diperlukan**:
  - `negara`, `provinsi`, `tahun`, `bulan`
  - `aset`, `aset_neto`, `investasi`
  - `jumlah_dana_pensiun`

### 6. Kredit Lokasi
- **Tabel**: `kredit_lokasi`
- **Kolom yang diperlukan**:
  - `sektor`, `lokasi`, `kredit`
  - `tahun`, `bulan` (opsional)

## Menyesuaikan Nama Tabel

Jika nama tabel di database Anda berbeda, edit file `db_loaders.py` dan ubah nama tabel di setiap query SQL.

## Testing Database Connection

### 1. Test via Web Browser
Jalankan aplikasi dan buka:
```
http://localhost:5000/test-db
```

Ini akan menampilkan status koneksi database dalam format JSON.

### 2. Test via Script
Jalankan script:
```bash
python check_db_tables.py
```

Script ini akan menampilkan:
- Status koneksi database
- Daftar semua tabel
- Struktur setiap tabel (kolom dan tipe data)

## Fallback ke Excel

Jika database tidak tersedia atau terjadi error, aplikasi akan otomatis fallback ke file Excel yang sudah ada. Pesan error akan ditampilkan di console.

## Catatan Penting

1. **raw-all-komoditas**: Data ini TETAP dimuat dari file Excel (`data/Komoditas.xlsx` sheet `raw-all-komoditas`) karena tabelnya tidak ada di database.

2. **Kredit Lokasi**: Jika tabel `kredit_lokasi` tidak ada atau kosong, akan fallback ke Excel.

3. **Error Handling**: Semua fungsi loader memiliki error handling yang akan fallback ke Excel jika terjadi masalah dengan database.

## Troubleshooting

### Error: "relation does not exist"
- Pastikan nama tabel sesuai dengan yang ada di database
- Gunakan `check_db_tables.py` untuk melihat tabel yang tersedia
- Edit `db_loaders.py` jika nama tabel berbeda

### Error: "column does not exist"
- Pastikan semua kolom yang diperlukan ada di tabel
- Gunakan `check_db_tables.py` untuk melihat struktur tabel
- Edit query di `db_loaders.py` jika nama kolom berbeda

### Error: "could not connect to server"
- Pastikan PostgreSQL server berjalan
- Periksa connection string di `database.py`
- Pastikan database `devs_kopg` sudah dibuat
- Periksa username dan password
