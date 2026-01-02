# 💾 Database Preservation Guide

## ✅ Database is Now Protected!

Your database will **NOT be dropped or recreated** during Docker builds or restarts.

---

## 🛡️ What Was Fixed

### Before (❌ DANGEROUS)
```python
# init_db_postgres.py (OLD)
db.drop_all()  # ❌ Deleted ALL data on every Docker restart!
db.create_all()
```

**Problem:** Every time you ran `docker-compose up --build -d`, it would:
1. Drop all tables
2. Delete all posts, users, comments, likes
3. Create empty tables

---

### After (✅ SAFE)
```python
# init_db_postgres.py (NEW - SAFE)
existing_tables = inspector.get_table_names()

if existing_tables:
    print("✅ Database already initialized")
    print("⚠️  Skipping to preserve existing data")
    return True  # ✅ Don't touch existing data!

# Only create if tables don't exist (first time)
db.create_all()
```

**Now:** When you run `docker-compose up --build -d`:
1. ✅ Checks if tables exist
2. ✅ If yes: **Skips** initialization → Data preserved!
3. ✅ If no: Creates tables (first time only)

---

## 📦 PostgreSQL Data Volume

Your database data is stored in a **persistent Docker volume**:

```yaml
# docker-compose.yml
volumes:
  postgres_data:     # ✅ Persists between restarts
    driver: local
```

**This means:**
- ✅ Data survives Docker restarts
- ✅ Data survives container recreation
- ✅ Data survives `docker-compose up --build`
- ❌ Data is lost only if you manually delete the volume

---

## 🔄 Safe Operations

### ✅ Safe - Won't Delete Data

```bash
# Rebuild and restart - Data preserved
docker-compose up --build -d

# Restart containers - Data preserved
docker-compose restart

# Stop and start - Data preserved
docker-compose stop
docker-compose start

# Recreate containers - Data preserved
docker-compose up --build -d --force-recreate
```

**All of these are SAFE** - your data is protected!

---

## 🗑️ When You WANT to Reset Database

### Option 1: Fresh Init Script (Recommended)

Use the dedicated script that includes a 5-second warning:

```bash
# ⚠️  WARNING: This will DELETE ALL DATA!
docker exec blogki-web python init_db_postgres_FRESH.py
```

**This will:**
- Give you 5 seconds to cancel (Ctrl+C)
- Drop all tables
- Create fresh tables
- Delete all posts, users, comments, likes

### Option 2: Delete Docker Volume

```bash
# Stop containers
docker-compose down

# Delete the database volume - ⚠️  DELETES ALL DATA!
docker volume rm demo_postgres_data

# Restart - will create fresh database
docker-compose up -d
```

### Option 3: PostgreSQL Command

```bash
# Connect to database
docker exec -it blogki-db psql -U bloguser -d blogsite

# Drop specific table
DROP TABLE post CASCADE;

# Or drop all tables
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

# Exit
\q
```

---

## 📊 Check Database Status

### View Existing Tables

```bash
docker exec blogki-web python -c "
from app import app
from models import db

with app.app_context():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print(f'Tables: {tables}')
    
    if 'post' in tables:
        from models import Post
        count = Post.query.count()
        print(f'Posts in database: {count}')
"
```

### Check PostgreSQL Data

```bash
# Connect to PostgreSQL
docker exec -it blogki-db psql -U bloguser -d blogsite

# List tables
\dt

# Count posts
SELECT COUNT(*) FROM post;

# View featured posts
SELECT id, title, is_featured FROM post WHERE is_featured = true;

# Exit
\q
```

---

## 🔍 Understanding the Init Scripts

### 1. `init_db_postgres.py` (SAFE - Default)

**When it runs:** Every Docker container start

**What it does:**
```python
1. Check if tables exist
2. If YES: Skip initialization (preserve data) ✅
3. If NO: Create tables (first time only)
```

**Used by:** `docker-compose up` automatically

**Safe:** ✅ YES - Never drops data

---

### 2. `init_db_postgres_FRESH.py` (DANGEROUS - Manual Only)

**When it runs:** Only when you manually execute it

**What it does:**
```python
1. Wait 5 seconds (chance to cancel)
2. Drop ALL tables
3. Delete ALL data
4. Create fresh tables
```

**Used by:** Manual command only
```bash
docker exec blogki-web python init_db_postgres_FRESH.py
```

**Safe:** ❌ NO - Deletes everything!

---

## 📝 Files Modified

