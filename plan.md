# NomNom - Complete Nutrition Tracking System

## Overview

Build a comprehensive nutrition tracking application with FastAPI backend, PostgreSQL database, and Svelte 5 frontend
for a shared household (users: `nyntjie` and `unit`).

### Core Features

- **Shared household meals** with percentage-based portion splits
  *(Example: Chicken Stir Fry → Nyntjie 60%, Unit 40%)*
- **Food item tracking** via barcode scanning, search, or manual entry
- **Meal templates** (reusable recipes with multiple ingredients)
- **Photo uploads** for meals with item tagging
- **Custom food overrides** (manually override API nutritional data)
- **Meal planning** (daily/weekly meal prep)
- **Shopping list generation** from planned meals
- **Goal tracking** with dashboard and progress visualization

---

## Technology Stack

| Layer                | Technology                   | Purpose                                                                      |
|----------------------|------------------------------|------------------------------------------------------------------------------|
| **Frontend**         | Svelte 5 (SvelteKit)         | Mobile-first UI with runes-based reactivity                                  |
| **Backend**          | FastAPI (async)              | REST API with auto-generated OpenAPI docs                                    |
| **Database**         | MongoDB 8.0                  | All data (OpenFoodFacts products + app data)                                 |
| **MongoDB Client**   | Motor (async)                | Async MongoDB driver for Python                                              |
| **Barcode Scanning** | html5-qrcode or QuaggaJS     | Camera-based barcode recognition                                             |
| **File Storage**     | Local filesystem (MVP)       | Meal photo storage                                                           |
| **Styling**          | Tailwind CSS                 | Utility-first styling (reuse from `/Users/dawiddutoit/projects/play/svelte`) |
| **Package Manager**  | uv (backend), npm (frontend) | Dependency management                                                        |

**Why MongoDB-only?**
- OpenFoodFacts already provides MongoDB dump (~3M products)
- Simpler architecture: one database, one connection pool
- No caching layer needed - query products directly
- Flexible schema perfect for MVP iteration
- Motor provides excellent async support for FastAPI

---

## MongoDB Collections

### Core Collections

#### **users**

```javascript
{
  _id: ObjectId("..."),
  username: "nyntjie",          // Unique: 'nyntjie', 'unit'
  display_name: "Nyntjie",
  goals: {
    daily_calories: 2000,
    daily_protein_g: 150.0,
    daily_carbs_g: 250.0,
    daily_fat_g: 65.0
  },
  created_at: ISODate("2025-01-28T10:00:00Z"),
  updated_at: ISODate("2025-01-28T10:00:00Z")
}
```

**Indexes:**
```javascript
db.users.createIndex({ username: 1 }, { unique: true })
```

### Food Collections

#### **products** (OpenFoodFacts - imported from dump)

**Purpose**: ~3M OpenFoodFacts products (imported via mongorestdump)

```javascript
{
  _id: ObjectId("..."),
  code: "3017620422003",  // Barcode
  product_name: "Nutella",
  brands: "Ferrero",
  quantity: "750g",
  nutriments: {
    energy_100g: 539,
    proteins_100g: 6.3,
    carbohydrates_100g: 57.5,
    fat_100g: 30.9,
    fiber_100g: null,
    sugars_100g: 56.3,
    sodium_100g: 0.107
  },
  images: {
    front_url: "https://...",
    ingredients_url: "https://...",
    nutrition_url: "https://..."
  }
  // ... many other OpenFoodFacts fields
}
```

**Indexes** (already present in dump):
```javascript
db.products.createIndex({ code: 1 }, { unique: true })
db.products.createIndex({ product_name: "text", brands: "text" })
```

#### **custom_foods** (User-created and overridden foods)

**Purpose**: Custom food items created manually or to override OpenFoodFacts data

```javascript
{
  _id: ObjectId("..."),
  barcode: "123456789",         // Optional - null for manual items
  name: "Homemade Banana Bread",
  brand: null,
  serving_size: "1 slice",
  serving_size_g: 80.0,

  // Macronutrients (per serving)
  nutrients: {
    calories: 105.0,
    protein_g: 2.5,
    carbs_g: 18.0,
    fat_g: 3.2,
    fiber_g: 1.5,
    sugar_g: 8.0,
    sodium_mg: 120.0,
    saturated_fat_g: 0.8
  },

  tags: ["homemade", "breakfast"],
  created_by: "nyntjie",        // Username who created it
  overrides_openfoodfacts: false,  // True if replacing OpenFoodFacts data
  created_at: ISODate("2025-01-28T10:00:00Z"),
  updated_at: ISODate("2025-01-28T10:00:00Z")
}
```

**Indexes:**
```javascript
db.custom_foods.createIndex({ barcode: 1 }, { unique: true, sparse: true })
db.custom_foods.createIndex({ name: "text", brand: "text" })
db.custom_foods.createIndex({ created_by: 1 })
```

### Meal Templates (Reusable Recipes)

