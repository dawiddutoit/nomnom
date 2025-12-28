# Scripts

Utility scripts for NomNom setup and maintenance.

## Setup Scripts

### `setup_mongodb.sh` (Complete Setup)

**All-in-one script** that downloads, verifies, extracts, and imports the OpenFoodFacts database.

```bash
./scripts/setup_mongodb.sh
```

**Features:**
- ✅ **Checksum verification** - Skips download if file already exists with correct checksum
- ✅ **Smart extraction** - Reuses existing extracted files
- ✅ **Import verification** - Confirms product count after import
- ✅ **Interactive prompts** - Asks before overwriting existing data
- ✅ **Error handling** - Stops on failures, provides clear error messages

**Requirements:**
- Docker running with `nomnom-mongodb` container
- ~100GB free disk space (20GB download + 80GB extracted)
- 30-90 minutes total time

**What it does:**
1. Checks MongoDB connection
2. Downloads checksum file from OpenFoodFacts
3. Downloads dump file (~20GB) if not present or checksum mismatch
4. Verifies download integrity
5. Extracts dump (~80GB)
6. Imports into MongoDB database `off` (~30-60 mins)
7. Verifies import (counts products and collections)

---

### `download_openfoodfacts.sh` (Download Only)

**Download-only script** for just getting the dump file without importing.

```bash
./scripts/download_openfoodfacts.sh
```

**Use when:**
- You want to download in advance
- You're on a metered connection and want to download during off-peak
- You want to verify the download before importing

**Features:**
- ✅ Checksum verification before and after download
- ✅ Skips re-download if file exists with correct checksum
- ✅ Progress indicator during download

---

## Maintenance Scripts

### `update_openfoodfacts.sh` (Daily Delta Updates)

**Incremental update script** that applies daily changes to keep the database fresh.

```bash
./scripts/update_openfoodfacts.sh
```

**Features:**
- Downloads today's delta file (changes from last 24 hours)
- Applies updates/inserts to existing products
- Much faster than full re-import (~minutes vs hours)
- Safe to run daily via cron

**Cron example (run at 2 AM daily):**
```cron
0 2 * * * cd /path/to/nomnom && ./scripts/update_openfoodfacts.sh >> logs/openfoodfacts_update.log 2>&1
```

---

### `create_indexes.py` (Database Indexes)

Creates MongoDB indexes for optimal query performance.

```bash
python scripts/create_indexes.py
```

**Run this after:**
- Initial database import
- Adding new collections
- Schema changes

**Creates indexes for:**
- `users` - username (unique)
- `custom_foods` - barcode, text search
- `meal_templates` - created_by, text search
- `meal_consumption` - date, user portions
- `meal_plans` - planned_by, date
- `shopping_lists` - created_by, date

---

### `seed_users.py` (Initial Users)

Seeds the database with initial users (nyntjie and unit).

```bash
python scripts/seed_users.py
```

**Creates:**
- **nyntjie**: 2000 cal, 150g protein, 250g carbs, 65g fat
- **unit**: 2200 cal, 160g protein, 275g carbs, 70g fat

**Run this:**
- After initial MongoDB setup
- To reset user data during development

---

## Quick Start (New Setup)

```bash
# 1. Start MongoDB
docker-compose up -d

# 2. Download and import OpenFoodFacts (~1-2 hours)
./scripts/setup_mongodb.sh

# 3. Create indexes
python scripts/create_indexes.py

# 4. Seed users
python scripts/seed_users.py

# 5. Start backend
python main.py
```

---

## Troubleshooting

### "MongoDB container not running"

```bash
docker-compose up -d
docker ps | grep nomnom-mongodb
```

### "Checksum mismatch"

The download may be corrupted. Remove and re-download:

```bash
rm openfoodfacts-mongodbdump.gz*
./scripts/download_openfoodfacts.sh
```

### "Out of disk space"

You need ~100GB free:
- 20GB for compressed dump
- 80GB for extracted dump
- Keep both for faster future re-imports

To clean up after successful import:
```bash
# Keep .gz file for future use
rm -rf openfoodfacts-mongodbdump/
```

### "Import failed"

Check MongoDB logs:
```bash
docker logs nomnom-mongodb
```

Try alternative import method in the script (it will prompt automatically).

---

## File Sizes

| File | Size | Description |
|------|------|-------------|
| `openfoodfacts-mongodbdump.gz` | ~20GB | Compressed dump |
| `openfoodfacts-mongodbdump/` | ~80GB | Extracted dump |
| MongoDB data directory | ~60-80GB | After import |

**Total needed:** ~100GB during setup, ~80GB after cleanup