| File | Status | Purpose |
|------|--------|---------|
| `init_db_postgres.py` | ✅ Safe | Auto-runs, preserves data |
| `init_db_postgres_FRESH.py` | ⚠️ Dangerous | Manual reset only |
| `docker-compose.yml` | ✅ Safe | Uses safe init script |

---

## 🎯 Common Scenarios

### Scenario 1: Update Code (No DB Changes)

```bash
# Edit Python files, templates, etc.
# Then rebuild:
docker-compose up --build -d
```

**Result:** ✅ Code updated, database unchanged

---

### Scenario 2: Add New Column to Model

```bash
# 1. Edit models.py (add new column)
# 2. Create migration script
# 3. Rebuild
docker-compose up --build -d

# 4. Run migration
docker exec blogki-web python migrate_add_NEWCOLUMN.py
```

**Result:** ✅ New column added, existing data preserved

---

### Scenario 3: Change Environment Variables

```bash
# Edit .env file
# Then rebuild:
docker-compose up --build -d
```

**Result:** ✅ New config applied, database unchanged

---

### Scenario 4: Want Fresh Start

```bash
# Option A: Use fresh init script
docker exec blogki-web python init_db_postgres_FRESH.py

# Option B: Delete volume
docker-compose down
docker volume rm demo_postgres_data
docker-compose up -d
```

**Result:** ⚠️ All data deleted, fresh database created

---

## 🛟 Recovery Options

### If You Accidentally Delete Data

#### 1. Check Docker Volume

```bash
# List volumes
docker volume ls | grep postgres

# Inspect volume
docker volume inspect demo_postgres_data
```

#### 2. PostgreSQL Backups

If you had backups:

```bash
# Restore from backup
docker exec -i blogki-db psql -U bloguser -d blogsite < backup.sql
```

#### 3. No Backup? 

Unfortunately, if data was deleted and you have no backup:
- ❌ Data cannot be recovered
- 💡 Consider setting up automated backups
- 💡 Use `pg_dump` regularly

---

## 📌 Best Practices

### ✅ DO:
1. **Run `docker-compose up --build -d`** freely - it's safe
2. **Create backups** before major changes
3. **Use migration scripts** for schema changes
4. **Test in staging** before production
5. **Keep separate .env files** for dev/prod

### ❌ DON'T:
1. **Don't run** `init_db_postgres_FRESH.py` unless you want to lose data
2. **Don't delete** the `postgres_data` volume unless intentional
3. **Don't modify** `init_db_postgres.py` to add `db.drop_all()`
4. **Don't use** `db.drop_all()` in production
5. **Don't skip** backups

---

## 🔐 Backup Recommendations

### Manual Backup

```bash
# Create backup
docker exec blogki-db pg_dump -U bloguser blogsite > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker exec -i blogki-db psql -U bloguser -d blogsite < backup_20260103_001234.sql
```

### Automated Backup (Add to cron)

```bash
# Add to crontab -e
0 2 * * * docker exec blogki-db pg_dump -U bloguser blogsite > /backups/blogsite_$(date +\%Y\%m\%d).sql
```

---

## ✅ Verification

### Check Protection is Working

```bash
# 1. Create a test post via Admin
# 2. Rebuild Docker
docker-compose up --build -d

# 3. Check if post still exists
docker exec blogki-web python -c "
from app import app
from models import db, Post

with app.app_context():
    count = Post.query.count()
    print(f'✅ Posts still in database: {count}')
"
```

**Expected:** Post count should be same as before rebuild

---

## 📊 Summary

| Action | Database Impact |
|--------|----------------|
| `docker-compose up --build -d` | ✅ No change |
| `docker-compose restart` | ✅ No change |
| `docker-compose stop/start` | ✅ No change |
| Edit code files | ✅ No change |
| Edit .env | ✅ No change |
| Run migration script | ✅ Adds columns only |
| `init_db_postgres_FRESH.py` | ❌ Deletes all data |
| Delete postgres_data volume | ❌ Deletes all data |

---

## 🎉 Status

- ✅ **Database preservation: ENABLED**
- ✅ **Safe init script: ACTIVE**
- ✅ **Data persistence: CONFIGURED**
- ✅ **Docker volume: MOUNTED**
- ✅ **Protection: MAXIMUM**

**Your database is now protected from accidental deletion during Docker builds!**

---

**Last Updated:** January 3, 2026
**Status:** ✅ Production Safe
**Data Protection:** ✅ Enabled