#### **meal_templates**

```javascript
{
  _id: ObjectId("..."),
  name: "Chicken Stir Fry",
  description: "Quick and healthy chicken stir fry with vegetables",
  meal_type: "dinner",          // 'breakfast', 'lunch', 'dinner', 'snack'
  servings: 2.0,                 // How many servings this recipe makes
  preparation_time_mins: 30,

  // Embedded ingredients (no separate collection needed)
  ingredients: [
    {
      food_ref: {
        source: "products",     // 'products' or 'custom_foods'
        id: ObjectId("..."),    // Reference to product or custom_food
        barcode: "1234567"      // Cached for lookup
      },
      quantity: 400.0,
      unit: "g",                // 'g', 'ml', 'serving', 'cup'
      notes: "Boneless, skinless",
      display_order: 0
    },
    {
      food_ref: {
        source: "custom_foods",
        id: ObjectId("..."),
        barcode: null
      },
      quantity: 200.0,
      unit: "g",
      notes: "Mixed bell peppers",
      display_order: 1
    }
  ],

  created_by: "nyntjie",        // Username
  is_favorite: false,
  tags: ["healthy", "quick", "asian"],
  created_at: ISODate("2025-01-28T10:00:00Z"),
  updated_at: ISODate("2025-01-28T10:00:00Z")
}
```

**Indexes:**
```javascript
db.meal_templates.createIndex({ created_by: 1 })
db.meal_templates.createIndex({ meal_type: 1 })
db.meal_templates.createIndex({ name: "text", description: "text" })
```

### Meal Consumption (Daily Tracking)

#### **meal_consumption** (What users actually ate)

```javascript
{
  _id: ObjectId("..."),

  // Reference to meal template (if using a template) OR food item (if simple item)
  meal_template_id: ObjectId("..."),  // null if ad-hoc food item
  food_ref: {                         // null if meal template
    source: "products",               // 'products' or 'custom_foods'
    id: ObjectId("..."),
    barcode: "1234567"
  },

  consumed_at: ISODate("2025-01-28T18:30:00Z"),
  meal_type: "dinner",               // 'breakfast', 'lunch', 'dinner', 'snack'

  // Embedded user splits (no separate collection)
  user_portions: [
    {
      username: "nyntjie",
      portion_percentage: 60.0,      // 60% of the meal
      quantity_override: null,       // Optional override
      unit_override: null
    },
    {
      username: "unit",
      portion_percentage: 40.0,
      quantity_override: null,
      unit_override: null
    }
  ],

  photos: [
    {
      file_path: "uploads/meals/20250128_183000.jpg",
      thumbnail_path: "uploads/meals/20250128_183000_thumb.jpg",
      uploaded_by: "nyntjie",
      created_at: ISODate("2025-01-28T18:31:00Z")
    }
  ],

  notes: "Extra vegetables added",
  created_at: ISODate("2025-01-28T18:30:00Z"),
  updated_at: ISODate("2025-01-28T18:30:00Z")
}
```

**Indexes:**
```javascript
db.meal_consumption.createIndex({ consumed_at: -1 })
db.meal_consumption.createIndex({ "user_portions.username": 1, consumed_at: -1 })
db.meal_consumption.createIndex({ meal_type: 1 })
```

### Meal Planning

#### **meal_plans**

```javascript
{
  _id: ObjectId("..."),
  planned_by: "nyntjie",        // Username who created the plan
  meal_template_id: ObjectId("..."),
  planned_date: ISODate("2025-02-05T00:00:00Z"),  // Date only
  meal_type: "dinner",          // 'breakfast', 'lunch', 'dinner', 'snack'
  servings: 2.0,
  notes: "Prepare ingredients night before",
  is_completed: false,          // True when converted to meal_consumption
  completed_at: null,           // Timestamp when marked complete
  created_at: ISODate("2025-01-28T10:00:00Z")
}
```

**Indexes:**
```javascript
db.meal_plans.createIndex({ planned_by: 1, planned_date: 1 })
db.meal_plans.createIndex({ planned_date: 1 })
db.meal_plans.createIndex({ is_completed: 1 })
```

### Shopping Lists

#### **shopping_lists**

```javascript
{
  _id: ObjectId("..."),
  created_by: "nyntjie",        // Username
  name: "Weekly Groceries - Feb 3-9",
  start_date: ISODate("2025-02-03T00:00:00Z"),
  end_date: ISODate("2025-02-09T00:00:00Z"),
  generated_from_meal_plans: true,  // True if auto-generated

  // Embedded items (no separate collection)
  items: [
    {
      food_ref: {
        source: "products",     // 'products', 'custom_foods', or null
        id: ObjectId("..."),
        barcode: "1234567"
      },
      item_name: "Chicken breast",  // Cached name
      quantity: 800.0,
      unit: "g",
      is_purchased: false,
      notes: "Organic if available",
      display_order: 0
    },
    {
      food_ref: null,           // Manual item (no food ref)
      item_name: "Paper towels",
      quantity: 2.0,
      unit: "rolls",
      is_purchased: true,
      notes: null,
      display_order: 1
    }
  ],

  created_at: ISODate("2025-01-28T10:00:00Z"),
  updated_at: ISODate("2025-01-28T10:00:00Z")
}
```

