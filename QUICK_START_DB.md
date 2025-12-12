# Quick Start - Database Integration

## Langkah 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Langkah 2: Cek Koneksi Database
```bash
python check_db_tables.py
```

Script ini akan menampilkan:
- Status koneksi
- Daftar tabel yang ada
- Struktur setiap tabel

## Langkah 3: Sesuaikan Nama Tabel (jika perlu)

Jika nama tabel di database berbeda, edit file `db_loaders.py`:
- Cari fungsi yang sesuai (misal: `load_perbankan_data_from_db`)
- Ubah nama tabel di query SQL sesuai dengan yang ada di database Anda

## Langkah 4: Test via Web

1. Jalankan aplikasi:
```bash
python app.py
```

2. Buka browser dan akses:
```
http://localhost:5000/test-db
```

Ini akan menampilkan JSON dengan status koneksi database.

## Langkah 5: Verifikasi Dashboard

Akses dashboard utama:
```
http://localhost:5000/
```

Data sekarang akan dimuat dari database (kecuali raw-all-komoditas yang tetap dari Excel).

## Catatan Penting

- **raw-all-komoditas**: Tetap dimuat dari Excel (sesuai permintaan)
- **Fallback**: Jika database error, aplikasi otomatis fallback ke Excel
- **Error Handling**: Semua error ditangani dengan graceful fallback

## Troubleshooting

Jika ada error "relation does not exist":
1. Jalankan `python check_db_tables.py` untuk melihat tabel yang ada
2. Edit `db_loaders.py` dan sesuaikan nama tabel
3. Pastikan semua kolom yang diperlukan ada di tabel
