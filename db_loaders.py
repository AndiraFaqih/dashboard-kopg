"""
Database loaders - functions to load data from PostgreSQL database
"""
import pandas as pd
from database import get_db_session
from sqlalchemy import text
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


def parse_bulan_from_db(x):
    """Parse bulan dari berbagai format (int, float, string) ke int"""
    if isinstance(x, (int, float)) and not pd.isna(x):
        return int(x)
    s = str(x).strip().lower()
    if s.isdigit():
        return int(s)
    
    # Normalisasi tulisan bulan panjang
    panjang_map = {
        "januari": 1,
        "februari": 2,
        "maret": 3,
        "april": 4,
        "mei": 5,
        "juni": 6,
        "juli": 7,
        "agustus": 8,
        "september": 9,
        "oktober": 10,
        "november": 11,
        "desember": 12,
    }
    if s in panjang_map:
        return panjang_map[s]
    
    # pendek
    s3 = s[:3]
    bulan_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
        "mei": 5, "jun": 6, "jul": 7, "agu": 8,
        "ags": 8, "sep": 9, "okt": 10, "nov": 11, "des": 12,
    }
    return bulan_map.get(s3, 1)


def bulan_nama(num: int) -> str:
    """Konversi angka bulan (1-12) menjadi nama bulan Indonesia."""
    names = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember",
    ]
    try:
        i = int(num)
        if 1 <= i <= 12:
            return names[i - 1]
    except Exception:
        pass
    return str(num)


def load_perbankan_data_from_db():
    """Load perbankan summary data from database"""
    session = get_db_session()
    try:
        query = text("""
SELECT 
    "Negara",
    "Provinsi",
    "Tahun",
    "Bulan",
    "Total Aset" AS "Total Aset",
    "Giro",
    "Tabungan",
    "Deposito",
    "Total DPK " AS "Total DPK",
    "Modal Kerja",
    "Investasi",
    "Konsumsi",
    "Total Kredit",
    "Nominal NPL Gross",
    "Rasio NPL Gross",
    "Nominal NPL Net",
    "Rasio NPL Net",
    "Loan to Deposit Rastio (LDR)"
FROM kinerja_perbankan_summary
            ORDER BY "Tahun", "Bulan", "Provinsi"
        """)
        df = pd.read_sql(query, session.bind)
        
        # Add periode column for sorting
        if not df.empty:
            # Parse Bulan column if it contains text (e.g., "Desember")
            if df["Bulan"].dtype == object:
                df["Bulan"] = df["Bulan"].apply(parse_bulan_from_db).astype(int)
            elif df["Bulan"].dtype not in [int, 'int64', 'int32']:
                df["Bulan"] = df["Bulan"].apply(parse_bulan_from_db).astype(int)
            
            df["periode"] = pd.to_datetime(
                dict(year=df["Tahun"], month=df["Bulan"], day=1)
            )
            df["Bulan Nama"] = df["Bulan"].apply(bulan_nama)
            logger.info(f"✅ [PERBANKAN] Data dimuat dari database: {len(df)} baris")
        else:
            logger.warning("⚠️  [PERBANKAN] Database kosong, tidak ada data")
        
        return df
    except Exception as e:
        logger.error(f"❌ [PERBANKAN] Error memuat dari database: {str(e)}")
        raise
    finally:
        session.close()