**Indexes:**
```javascript
db.shopping_lists.createIndex({ created_by: 1, created_at: -1 })
db.shopping_lists.createIndex({ start_date: 1, end_date: 1 })
```

---

## API Endpoints

### Users & Goals

| Method | Endpoint                      | Description                    |
|--------|-------------------------------|--------------------------------|
| GET    | `/api/users`                  | List all users (nyntjie, unit) |
| GET    | `/api/users/{username}`       | Get user profile               |
| GET    | `/api/users/{username}/goals` | Get user's goals               |
| PUT    | `/api/users/{username}/goals` | Update user's goals            |

### Food Items

| Method | Endpoint                                    | Description                                               |
|--------|---------------------------------------------|-----------------------------------------------------------|
| GET    | `/api/food/search?q={query}`                | Search by name (custom_foods → products text search)      |
| GET    | `/api/food/barcode/{code}`                  | Lookup by barcode (custom_foods → products → not found)   |
| GET    | `/api/food/{id}?source={source}`            | Get food item details (source: products or custom_foods)  |
| POST   | `/api/food`                                 | Create custom food item                                   |
| PUT    | `/api/food/{id}`                            | Update custom food item                                   |
| DELETE | `/api/food/{id}`                            | Delete custom food item                                   |
| GET    | `/api/food/recent?user={username}&limit=10` | Get recently consumed items (from meal_consumption)       |

**Lookup Strategy** (barcode):
1. Check `custom_foods` collection first (user overrides/custom items)
2. If not found, query `products` collection (OpenFoodFacts)
3. If not found, return 404 → user can create custom item
4. Transform OpenFoodFacts document format to app format on the fly

### Meals (Daily Consumption)

| Method | Endpoint                                       | Description                             |
|--------|------------------------------------------------|-----------------------------------------|
| GET    | `/api/meals?user={username}&date={YYYY-MM-DD}` | Get user's meals for specific date      |
| GET    | `/api/meals/{id}`                              | Get meal details with users and splits  |
| POST   | `/api/meals`                                   | Add meal consumption (with user splits) |
| PUT    | `/api/meals/{id}`                              | Update meal (quantity, users, splits)   |
| DELETE | `/api/meals/{id}`                              | Remove meal entry                       |
| POST   | `/api/meals/{id}/photo`                        | Upload photo for meal                   |

**Example POST /api/meals**:

```json
{
  "meal_template_id": 5,
  "food_item_id": null,
  "consumed_at": "2025-01-28T18:30:00Z",
  "meal_type": "dinner",
  "users": [
    {
      "username": "nyntjie",
      "portion_percentage": 60.0
    },
    {
      "username": "unit",
      "portion_percentage": 40.0
    }
  ],
  "notes": "Made with extra vegetables"
}
```

### Meal Templates (Recipes)

| Method | Endpoint                              | Description                   |
|--------|---------------------------------------|-------------------------------|
| GET    | `/api/templates`                      | List all meal templates       |
| GET    | `/api/templates/{id}`                 | Get template with ingredients |
| POST   | `/api/templates`                      | Create new meal template      |
| PUT    | `/api/templates/{id}`                 | Update template               |
| DELETE | `/api/templates/{id}`                 | Delete template               |
| POST   | `/api/templates/{id}/items`           | Add ingredient to template    |
| PUT    | `/api/templates/{id}/items/{item_id}` | Update ingredient             |
| DELETE | `/api/templates/{id}/items/{item_id}` | Remove ingredient             |

### Meal Planning

| Method | Endpoint                                             | Description                                       |
|--------|------------------------------------------------------|---------------------------------------------------|
| GET    | `/api/plans?user={username}&start={date}&end={date}` | Get meal plans for date range                     |
| POST   | `/api/plans`                                         | Create meal plan                                  |
| PUT    | `/api/plans/{id}`                                    | Update meal plan                                  |
| DELETE | `/api/plans/{id}`                                    | Delete meal plan                                  |
| POST   | `/api/plans/{id}/complete`                           | Mark plan as completed (creates meal consumption) |

### Shopping Lists

| Method | Endpoint                                   | Description                                |
|--------|--------------------------------------------|--------------------------------------------|
| GET    | `/api/shopping-lists?user={username}`      | Get user's shopping lists                  |
| GET    | `/api/shopping-lists/{id}`                 | Get shopping list with items               |
| POST   | `/api/shopping-lists/generate`             | Generate list from meal plans (date range) |
| POST   | `/api/shopping-lists`                      | Create manual shopping list                |
| PUT    | `/api/shopping-lists/{id}`                 | Update shopping list                       |
| DELETE | `/api/shopping-lists/{id}`                 | Delete shopping list                       |
| POST   | `/api/shopping-lists/{id}/items`           | Add item to list                           |
| PUT    | `/api/shopping-lists/{id}/items/{item_id}` | Update item (mark purchased)               |
| DELETE | `/api/shopping-lists/{id}/items/{item_id}` | Remove item                                |

