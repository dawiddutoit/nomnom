# OpenFoodFacts Quick Reference

One-page cheatsheet for NomNom developers.

## 🚀 Quick Start

```bash
# Install
pip install openfoodfacts

# Basic usage
import openfoodfacts
api = openfoodfacts.API(user_agent="NomNom/1.0 (contact@nomnom.app)")
product = api.product.get("3017620422003")
```

## 🌐 API Endpoints

| Endpoint | Purpose | Example |
|----------|---------|---------|
| `/api/v2/product/{barcode}.json` | Get product by barcode | `https://world.openfoodfacts.net/api/v2/product/3017620422003.json` |
| `/api/v2/product/{barcode}.json?fields=X,Y` | Get specific fields | `?fields=product_name,nutriments` |
| `/api/v2/product?code=X,Y` | Bulk lookup (multiple barcodes) | `?code=123,456,789&fields=code,product_name` |
| `/api/v2/search?search_terms=X` | Text search | `?search_terms=greek yogurt&page_size=20` |
| `/cgi/suggest.pl?tagtype=X&term=Y` | Autocomplete suggestions | `?tagtype=brands&term=nestle` |

## 📊 Essential Nutritional Fields

**Per 100g/100ml:**

| Field | Unit | Description |
|-------|------|-------------|
| `energy-kcal_100g` | kcal | Calories |
| `proteins_100g` | g | Protein |
| `carbohydrates_100g` | g | Carbs |
| `sugars_100g` | g | Sugar |
| `fat_100g` | g | Total fat |
| `saturated-fat_100g` | g | Saturated fat |
| `fiber_100g` | g | Fiber |
| `sodium_100g` | g | Sodium |
| `salt_100g` | g | Salt |

**Per serving:**
- Append `_serving` instead of `_100g`

## 🏷️ Product Metadata

| Field | Type | Example |
|-------|------|---------|
| `code` | string | "3017620422003" |
| `product_name` | string | "Nutella" |
| `brands` | string | "Ferrero" |
| `categories` | string | "Spreads,Chocolate spreads" |
| `ingredients_text` | string | "Sugar, palm oil..." |
| `allergens` | string | "en:milk,en:nuts" |
| `serving_size` | string | "15 g" |
| `image_url` | string | URL to product image |

## 🎯 Quality Scores

| Field | Values | Meaning |
|-------|--------|---------|
| `nutriscore_grade` | a-e | Nutrition quality (a=best) |
| `nova_group` | 1-4 | Processing level (1=minimal) |
| `ecoscore_grade` | a-e | Environmental impact |

## ⚡ Rate Limits

| Operation | Limit |
|-----------|-------|
| Product reads | 100/min |
| Search | 10/min |
| Facets | 2/min |

## 🔧 Python Code Templates

### Basic Lookup

```python
import openfoodfacts

api = openfoodfacts.API(user_agent="NomNom/1.0 (contact@nomnom.app)")
product = api.product.get("3017620422003", fields=["product_name", "nutriments"])

if product:
    print(product["product_name"])  # "Nutella"
    print(product["nutriments"]["energy-kcal_100g"])  # 539
```

### With Error Handling

```python
def get_food(barcode: str) -> dict | None:
    try:
        api = openfoodfacts.API(user_agent="NomNom/1.0")
        product = api.product.get(barcode)
        return product if product and "product_name" in product else None
    except Exception as e:
        print(f"Error: {e}")
        return None
```

### Parse Nutritional Data

```python
def parse_nutrition(product: dict) -> dict:
    nutriments = product.get("nutriments", {})
    return {
        "calories": nutriments.get("energy-kcal_100g", 0),
        "protein": nutriments.get("proteins_100g", 0),
        "carbs": nutriments.get("carbohydrates_100g", 0),
        "fat": nutriments.get("fat_100g", 0),
        "fiber": nutriments.get("fiber_100g"),
        "sodium": nutriments.get("sodium_100g"),
    }
```

### Parse Allergens

```python
def parse_allergens(product: dict) -> list[str]:
    allergens_str = product.get("allergens", "")
    if not allergens_str:
        return []
    return [a.replace("en:", "").strip() for a in allergens_str.split(",")]
```

## 💾 Caching Strategy

```python
from datetime import datetime, timedelta
import sqlite3
import json

class FoodCache:
    def __init__(self, db_path="food_cache.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                barcode TEXT PRIMARY KEY,
                data TEXT,
                expires_at TIMESTAMP
            )
        """)

    def get(self, barcode: str) -> dict | None:
        cursor = self.conn.execute(
            "SELECT data FROM cache WHERE barcode = ? AND expires_at > ?",
            (barcode, datetime.now())
        )
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None

    def set(self, barcode: str, data: dict, ttl_days=30):
        expires = datetime.now() + timedelta(days=ttl_days)
        self.conn.execute(
            "INSERT OR REPLACE INTO cache VALUES (?, ?, ?)",
            (barcode, json.dumps(data), expires)
        )
        self.conn.commit()
```

