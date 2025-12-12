"""
Database models for the dashboard application
"""
from database import db
from sqlalchemy import Column, Integer, Float, String, Date, DateTime
from datetime import datetime


class PerbankanSummary(db.Model):
    """Model for perbankan summary data"""
    __tablename__ = 'kinerja_perbankan_summary'  # Adjust table name as needed
    
    id = Column(Integer, primary_key=True)
    negara = Column("Negara", String(100))
    provinsi = Column("Provinsi", String(100))
    tahun = Column("Tahun", Integer)
    bulan = Column("Bulan", Integer)
    total_aset = Column("Total Aset", Float)
    giro = Column("Giro", Float)
    tabungan = Column("Tabungan", Float)
    deposito = Column("Deposito", Float)
    total_dpk = Column("Total DPK ", Float)
    modal_kerja = Column("Modal Kerja", Float)
    investasi = Column("Investasi", Float)
    konsumsi = Column("Konsumsi", Float)
    total_kredit = Column("Total Kredit", Float)
    nominal_npl_gross = Column("Nominal NPL Gross", Float)
    rasio_npl_gross = Column("Rasio NPL Gross", Float)
    nominal_npl_net = Column("Nominal NPL Net", Float)
    rasio_npl_net = Column("Rasio NPL Net", Float)
    loan_to_deposit_ratio_ldr = Column("Loan to Deposit Rastio (LDR)", Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'Negara': self.negara,
            'Provinsi': self.provinsi,
            'Tahun': self.tahun,
            'Bulan': self.bulan,
            'Total Aset': self.total_aset,
            'Giro': self.giro,
            'Tabungan': self.tabungan,
            'Deposito': self.deposito,
            'Total DPK': self.total_dpk,
            'Modal Kerja': self.modal_kerja,
            'Investasi': self.investasi,
            'Konsumsi': self.konsumsi,
            'Total Kredit': self.total_kredit,
            'Nominal NPL Gross': self.nominal_npl_gross,
            'Rasio NPL Gross': self.rasio_npl_gross,
            'Nominal NPL Net': self.nominal_npl_net,
            'Rasio NPL Net': self.rasio_npl_net,
            'Loan to Deposit Rastio (LDR)': self.loan_to_deposit_ratio_ldr,
        }


class PerbankanJenisUsaha(db.Model):
    """Model for perbankan per jenis usaha (UMKM)"""
    __tablename__ = 'jenis_usaha'  # Adjust table name as needed
    
    id = Column(Integer, primary_key=True)
    provinsi = Column(String(100))
    tahun = Column(Integer)
    bulan = Column(String(20))  # simpan nama bulan (Januari, Februari, ...)
    jenis = Column(String(200))  # Jenis Kredit
    nominal_kredit = Column(Float)
    nominal_npl = Column(Float)
    nominal_npl_net = Column(Float)
    jumlah_rekening_umkm = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'Provinsi': self.provinsi,
            'Tahun': self.tahun,
            'Bulan': self.bulan,
            'Jenis': self.jenis,
            'Nominal Kredit': self.nominal_kredit,
            'Nominal NPL': self.nominal_npl,
            'Nominal NPL Net': self.nominal_npl_net,
            'Jumlah Rekening UMKM': self.jumlah_rekening_umkm,
        }


class PerbankanPerDaerah(db.Model):
    """Model for perbankan per daerah (Konvensional/Syariah)"""
    __tablename__ = 'daerah_perbankan'  # Adjust table name as needed
    
    id = Column(Integer, primary_key=True)
    provinsi = Column(String(100))
    kab_kota = Column(String(100))
    tahun = Column(Integer)
    bulan = Column(Integer)
    jenis_bank = Column(String(100))
    skema = Column(String(50))  # Konvensional/Syariah
    aset = Column(Float)
    kredit = Column(Float)
    dpk = Column(Float)
    npl = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'Provinsi': self.provinsi,
            'Kab/Kota': self.kab_kota,
            'Tahun': self.tahun,
            'Bulan': self.bulan,
            'Jenis Bank': self.jenis_bank,
            'Skema': self.skema,
            'Aset': self.aset,
            'Kredit': self.kredit,
            'DPK': self.dpk,
            'NPL': self.npl,
        }


class Asuransi(db.Model):
    """Model for asuransi data"""
    __tablename__ = 'asuransi'  # Adjust table name as needed
    
    id = Column(Integer, primary_key=True)
    provinsi = Column("Provinsi", String(100))
    kabupaten = Column("Kabupaten", String(100))
    periode = Column("Periode", String(50))  # Triwulan I, II, etc.
    tahun = Column("Tahun", Integer)
    jenis = Column("Jenis", String(100))
    premi = Column("Premi (Rp Juta)", Float)  # Rp Juta
    klaim = Column("Klaim (Rp Juta)", Float)  # Rp Juta
    jumlah_peserta_premi = Column("Jumlah Peserta Premi", Integer)
    jumlah_peserta_klaim = Column("Jumlah Peserta Klaim ", Integer)
    jumlah_polis_premi = Column("Jumlah Polis Premi", Integer)
    jumlah_polis_klaim = Column("Jumlah Polis Klaim ", Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'Provinsi': self.provinsi,
            'Kabupaten': self.kabupaten,
            'Periode': self.periode,
            'Tahun': self.tahun,
            'Jenis': self.jenis,
            'Premi': self.premi,
            'Klaim': self.klaim,
            'Peserta Premi': self.jumlah_peserta_premi,
            'Peserta Klaim': self.jumlah_peserta_klaim,
            'Polis Premi': self.jumlah_polis_premi,
            'Polis Klaim': self.jumlah_polis_klaim,
        }


class DanaPensiun(db.Model):
    """Model for dana pensiun data"""
    __tablename__ = 'dana_pensiun'  # Adjust table name as needed
    
    id = Column(Integer, primary_key=True)
    negara = Column("Negara", String(100))
    provinsi = Column("Provinsi", String(100))
    tahun = Column("Tahun", Integer)
    bulan = Column("Bulan", Integer)
    aset = Column("Aset (Rp Miliar)", Float)  # Rp Miliar
    aset_neto = Column("Aset Neto (Rp Miliar)", Float)  # Rp Miliar
    investasi = Column("Investasi (Rp Miliar)", Float)  # Rp Miliar
    jumlah_dana_pensiun = Column("Jumlah Dana Pensiun", Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'Negara': self.negara,
            'Provinsi': self.provinsi,
            'Tahun': self.tahun,
            'Bulan': self.bulan,
            'Aset': self.aset,
            'Aset Neto': self.aset_neto,
            'Investasi': self.investasi,
            'Jumlah Dana Pensiun': self.jumlah_dana_pensiun,
        }


class KreditLokasi(db.Model):
    """Model for kredit lokasi data"""
    __tablename__ = 'kredit_lokasi'  # Adjust table name as needed
    
    id = Column(Integer, primary_key=True)
    sektor = Column(String(200))
    lokasi = Column(String(100))
    kredit = Column(Float)
    tahun = Column(Integer, nullable=True)
    bulan = Column(String(20), nullable=True)  # simpan nama bulan
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'Sektor': self.sektor,
            'Lokasi': self.lokasi,
            'Kredit': self.kredit,
            'Tahun': self.tahun,
            'Bulan': self.bulan,
        }
