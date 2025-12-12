# 🎯 Quick Start Guide - Dashboard Keuangan Perbankan

Dashboard Keuangan Perbankan Anda sudah terintegrasi dengan **kwd-dashboard**! Berikut cara menggunakannya.

## ⚡ Quick Setup (3 Langkah)

### 1️⃣ Jalankan Script Setup

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```bash
setup.bat
```

Script ini akan:
- ✅ Install Python dependencies
- ✅ Install Node.js dependencies
- ✅ Verify file data Excel

### 2️⃣ Build Frontend

```bash
cd kwd-dashboard
npm run dev
```

Buka browser: **http://localhost:5173**

### 3️⃣ Jalankan Backend

Di terminal baru:

```bash
python3 server.py
```

Buka: **http://localhost:5000/keuangan**

---

## 📊 Fitur Dashboard

### KPI Cards
Menampilkan 4 metrik utama dengan growth indicators:

- 📈 **Total Aset** - Aset bank secara keseluruhan
- 💰 **Total Kredit** - Total kredit yang disalurkan
- 💵 **Total DPK** - Dana Pihak Ketiga (Deposits)
- ⚠️ **Rasio NPL Gross** - Non-Performing Loans

Setiap card menampilkan:
- Nilai current
- YtD (Year-to-Date) growth
- YoY (Year-over-Year) growth

### Charts & Visualizations

#### 1. Mini Bar Charts (3 Periode Terakhir)
- Total Aset
- Total Kredit
- Total DPK

#### 2. Trend Chart (Tahunan)
Multi-series bar chart menampilkan trend semua 3 metrik utama

#### 3. DPK Share (Pie Chart)
Breakdown komposisi DPK:
- Giro (Current account)
- Tabungan (Savings)
- Deposito (Fixed deposits)

#### 4. Kredit Usage (Pie Chart)
Penyaluran kredit berdasarkan jenis:
- Produktif
- Konsumtif

#### 5. Produktif Detail (Pie Chart)
Rincian kredit produktif:
- Modal Kerja (Working capital)
- Investasi (Investment)

#### 6. NPL & LDR Trend (Line Chart)
Tren tahunan (Desember setiap tahun):
- Rasio NPL Gross (left axis)
- LDR (Loan-to-Deposit Ratio) (right axis)

---

## 🎛️ Filters

Dashboard dilengkapi dengan filter power untuk analisis:

### Tersedia Filter:
- 🌍 **Negara** - Filter by country
- 🗺️ **Provinsi** - Filter by province
- 📅 **Tahun (Anchor)** - Base year untuk perhitungan
- 📆 **Bulan (Anchor)** - Base month untuk perhitungan
- ⏱️ **Rentang Waktu** - Data interval:
  - Bulanan (Monthly)
  - Triwulan (Quarterly)
  - Semesteran (Semi-annual)
  - Tahunan (Annual)

### Cara Menggunakan:
1. Pilih filter yang diinginkan
2. Klik **"Terapkan Filter"**
3. Dashboard akan update secara otomatis
4. Klik **"Reset"** untuk mengembalikan ke default

---

## 📊 UMKM Section

Bagian khusus untuk analisis UMKM (Micro, Small & Medium Enterprise):

### KPI UMKM:
- 💳 **Kredit UMKM** - Nominal kredit untuk segmen UMKM
- 📉 **Nominal NPL UMKM** - Non-performing loans UMKM
- 🏦 **Jumlah Rekening UMKM** - Number of UMKM accounts
- 💶 **NPL Ratio UMKM** - Persentase NPL UMKM
- 📈 **Rata-rata Kredit per Rekening** - Average credit per account

### UMKM Charts:
1. **Kredit UMKM & NPL Ratio (Tahunan)**
   - Bar chart untuk nominal kredit
   - Line chart overlay untuk NPL ratio

2. **Rata-rata Kredit per Rekening (Tahunan)**
   - Bar chart menampilkan trend productivity

---

## 🔧 API Reference

### GET `/api/data`

Returns semua data dashboard dalam JSON format.

**Query Parameters:**
```
?negara=Indonesia&provinsi=DKI%20Jakarta&tahun=2024&bulan=12&interval=bulanan
```

**Response Structure:**
```json
{
  "filters": {
    "negara_list": [],
    "provinsi_list": [],
    "tahun_list": [],
    "bulan_list": [],
    "negara_selected": "",
    "provinsi_selected": "",
    "tahun_selected": "",
    "bulan_selected": "",
    "interval_selected": "bulanan"
  },
  "kpi": {
    "aset_val": 12345.67,
    "aset_yoy": 5.2,
    "aset_ytd": 3.1,
    "aset_yoy_class": "success",
    // ... more KPI fields
  },
  "shares": {
    "share_giro": 35.5,
    "share_tab": 25.3,
    "share_dep": 39.2,
    // ... more share fields
  },
  "charts": {
    "mini_labels": ["Nov '24", "Dec '24", "Jan '25"],
    "mini_aset": [12000, 12500, 13000],
    // ... more chart data
  },
  "umkm": {
    "kredit_val": 5000.0,
    "kredit_yoy": 2.5,
    // ... more UMKM metrics
  }
}
```