### Dashboard

| Method | Endpoint                                      | Description                     |
|--------|-----------------------------------------------|---------------------------------|
| GET    | `/api/dashboard/{username}?date={YYYY-MM-DD}` | Daily summary (totals vs goals) |
| GET    | `/api/dashboard/{username}/week?start={date}` | Weekly overview                 |

---

## Project Structure

### Backend (FastAPI)

```
/Users/dawiddutoit/projects/play/nomnom/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app factory
│   ├── config.py                  # Settings (env vars)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py               # Dependency injection
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py         # Main router
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── users.py
│   │           ├── foods.py
│   │           ├── meals.py      # Daily consumption
│   │           ├── templates.py  # Meal templates
│   │           ├── plans.py      # Meal planning
│   │           ├── shopping.py   # Shopping lists
│   │           └── dashboard.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py              # Base + TimestampMixin
│   │   ├── user.py              # User, UserGoal
│   │   ├── food.py              # FoodItem
│   │   ├── meal.py              # MealTemplate, MealTemplateItem
│   │   ├── consumption.py       # MealConsumption, MealConsumptionUser
│   │   ├── photo.py             # MealPhoto
│   │   ├── plan.py              # MealPlan
│   │   └── shopping.py          # ShoppingList, ShoppingListItem
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── food.py
│   │   ├── meal.py
│   │   ├── consumption.py
│   │   ├── plan.py
│   │   └── shopping.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── openfoodfacts.py     # OpenFoodFacts API
│   │   ├── usda.py              # USDA FoodData Central API
│   │   ├── food_lookup.py       # Unified food lookup service
│   │   ├── nutrition.py         # Nutrition calculations
│   │   ├── meal_service.py      # Meal business logic
│   │   └── shopping_service.py  # Shopping list generation
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py          # Async engine + session
│   ├── core/
│   │   ├── __init__.py
│   │   └── exceptions.py        # Custom exceptions
│   └── utils/
│       ├── __init__.py
│       └── files.py             # File upload helpers
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── scripts/
│   ├── seed_users.py            # Create nyntjie and unit
│   ├── seed_sample_data.py      # Sample meals, foods
│   └── reset_db.sh
├── uploads/
│   └── meals/                   # Photo storage
├── tests/
│   ├── conftest.py
│   ├── api/
│   │   └── v1/
│   │       ├── test_meals.py
│   │       ├── test_templates.py
│   │       └── test_shopping.py
│   └── services/
│       └── test_food_lookup.py
├── docker-compose.yml
├── .env.example
├── .env
├── alembic.ini
├── pyproject.toml
├── main.py                      # Entry point
└── CLAUDE.md
```

### Frontend (SvelteKit)

```
frontend/
├── src/
│   ├── routes/
│   │   ├── +page.svelte         # Landing/redirect
│   │   ├── nyntjie/
│   │   │   ├── +page.svelte     # Day planner
│   │   │   ├── +layout.svelte   # User layout
│   │   │   ├── dashboard/
│   │   │   │   └── +page.svelte
│   │   │   ├── plans/
│   │   │   │   └── +page.svelte # Meal planning
│   │   │   ├── shopping/
│   │   │   │   └── +page.svelte
│   │   │   └── settings/
│   │   │       └── +page.svelte
│   │   └── unit/
│   │       └── [same structure as nyntjie]
│   ├── lib/
│   │   ├── components/
│   │   │   ├── DayPlanner.svelte
│   │   │   ├── MealCard.svelte
│   │   │   ├── MealSplitSelector.svelte  # User split percentage UI
│   │   │   ├── AddMealModal.svelte
│   │   │   ├── BarcodeScanner.svelte
│   │   │   ├── FoodSearch.svelte
│   │   │   ├── MacroProgress.svelte
│   │   │   ├── MealTemplateBuilder.svelte
│   │   │   ├── MealPlanner.svelte
│   │   │   ├── ShoppingList.svelte
│   │   │   └── PhotoUpload.svelte
│   │   ├── stores/
│   │   │   ├── user.ts
│   │   │   ├── meals.ts
│   │   │   └── plans.ts
│   │   └── api/
│   │       └── client.ts
│   └── app.html
├── static/
├── svelte.config.js
├── package.json
├── tailwind.config.js
└── .env
```

---

## Implementation Plan

### Phase 1: Foundation (Backend)

**1. Environment & Dependencies**

