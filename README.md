# 📊 Dashboard Keuangan Perbankan - kwd-dashboard Integration

**Transformasi dashboard finansial Anda menjadi aplikasi modern dengan kwd-dashboard!**

Mengintegrasikan semua grafik, komponen, dan data finansial Anda ke dalam template dashboard profesional berbasis **Tailwind CSS** dan **Alpine.js**.

---

## 🎯 Apa Yang Baru?

✨ **Sebelum:**
- Tampilan basic dengan Tailwind CDN
- Layout sederhana dengan single page
- Kurang profesional

✨ **Sesudah:**
- Template dashboard modern & profesional
- Dark mode built-in
- Responsive design (mobile-friendly)
- Navigasi sidebar yang intuitif
- Semua grafik & komponen tetap terjaga
- Production-ready code

---

## 📁 Struktur File

```
dashboard_keuangan/
├── 📄 START_HERE.md                 ← Mulai dari sini!
├── 📄 SETUP.md                       ← Setup detail
├── 📄 index.html                     ← Landing page
├── 🐍 server.py                      ← Flask API server
├── 📋 requirements.txt               ← Python dependencies
├── 🚀 setup.sh / setup.bat          ← Auto setup script
│
├── 📂 kwd-dashboard/                 ← Frontend template
│   ├── src/
│   │   ├── html/
│   │   │   ├── index.html           ← Main dashboard
│   │   │   └── 📍 keuangan.html     ← Dashboard keuangan BARU
│   │   ├── data/
│   │   │   ├── pages/
│   │   │   │   ├── home.js
│   │   │   │   └── 📍 keuangan.js   ← Data structure BARU
│   │   │   └── 📍 navigationLinks.js ← Updated dengan keuangan
│   │   ├── js/
│   │   ├── css/
│   │   └── ...
│   ├── package.json
│   ├── vite.config.js
│   └── dist/                         ← Build output
│
├── 📂 data/
│   └── KINERJA PERBANKAN.xlsx       ← Your data file
│
└── 📂 templates/ (legacy)
    └── dashboard.html               ← Old version
```

---

## ⚡ Quick Start (3 Menit)

### 1. Jalankan Setup
```bash
# macOS/Linux
chmod +x setup.sh && ./setup.sh

# Windows
setup.bat
```

### 2. Development Mode
```bash
# Terminal 1: Frontend (Vite)
cd kwd-dashboard && npm run dev
# → Open http://localhost:5173

# Terminal 2: Backend (Flask)
python3 server.py
# → Open http://localhost:5000/keuangan
```

### 3. Production Build
```bash
cd kwd-dashboard && npm run build
# Flask akan melayani dari dist/ folder secara otomatis
```

---

## 📊 Fitur & Komponen

### KPI Cards (4x Cards)
| Metrik | Deskripsi | Growth Metrics |
|--------|-----------|----------------|
| 📈 Total Aset | Aset bank keseluruhan | YtD, YoY |
| 💰 Total Kredit | Total kredit disalurkan | YtD, YoY |
| 💵 Total DPK | Dana Pihak Ketiga | YtD, YoY |
| ⚠️ Rasio NPL | Non-Performing Loans | YtD, YoY |

### Charts (8+ Visualizations)
1. **Mini Bars** - 3 periode terakhir (Aset, Kredit, DPK)
2. **Trend Bar** - Tren tahunan semua metrik
3. **DPK Pie** - Share Giro, Tabungan, Deposito
4. **Kredit Usage** - Produktif vs Konsumtif
5. **Produktif Detail** - Modal Kerja vs Investasi
6. **NPL & LDR Line** - Trend tahunan (dual axis)
7. **UMKM Kredit + NPL** - Bar + Line chart
8. **UMKM KPR** - Rata-rata kredit per rekening

### Filters
- 🌍 Negara
- 🗺️ Provinsi
- 📅 Tahun (Anchor)
- 📆 Bulan (Anchor)
- ⏱️ Interval (Bulanan/Triwulan/Semesteran/Tahunan)

### UMKM Section
- 💳 Kredit UMKM dengan growth
- 📉 NPL metrics
- 🏦 Jumlah rekening
- 💶 Kredit per rekening
- 📊 Tahunan trends

---

## 🔧 API Reference

### GET `/api/data`

Returns semua data dashboard dalam JSON.

```
Query Parameters:
- negara: string
- provinsi: string
- tahun: number
- bulan: number (1-12)
- interval: "bulanan"|"triwulan"|"semesteran"|"tahunan"
```

