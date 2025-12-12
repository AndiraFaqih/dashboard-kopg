# Dashboard Keuangan Perbankan - kwd-dashboard Integration

Integrasi Dashboard Keuangan Perbankan dengan **kwd-dashboard**, template dashboard modern berbasis Tailwind CSS dan Alpine.js.

## 📋 Struktur Proyek

```
dashboard_keuangan/
├── kwd-dashboard/              # Frontend template (Vite + Handlebars)
│   ├── src/
│   │   ├── data/
│   │   │   ├── pages/
│   │   │   │   ├── home.js
│   │   │   │   └── keuangan.js   # ✨ Data untuk dashboard keuangan
│   │   │   └── index.js
│   │   ├── html/
│   │   │   ├── index.html        # Main page
│   │   │   └── keuangan.html     # ✨ Dashboard keuangan
│   │   ├── css/
│   │   └── js/
│   ├── vite.config.js
│   ├── package.json
│   └── ...
├── data/                          # Folder data Excel
│   └── KINERJA PERBANKAN.xlsx
├── server.py                       # ✨ Flask API server
├── app.py                          # Legacy (bisa dihapus)
└── README.md                       # File ini
```

## 🚀 Setup & Installation

### 1. Install Dependencies Node.js

```bash
cd kwd-dashboard
npm install
```

### 2. Install Python Dependencies

```bash
pip install flask pandas openpyxl
```

### 3. Pastikan File Data Excel Sudah Ada

File `data/KINERJA PERBANKAN.xlsx` harus ada dengan sheets:
- `SUMMARY` - Data perbankan utama
- `PERBANKAN - Per Jenis Usaha` - Data UMKM

## 🏗️ Build & Run

### Development Mode

**Terminal 1: Build Frontend (Vite)**
```bash
cd kwd-dashboard
npm run dev
```
Frontend akan run di `http://localhost:5173`

**Terminal 2: Run Flask Server**
```bash
python server.py
```
Server akan run di `http://localhost:5000`

### Production Build

```bash
cd kwd-dashboard
npm run build
```

Output build files akan tersimpan di `kwd-dashboard/dist/`

Flask akan melayani dari folder `dist/` secara otomatis.

## 📊 Halaman Dashboard

### Main Pages
- **Dashboard Home**: `/` (dari kwd-dashboard default)
- **Dashboard Keuangan**: `/keuangan` (dashboard finansial dengan data real)

### API Endpoints

#### GET `/api/data`
Returns semua data dashboard dalam format JSON

Query Parameters:
- `negara` - Filter negara
- `provinsi` - Filter provinsi  
- `tahun` - Filter tahun (anchor)
- `bulan` - Filter bulan (anchor)
- `interval` - Periode data: `bulanan`, `triwulan`, `semesteran`, `tahunan`

Contoh:
```
GET /api/data?provinsi=DKI%20Jakarta&tahun=2024&interval=bulanan
```

Response:
```json
{
  "filters": {...},
  "kpi": {
    "aset_val": 12345.67,
    "aset_yoy": 5.2,
    "aset_ytd": 3.1,
    ...
  },
  "shares": {...},
  "charts": {...},
  "umkm": {...}
}
```

## 🎨 Features

### KPI Cards
- **Total Aset** dengan YtD & YoY growth
- **Total Kredit** dengan growth metrics
- **Total DPK** (Dana Pihak Ketiga)
- **Rasio NPL Gross** dengan growth trends

### Charts (Chart.js)
- **Mini Bar Charts** - 3 periode terakhir (Aset, Kredit, DPK)
- **Trend Bar Chart** - Tren tahunan semua metrik
- **DPK Pie Chart** - Share Giro, Tabungan, Deposito
- **Kredit Usage Pie** - Produktif vs Konsumtif
- **Produktif Detail** - Modal Kerja vs Investasi
- **NPL & LDR Line Chart** - Tren tahunan Desember