```bash
# Update pyproject.toml
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "motor>=3.6.0",              # Async MongoDB driver
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    "python-dotenv>=1.0.0",
    "python-multipart>=0.0.12",  # For file uploads
    "pillow>=10.0.0",            # For image processing
]
dev = ["pytest>=8.3.0", "pytest-asyncio>=0.24.0", "pytest-mongodb>=2.0.0", "httpx", "ruff>=0.8.0", "mypy>=1.13.0"]
```

**Removed dependencies:**
- ❌ SQLAlchemy
- ❌ asyncpg
- ❌ Alembic

**2. Docker Compose**

```yaml
services:
  mongodb:
    image: mongo:8.0
    container_name: nomnom-mongodb
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: off

volumes:
  mongodb_data:
```

**3. Environment Variables (.env)**

```env
# MongoDB (all data)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=off

# File storage
UPLOAD_DIR=./uploads
```

**4. Create Project Structure**

```
app/
├── __init__.py
├── main.py                    # FastAPI app
├── config.py                  # Settings (Pydantic)
├── api/
│   ├── __init__.py
│   ├── deps.py               # Dependencies
│   └── v1/
│       ├── __init__.py
│       ├── router.py
│       └── endpoints/
│           ├── users.py
│           ├── foods.py
│           ├── meals.py
│           ├── templates.py
│           ├── plans.py
│           ├── shopping.py
│           └── dashboard.py
├── db/
│   ├── __init__.py
│   └── mongodb.py            # Motor client
├── schemas/
│   ├── __init__.py
│   ├── user.py
│   ├── food.py
│   ├── meal.py
│   ├── consumption.py
│   ├── plan.py
│   └── shopping.py
├── services/
│   ├── __init__.py
│   ├── food_lookup.py        # Unified food lookup
│   ├── meal_service.py
│   ├── nutrition.py
│   └── shopping_service.py
├── core/
│   ├── __init__.py
│   └── exceptions.py
└── utils/
    ├── __init__.py
    └── files.py
```

**5. MongoDB Client Setup**

Create `app/db/mongodb.py`:

```python
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None

async def connect_to_mongo():
    MongoDB.client = AsyncIOMotorClient(settings.MONGODB_URL)

async def close_mongo_connection():
    MongoDB.client.close()

def get_database():
    return MongoDB.client[settings.MONGODB_DATABASE]
```

**6. Create Indexes**

Create `scripts/create_indexes.py`:

```python
async def create_indexes():
    db = get_database()

    # Users
    await db.users.create_index([("username", 1)], unique=True)

    # Custom foods
    await db.custom_foods.create_index([("barcode", 1)], unique=True, sparse=True)
    await db.custom_foods.create_index([("name", "text"), ("brand", "text")])

    # Meal templates
    await db.meal_templates.create_index([("created_by", 1)])
    await db.meal_templates.create_index([("name", "text")])

    # Meal consumption
    await db.meal_consumption.create_index([("consumed_at", -1)])
    await db.meal_consumption.create_index([("user_portions.username", 1), ("consumed_at", -1)])

    # Meal plans
    await db.meal_plans.create_index([("planned_by", 1), ("planned_date", 1)])

    # Shopping lists
    await db.shopping_lists.create_index([("created_by", 1), ("created_at", -1)])
```

**7. Seed Users**

Create `scripts/seed_users.py`:

```python
async def seed_users():
    db = get_database()

    users = [
        {
            "username": "nyntjie",
            "display_name": "Nyntjie",
            "goals": {
                "daily_calories": 2000,
                "daily_protein_g": 150.0,
                "daily_carbs_g": 250.0,
                "daily_fat_g": 65.0
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "username": "unit",
            "display_name": "Unit",
            "goals": {
                "daily_calories": 2200,
                "daily_protein_g": 160.0,
                "daily_carbs_g": 275.0,
                "daily_fat_g": 70.0
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]

    await db.users.insert_many(users)
```

### Phase 2: Food Database Setup & Management

**8. MongoDB Setup & OpenFoodFacts Import**

```bash
# Start MongoDB container
docker-compose up -d

# Download OpenFoodFacts MongoDB dump (~20GB compressed, ~80GB uncompressed)
wget https://static.openfoodfacts.org/data/openfoodfacts-mongodbdump.gz

# Extract
gunzip openfoodfacts-mongodbdump.gz

# Import into MongoDB (takes 30-60 mins)
mongorestore --host localhost:27017 --db off openfoodfacts-mongodbdump/

# Verify import
docker exec -it nomnom-mongodb mongosh
> use off
> db.products.countDocuments()  // Should show ~3M products
> db.products.findOne({code: "3017620422003"})  // Test barcode lookup
> db.products.getIndexes()  // Verify indexes exist
```

**9. Food Lookup Service**

Create `app/services/food_lookup.py`:

