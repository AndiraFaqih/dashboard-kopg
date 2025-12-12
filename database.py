"""
Database configuration and connection setup
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database connection string
DATABASE_URL = "postgresql://960072:12345678@localhost:5432/devs_kopg"

# Initialize SQLAlchemy
db = SQLAlchemy()

def init_db(app: Flask):
    """Initialize database connection for Flask app"""
    try:
        logger.info("🔌 Memulai inisialisasi koneksi database...")
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        
        # Test connection
        with app.app_context():
            engine = get_db_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT current_database();"))
                db_name = result.fetchone()[0]
                logger.info(f"✅ Database berhasil terhubung: {db_name}")
                logger.info(f"📍 Database URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
        
        return db
    except Exception as e:
        logger.error(f"❌ Gagal menghubungkan ke database: {str(e)}")
        raise


def get_db_engine():
    """Get SQLAlchemy engine for direct queries"""
    try:
        engine = create_engine(DATABASE_URL)
        logger.debug("Engine database berhasil dibuat")
        return engine
    except Exception as e:
        logger.error(f"❌ Gagal membuat engine database: {str(e)}")
        raise


def get_db_session():
    """Get database session for direct queries"""
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def test_db_connection():
    """
    Test database connection and return status information
    Returns: dict with connection status and database info
    """
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            
            # Get database name
            result = conn.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            
            # Get list of tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            
            return {
                "status": "success",
                "connected": True,
                "database": db_name,
                "postgres_version": version,
                "tables": tables,
                "table_count": len(tables),
                "message": "Database connection successful"
            }
    except Exception as e:
        return {
            "status": "error",
            "connected": False,
            "error": str(e),
            "message": f"Database connection failed: {str(e)}"
        }