def load_umkm_data_from_db():
    """Load UMKM data from database"""
    session = get_db_session()
    try:
        query = text("""
            SELECT 
                "Provinsi",
                "Tahun",
                "Bulan",
                "Jenis Kredit/Pembiayaan",
                "Nominal Kredit \n(Rp Miliar)",
                "Nominal NPL \n(Rp Miliar)",
                "Nominal NPL Net (Rp Miliar)",
                "Jumlah Rekening UMKM"
            FROM perbankan
            ORDER BY "Tahun", "Bulan", "Provinsi"
        """)
        df = pd.read_sql(query, session.bind)
        
        # Add periode column
        if not df.empty:
            # Parse Bulan column if it contains text (e.g., "Desember")
            if df["Bulan"].dtype == object:
                df["Bulan"] = df["Bulan"].apply(parse_bulan_from_db).astype(int)
            elif df["Bulan"].dtype not in [int, 'int64', 'int32']:
                df["Bulan"] = df["Bulan"].apply(parse_bulan_from_db).astype(int)
            
            df["periode"] = pd.to_datetime(
                dict(year=df["Tahun"], month=df["Bulan"], day=1)
            )
            logger.info(f"✅ [UMKM] Data dimuat dari database: {len(df)} baris")
        else:
            logger.warning("⚠️  [UMKM] Database kosong, tidak ada data")
        
        return df
    except Exception as e:
        logger.error(f"❌ [UMKM] Error memuat dari database: {str(e)}")
        raise
    finally:
        session.close()


def load_konv_syariah_data_from_db():
    """Load konvensional/syariah data from database"""
    session = get_db_session()
    try:
        query = text("""
            SELECT 
                "Provinsi",
                "Kab/Kota",
                "Tahun",
                "Bulan",
                "Jenis Bank",
                "Skema",
                "Aset",
                "Kredit ",
                "DPK",
                "NPL"
            FROM daerah_perbankan
            WHERE LOWER("Kab/Kota") LIKE '%all%'
                AND UPPER("Jenis Bank") LIKE '%BANK UMUM%'
            ORDER BY "Tahun", "Bulan", "Provinsi"
        """)
        df = pd.read_sql(query, session.bind)
        
        # Add periode column
        if not df.empty:
            # Parse Bulan column if it contains text (e.g., "Desember")
            if df["Bulan"].dtype == object:
                df["Bulan"] = df["Bulan"].apply(parse_bulan_from_db).astype(int)
            elif df["Bulan"].dtype not in [int, 'int64', 'int32']:
                df["Bulan"] = df["Bulan"].apply(parse_bulan_from_db).astype(int)
            
            df["periode"] = pd.to_datetime(
                dict(year=df["Tahun"], month=df["Bulan"], day=1)
            )
            logger.info(f"✅ [KONV-SYARIAH] Data dimuat dari database: {len(df)} baris")
        else:
            logger.warning("⚠️  [KONV-SYARIAH] Database kosong, tidak ada data")
        
        return df
    except Exception as e:
        logger.error(f"❌ [KONV-SYARIAH] Error memuat dari database: {str(e)}")
        raise
    finally:
        session.close()


def load_asuransi_data_from_db():
    """Load asuransi data from database"""
    session = get_db_session()
    try:
        query = text("""
            SELECT 
                "Provinsi",
                "Kabupaten",
                "Periode",
                "Tahun",
                "Jenis",
                "Premi (Rp Juta)",
                "Klaim (Rp Juta)",
                "Jumlah Peserta Premi",
                "Jumlah Peserta Klaim ",
                "Jumlah Polis Premi",
                "Jumlah Polis Klaim "
            FROM asuransi
            ORDER BY "Tahun", "Periode", "Provinsi"
        """)
        df = pd.read_sql(query, session.bind)
        
        # Parse quarter from periode
        if not df.empty:
            def parse_quarter(x):
                s = str(x).strip().lower()
                mapping = {
                    "triwulan i": 1, "triwulan 1": 1,
                    "triwulan ii": 2, "triwulan 2": 2,
                    "triwulan iii": 3, "triwulan 3": 3,
                    "triwulan iv": 4, "triwulan 4": 4,
                }
                return mapping.get(s, 1)
            
            df["Quarter"] = df["Periode"].apply(parse_quarter).astype(int)
            
            # Add periode_dt column
            df["periode_dt"] = pd.to_datetime(
                dict(year=df["Tahun"], month=df["Quarter"] * 3, day=1)
            )
            logger.info(f"✅ [ASURANSI] Data dimuat dari database: {len(df)} baris")
        else:
            logger.warning("⚠️  [ASURANSI] Database kosong, tidak ada data")
        
        return df
    except Exception as e:
        logger.error(f"❌ [ASURANSI] Error memuat dari database: {str(e)}")
        raise
    finally:
        session.close()


