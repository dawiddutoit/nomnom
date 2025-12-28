# OpenFoodFacts API Integration Guide for NomNom

Complete integration guide for using OpenFoodFacts API in the NomNom calorie tracking application.

## Table of Contents

1. [Quick Start](#quick-start)
2. [API Overview](#api-overview)
3. [Authentication & Rate Limits](#authentication--rate-limits)
4. [Product Lookup by Barcode](#product-lookup-by-barcode)
5. [Nutritional Data Fields](#nutritional-data-fields)
6. [Python SDK Integration](#python-sdk-integration)
7. [Backend Implementation Pattern](#backend-implementation-pattern)
8. [Database Schema Mapping](#database-schema-mapping)
9. [Error Handling](#error-handling)
10. [Caching Strategy](#caching-strategy)
11. [Data Quality Considerations](#data-quality-considerations)
12. [Testing Strategy](#testing-strategy)

---

## Quick Start

**Basic barcode lookup:**
```bash
curl "https://world.openfoodfacts.net/api/v2/product/3017620422003.json?fields=product_name,brands,nutriments"
```

**Python SDK installation:**
```bash
pip install openfoodfacts
```

**Minimal Python example:**
```python
import openfoodfacts

api = openfoodfacts.API(user_agent="NomNom/1.0 (contact@nomnom.app)")
product = api.product.get("3017620422003", fields=["product_name", "nutriments"])
print(product)  # {'product_name': 'Nutella', 'nutriments': {...}}
```

---

## API Overview

### Base Information

- **Base URL**: `https://world.openfoodfacts.net/api/v2/`
- **Production URL**: `https://world.openfoodfacts.org/api/v2/`
- **Staging URL**: `https://world.openfoodfacts.net/api/v2/` (credentials: `off`/`off`)
- **Database Size**: 2.8+ million products
- **License**: Open Database License (ODbL)
- **Cost**: Free, no API key required for read operations

### Core Capabilities

- ✅ Barcode lookup (EAN-13, UPC-A, internal codes)
- ✅ Text search for products
- ✅ Nutritional data (calories, macros, vitamins, minerals)
- ✅ Allergen information
- ✅ Ingredient lists
- ✅ Nutri-Score and NOVA classification
- ✅ Eco-Score (environmental impact)
- ✅ Product images
- ⚠️ Data quality varies (crowd-sourced)

---

## Authentication & Rate Limits

### Read Operations (No Authentication)

**Required Headers:**
```http
User-Agent: AppName/Version (ContactEmail)
```

**Example:**
```python
headers = {
    "User-Agent": "NomNom/1.0 (contact@nomnom.app)"
}
```

### Rate Limits

| Operation | Limit | Notes |
|-----------|-------|-------|
| Product reads | 100 req/min | Per IP address |
| Search queries | 10 req/min | Per IP address |
| Facet queries | 2 req/min | Per IP address |

**Exceeding limits:** May result in temporary IP-based access denial.

**Best Practice:** Implement exponential backoff and respect `Retry-After` headers.

### Write Operations (Authentication Required)

Write operations (editing products) require authentication via:
1. Session cookies from login API (preferred)
2. `user_id` and `password` parameters

**For NomNom:** We only need READ operations (no authentication needed).

---

## Product Lookup by Barcode

### Endpoint

```
GET /api/v2/product/{barcode}.json
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `barcode` | string | Yes | EAN-13, UPC-A, or internal code |
| `fields` | string | No | Comma-separated list of fields to return |

### Example Requests

**Full product data:**
```bash
curl "https://world.openfoodfacts.net/api/v2/product/3017620422003.json"
```

**Selective fields (recommended):**
```bash
curl "https://world.openfoodfacts.net/api/v2/product/3017620422003.json?fields=code,product_name,brands,nutriments,nutriscore_grade,nutrition_grades,categories,ingredients_text,allergens,serving_size,nova_group,ecoscore_grade"
```

### Response Structure

**Successful Response:**
```json
{
  "code": "3017620422003",
  "product": {
    "code": "3017620422003",
    "product_name": "Nutella",
    "brands": "Nutella,Ferrero",
    "categories": "Breakfasts,Spreads,Sweet spreads,Hazelnut spreads,Chocolate spreads",
    "ingredients_text": "Sucre, huile de palme, NOISETTES 13%, cacao maigre 7,4%...",
    "allergens": "en:milk,en:nuts,en:soybeans",
    "serving_size": "15 g",
    "nutriscore_grade": "e",
    "nutrition_grades": "e",
    "nova_group": 4,
    "ecoscore_grade": "d",
    "nutriments": {
      "energy-kcal_100g": 539,
      "fat_100g": 30.9,
      "saturated-fat_100g": 10.6,
      "carbohydrates_100g": 57.5,
      "sugars_100g": 56.3,
      "proteins_100g": 6.3,
      "salt_100g": 0.107,
      "sodium_100g": 0.0428
    }
  },
  "status": 1,
  "status_verbose": "product found"
}
```

**Product Not Found:**
```json
{
  "code": "invalid_barcode",
  "status": 0,
  "status_verbose": "product not found"
}
```

---

## Nutritional Data Fields

### Nutriments Object Structure

All nutritional values follow this pattern:
- **Base value**: `nutriment_name` (e.g., `energy`)
- **Per 100g/100ml**: `nutriment_name_100g` (e.g., `energy-kcal_100g`)
- **Per serving**: `nutriment_name_serving` (e.g., `energy-kcal_serving`)
- **Unit**: `nutriment_name_unit` (e.g., `energy_unit`)
- **Raw value**: `nutriment_name_value` (e.g., `energy_value`)

### Core Nutritional Fields (NomNom Priority)

| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `energy-kcal_100g` | float | kcal | Calories per 100g |
| `energy-kj_100g` | float | kJ | Energy in kilojoules |
| `fat_100g` | float | g | Total fat |
| `saturated-fat_100g` | float | g | Saturated fat |
| `carbohydrates_100g` | float | g | Total carbohydrates |
| `sugars_100g` | float | g | Sugars |
| `fiber_100g` | float | g | Dietary fiber |
| `proteins_100g` | float | g | Protein |
| `salt_100g` | float | g | Salt |
| `sodium_100g` | float | g | Sodium |

### Extended Nutritional Fields

**Fatty Acids:**
- `trans-fat_100g`
- `monounsaturated-fat_100g`
- `polyunsaturated-fat_100g`
- `omega-3-fat_100g`
- `omega-6-fat_100g`
- `cholesterol_100g`

**Vitamins:**
- `vitamin-a_100g`, `vitamin-b1_100g`, `vitamin-b2_100g`, `vitamin-b6_100g`
- `vitamin-b12_100g`, `vitamin-c_100g`, `vitamin-d_100g`, `vitamin-e_100g`
- `vitamin-k_100g`

**Minerals:**
- `calcium_100g`, `iron_100g`, `magnesium_100g`, `phosphorus_100g`
- `potassium_100g`, `zinc_100g`

**Other:**
- `caffeine_100g`
- `taurine_100g`
- `ph_100g`

### Quality Scores

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `nutriscore_grade` | string | a-e | Nutrition quality (a=best, e=worst) |
| `nutrition_grades` | string | a-e | Same as nutriscore_grade |
| `nova_group` | int | 1-4 | Food processing level (1=unprocessed, 4=ultra-processed) |
| `ecoscore_grade` | string | a-e | Environmental impact score |

### Serving Size Information

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `serving_size` | string | "15 g" | Serving size with unit |
| `quantity` | string | "400 g" | Package quantity |

---

## Python SDK Integration

### Installation

```bash
pip install openfoodfacts
```

**Requirements:** Python >=3.10

### Basic Usage

```python
import openfoodfacts

# Initialize API with User-Agent
api = openfoodfacts.API(user_agent="NomNom/1.0 (contact@nomnom.app)")

# Get product by barcode
product = api.product.get(
    "3017620422003",
    fields=["code", "product_name", "brands", "nutriments", "allergens"]
)

# Response structure
print(product["product_name"])  # "Nutella"
print(product["nutriments"]["energy-kcal_100g"])  # 539
```

### Error Handling

```python
def get_product_by_barcode(barcode: str) -> dict | None:
    """Fetch product data from OpenFoodFacts API."""
    try:
        api = openfoodfacts.API(user_agent="NomNom/1.0 (contact@nomnom.app)")
        product = api.product.get(barcode)

        # Check if product was found
        if not product or "product_name" not in product:
            return None

        return product
    except Exception as e:
        logger.error(f"OpenFoodFacts API error for barcode {barcode}: {e}")
        return None
```

### Text Search (Optional)

```python
# Search for products by name
results = api.product.text_search("greek yogurt")

# Results include pagination
print(results["count"])  # Total results
print(results["page"])   # Current page
print(results["products"])  # List of products
```

---

## Backend Implementation Pattern

### Service Layer

```python
# src/services/food_database_service.py
from dataclasses import dataclass
from typing import Optional
import openfoodfacts


@dataclass
class NutritionalData:
    """Nutritional information per 100g."""
    calories: float  # kcal
    protein: float  # g
    carbs: float  # g
    fat: float  # g
    fiber: Optional[float] = None  # g
    sodium: Optional[float] = None  # g
    sugar: Optional[float] = None  # g
    saturated_fat: Optional[float] = None  # g


@dataclass
class FoodItem:
    """Food item from OpenFoodFacts."""
    barcode: str
    name: str
    brand: Optional[str]
    nutrition: NutritionalData
    categories: list[str]
    ingredients: Optional[str]
    allergens: list[str]
    serving_size: Optional[str]
    nutriscore_grade: Optional[str]
    nova_group: Optional[int]
    image_url: Optional[str]


class OpenFoodFactsService:
    """Service for interacting with OpenFoodFacts API."""

    def __init__(self, user_agent: str = "NomNom/1.0 (contact@nomnom.app)"):
        self.api = openfoodfacts.API(user_agent=user_agent)

    def get_food_by_barcode(self, barcode: str) -> Optional[FoodItem]:
        """
        Fetch food item by barcode.

        Returns None if product not found or API error occurs.
        """
        try:
            product = self.api.product.get(
                barcode,
                fields=[
                    "code", "product_name", "brands", "nutriments",
                    "categories", "ingredients_text", "allergens",
                    "serving_size", "nutriscore_grade", "nova_group",
                    "image_url"
                ]
            )

            if not product or "product_name" not in product:
                return None

            return self._parse_product(product)

        except Exception as e:
            # Log error but don't crash
            print(f"OpenFoodFacts API error: {e}")
            return None

    def _parse_product(self, product: dict) -> FoodItem:
        """Convert OpenFoodFacts response to FoodItem."""
        nutriments = product.get("nutriments", {})

        nutrition = NutritionalData(
            calories=nutriments.get("energy-kcal_100g", 0.0),
            protein=nutriments.get("proteins_100g", 0.0),
            carbs=nutriments.get("carbohydrates_100g", 0.0),
            fat=nutriments.get("fat_100g", 0.0),
            fiber=nutriments.get("fiber_100g"),
            sodium=nutriments.get("sodium_100g"),
            sugar=nutriments.get("sugars_100g"),
            saturated_fat=nutriments.get("saturated-fat_100g")
        )

        # Parse categories (comma-separated string)
        categories_str = product.get("categories", "")
        categories = [c.strip() for c in categories_str.split(",")] if categories_str else []

        # Parse allergens (comma-separated string with en: prefix)
        allergens_str = product.get("allergens", "")
        allergens = [
            a.replace("en:", "").strip()
            for a in allergens_str.split(",")
        ] if allergens_str else []

        return FoodItem(
            barcode=product.get("code", ""),
            name=product.get("product_name", "Unknown"),
            brand=product.get("brands"),
            nutrition=nutrition,
            categories=categories,
            ingredients=product.get("ingredients_text"),
            allergens=allergens,
            serving_size=product.get("serving_size"),
            nutriscore_grade=product.get("nutriscore_grade"),
            nova_group=product.get("nova_group"),
            image_url=product.get("image_url")
        )
```

### Usage Example

```python
# In FastAPI endpoint
from fastapi import FastAPI, HTTPException

app = FastAPI()
food_service = OpenFoodFactsService()


@app.get("/api/v1/foods/barcode/{barcode}")
async def get_food_by_barcode(barcode: str):
    """Look up food item by barcode."""
    food_item = food_service.get_food_by_barcode(barcode)

    if not food_item:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "BARCODE_NOT_FOUND",
                "message": f"No food item found for barcode {barcode}"
            }
        )

    return {
        "success": True,
        "data": food_item,
        "error": None
    }
```

---

## Database Schema Mapping

### Recommended Schema

```sql
-- Food items from OpenFoodFacts (cached locally)
CREATE TABLE food_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    barcode VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),

    -- Nutritional values (per 100g)
    calories DECIMAL(10, 2) NOT NULL,
    protein DECIMAL(10, 2) NOT NULL,
    carbs DECIMAL(10, 2) NOT NULL,
    fat DECIMAL(10, 2) NOT NULL,
    fiber DECIMAL(10, 2),
    sodium DECIMAL(10, 2),
    sugar DECIMAL(10, 2),
    saturated_fat DECIMAL(10, 2),

    -- Additional info
    categories TEXT[],  -- PostgreSQL array
    ingredients TEXT,
    allergens TEXT[],
    serving_size VARCHAR(50),

    -- Quality scores
    nutriscore_grade CHAR(1),  -- a, b, c, d, e
    nova_group SMALLINT,  -- 1, 2, 3, 4
    ecoscore_grade CHAR(1),

    -- Images
    image_url TEXT,

    -- Metadata
    source VARCHAR(50) DEFAULT 'openfoodfacts',
    data_quality VARCHAR(20),  -- 'complete', 'partial', 'minimal'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_food_items_barcode ON food_items(barcode);
CREATE INDEX idx_food_items_name ON food_items USING gin(to_tsvector('english', name));
CREATE INDEX idx_food_items_brand ON food_items(brand);

-- User food log (consumed foods)
CREATE TABLE food_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    food_item_id UUID NOT NULL REFERENCES food_items(id),
    consumed_at TIMESTAMP NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,  -- Amount consumed
    unit VARCHAR(20) NOT NULL,  -- 'g', 'ml', 'serving'
    user_notes TEXT,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_food_log_user_id ON food_log(user_id);
CREATE INDEX idx_food_log_consumed_at ON food_log(consumed_at);
```

### Field Mapping

| OpenFoodFacts Field | Database Field | Type | Notes |
|---------------------|----------------|------|-------|
| `code` | `barcode` | VARCHAR(50) | Primary lookup key |
| `product_name` | `name` | VARCHAR(255) | Required |
| `brands` | `brand` | VARCHAR(255) | First brand if multiple |
| `energy-kcal_100g` | `calories` | DECIMAL(10,2) | Required |
| `proteins_100g` | `protein` | DECIMAL(10,2) | Required |
| `carbohydrates_100g` | `carbs` | DECIMAL(10,2) | Required |
| `fat_100g` | `fat` | DECIMAL(10,2) | Required |
| `fiber_100g` | `fiber` | DECIMAL(10,2) | Optional |
| `sodium_100g` | `sodium` | DECIMAL(10,2) | Optional |
| `sugars_100g` | `sugar` | DECIMAL(10,2) | Optional |
| `saturated-fat_100g` | `saturated_fat` | DECIMAL(10,2) | Optional |
| `categories` | `categories` | TEXT[] | Split by comma |
| `ingredients_text` | `ingredients` | TEXT | Full text |
| `allergens` | `allergens` | TEXT[] | Remove "en:" prefix |
| `serving_size` | `serving_size` | VARCHAR(50) | As-is |
| `nutriscore_grade` | `nutriscore_grade` | CHAR(1) | a-e |
| `nova_group` | `nova_group` | SMALLINT | 1-4 |
| `ecoscore_grade` | `ecoscore_grade` | CHAR(1) | a-e |
| `image_url` | `image_url` | TEXT | Product image |

---

## Error Handling

### Common Error Scenarios

| Scenario | HTTP Status | API Response | NomNom Action |
|----------|-------------|--------------|---------------|
| Product not found | 200 | `status: 0` | Show "Product not in database" |
| Invalid barcode | 200 | `status: 0` | Prompt manual entry |
| Rate limit exceeded | 429 | - | Show retry message, cache response |
| Network error | - | Exception | Show offline message, check local cache |
| Incomplete data | 200 | Missing fields | Use defaults, flag as "incomplete" |

### Python Error Handling Pattern

```python
from enum import Enum
from typing import Optional


class FoodLookupError(Enum):
    """Error types for food lookup."""
    NOT_FOUND = "PRODUCT_NOT_FOUND"
    RATE_LIMITED = "RATE_LIMIT_EXCEEDED"
    NETWORK_ERROR = "NETWORK_ERROR"
    INVALID_BARCODE = "INVALID_BARCODE"
    INCOMPLETE_DATA = "INCOMPLETE_DATA"


@dataclass
class FoodLookupResult:
    """Result of food lookup operation."""
    success: bool
    food_item: Optional[FoodItem] = None
    error: Optional[FoodLookupError] = None
    error_message: Optional[str] = None


def lookup_food_with_error_handling(barcode: str) -> FoodLookupResult:
    """
    Look up food with comprehensive error handling.
    """
    # Validate barcode format
    if not barcode.isdigit() or len(barcode) < 8:
        return FoodLookupResult(
            success=False,
            error=FoodLookupError.INVALID_BARCODE,
            error_message=f"Invalid barcode format: {barcode}"
        )

    try:
        service = OpenFoodFactsService()
        food_item = service.get_food_by_barcode(barcode)

        if not food_item:
            return FoodLookupResult(
                success=False,
                error=FoodLookupError.NOT_FOUND,
                error_message=f"Product not found: {barcode}"
            )

        # Check data quality
        if food_item.nutrition.calories == 0:
            return FoodLookupResult(
                success=False,
                error=FoodLookupError.INCOMPLETE_DATA,
                error_message="Product found but missing nutritional data"
            )

        return FoodLookupResult(success=True, food_item=food_item)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return FoodLookupResult(
                success=False,
                error=FoodLookupError.RATE_LIMITED,
                error_message="API rate limit exceeded. Please try again later."
            )
        raise

    except requests.exceptions.RequestException as e:
        return FoodLookupResult(
            success=False,
            error=FoodLookupError.NETWORK_ERROR,
            error_message=f"Network error: {str(e)}"
        )
```

---

## Caching Strategy

### Why Cache?

1. **Rate Limits**: Avoid hitting 100 req/min limit
2. **Performance**: Instant lookups for repeated scans
3. **Offline Support**: Access previously scanned items offline
4. **Cost Savings**: Reduce API calls (even though free)

### Cache Implementation

```python
from datetime import datetime, timedelta
from typing import Optional
import sqlite3


class FoodItemCache:
    """Local cache for food items."""

    def __init__(self, db_path: str = "food_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize SQLite cache database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cached_foods (
                barcode TEXT PRIMARY KEY,
                data JSON NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def get(self, barcode: str) -> Optional[dict]:
        """Get cached food item if not expired."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT data FROM cached_foods WHERE barcode = ? AND expires_at > ?",
            (barcode, datetime.now())
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
        return None

    def set(self, barcode: str, data: dict, ttl_days: int = 30):
        """Cache food item with expiration."""
        conn = sqlite3.connect(self.db_path)
        expires_at = datetime.now() + timedelta(days=ttl_days)

        conn.execute(
            """
            INSERT OR REPLACE INTO cached_foods (barcode, data, expires_at)
            VALUES (?, ?, ?)
            """,
            (barcode, json.dumps(data), expires_at)
        )
        conn.commit()
        conn.close()

    def clear_expired(self):
        """Remove expired cache entries."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM cached_foods WHERE expires_at <= ?", (datetime.now(),))
        conn.commit()
        conn.close()


# Usage in service
class CachedOpenFoodFactsService:
    """OpenFoodFacts service with caching."""

    def __init__(self):
        self.api_service = OpenFoodFactsService()
        self.cache = FoodItemCache()

    def get_food_by_barcode(self, barcode: str) -> Optional[FoodItem]:
        """Get food from cache or API."""
        # Check cache first
        cached_data = self.cache.get(barcode)
        if cached_data:
            return self._parse_cached_data(cached_data)

        # Fetch from API
        food_item = self.api_service.get_food_by_barcode(barcode)

        # Cache result if found
        if food_item:
            self.cache.set(barcode, self._serialize_food_item(food_item))

        return food_item
```

### Cache Invalidation Strategy

| Scenario | TTL | Strategy |
|----------|-----|----------|
| Complete product data | 30 days | Long cache, data rarely changes |
| Incomplete product data | 7 days | Shorter cache, may be updated |
| Popular products | 90 days | Extended cache |
| User-created items | Never expire | Permanent local storage |

---

## Data Quality Considerations

### Data Quality Indicators

OpenFoodFacts is crowd-sourced, so data quality varies:

```python
def assess_data_quality(food_item: FoodItem) -> str:
    """
    Assess data completeness and quality.

    Returns: 'complete', 'partial', or 'minimal'
    """
    score = 0

    # Required fields
    if food_item.nutrition.calories > 0:
        score += 3
    if food_item.nutrition.protein > 0:
        score += 2
    if food_item.nutrition.carbs > 0:
        score += 2
    if food_item.nutrition.fat > 0:
        score += 2

    # Optional but valuable fields
    if food_item.nutrition.fiber is not None:
        score += 1
    if food_item.nutrition.sodium is not None:
        score += 1
    if food_item.nutrition.sugar is not None:
        score += 1
    if food_item.brand:
        score += 1
    if food_item.ingredients:
        score += 1
    if food_item.serving_size:
        score += 1

    if score >= 12:
        return "complete"
    elif score >= 7:
        return "partial"
    else:
        return "minimal"
```

### Missing Data Handling

**Strategy:**
1. **Display warning**: "Incomplete nutritional data"
2. **Allow manual override**: Let users edit/complete data
3. **Mark in database**: Store `data_quality` field
4. **Suggest alternatives**: Offer text search for similar products

### Data Validation

```python
def validate_nutritional_data(nutrition: NutritionalData) -> bool:
    """
    Validate nutritional data for sanity.

    Common issues:
    - Missing required fields (calories, protein, carbs, fat)
    - Impossible values (negative numbers, >100g for percentages)
    - Inconsistent totals (fat + carbs + protein > 100g)
    """
    # Check required fields exist
    if nutrition.calories <= 0:
        return False

    # Validate ranges
    if any(v < 0 for v in [nutrition.protein, nutrition.carbs, nutrition.fat]):
        return False

    # Macros should sum to ~100g or less (accounting for water/ash)
    macro_sum = nutrition.protein + nutrition.carbs + nutrition.fat
    if macro_sum > 110:  # Allow 10% margin for measurement error
        return False

    # Calories should roughly match macros (4/4/9 rule)
    estimated_calories = (
        nutrition.protein * 4 +
        nutrition.carbs * 4 +
        nutrition.fat * 9
    )

    # Allow 20% margin for fiber, alcohol, etc.
    if abs(nutrition.calories - estimated_calories) > nutrition.calories * 0.2:
        return False

    return True
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_openfoodfacts_service.py
import pytest
from unittest.mock import Mock, patch
from services.food_database_service import OpenFoodFactsService, FoodItem


@pytest.fixture
def mock_api_response():
    """Mock OpenFoodFacts API response."""
    return {
        "code": "3017620422003",
        "product_name": "Nutella",
        "brands": "Ferrero",
        "nutriments": {
            "energy-kcal_100g": 539,
            "proteins_100g": 6.3,
            "carbohydrates_100g": 57.5,
            "fat_100g": 30.9,
            "fiber_100g": 0,
            "sodium_100g": 0.0428,
            "sugars_100g": 56.3,
            "saturated-fat_100g": 10.6
        },
        "categories": "Spreads,Chocolate spreads",
        "allergens": "en:milk,en:nuts",
        "serving_size": "15 g",
        "nutriscore_grade": "e",
        "nova_group": 4
    }


def test_get_food_by_barcode_success(mock_api_response):
    """Test successful food lookup."""
    service = OpenFoodFactsService()

    with patch.object(service.api.product, 'get', return_value=mock_api_response):
        food_item = service.get_food_by_barcode("3017620422003")

    assert food_item is not None
    assert food_item.barcode == "3017620422003"
    assert food_item.name == "Nutella"
    assert food_item.nutrition.calories == 539
    assert food_item.nutrition.protein == 6.3
    assert "milk" in food_item.allergens


def test_get_food_by_barcode_not_found():
    """Test product not found."""
    service = OpenFoodFactsService()

    with patch.object(service.api.product, 'get', return_value=None):
        food_item = service.get_food_by_barcode("invalid_barcode")

    assert food_item is None


def test_parse_allergens():
    """Test allergen parsing."""
    service = OpenFoodFactsService()
    product = {"allergens": "en:milk,en:nuts,en:soybeans"}

    # This would be part of _parse_product method
    allergens_str = product.get("allergens", "")
    allergens = [a.replace("en:", "").strip() for a in allergens_str.split(",")]

    assert allergens == ["milk", "nuts", "soybeans"]
```

### Integration Tests

```python
# tests/integration/test_openfoodfacts_integration.py
import pytest
from services.food_database_service import OpenFoodFactsService


@pytest.mark.integration
def test_real_api_lookup():
    """Test against real OpenFoodFacts API."""
    service = OpenFoodFactsService()

    # Use well-known product (Nutella)
    food_item = service.get_food_by_barcode("3017620422003")

    assert food_item is not None
    assert food_item.name.lower() == "nutella"
    assert food_item.nutrition.calories > 0
    assert food_item.nutrition.protein > 0


@pytest.mark.integration
def test_api_rate_limiting():
    """Test rate limiting behavior."""
    service = OpenFoodFactsService()

    # Make 10 requests (well under 100/min limit)
    for i in range(10):
        food_item = service.get_food_by_barcode("3017620422003")
        assert food_item is not None
```

### E2E Tests (Playwright)

```typescript
// tests/e2e/barcode-scan.spec.ts
import { test, expect } from '@playwright/test';

test('scan barcode and display nutritional info', async ({ page }) => {
  await page.goto('/food-entry');

  // Click scan button
  await page.click('button:has-text("Scan Barcode")');

  // Mock barcode scan result
  await page.evaluate(() => {
    window.dispatchEvent(new CustomEvent('barcode-scanned', {
      detail: { barcode: '3017620422003' }
    }));
  });

  // Wait for API call and display
  await expect(page.locator('h1')).toContainText('Nutella');
  await expect(page.locator('[data-testid="calories"]')).toContainText('539');
  await expect(page.locator('[data-testid="protein"]')).toContainText('6.3');
});
```

---

## Summary & Recommendations

### ✅ OpenFoodFacts is Ideal for NomNom Because:

1. **Free & Open**: No API key, no cost, open data
2. **Large Database**: 2.8M+ products
3. **Rich Data**: Calories, macros, allergens, ingredients, scores
4. **Python SDK**: Official library available
5. **Active Community**: Continuously updated
6. **No Authentication**: For read operations

### ⚠️ Considerations:

1. **Data Quality Varies**: Implement validation and quality scoring
2. **Rate Limits**: Cache aggressively (100 req/min)
3. **Incomplete Data**: Handle missing fields gracefully
4. **Crowd-Sourced**: May have errors or outdated info
5. **No SLA**: Free service, no uptime guarantees

### 🚀 Implementation Checklist:

- [ ] Install `openfoodfacts` Python SDK
- [ ] Implement `OpenFoodFactsService` with error handling
- [ ] Create database schema for caching food items
- [ ] Implement local cache with 30-day TTL
- [ ] Add data quality assessment
- [ ] Validate nutritional data sanity
- [ ] Create API endpoint: `GET /api/v1/foods/barcode/{barcode}`
- [ ] Add unit tests for service layer
- [ ] Add integration tests for real API
- [ ] Implement frontend barcode scanner
- [ ] Add error handling for "product not found"
- [ ] Display data quality warnings
- [ ] Allow manual data entry/override

### 📚 Alternative APIs (If Needed):

| API | Pros | Cons | Cost |
|-----|------|------|------|
| **FatSecret** | High quality, commercial data | Requires API key | $$ (paid) |
| **Nutritionix** | Good US coverage | Limited free tier | $$ (paid) |
| **USDA FoodData** | Highly accurate | Limited to US foods, no barcodes | Free |

**Recommendation:** Start with OpenFoodFacts. Implement fallback to manual entry. Consider FatSecret/Nutritionix as premium upgrade later.

---

## Sources

- [OpenFoodFacts API Introduction](https://openfoodfacts.github.io/openfoodfacts-server/api/)
- [OpenFoodFacts API Tutorial](https://openfoodfacts.github.io/openfoodfacts-server/api/tutorial-off-api/)
- [OpenFoodFacts Data & SDKs](https://world.openfoodfacts.org/data)
- [OpenFoodFacts Python SDK](https://pypi.org/project/openfoodfacts/)
- [OpenFoodFacts API Reference CheatSheet](https://openfoodfacts.github.io/openfoodfacts-server/api/ref-cheatsheet/)
- [Open Food Facts API - PublicAPI](https://publicapi.dev/open-food-facts-api)
- [Open Food Facts API - Public APIs Directory](https://publicapis.io/open-food-facts-api)
- [Open Food Facts API - Gigasheet](https://www.gigasheet.com/no-code-api/open-food-facts-api)
- [Open Food Facts API - Free API Hub](https://freeapihub.com/apis/open-food-facts-api)

---

## Addendum: Advanced API Capabilities

### Bulk Barcode Lookup

The API supports querying **multiple barcodes in a single request** using comma-separated codes:

```bash
curl "https://world.openfoodfacts.net/api/v2/product?code=3263859883713,8037011606013&fields=code,product_name,brands,nutriments"
```

**Response Format:**
```json
{
  "products": [
    {"code": "3263859883713", "product_name": "...", ...},
    {"code": "8037011606013", "product_name": "...", ...}
  ]
}
```

**Use Case for NomNom:**
- Batch scanning: If users scan multiple items in quick succession, queue barcodes and fetch in batches
- Reduces API request count (important for rate limits)
- Faster response when scanning grocery haul

**Implementation Pattern:**
```python
class BatchFoodLookupService:
    """Batch lookup service for multiple barcodes."""

    def __init__(self, batch_size: int = 10, batch_delay_seconds: float = 2.0):
        self.api = openfoodfacts.API(user_agent="NomNom/1.0")
        self.batch_size = batch_size
        self.batch_delay = batch_delay_seconds
        self.queue: list[str] = []

    async def add_to_queue(self, barcode: str) -> None:
        """Add barcode to batch queue."""
        self.queue.append(barcode)

        if len(self.queue) >= self.batch_size:
            await self.flush_queue()

    async def flush_queue(self) -> dict[str, FoodItem]:
        """Process queued barcodes in batch."""
        if not self.queue:
            return {}

        barcodes = ",".join(self.queue[:self.batch_size])
        self.queue = self.queue[self.batch_size:]

        # Batch API call
        response = requests.get(
            "https://world.openfoodfacts.net/api/v2/product",
            params={
                "code": barcodes,
                "fields": "code,product_name,brands,nutriments,allergens"
            },
            headers={"User-Agent": "NomNom/1.0"}
        )

        results = {}
        for product in response.json().get("products", []):
            results[product["code"]] = self._parse_product(product)

        return results
```

---

### Text Search API

When barcode scanning fails or for non-packaged foods, use the **search endpoint**:

**Endpoint:**
```
GET /api/v2/search?{parameters}
```

**Search Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `search_terms` | string | Free-text product search | `search_terms=greek yogurt` |
| `categories_tags_en` | string | Filter by category | `categories_tags_en=yogurts` |
| `brands_tags` | string | Filter by brand | `brands_tags=danone` |
| `nutrition_grades_tags` | string | Filter by Nutri-Score | `nutrition_grades_tags=a` |
| `nova_groups_tags` | string | Filter by NOVA group | `nova_groups_tags=1` |
| `sort_by` | string | Sort field | `sort_by=popularity` or `sort_by=last_modified_t` |
| `page_size` | int | Results per page (max 100) | `page_size=20` |
| `page` | int | Page number | `page=1` |
| `fields` | string | Limit returned fields | `fields=code,product_name` |

**Example Search:**
```bash
# Find healthy breakfast cereals
curl "https://world.openfoodfacts.net/api/v2/search?categories_tags_en=breakfast-cereals&nutrition_grades_tags=a,b&page_size=10&fields=code,product_name,brands,nutriscore_grade"
```

**Response Format:**
```json
{
  "count": 1523,
  "page": 1,
  "page_count": 153,
  "page_size": 10,
  "products": [
    {"code": "...", "product_name": "...", ...}
  ],
  "skip": 0
}
```

**Use Case for NomNom:**
- Fallback when barcode scan fails
- Search for generic foods (e.g., "banana", "chicken breast")
- Product discovery and alternatives
- Filtering by nutrition quality (Nutri-Score A/B)

**Implementation:**
```python
async def search_foods(
    query: str,
    category: Optional[str] = None,
    min_nutriscore: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
) -> dict:
    """Search foods by text query with filters."""
    params = {
        "search_terms": query,
        "page": page,
        "page_size": min(page_size, 100),
        "fields": "code,product_name,brands,nutriments,nutriscore_grade"
    }

    if category:
        params["categories_tags_en"] = category

    if min_nutriscore:
        # Filter to A, B grades
        params["nutrition_grades_tags"] = ",".join(["a", "b"][:ord(min_nutriscore.lower()) - ord("a") + 1])

    response = requests.get(
        "https://world.openfoodfacts.net/api/v2/search",
        params=params,
        headers={"User-Agent": "NomNom/1.0"}
    )

    return response.json()
```

---

### Auto-Suggestion Endpoints

The API provides **autocomplete suggestions** for various field types:

**Endpoint:**
```
GET /cgi/suggest.pl?tagtype={type}&term={query}
```

**Supported Tag Types:**

| Tag Type | Description | Example Query |
|----------|-------------|---------------|
| `brands` | Brand names | `term=nest` → "Nestle", "Nescafe" |
| `categories` | Product categories | `term=yogu` → "Yogurts", "Greek yogurts" |
| `ingredients` | Ingredient names | `term=choc` → "Chocolate", "Chocolate chips" |
| `allergens` | Allergen types | `term=milk` → "Milk", "Milk protein" |
| `stores` | Store names | `term=walm` → "Walmart", "Walgreens" |
| `countries` | Countries | `term=fra` → "France", "French Guiana" |
| `labels` | Labels (organic, fair trade) | `term=org` → "Organic", "Organic EU" |

**Example:**
```bash
curl "https://world.openfoodfacts.net/cgi/suggest.pl?tagtype=brands&term=dan"
```

**Response:**
```json
{
  "suggestions": [
    {"id": "danone", "name": "Danone"},
    {"id": "dannon", "name": "Dannon"}
  ]
}
```

**Use Case for NomNom:**
- Brand autocomplete in manual food entry
- Category selection dropdowns
- Allergen filtering UI
- Store location tracking

---

### Data Quality Detection

Use the `misc_tags` field to **detect missing or incomplete data**:

**Request:**
```bash
curl "https://world.openfoodfacts.net/api/v2/product/3017620422003.json?fields=misc_tags"
```

**Common `misc_tags` Values:**

| Tag | Meaning | Action |
|-----|---------|--------|
| `en:nutriscore-missing-nutrition-data-sodium` | Missing sodium value | Request user input |
| `en:nutriscore-missing-nutrition-data-fiber` | Missing fiber value | Mark as incomplete |
| `en:nutrition-not-enough-data-to-compute-nutrition-score` | Insufficient data | Warn user |
| `en:packagings-not-complete` | Incomplete packaging info | Low priority |

**Implementation:**
```python
def check_data_completeness(product: dict) -> list[str]:
    """Identify missing nutritional data."""
    misc_tags = product.get("misc_tags", [])
    missing_fields = []

    for tag in misc_tags:
        if "nutriscore-missing-nutrition-data" in tag:
            # Extract field name: "en:nutriscore-missing-nutrition-data-sodium" → "sodium"
            field = tag.split("-")[-1]
            missing_fields.append(field)

    return missing_fields

# Usage
missing = check_data_completeness(product)
if missing:
    print(f"Missing data: {', '.join(missing)}")
    # Prompt user to manually enter these values
```

---

### Edit History and Audit Trail

Retrieve **product edit history** using the `blame` parameter:

**Request:**
```bash
curl "https://world.openfoodfacts.net/api/v2/product/3017620422003.json?blame=1"
```

**Response Enhancement:**
```json
{
  "product": {
    "product_name": "Nutella",
    "product_name_t": 1703001234,
    "product_name_userid": "john-contributor",
    "product_name_rev": 45,
    "nutriments": {...},
    "nutriments_t": 1703002456,
    "nutriments_userid": "nutrition-bot"
  }
}
```

**Field Suffixes:**
- `_t`: Unix timestamp of last edit
- `_userid`: Username of contributor
- `_rev`: Revision number

**Use Case for NomNom:**
- Display data freshness ("Last updated 2 weeks ago")
- Trust scoring (bot-edited vs. human-verified)
- Trigger re-sync for stale data (>90 days old)

---

### Future Consideration: Write API

If NomNom users manually enter products not in the database, we can **contribute back** to OpenFoodFacts:

**Endpoint:**
```
POST /cgi/product_jqm2.pl
```

**Required Parameters:**
- `user_id`: OpenFoodFacts username
- `password`: User password (or session cookie)
- `code`: Barcode
- `product_name`: Product name
- `brands`: Brand name
- `quantity`: Package size
- `nutrition_data_per`: "100g" or "serving"
- `nutriment_energy`: Energy value
- `nutriment_energy_unit`: "kJ" or "kcal"
- `nutriment_proteins`: Protein (g)
- `nutriment_carbohydrates`: Carbs (g)
- `nutriment_fat`: Fat (g)

**Adding Values (Append vs. Replace):**
- Regular field: `categories=Yogurts` (replaces)
- Append mode: `add_categories=Greek yogurts` (appends)

**Use Case for NomNom:**
- Optional "Contribute to OpenFoodFacts" feature
- Gamification: "You've helped add 5 products!"
- Community benefit (improved data quality)

**Implementation Consideration:**
- Requires user consent
- Should validate data quality before submission
- Rate limited separately from read operations

---

**Document Version:** 1.1
**Last Updated:** 2025-12-28
**Changelog:**
- Added bulk barcode lookup capabilities
- Added text search API documentation
- Added auto-suggestion endpoints
- Added data quality detection using misc_tags
- Added edit history/audit trail features
- Added write API overview for future consideration

**Maintained By:** NomNom Development Team
