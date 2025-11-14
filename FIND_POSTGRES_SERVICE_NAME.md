# How to Find Your PostgreSQL Service Name - Click-by-Click Guide

## Step 1: Find Your PostgreSQL Service Name

### Method 1: Check the Service List (Easiest)

1. **In Railway Dashboard:**
   - Look at the left side or main area where all your services are listed
   - You should see cards/boxes for each service
   - Find the one that says **"Postgres"** or **"PostgreSQL"** or similar
   - **The name shown on the card is your service name**
   - Common names: `Postgres`, `PostgreSQL`, `postgres`, `database`

### Method 2: Check the URL

1. **When you're viewing the Postgres service:**
   - Look at your browser's address bar (URL)
   - The URL looks like: `railway.app/project/.../service/.../...`
   - The service name might be visible in the breadcrumb or page title
   - But the easiest way is Method 1 above

### Method 3: Check Variables Tab

1. **Click on your Postgres service** (the one you just created)
2. **Click on the "Variables" tab**
3. Look for variables like:
   - `DATABASE_URL`
   - `POSTGRES_URL`
   - `PGDATABASE`
   - `POSTGRES_DATABASE_URL`
4. The variable name format might give you a hint, but the service name is what you see in the service list

## Step 2: Use the Service Name

Once you know your PostgreSQL service name:

### Example 1: If service name is "Postgres"
- Use: `${{Postgres.DATABASE_URL}}`

### Example 2: If service name is "PostgreSQL"  
- Use: `${{PostgreSQL.DATABASE_URL}}`

### Example 3: If service name is "postgres" (lowercase)
- Use: `${{postgres.DATABASE_URL}}`

### Example 4: If service name is "database"
- Use: `${{database.DATABASE_URL}}`

## Step 3: Alternative - Copy Connection String Directly

If you're not sure about the service name, you can skip the `${{...}}` syntax and copy the connection string directly:

1. **Go to Postgres service** → **"Variables" tab**
2. **Find `DATABASE_URL`** (or `POSTGRES_URL` or similar)
3. **Click on the value** to reveal it (it might be hidden with dots)
4. **Copy the entire value** (looks like: `postgresql://user:password@host:port/dbname`)
5. **Go to Backend service** → **"Variables" tab**
6. **Add new variable:**
   - Name: `DATABASE_URL`
   - Value: Paste the connection string you copied
7. **Save**

This method works regardless of service names!

## Visual Guide

```
Railway Dashboard
├── Services List (left side or main area)
│   ├── [Backend Service] ← Your backend
│   ├── [Postgres] ← This is your PostgreSQL service name!
│   └── [Other services...]
│
└── When you click on Postgres:
    ├── Variables tab
    │   └── DATABASE_URL = postgresql://... ← Copy this if needed
    └── Other tabs...
```

## Quick Check

**Answer this:**
- When you look at your Railway project, what does the PostgreSQL service card/box say?
  - Is it "Postgres"?
  - Is it "PostgreSQL"?
  - Is it something else?

That's your service name! Use it exactly as shown (case-sensitive).