```python
from motor.motor_asyncio import AsyncIOMotorDatabase

class FoodLookupService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def find_by_barcode(self, barcode: str):
        """
        Lookup strategy:
        1. Check custom_foods first (user overrides)
        2. Check products (OpenFoodFacts)
        3. Return None if not found
        """
        # Check custom foods first
        custom = await self.db.custom_foods.find_one({"barcode": barcode})
        if custom:
            return self._transform_custom_food(custom)

        # Check OpenFoodFacts products
        product = await self.db.products.find_one({"code": barcode})
        if product:
            return self._transform_openfoodfacts_product(product)

        return None

    async def search_by_name(self, query: str, limit: int = 20):
        """
        Text search across custom_foods and products
        """
        # Search custom foods
        custom_results = await self.db.custom_foods.find(
            {"$text": {"$search": query}}
        ).limit(limit // 2).to_list(length=limit // 2)

        # Search OpenFoodFacts products
        product_results = await self.db.products.find(
            {"$text": {"$search": query}}
        ).limit(limit // 2).to_list(length=limit // 2)

        # Combine and transform
        results = []
        results.extend([self._transform_custom_food(f) for f in custom_results])
        results.extend([self._transform_openfoodfacts_product(p) for p in product_results])

        return results[:limit]

    def _transform_openfoodfacts_product(self, product: dict) -> dict:
        """Transform OpenFoodFacts document to app format"""
        nutriments = product.get("nutriments", {})
        return {
            "source": "products",
            "id": str(product["_id"]),
            "barcode": product.get("code"),
            "name": product.get("product_name", "Unknown"),
            "brand": product.get("brands"),
            "nutrients": {
                "calories": nutriments.get("energy-kcal_100g"),
                "protein_g": nutriments.get("proteins_100g"),
                "carbs_g": nutriments.get("carbohydrates_100g"),
                "fat_g": nutriments.get("fat_100g"),
                "fiber_g": nutriments.get("fiber_100g"),
                "sugar_g": nutriments.get("sugars_100g"),
                "sodium_mg": nutriments.get("sodium_100g", 0) * 1000  # Convert to mg
            },
            "images": product.get("images", {})
        }

    def _transform_custom_food(self, food: dict) -> dict:
        """Transform custom_food document to app format"""
        return {
            "source": "custom_foods",
            "id": str(food["_id"]),
            "barcode": food.get("barcode"),
            "name": food.get("name"),
            "brand": food.get("brand"),
            "nutrients": food.get("nutrients"),
            "tags": food.get("tags", []),
            "created_by": food.get("created_by")
        }
```

**10. Food Endpoints**

Create `app/api/v1/endpoints/foods.py`:
- GET `/api/food/search?q=...`
- GET `/api/food/barcode/{code}`
- POST `/api/food` (create custom item)
- PUT `/api/food/{id}` (update custom item)
- DELETE `/api/food/{id}` (delete custom item)

**11. Pydantic Schemas**

Create `app/schemas/food.py`:
- `FoodItemOut`: Unified response format
- `CustomFoodCreate`: For creating custom foods
- `CustomFoodUpdate`: For updating custom foods

**12. Delta Updates (Optional - keep MongoDB fresh)**

Create `scripts/update_openfoodfacts.sh`:

```bash
#!/bin/bash
# Download today's delta file
DELTA_URL="https://static.openfoodfacts.org/data/delta/$(date +%Y-%m-%d).json.gz"
wget $DELTA_URL -O delta.json.gz
gunzip delta.json.gz

# Import delta (updates/inserts changed products)
mongoimport --host localhost:27017 --db off --collection products \
  --file delta.json --mode upsert --upsertFields code
```

Run nightly via cron to stay up to date.

### Phase 3: Meal Templates (Recipes)

**13. Meal Template Models & Endpoints**

- `app/api/v1/endpoints/templates.py`:
    - CRUD for meal templates
    - Add/update/remove ingredients
- `app/schemas/meal.py`: MealTemplateCreate, MealTemplateOut, etc.

**14. Meal Service**

- `app/services/meal_service.py`:
    - Calculate total nutrition for meal template
    - Handle ingredient quantities and units

### Phase 4: Meal Consumption (Daily Tracking)

**15. Consumption Endpoints**

- `app/api/v1/endpoints/meals.py`:
    - GET `/api/meals?user={username}&date={date}`
    - POST `/api/meals` (with user splits)
    - PUT `/api/meals/{id}`
    - DELETE `/api/meals/{id}`

**16. User Split Logic**

- Calculate nutrients per user based on portion percentages
- Support both meal templates and individual food items
- Handle quantity overrides per user

**17. Photo Upload**

- `app/api/v1/endpoints/meals.py`:
    - POST `/api/meals/{id}/photo`
- `app/utils/files.py`: File upload, resize, thumbnail generation

### Phase 5: Meal Planning & Shopping Lists

**18. Meal Planning**

- `app/api/v1/endpoints/plans.py`:
    - CRUD for meal plans
    - Mark plan as completed (creates consumption record)
- `app/schemas/plan.py`: MealPlanCreate, MealPlanOut

**19. Shopping List Generation**