**Status Codes:**
- `200` - Success
- `500` - Server error

**Example Usage:**
```javascript
// Fetch data via JavaScript
fetch('/api/data?provinsi=DKI%20Jakarta&interval=bulanan')
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));
```

---

## 📁 Project Structure

```
dashboard_keuangan/
├── server.py                      # Flask API server
├── setup.sh / setup.bat          # Setup script
├── SETUP.md                       # Detailed setup guide
├── START_HERE.md                  # This file
│
├── kwd-dashboard/                # Frontend (Vite + Handlebars)
│   ├── src/
│   │   ├── html/
│   │   │   ├── index.html        # Main dashboard
│   │   │   └── keuangan.html     # ✨ Keuangan dashboard
│   │   ├── data/
│   │   │   ├── pages/
│   │   │   │   ├── home.js
│   │   │   │   └── keuangan.js   # ✨ Keuangan data structure
│   │   │   └── navigationLinks.js # ✨ Updated with keuangan link
│   │   ├── js/
│   │   ├── css/
│   │   └── support/
│   ├── vite.config.js
│   ├── package.json
│   └── dist/                      # Build output
│
├── data/
│   └── KINERJA PERBANKAN.xlsx    # Your data file
│
└── README.md / SETUP.md / START_HERE.md
```

---

## 🎨 Styling & Customization

Dashboard menggunakan:
- **Tailwind CSS** - Utility-first CSS framework
- **Dark Mode** - Built-in dark mode support
- **Responsive Design** - Mobile-friendly layouts

### Customizing Colors

Edit di `kwd-dashboard/tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#your-color',
        // ...
      },
    },
  },
}
```

### Adding New KPI Card

Edit `kwd-dashboard/src/html/keuangan.html` dan tambahkan:

```hbs
{{#base-card className="border-l-4 border-purple-400"}}
    <div class="flex justify-between items-start mb-4">
        <div>
            <p class="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">METRIK BARU</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">Rp 0 T</p>
        </div>
    </div>
    <div class="flex gap-6 text-xs">
        <div>
            <p class="text-gray-500 dark:text-gray-400">YtD</p>
            <p class="font-semibold text-gray-900 dark:text-white">0%</p>
        </div>
        <div>
            <p class="text-gray-500 dark:text-gray-400">YoY</p>
            <p class="font-semibold text-gray-900 dark:text-white">0%</p>
        </div>
    </div>
{{/base-card}}
```

---

## 🐛 Troubleshooting

### ❌ Error: "Port 5000 already in use"
```bash
# Gunakan port lain
python3 -c "import server; server.app.run(debug=True, port=8000)"
```

### ❌ Error: "Excel file not found"
```
Pastikan:
- Folder "data/" ada di root directory
- File bernama: KINERJA PERBANKAN.xlsx
- File memiliki sheets: SUMMARY, PERBANKAN - Per Jenis Usaha
```

### ❌ Charts tidak muncul
1. Buka DevTools: `F12` di browser
2. Cek Console untuk errors
3. Verify API response: http://localhost:5000/api/data

### ❌ Filter tidak bekerja
- Refresh halaman
- Check URL query parameters
- Verify filter values ada di dropdown

---

## 📞 Support Resources

- **Tailwind CSS Docs**: https://tailwindcss.com/docs
- **Chart.js Documentation**: https://www.chartjs.org/docs/latest/
- **Alpine.js Guide**: https://alpinejs.dev/
- **kwd-dashboard Repo**: https://github.com/Kamona-WD/kwd-dashboard

---

## 🚀 Production Deploy

### Build untuk Production

```bash
cd kwd-dashboard
npm run build
```

Hasilnya ada di `kwd-dashboard/dist/`

### Deploy ke Server

```bash
# Copy files
cp -r kwd-dashboard/dist/* /var/www/dashboard/

# Start Flask (production)
python3 server.py
# atau gunakan gunicorn:
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

---

## 📊 Data Requirements

File `data/KINERJA PERBANKAN.xlsx` harus memiliki columns:

### Sheet: SUMMARY
- Negara, Provinsi, Tahun, Bulan
- Total Aset, Giro, Tabungan, Deposito, Total DPK
- Modal Kerja, Investasi, Konsumsi, Total Kredit
- Nominal NPL Gross, Rasio NPL Gross
- Nominal NPL Net, Rasio NPL Net
- Loan to Deposit Rastio (LDR)

### Sheet: PERBANKAN - Per Jenis Usaha
- Provinsi, Tahun, Bulan, Jenis Kredit/Pembiayaan
- Nominal Kredit (Rp Miliar)
- Nominal NPL (Rp Miliar)
- Nominal NPL Net (Rp Miliar)
- Jumlah Rekening UMKM

---

## ✨ What's New?

✅ Beautiful kwd-dashboard integration
✅ All your charts & graphs preserved
✅ Real-time data from Excel
✅ Dark mode support
✅ Fully responsive design
✅ Professional styling
✅ Easy filtering & customization

---

**Happy Dashboard Exploring! 🎉**

For more info, see: [SETUP.md](./SETUP.md)