## 🧪 Test Data

**Known Good Barcodes:**

| Barcode | Product | Notes |
|---------|---------|-------|
| `3017620422003` | Nutella | Complete data, good for demos |
| `5000112637588` | Coca-Cola | Beverage example |
| `8714100770221` | Greek Yogurt | Dairy example |
| `737628064502` | Cheerios | Cereal example |

## ⚠️ Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Product not found | Invalid/unknown barcode | Return 404, allow manual entry |
| Missing calories | Incomplete data | Check `nutriments` object, validate |
| Rate limit error | >100 req/min | Implement caching, exponential backoff |
| Network timeout | API slow/down | Catch exception, show offline message |
| Allergens empty | Not declared | Show "Unknown allergens" warning |

## 📋 Response Structure

```json
{
  "code": "3017620422003",
  "product": {
    "code": "3017620422003",
    "product_name": "Nutella",
    "brands": "Ferrero",
    "nutriments": {
      "energy-kcal_100g": 539,
      "proteins_100g": 6.3,
      "carbohydrates_100g": 57.5,
      "sugars_100g": 56.3,
      "fat_100g": 30.9,
      "saturated-fat_100g": 10.6,
      "fiber_100g": 0,
      "sodium_100g": 0.0428,
      "salt_100g": 0.107
    },
    "allergens": "en:milk,en:nuts",
    "serving_size": "15 g",
    "nutriscore_grade": "e",
    "nova_group": 4
  },
  "status": 1,
  "status_verbose": "product found"
}
```

**Not Found:**
```json
{
  "code": "invalid",
  "status": 0,
  "status_verbose": "product not found"
}
```

## 🎨 FastAPI Endpoint Template

```python
from fastapi import FastAPI, HTTPException
import openfoodfacts

app = FastAPI()
api = openfoodfacts.API(user_agent="NomNom/1.0")

@app.get("/api/v1/foods/barcode/{barcode}")
async def get_food(barcode: str):
    product = api.product.get(barcode)

    if not product or "product_name" not in product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "success": True,
        "data": {
            "barcode": product["code"],
            "name": product["product_name"],
            "nutrition": {
                "calories": product["nutriments"].get("energy-kcal_100g", 0),
                "protein": product["nutriments"].get("proteins_100g", 0),
                "carbs": product["nutriments"].get("carbohydrates_100g", 0),
                "fat": product["nutriments"].get("fat_100g", 0)
            }
        }
    }
```

## 🆕 Advanced Features

### Bulk Barcode Lookup
```python
# Fetch multiple barcodes in one request
response = requests.get(
    "https://world.openfoodfacts.net/api/v2/product",
    params={"code": "123,456,789", "fields": "code,product_name"},
    headers={"User-Agent": "NomNom/1.0"}
)
products = response.json()["products"]
```

### Text Search
```python
# Search for products by name/category
response = requests.get(
    "https://world.openfoodfacts.net/api/v2/search",
    params={
        "search_terms": "greek yogurt",
        "nutrition_grades_tags": "a,b",  # Only healthy options
        "page_size": 20
    },
    headers={"User-Agent": "NomNom/1.0"}
)
```

### Autocomplete Suggestions
```python
# Get brand suggestions for autocomplete
response = requests.get(
    "https://world.openfoodfacts.net/cgi/suggest.pl",
    params={"tagtype": "brands", "term": "dan"}
)
# Returns: [{"id": "danone", "name": "Danone"}, ...]
```

### Data Quality Detection
```python
# Check for missing nutritional data
misc_tags = product.get("misc_tags", [])
missing = [tag.split("-")[-1] for tag in misc_tags
           if "nutriscore-missing-nutrition-data" in tag]
# Returns: ["sodium", "fiber"] if those fields are missing
```

## 🔗 Useful Links

- [API Docs](https://openfoodfacts.github.io/openfoodfacts-server/api/)
- [Python SDK](https://pypi.org/project/openfoodfacts/)
- [Tutorial](https://openfoodfacts.github.io/openfoodfacts-server/api/tutorial-off-api/)
- [API Cheatsheet](https://openfoodfacts.github.io/openfoodfacts-server/api/ref-cheatsheet/)
- [Data Fields](https://world.openfoodfacts.org/data/data-fields.txt)
- [Web App](https://world.openfoodfacts.org/)

---

**Version:** 1.1 | **Last Updated:** 2025-12-28
**Changelog:** Added bulk lookup, search, autocomplete, and data quality detection