- `app/services/shopping_service.py`:
    - Aggregate ingredients from meal plans
    - Group by food item
    - Calculate total quantities
- `app/api/v1/endpoints/shopping.py`:
    - Generate list from date range
    - Manual list creation
    - Mark items purchased

### Phase 6: Dashboard & Analytics

**20. Dashboard Endpoint**

- `app/api/v1/endpoints/dashboard.py`:
    - Daily summary (totals vs goals)
    - Weekly overview
- Aggregate nutrition from meal consumption with user splits

**21. Nutrition Calculations**

- `app/services/nutrition.py`:
    - Calculate totals for user and date
    - Compare against goals
    - Generate progress percentages

### Phase 7: Frontend (Svelte 5)

**22. SvelteKit Setup**

```bash
npm create svelte@latest frontend
cd frontend
npm install
npm install -D tailwindcss autoprefixer
```

**23. Reuse Components from Showcase**

- Copy relevant components from `/Users/dawiddutoit/projects/play/svelte`:
    - Form components
    - Button styles
    - Card layouts
    - Modal/dialog patterns
    - Charts (for macros)

**24. Core Frontend Features**

- Day planner view (meal timeline)
- Add meal modal with user split selector
- Barcode scanner integration
- Meal template builder
- Meal planner calendar
- Shopping list interface
- Dashboard with progress charts

**25. API Client**

- `frontend/src/lib/api/client.ts`:
    - Type-safe API calls
    - Error handling
    - Loading states

### Phase 8: Testing & Polish

**26. Backend Tests**

- Meal consumption with user splits
- Shopping list generation
- Nutrition calculations
- Photo uploads
- MongoDB food lookup service

**27. Frontend Tests**

- Component tests (Vitest)
- E2E tests (Playwright) for critical flows:
    - Add meal with split
    - Create meal template
    - Generate shopping list

**28. Documentation**

- Update CLAUDE.md with final architecture
- API documentation in OpenAPI
- Frontend component documentation

---

## Key Data Flows

### 1. Add Shared Meal Flow

```
User (Nyntjie) → "Add Chicken Stir Fry for dinner"
    ↓
Select meal template or create new
    ↓
Choose users: [ ✓ Nyntjie 60% ] [ ✓ Unit 40% ]
    ↓
POST /api/meals
{
  "meal_template_id": 5,
  "consumed_at": "2025-01-28T18:00:00Z",
  "meal_type": "dinner",
  "users": [
    {"username": "nyntjie", "portion_percentage": 60.0},
    {"username": "unit", "portion_percentage": 40.0}
  ]
}
    ↓
Backend:
- Create MealConsumption record
- Create MealConsumptionUser records (2 entries)
- Calculate nutrients for each user based on percentage
    ↓
Return: Meal with calculated per-user nutrition
```

### 2. Food Lookup with Custom Override Flow

```
User scans barcode "123456789"
    ↓
GET /api/food/barcode/123456789
    ↓
Check custom_foods collection → Not found
    ↓
Query products collection (db.products.findOne({code: "123456789"}))
    ↓
Found: {name: "Banana", nutriments: {energy-kcal_100g: 89, ...}}
    ↓
Transform OpenFoodFacts format to app format
    ↓
Return to user
    ↓
User says "This is wrong, it's 105 calories"
    ↓
POST /api/food (create custom override)
{
  "barcode": "123456789",
  "name": "Banana",
  "nutrients": {
    "calories": 105,
    "protein_g": 1.3,
    ...
  },
  "overrides_openfoodfacts": true
}
    ↓
Insert into custom_foods collection
    ↓
Future barcode lookups find custom_foods first (takes precedence)
```

### 3. Meal Planning → Shopping List Flow

```
User creates meal plans for next week
    ↓
Plans include:
- Monday Dinner: Chicken Stir Fry
- Tuesday Lunch: Tuna Salad
- Wednesday Dinner: Pasta Carbonara
    ↓
Click "Generate Shopping List"
    ↓
POST /api/shopping-lists/generate
{
  "user": "nyntjie",
  "start_date": "2025-02-03",
  "end_date": "2025-02-09"
}
    ↓
Backend:
- Find all meal plans in date range
- Get ingredients from meal templates
- Aggregate quantities by food item
- Create shopping list with items
    ↓
Return: Shopping list with grouped items
[
  {"item": "Chicken breast", "quantity": 800, "unit": "g"},
  {"item": "Rice", "quantity": 400, "unit": "g"},
  {"item": "Tuna", "quantity": 200, "unit": "g"}
]
```

---

## Critical Files (Creation Order)

### Backend Core (First 10 files)

1. `pyproject.toml` - Dependencies (Motor, FastAPI, Pydantic)
2. `docker-compose.yml` - MongoDB only
3. `.env.example` + `.env` - Configuration
4. `app/config.py` - Pydantic Settings
5. `app/db/mongodb.py` - Motor async client
6. `app/core/exceptions.py` - Custom exceptions
7. `app/main.py` - FastAPI app with MongoDB lifecycle
8. `app/api/deps.py` - Dependency injection
9. `app/utils/files.py` - File upload helpers
10. `main.py` - Entry point

