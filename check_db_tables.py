"""
Script to check database tables and their structure
Run this to see what tables exist in your database
"""
from database import test_db_connection, get_db_session
from sqlalchemy import text

def check_tables():
    """Check database connection and list all tables"""
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    
    result = test_db_connection()
    print(f"\nStatus: {result['status']}")
    print(f"Connected: {result['connected']}")
    
    if result['connected']:
        print(f"\nDatabase: {result['database']}")
        print(f"PostgreSQL Version: {result['postgres_version']}")
        print(f"\nTables found: {result['table_count']}")
        print("\nTable list:")
        for i, table in enumerate(result['tables'], 1):
            print(f"  {i}. {table}")
        
        # Show structure of each table
        if result['tables']:
            print("\n" + "=" * 60)
            print("TABLE STRUCTURES")
            print("=" * 60)
            session = get_db_session()
            try:
                for table_name in result['tables']:
                    print(f"\n{table_name}:")
                    query = text(f"""
                        SELECT column_name, data_type, character_maximum_length
                        FROM information_schema.columns
                        WHERE table_name = '{table_name}'
                        ORDER BY ordinal_position;
                    """)
                    columns = session.execute(query).fetchall()
                    for col in columns:
                        col_name, data_type, max_len = col
                        if max_len:
                            print(f"  - {col_name}: {data_type}({max_len})")
                        else:
                            print(f"  - {col_name}: {data_type}")
            finally:
                session.close()
    else:
        print(f"\nError: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_tables()