**Response:**
```json
{
  "filters": {...},
  "kpi": {
    "aset_val": 12345.67,
    "aset_yoy": 5.2,
    "aset_ytd": 3.1,
    "aset_yoy_class": "success",
    ...
  },
  "shares": {
    "share_giro": 35.5,
    "share_tab": 25.3,
    ...
  },
  "charts": {
    "mini_labels": ["Nov", "Dec", "Jan"],
    "mini_aset": [12000, 12500, 13000],
    ...
  },
  "umkm": {...}
}
```

---

## 🎨 Customization

### Mengubah Warna Theme
Edit: `kwd-dashboard/tailwind.config.js`

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#your-color',
      },
    },
  },
}
```

### Menambah KPI Card
Edit: `kwd-dashboard/src/html/keuangan.html`

```hbs
{{#base-card className="border-l-4 border-purple-400"}}
    <div class="flex justify-between items-start mb-4">
        <div>
            <p class="text-xs font-semibold text-gray-500">METRIK BARU</p>
            <p class="text-2xl font-bold text-gray-900">Nilai</p>
        </div>
    </div>
{{/base-card}}
```

### Menambah Chart
1. Tambah canvas: `<canvas id="chartBaru"></canvas>`
2. Tambah JavaScript di `after-script`
3. Update `server.py` untuk include data

---

## 🐛 Troubleshooting

| Error | Solusi |
|-------|--------|
| Port 5000 sudah dipakai | `python3 server.py --port 8000` |
| File Excel tidak ditemukan | Pastikan `data/KINERJA PERBANKAN.xlsx` ada |
| Chart tidak muncul | Cek DevTools (F12) → Console untuk errors |
| Filter tidak bekerja | Refresh halaman atau cek URL params |
| Dark mode error | Clear browser cache |

---

## 📚 Documentation Files

1. **START_HERE.md** - Quick start guide (Bahasa Indonesia)
2. **SETUP.md** - Detailed setup instructions
3. **README.md** - This file
4. **requirements.txt** - Python dependencies

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vite + Handlebars + Tailwind CSS |
| Backend | Flask + Pandas + openpyxl |
| Charts | Chart.js |
| Styling | Tailwind CSS + Dark Mode |
| Build | npm/vite |

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Excel file dengan data

### Manual Installation
```bash
# Clone or extract project
cd dashboard_keuangan

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
cd kwd-dashboard
npm install
cd ..
```

---

## 🚀 Deployment

### Local Development
```bash
python3 server.py
# Access: http://localhost:5000
```

### Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN cd kwd-dashboard && npm install && npm run build
CMD ["python3", "server.py"]
```

### Production (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

---

## 📊 Data Format

### Requirements
File: `data/KINERJA PERBANKAN.xlsx`

**Sheet: SUMMARY**
- Required columns: Negara, Provinsi, Tahun, Bulan
- Nominal columns: Total Aset, DPK, Kredit, etc.
- Ratio columns: NPL Gross, NPL Net, LDR

**Sheet: PERBANKAN - Per Jenis Usaha**
- UMKM data dengan columns: Provinsi, Tahun, Bulan, Jenis, Nominal Kredit, NPL, Rekening

---

## 🎯 Features Preserved

✅ Semua grafik dari dashboard original tetap ada:
- Mini bar charts
- Trend charts
- Pie charts
- Line charts
- Dual-axis charts

✅ Semua KPI metrics:
- Total Aset, Kredit, DPK
- NPL & LDR ratios
- Growth indicators (YoY, YtD)

✅ UMKM section lengkap:
- Kredit metrics
- NPL analysis
- Produktivitas

---

## 📞 Support

- **Dokumentasi**: Lihat START_HERE.md
- **Setup Masalah**: Lihat SETUP.md
- **API Questions**: Check API Reference di atas
- **Customization**: Edit template files di kwd-dashboard/src/

---

## 📝 License

Mengikuti lisensi original kwd-dashboard (MIT)

---

## 🙌 Credits

- **kwd-dashboard**: https://github.com/Kamona-WD/kwd-dashboard
- **Tailwind CSS**: https://tailwindcss.com
- **Chart.js**: https://www.chartjs.org
- **Flask**: https://flask.palletsprojects.com
- **Pandas**: https://pandas.pydata.org

---

## 🎉 Next Steps

1. **Jalankan setup script** - `./setup.sh` atau `setup.bat`
2. **Baca START_HERE.md** - Quick reference
3. **Jalankan development server** - `npm run dev` + `python3 server.py`
4. **Akses dashboard** - http://localhost:5000/keuangan
5. **Customize sesuai kebutuhan** - Edit template & styles
6. **Deploy ke production** - `npm run build`

---

**Selamat datang di Dashboard Keuangan Perbankan yang lebih indah! 🎨✨**

Untuk pertanyaan lebih lanjut, baca dokumentasi lengkap di **START_HERE.md**.