### Services (Next 4 files)

11. `app/services/food_lookup.py` - Food lookup service (custom_foods → products)
12. `app/services/meal_service.py` - Meal business logic
13. `app/services/nutrition.py` - Nutrition calculations
14. `app/services/shopping_service.py` - Shopping list generation

### Schemas (Next 6 files)

15. `app/schemas/user.py` - User and goal schemas
16. `app/schemas/food.py` - Food item schemas
17. `app/schemas/meal.py` - Meal template schemas
18. `app/schemas/consumption.py` - Meal consumption schemas
19. `app/schemas/plan.py` - Meal plan schemas
20. `app/schemas/shopping.py` - Shopping list schemas

### API Endpoints (Next 7 files)

21. `app/api/v1/endpoints/users.py` - User management
22. `app/api/v1/endpoints/foods.py` - Food lookup & custom items
23. `app/api/v1/endpoints/templates.py` - Meal templates
24. `app/api/v1/endpoints/meals.py` - Daily consumption
25. `app/api/v1/endpoints/plans.py` - Meal planning
26. `app/api/v1/endpoints/shopping.py` - Shopping lists
27. `app/api/v1/endpoints/dashboard.py` - Analytics

### Scripts (Setup & Utilities)

28. `scripts/create_indexes.py` - Create MongoDB indexes
29. `scripts/seed_users.py` - Seed nyntjie and unit
30. `scripts/setup_mongodb.sh` - Download and import OpenFoodFacts dump
31. `scripts/update_openfoodfacts.sh` - Apply daily delta updates (optional)

**What we removed:**
- ❌ All SQLAlchemy model files (app/models/)
- ❌ Alembic migration files
- ❌ PostgreSQL database setup
- ❌ app/db/database.py (SQLAlchemy engine)

---

## Development Commands

```bash
# Backend Setup
cd /Users/dawiddutoit/projects/play/nomnom
uv pip install -e ".[dev]"

# Start MongoDB
docker-compose up -d

# Import OpenFoodFacts database (first time only)
./scripts/setup_mongodb.sh

# Create indexes and seed users
python scripts/create_indexes.py
python scripts/seed_users.py

# Run backend
python main.py  # Runs on http://localhost:8000

# Frontend
cd frontend
npm install
npm run dev  # Runs on http://localhost:5173

# MongoDB Admin
docker exec -it nomnom-mongodb mongosh
> use off
> db.products.countDocuments()
> db.custom_foods.find()
> db.users.find()

# Testing
pytest
npm test

# Quality checks
ruff check .
ruff format .
mypy app/
npm run lint

# Update OpenFoodFacts (optional, nightly)
./scripts/update_openfoodfacts.sh
```

---

## Success Criteria

✅ MongoDB running with OpenFoodFacts products (~3M items)
✅ Two users (nyntjie, unit) seeded in database with goals
✅ Barcode lookup works (custom_foods → products)
✅ Custom food items can be created and override OpenFoodFacts data
✅ Text search works across custom_foods and products
✅ Meal templates can be created with embedded ingredients
✅ Meals can be logged with user splits (percentage-based)
✅ Photos can be embedded in meal consumption documents
✅ Meal plans can be created for future dates
✅ Shopping lists can be generated from meal plans with embedded items
✅ Dashboard aggregates daily totals vs goals for each user
✅ Frontend routes work for both `/nyntjie` and `/unit`
✅ All MongoDB indexes created for performance

---

## Estimated Timeline

- **Phase 1** (Foundation): 2-3 hours *(simplified - no SQLAlchemy/Alembic)*
- **Phase 2** (Food Setup): 2-3 hours *(MongoDB import + lookup service)*
- **Phase 3** (Meal Templates): 2-3 hours
- **Phase 4** (Meal Consumption): 3-4 hours
- **Phase 5** (Planning & Shopping): 2-3 hours
- **Phase 6** (Dashboard): 2-3 hours
- **Phase 7** (Frontend): 10-15 hours
- **Phase 8** (Testing & Polish): 3-4 hours

**Total: 26-38 hours for complete system**

**Time savings from MongoDB-only approach:**
- ✅ No SQLAlchemy model definitions (~2 hours)
- ✅ No Alembic migrations (~2 hours)
- ✅ No PostgreSQL setup/configuration (~1 hour)
- ✅ Simpler service layer (no ORM queries) (~2 hours)
- ✅ **Total savings: ~7 hours**

---

## Post-MVP Features

- **Cloudflare Tunnel** with email authentication
- **Image recognition** for food identification from photos
- **Recipe import** from URLs or text
- **Social sharing** of meals and recipes
- **Meal history** and favorites
- **Nutritional insights** and trends
- **Export data** (CSV, PDF reports)
- **Mobile app** (React Native or Flutter)