### UMKM Section
- **Kredit UMKM** - Nominal kredit untuk segmen UMKM
- **NPL Metrics** - Nominal & Rasio NPL UMKM
- **Jumlah Rekening** - Total rekening UMKM
- **Kredit per Rekening** - Rata-rata kredit per rekening

### Filters
- Negara, Provinsi, Tahun, Bulan (anchor)
- Rentang waktu: Bulanan, Triwulan, Semesteran, Tahunan
- Reset filter ke default

## 📝 Data Processing

### Backend (server.py)

1. **Load Data** dari Excel:
   - Parsing kolom numerik (Rp Miliar/Triliun)
   - Parsing rasio (%)
   - Cleanup kolom nama

2. **Aggregation**:
   - Group by Tahun-Bulan
   - Sum untuk nominal, Mean untuk rasio

3. **Growth Calculation**:
   - **YoY (Year-over-Year)**: Dibanding periode sama tahun lalu
   - **YtD (Year-to-Date)**: Dibanding awal tahun

4. **Formatting**:
   - Konversi ke format JSON
   - Round 2 desimal untuk presentase

### Frontend (keuangan.html)

1. **Data Injection**:
   - Chart.js akan membaca data dari API
   - Update KPI cards secara real-time

2. **Responsive Design**:
   - Grid layouts untuk berbagai ukuran layar
   - Tailwind CSS untuk styling

3. **Dark Mode Support**:
   - Built-in dark mode dari kwd-dashboard
   - Semua warna sudah support dark variant

## 🔧 Customization

### Menambah KPI Card Baru

Edit `kwd-dashboard/src/html/keuangan.html`:

```hbs
<!-- Tambah di section KPI CARDS UTAMA -->
{{#base-card className="border-l-4 border-purple-400"}}
    <div class="flex justify-between items-start mb-4">
        <div>
            <p class="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">METRIK BARU</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">Nilai 0</p>
        </div>
    </div>
    <!-- Growth indicators -->
{{/base-card}}
```

### Menambah Chart Baru

1. Tambah canvas element:
```hbs
<canvas id="chartBaru" height="250"></canvas>
```

2. Tambah JavaScript di section `after-script`:
```javascript
new Chart(document.getElementById('chartBaru'), {
    type: 'bar',
    data: {...},
    options: {...}
});
```

3. Update `server.py` untuk include data baru di `/api/data`

## 📱 Responsive Breakpoints

- Mobile: < 640px (grid-cols-1)
- Tablet: 640px - 1024px (md:grid-cols-2)
- Desktop: > 1024px (lg:grid-cols-3+)

## 🐛 Troubleshooting

### File Excel tidak ditemukan
```
Pastikan folder `data/` ada di root directory
File harus bernama: KINERJA PERBANKAN.xlsx
```

### Port 5000 sudah terpakai
```bash
# Ubah port di server.py, baris terakhir:
app.run(debug=True, port=8000)  # Ganti 5000 dengan 8000
```

### Chart tidak muncul
1. Buka Browser DevTools (F12)
2. Cek Console untuk error JavaScript
3. Pastikan Chart.js CDN accessible
4. Verify API endpoint `/api/data` returns valid JSON

### Data tidak update setelah filter
```
Refresh halaman atau check query parameters di URL
```

## 📚 Resources

- **kwd-dashboard**: https://github.com/Kamona-WD/kwd-dashboard
- **Tailwind CSS**: https://tailwindcss.com
- **Alpine.js**: https://alpinejs.dev
- **Chart.js**: https://www.chartjs.org
- **Vite**: https://vitejs.dev
- **Handlebars**: https://handlebarsjs.com

## 📄 License

Sesuai dengan lisensi original kwd-dashboard (MIT)

## 🤝 Support

Untuk pertanyaan atau issue, silakan buat issue di repository.

---

**Last Updated**: December 5, 2025