def load_dana_pensiun_data_from_db():
    """Load dana pensiun data from database"""
    session = get_db_session()
    try:
        query = text("""
            SELECT 
                "Negara",
                "Provinsi",
                "Tahun",
                "Bulan",
                "Aset (Rp Miliar)",
                "Aset Neto (Rp Miliar)",
                "Investasi (Rp Miliar)",
                "Jumlah Dana Pensiun"
            FROM dana_pensiun
            ORDER BY "Tahun", "Bulan", "Provinsi"
        """)
        df = pd.read_sql(query, session.bind)
        
        # Add periode column
        if not df.empty:
            # Parse Bulan column if it contains text (e.g., "Desember")
            if df["Bulan"].dtype == object:
                df["Bulan"] = df["Bulan"].apply(parse_bulan_from_db).astype(int)
            elif df["Bulan"].dtype not in [int, 'int64', 'int32']:
                df["Bulan"] = df["Bulan"].apply(parse_bulan_from_db).astype(int)
            
            df["periode"] = pd.to_datetime(
                dict(year=df["Tahun"], month=df["Bulan"], day=1)
            )
            df["Bulan Nama"] = df["Bulan"].apply(bulan_nama)
            logger.info(f"✅ [DANA PENSIUN] Data dimuat dari database: {len(df)} baris")
        else:
            logger.warning("⚠️  [DANA PENSIUN] Database kosong, tidak ada data")
        
        return df
    except Exception as e:
        logger.error(f"❌ [DANA PENSIUN] Error memuat dari database: {str(e)}")
        raise
    finally:
        session.close()


def load_kredit_lokasi_data_from_db():
    """Load kredit lokasi data from database"""
    session = get_db_session()
    try:
        query = text("""
            SELECT 
                "Sektor",
                "Lokasi",
                "Kredit"
            FROM kredit_lok_bank
            WHERE LOWER("Sektor") LIKE '%perkebunan%'
            ORDER BY "Sektor", "Lokasi"
        """)
        df = pd.read_sql(query, session.bind)

        if not df.empty:
            logger.info(f"✅ [KREDIT LOKASI] Data dimuat dari database: {len(df)} baris")
        else:
            logger.warning("⚠️  [KREDIT LOKASI] Database kosong, tidak ada data")
        
        # Metadata tahun/bulan tidak tersedia di tabel; kembalikan None sebagai placeholder
        return df, None, None
    except Exception as e:
        logger.error(f"❌ [KREDIT LOKASI] Error memuat dari database: {str(e)}")
        raise
    finally:
        session.close()


def load_jumlah_petani_data_from_db():
    """Load jumlah petani data from database"""
    session = get_db_session()
    try:
        query = text("""
            SELECT 
                "Komoditi",
                "Provinsi",
                "Kabupaten/Kota" AS "KabKota",
                "Jumlah Petani" AS "JumlahPetani"
            FROM jumlah_petani_kelapa_sumatera_selatan
            ORDER BY "Jumlah Petani" DESC
        """)
        df = pd.read_sql(query, session.bind)

        if not df.empty:
            logger.info(f"✅ [JUMLAH PETANI] Data dimuat dari database: {len(df)} baris")
        else:
            logger.warning("⚠️  [JUMLAH PETANI] Database kosong, tidak ada data")
        
        return df
    except Exception as e:
        logger.error(f"❌ [JUMLAH PETANI] Error memuat dari database: {str(e)}")
        raise
    finally:
        session.close()
