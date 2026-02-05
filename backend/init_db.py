import psycopg2
import os
import time

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'database': os.getenv('DB_NAME', 'sqlinjection_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'port': os.getenv('DB_PORT', '5432')
}

def init_database():
    """Initialize database with tables and sample data"""
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            break
        except psycopg2.OperationalError as e:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Failed to connect to database after {max_retries} attempts")
                raise
            print(f"Database connection failed, retrying ({retry_count}/{max_retries})...")
            time.sleep(1)
    
    try:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user'
            )
        """)
        
        # Create computers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS computers (
                id SERIAL PRIMARY KEY,
                computer_name VARCHAR(100) NOT NULL,
                ip_address VARCHAR(15) NOT NULL
            )
        """)
        
        # Create flag table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flag (
                id SERIAL PRIMARY KEY,
                flag VARCHAR(100) NOT NULL
            )
        """)
        
        # Insert sample users
        cursor.execute("""
            INSERT INTO users (username, password, role) 
            VALUES 
                ('admin', 'admin123', 'admin'),
                ('user1', 'password1', 'user'),
                ('test', 'test123', 'user')
            ON CONFLICT (username) DO NOTHING
        """)
        
        # Insert sample computers
        cursor.execute("""
            INSERT INTO computers (computer_name, ip_address) 
            VALUES 
                ('SERVER-01', '192.168.1.10'),
                ('WORKSTATION-05', '192.168.1.25'),
                ('LAPTOP-12', '192.168.1.42'),
                ('SERVER-02', '192.168.1.11'),
                ('WORKSTATION-08', '192.168.1.28'),
                ('LAPTOP-15', '192.168.1.45'),
                ('SERVER-03', '192.168.1.12'),
                ('WORKSTATION-10', '192.168.1.30')
            ON CONFLICT DO NOTHING
        """)
        
        # Insert flag (only if table is empty)
        cursor.execute("""
            INSERT INTO flag (flag) 
            SELECT 'flag{well_done_cafebeef0e4d}'
            WHERE NOT EXISTS (SELECT 1 FROM flag)
        """)
        
        conn.commit()
        print("Database initialized successfully!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

if __name__ == '__main__':
    init_database()
