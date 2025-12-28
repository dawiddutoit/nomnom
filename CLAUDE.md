# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start for Claude

**Before doing ANY work**:
1. 📖 **Read `plan.md`** for detailed schemas, data flows, and implementation steps
2. ✅ **Use skills proactively** - Don't just write code, use skills to guide implementation
3. 🔍 **Check existing resources** - OpenFoodFacts docs in `.claude/artifacts/`, testing in `tests/`

**Mandatory skill usage**:
- ✅ `util-manage-todo` - When starting multi-step work (MUST use for features)
- ✅ `quality-verify-integration` - Before marking ANY task complete (prevents orphaned code)
- ✅ `quality-detect-regressions` - After implementation (MANDATORY before "done")
- ✅ `quality-capture-baseline` - Before refactoring or starting features

**Common workflows**:
- Creating features → Use `implement-*` skills + `util-manage-todo` + `quality-verify-integration`
- Testing → Use `playwright-e2e-testing` or `chrome-browser-automation` skills
- Type errors → Use `python-best-practices-type-safety` skill
- Architecture validation → Use `architecture-validate-architecture` skill

**Information sources** (read, don't duplicate):
- `plan.md` - MongoDB schemas, API endpoints, implementation phases
- `.claude/artifacts/2025-12-28/openfoodfacts/` - OpenFoodFacts field mapping
- `tests/CHROME_WORKFLOWS.md` - Copy/paste test prompts
- `/Users/dawiddutoit/projects/play/svelte/` - Reusable Svelte components

## Project Overview

**NomNom** is a comprehensive nutrition tracking application for shared household management with the following core features:

**Shared Household Management**:
- **Two users**: `nyntjie` and `unit` with individual nutritional goals
- **Percentage-based meal splits**: Track shared meals (e.g., Chicken Stir Fry → Nyntjie 60%, Unit 40%)
- **Individual and shared meal tracking**: Both personal and household meals

**Food Management**:
- **Food Entry**: Barcode scanning, text search, or manual entry
- **Barcode Recognition**: Camera-based scanning with OpenFoodFacts database (~3M products)
- **Custom food overrides**: Override API data with user-provided nutritional values
- **Recent foods**: Quick access to frequently consumed items

**Meal Features**:
- **Meal templates**: Reusable recipes with multiple ingredients
- **Photo uploads**: Attach photos to meals with item tagging
- **Meal planning**: Daily/weekly meal prep calendar
- **Shopping list generation**: Auto-generate from planned meals

**Analytics & Goals**:
- **Goal tracking**: Dashboard comparing actual intake vs. individual goals
- **Daily summaries**: Calories, protein, carbs, fat per user
- **Weekly overview**: Trend analysis and progress

## Architecture

### Technology Stack

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

**Why MongoDB-only Architecture?**
- ✅ OpenFoodFacts provides MongoDB dump (~3M products) - no API rate limits
- ✅ Simpler architecture: one database, one connection pool
- ✅ No caching layer needed - query products directly from MongoDB
- ✅ Flexible schema perfect for MVP iteration
- ✅ Motor provides excellent async support for FastAPI
- ✅ Embedded documents (meal templates with ingredients, consumption with user splits) eliminate joins
- ✅ Time savings: ~7 hours compared to PostgreSQL + SQLAlchemy + Alembic

**Integration Pattern**:
- Backend serves RESTful API endpoints via FastAPI
- Frontend consumes API via typed client functions (TypeScript)
- OpenAPI/Swagger auto-generated from FastAPI for API documentation
- MongoDB Motor for async database operations

### Data Flow

1. **Food Lookup Path** (MongoDB-optimized):
   - User scans barcode → Frontend sends to backend
   - Backend checks `custom_foods` collection first (user overrides)
   - If not found → Query `products` collection (OpenFoodFacts ~3M products)
   - If not found → Return 404 → User can create custom food item
   - Transform OpenFoodFacts format to app format on-the-fly
   - Return to frontend (no external API calls!)

2. **Shared Meal Entry Path**:
   - User (Nyntjie) adds "Chicken Stir Fry for dinner"
   - Select meal template or individual food item
   - Choose users and percentages: [Nyntjie 60%] [Unit 40%]
   - POST /api/meals with user splits
   - Backend creates `meal_consumption` document with embedded `user_portions`
   - Calculate nutrients for each user based on percentage
   - Return meal with per-user nutrition breakdown

3. **Meal Planning → Shopping List Path**:
   - User creates meal plans for week (meal templates + dates)
   - Click "Generate Shopping List"
   - Backend aggregates ingredients from all meal templates in date range
   - Group by food item and sum quantities
   - Create shopping list with embedded items
   - Return shopping list for user review

4. **Goal Tracking Path**:
   - Each user has individual goals (calories, protein, carbs, fat)
   - Daily intake aggregated from `meal_consumption` using user splits
   - Dashboard queries consumption for user + date, sums nutrients
   - Compare totals vs. goals, show progress percentages

### Key Architectural Decisions

**Database Architecture**:
- ✅ **MongoDB-only**: Single database for both OpenFoodFacts products and app data
- ✅ **Embedded documents**: Meal templates with ingredients, consumption with user splits (eliminates joins)
- ✅ **Direct product queries**: No caching layer needed - query 3M products directly
- ✅ **Custom overrides**: `custom_foods` collection checked before `products` collection

**Backend**:
- ✅ **FastAPI**: Async framework with auto-generated OpenAPI docs
- ✅ **Motor**: Async MongoDB driver for Python
- ✅ **No ORM**: Direct MongoDB queries (simpler than SQLAlchemy)
- ✅ **No migrations**: MongoDB schema flexibility eliminates Alembic

**Frontend**:
- ✅ **Svelte 5 runes**: Modern reactivity patterns
- ✅ **Component reuse**: Leverage `/Users/dawiddutoit/projects/play/svelte` showcase library
- ✅ **Mobile-first**: Designed for phone camera barcode scanning
- ✅ **User-specific routes**: `/nyntjie` and `/unit` for personalized views

**Shared Household**:
- ✅ **Percentage-based splits**: Meals divided between users (60%/40%)
- ✅ **Individual goals**: Each user has separate nutritional targets
- ✅ **Unified meal planning**: Both users can plan and track shared meals

## Development Setup

### Prerequisites

- Python 3.13+
- Node.js 18+ or 20+ (for Svelte frontend)
- Docker & Docker Compose (for MongoDB)
- uv package manager (recommended) or pip

### MongoDB Setup

**First-time setup** (imports ~3M OpenFoodFacts products):

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
> db.products.findOne({code: "3017620422003"})  // Test Nutella lookup
```

**Create indexes and seed users**:

```bash
python scripts/create_indexes.py
python scripts/seed_users.py  # Creates nyntjie and unit
```

### Backend Setup

```bash
# Install dependencies with uv
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"

# Run development server
python main.py  # Runs on http://localhost:8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev  # Runs on http://localhost:5173
```

## Development Commands

### Backend (Python)

```bash
# Run tests
pytest

# Run type checking (once mypy/pyright configured)
mypy .

# Run linting (once ruff/black configured)
ruff check .
ruff format .
```

### Frontend (Svelte)

See `/Users/dawiddutoit/projects/play/svelte/CLAUDE.md` for comprehensive Svelte development guidelines.

Key commands:
```bash
npm run dev          # Start dev server
npm run build        # Build for production
npm run format       # Format code with Prettier
npm run lint         # Check ESLint rules
npm run check        # TypeScript + Svelte validation
npm test             # Run Vitest unit tests
npm run test:e2e     # Run Playwright E2E tests
```

### Testing & Quality

NomNom has comprehensive testing infrastructure using **Playwright MCP** (automated) and **Claude-in-Chrome** (interactive).

```bash
# Verify testing environment
python tests/setup_test_environment.py

# Run E2E tests (Playwright MCP)
python tests/e2e/test_barcode_scanning.py

# Interactive testing (Claude-in-Chrome)
# Copy prompts from tests/CHROME_WORKFLOWS.md
# Example: "Open NomNom and test the barcode scanner with Nutella (3017620422003)"
```

**Documentation:**
- `TESTING.md` - Comprehensive testing guide (900+ lines)
- `tests/README.md` - Quick start guide
- `tests/CHROME_WORKFLOWS.md` - 50+ ready-to-use test prompts
- `.claude/artifacts/2025-12-28/openfoodfacts/` - OpenFoodFacts API integration guide

## MongoDB Collections & Schema

**Complete schema documentation**: See `plan.md` for detailed collection schemas, indexes, and examples.

**Key collections**:
- `users` - User profiles (nyntjie, unit) with goals
- `products` - OpenFoodFacts (~3M products)
- `custom_foods` - User-created/overridden foods
- `meal_templates` - Reusable recipes with embedded ingredients
- `meal_consumption` - Daily tracking with embedded user splits
- `meal_plans` - Future meal planning
- `shopping_lists` - Generated or manual lists with embedded items

**Critical MongoDB patterns**:
- ✅ **Embedded documents**: No joins needed (ingredients in templates, user splits in consumption)
- ✅ **Lookup priority**: Always check `custom_foods` BEFORE `products` to respect user overrides
- ✅ **Indexes**: Text search on names, unique barcodes, composite indexes for queries
- ✅ **No migrations**: Schema flexibility allows iteration without Alembic

**To understand schema details**: Read `plan.md` sections on MongoDB Collections (lines 44-334)

## Development Workflow with Skills

### MANDATORY Skills (Use Proactively)

**Before marking ANY task complete**:
1. ✅ **Use `quality-verify-integration`** - Verify CCV compliance (Creation-Connection-Verification)
   - Ensures code is not just created and tested, but actually integrated into the system
   - Prevents "orphaned code" that exists but never runs
   - Required before marking features complete or moving ADRs to completed status

**When starting multi-step work**:
2. ✅ **Use `util-manage-todo`** - Track progress with CCV enforcement
   - Proactively invoke when detecting multi-step work
   - Enforces three-phase pattern (Creation → Connection → Verification)
   - Prevents "done but not integrated" failures

**After completing implementation**:
3. ✅ **Use `quality-detect-regressions`** - Compare metrics to baseline
   - MANDATORY before task completion
   - Detects test failures, coverage drops, type errors, linting issues
   - Blocks on regressions to prevent quality degradation

**Before starting implementation**:
4. ✅ **Use `quality-capture-baseline`** - Capture quality metrics
   - Proactively invoke at feature start or before refactor work
   - Establishes baseline for regression detection

### Recommended Skills (Use as Needed)

**Python Development**:
- `python-best-practices-type-safety` - Resolve pyright/mypy type errors systematically
- `python-best-practices-fail-fast-imports` - Validate imports follow fail-fast principle
- `implement-repository-pattern` - Create repositories following Clean Architecture
- `implement-cqrs-handler` - Create CQRS handlers with ServiceResult pattern
- `implement-value-object` - Create immutable domain value objects

**Testing**:
- `playwright-e2e-testing` - Create E2E tests following project patterns
- `test-debug-failures` - Debug test failures with evidence-based analysis
- `test-setup-async` - Set up async tests with pytest-asyncio

**Quality & Architecture**:
- `quality-code-review` - Systematic self-review before commits
- `architecture-validate-architecture` - Validate Clean Architecture patterns
- `create-adr-spike` - Create Architecture Decision Records

**Browser Testing**:
- `chrome-browser-automation` - Interactive testing workflows
- `chrome-gif-recorder` - Record workflows as GIFs for documentation

### Code Standards

## CRITICAL: Production-Quality Code Only

**These rules are NON-NEGOTIABLE**:

### 1. No Placeholder Code
- ❌ **NEVER** write `pass`, `...`, or `NotImplementedError` in production code
- ❌ **NEVER** write `TODO` or `FIXME` comments without implementation
- ❌ **NEVER** write functions that return mock/dummy data
- ✅ **ALWAYS** implement complete, working functionality
- ✅ If a feature cannot be completed, **FAIL EXPLICITLY** with clear error message

```python
# ❌ WRONG - Placeholder
async def get_food_by_barcode(barcode: str) -> dict:
    # TODO: Implement barcode lookup
    pass

# ✅ CORRECT - Complete implementation
async def get_food_by_barcode(barcode: str) -> FoodItem:
    """Lookup food item by barcode in custom_foods then products."""
    # Check custom foods first
    custom = await db.custom_foods.find_one({"barcode": barcode})
    if custom:
        return transform_custom_food(custom)

    # Check OpenFoodFacts products
    product = await db.products.find_one({"code": barcode})
    if product:
        return transform_product(product)

    raise FoodNotFoundError(f"No food found for barcode: {barcode}")
```

### 2. Type Safety - NO `Any` Types
- ❌ **NEVER** use `Any`, `object`, or untyped parameters
- ❌ **NEVER** use `dict` without type parameters (use `dict[str, str]`)
- ❌ **NEVER** use `list` without type parameters (use `list[FoodItem]`)
- ❌ **AVOID** `| None` unless the value is genuinely optional
- ✅ **ALWAYS** use specific types, Pydantic models, or TypedDict
- ✅ **ALWAYS** use strict mypy/pyright with no exceptions

```python
# ❌ WRONG - Untyped
async def search_foods(query, limit=20):
    results = await db.products.find({"$text": {"$search": query}})
    return results

# ❌ WRONG - Using Any
from typing import Any
async def search_foods(query: str, limit: int = 20) -> list[Any]:
    ...

# ✅ CORRECT - Fully typed
async def search_foods(query: str, limit: int = 20) -> list[FoodItem]:
    """Search products by name with text index."""
    cursor = db.products.find({"$text": {"$search": query}}).limit(limit)
    products = await cursor.to_list(length=limit)
    return [transform_product(p) for p in products]
```

### 3. No Optional Types Without Reason
- ❌ **AVOID** `| None` for return types when failure should raise exception
- ❌ **AVOID** `| None` for parameters when value is always required
- ✅ **USE** `| None` ONLY when value is genuinely optional (like `brand` field)
- ✅ **RAISE EXCEPTIONS** instead of returning `None` for "not found" cases

```python
# ❌ WRONG - Optional return type masks errors
async def get_user(username: str) -> User | None:
    return await db.users.find_one({"username": username})

# ✅ CORRECT - Explicit exception on not found
async def get_user(username: str) -> User:
    """Get user by username. Raises UserNotFound if not exists."""
    user_doc = await db.users.find_one({"username": username})
    if not user_doc:
        raise UserNotFoundError(f"User not found: {username}")
    return User.model_validate(user_doc)
```

### 4. Dependency Injection - ALWAYS
- ❌ **NEVER** instantiate dependencies inside functions
- ❌ **NEVER** access global singletons or config directly
- ❌ **NEVER** use `settings.MONGODB_URL` inside service methods
- ✅ **ALWAYS** inject database connections via function parameters
- ✅ **ALWAYS** inject settings via dependency injection
- ✅ **ALWAYS** use FastAPI's `Depends()` for dependencies

```python
# ❌ WRONG - Global access
from app.db.mongodb import get_database
from app.config import settings

async def find_food(barcode: str):
    db = get_database()  # Global singleton
    mongo_url = settings.MONGODB_URL  # Direct config access
    ...

# ✅ CORRECT - Dependency injection
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends

async def find_food(
    barcode: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> FoodItem:
    """Find food by barcode using injected database."""
    ...
```

### 5. Settings Must Be Injected
- ❌ **NEVER** import `settings` directly in service/repository code
- ❌ **NEVER** use `os.getenv()` in application code
- ✅ **ALWAYS** inject `Settings` object via dependency injection
- ✅ **ONLY** access `settings` in FastAPI dependency providers

```python
# ❌ WRONG
from app.config import settings

class FoodService:
    async def upload_photo(self, file: UploadFile):
        path = f"{settings.UPLOAD_DIR}/photo.jpg"  # Direct access
        ...

# ✅ CORRECT
class FoodService:
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir

    async def upload_photo(self, file: UploadFile):
        path = f"{self.upload_dir}/photo.jpg"
        ...

# In dependency provider
def get_food_service(settings: Settings = Depends(get_settings)) -> FoodService:
    return FoodService(upload_dir=settings.UPLOAD_DIR)
```

### 6. Fail-Fast Principle
- ❌ **NEVER** catch exceptions and return `None` or default values
- ❌ **NEVER** use `try/except: pass` to silence errors
- ✅ **ALWAYS** let exceptions bubble up with context
- ✅ **ALWAYS** validate inputs at boundaries (API endpoints, not services)
- ✅ **ALWAYS** use specific exception types

```python
# ❌ WRONG - Silencing errors
async def get_food(barcode: str) -> dict | None:
    try:
        food = await db.products.find_one({"code": barcode})
        return food
    except Exception:
        return None  # What went wrong? No one knows!

# ✅ CORRECT - Explicit errors with context
async def get_food(barcode: str) -> FoodItem:
    """Get food by barcode. Raises FoodNotFound if not exists."""
    try:
        food_doc = await db.products.find_one({"code": barcode})
    except pymongo.errors.PyMongoError as e:
        raise DatabaseError(f"Failed to query products: {e}") from e

    if not food_doc:
        raise FoodNotFoundError(f"No food found for barcode: {barcode}")

    return transform_product(food_doc)
```

## Enforcement

**These standards are enforced by**:
- `mypy` with `--strict` flag
- `pyright` with strict type checking
- Code review before commits
- `quality-verify-integration` skill checks
- Manual verification by Claude Code

**If you encounter code that violates these standards**:
1. **Refactor immediately** - Don't propagate bad patterns
2. **Use skills** - `python-best-practices-type-safety` for type issues
3. **Ask for clarification** - If requirements are unclear

---

## Python Standards

**Python**:
- Type hints required (use `python-best-practices-type-safety` for issues)
- Async/await for all I/O operations
- Fail-fast imports (use `python-best-practices-fail-fast-imports` to validate)
- Concise docstrings (see global CLAUDE.md)

**API Design**:
- RESTful endpoints with OpenAPI auto-generation
- Versioning via `/api/v1/`
- Consistent JSON response format:

```python
# Success: {"success": true, "data": {...}, "error": null}
# Error: {"success": false, "data": null, "error": {"code": "...", "message": "..."}}
```

## API Endpoints

See the comprehensive API endpoint documentation in `plan.md` for complete details. Key endpoint categories:

- **Users & Goals**: `/api/users`, `/api/users/{username}/goals`
- **Food Items**: `/api/food/search`, `/api/food/barcode/{code}`, `/api/food/{id}`
- **Meals** (Daily Consumption): `/api/meals`, `/api/meals/{id}`, `/api/meals/{id}/photo`
- **Meal Templates**: `/api/templates`, `/api/templates/{id}`, `/api/templates/{id}/items`
- **Meal Planning**: `/api/plans`, `/api/plans/{id}/complete`
- **Shopping Lists**: `/api/shopping-lists`, `/api/shopping-lists/generate`
- **Dashboard**: `/api/dashboard/{username}`, `/api/dashboard/{username}/week`

**Key Patterns**:
- All endpoints return consistent JSON format with `{success, data, error}`
- POST /api/meals includes `user_portions` array with percentage splits
- Food lookup checks `custom_foods` → `products` → 404
- Shopping list generation aggregates ingredients from meal plans by date range

## Frontend Integration

### Component Reuse Strategy

1. **Browse existing components**: Check `/Users/dawiddutoit/projects/play/svelte/src/lib/components/`
2. **Copy relevant components**: Extract needed components (buttons, cards, forms, modals, etc.)
3. **Adapt as needed**: Customize for NomNom branding and specific use cases
4. **Follow Svelte 5 patterns**: Use runes (`$state`, `$derived`, `$effect`) exclusively

### Recommended Components to Reuse

Based on the Svelte showcase library:

- **Forms**: Input fields, validation patterns (via formsnap + sveltekit-superforms)
- **Cards**: Food item cards, daily summary cards
- **Buttons**: Action buttons (scan, add, save)
- **Modals/Dialogs**: Food detail view, settings
- **Charts**: Nutritional charts (via LayerChart)
- **Icons**: lucide-svelte for UI icons
- **Toasts**: User feedback notifications

### API Client Pattern

```typescript
// frontend/src/lib/api/foods.ts
import { z } from 'zod';

const foodItemSchema = z.object({
	id: z.string(),
	barcode: z.string(),
	name: z.string(),
	brand: z.string().optional(),
	calories: z.number(),
	protein: z.number(),
	carbs: z.number(),
	fat: z.number()
});

type FoodItem = z.infer<typeof foodItemSchema>;

export async function getFoodByBarcode(barcode: string): Promise<FoodItem | null> {
	const response = await fetch(`/api/v1/foods/barcode/${barcode}`);
	if (response.status === 404) return null;
	const data = await response.json();
	return foodItemSchema.parse(data.data);
}
```

## Implementation Phases

**Complete phase breakdown**: See `plan.md` lines 582-1046 for detailed implementation steps.

**8 Phases** (26-38 hours total):
1. **Foundation** (2-3h) - FastAPI, Motor, MongoDB setup
2. **Food Database** (2-3h) - OpenFoodFacts import, FoodLookupService
3. **Meal Templates** (2-3h) - Recipes with ingredients
4. **Meal Consumption** (3-4h) - Daily tracking with user splits
5. **Planning & Shopping** (2-3h) - Meal plans, shopping lists
6. **Dashboard** (2-3h) - Analytics and goal tracking
7. **Frontend** (10-15h) - SvelteKit UI with Svelte 5 runes
8. **Testing & Polish** (3-4h) - E2E tests, optimization

**When implementing each phase**:
1. ✅ Use `util-manage-todo` to create phase checklist
2. ✅ Read relevant `plan.md` section for code examples
3. ✅ Use `implement-*` skills for standard patterns
4. ✅ Use `quality-verify-integration` after each phase
5. ✅ Use `quality-detect-regressions` before moving to next phase

## Architecture Decisions Made ✅

All critical decisions have been finalized:

1. ✅ **Backend Framework**: FastAPI (async, auto-generated OpenAPI)
2. ✅ **Database**: MongoDB 8.0 (single database for all data)
3. ✅ **MongoDB Client**: Motor (async driver)
4. ✅ **Food Data**: OpenFoodFacts MongoDB dump (~3M products)
5. ✅ **Authentication**: None for MVP (two hardcoded users: nyntjie, unit)
6. ✅ **File Storage**: Local filesystem (uploads/meals/)
7. ✅ **Frontend**: Svelte 5 with SvelteKit
8. ✅ **Styling**: Tailwind CSS
9. ✅ **Deployment**: Docker Compose for local development

**Post-MVP**:
- Cloudflare Tunnel with email authentication
- Image recognition for food identification
- Recipe import from URLs
- Mobile app (React Native or Flutter)

## OpenFoodFacts Integration ✅

**Status:** MongoDB dump approach - NO API calls needed!

**Why MongoDB Dump Instead of API?**
- ✅ **~3M products** available offline in MongoDB
- ✅ **No rate limits** - query local database directly
- ✅ **No network latency** - instant lookups
- ✅ **No API failures** - always available
- ✅ **Comprehensive data** - All 50+ nutritional fields
- ✅ **Quality scores** - Nutri-Score, NOVA, Eco-Score included

**Data Source:**
- Download: `https://static.openfoodfacts.org/data/openfoodfacts-mongodbdump.gz`
- Size: ~20GB compressed, ~80GB uncompressed
- Import time: 30-60 minutes one-time setup
- Updates: Optional daily delta imports to stay current

**Documentation:**
- `.claude/artifacts/2025-12-28/openfoodfacts/OPENFOODFACTS_INTEGRATION.md` - Complete API guide (for reference)
- `.claude/artifacts/2025-12-28/openfoodfacts/QUICK_REFERENCE.md` - Field mapping cheatsheet
- `scripts/setup_mongodb.sh` - Automated MongoDB dump import (to be created)
- `scripts/update_openfoodfacts.sh` - Daily delta updates (optional)

**Nutritional Data Available:**
- Macronutrients: calories, protein, carbs, fat, fiber, sugar, sodium
- Micronutrients: vitamins, minerals (50+ fields)
- Quality scores: Nutri-Score (A-E), NOVA (1-4), Eco-Score
- Product info: name, brand, quantity, images, ingredients

**OpenFoodFacts API** (Alternative - Not Used in MVP):
- Endpoint: `https://world.openfoodfacts.org/api/v2/product/{barcode}.json`
- Python SDK: `pip install openfoodfacts`
- Use case: Real-time updates, missing products
- Note: API has rate limits; MongoDB dump preferred for production

## Testing Strategy

NomNom uses a **dual testing approach**: automated E2E tests (Playwright MCP) for CI/CD pipelines, and interactive testing (Claude-in-Chrome) for exploratory testing and debugging.

### E2E Tests (Playwright MCP) - Automated

**Purpose:** Repeatable regression testing, CI/CD integration, performance benchmarks

**Available Tools:**
- `browser_navigate` - Navigate to URL
- `browser_snapshot` - Get page state with interactive elements
- `browser_click` - Click elements
- `browser_fill_form` - Fill multiple form fields
- `browser_screenshot` - Capture visual evidence
- `browser_wait_for` - Wait for async operations
- `browser_console_messages` - Monitor JavaScript errors
- `browser_network_requests` - Verify API calls

**Test Suite:**
- `tests/e2e/test_barcode_scanning.py` - 5 comprehensive tests
  1. Scan Nutella barcode (success case)
  2. Scan multiple products (Coke, Yogurt, Cheerios)
  3. Handle unknown barcode (error state)
  4. Manual entry fallback
  5. Performance testing (< 5s response time)

**Helper Functions:** 30+ wrapper functions in `tests/fixtures/helpers.py`

**Test Data:** 4 verified barcodes with complete nutritional data in `tests/fixtures/test_data.py`

**Run Tests:**
```bash
# Verify environment
python tests/setup_test_environment.py

# Run all barcode tests
python tests/e2e/test_barcode_scanning.py
```

### Interactive Testing (Claude-in-Chrome)

**Purpose:** Exploratory testing, visual verification, GIF tutorials, debugging

**Available Tools:**
- Tab management (create, navigate, context)
- Form interaction (read, fill, submit)
- Visual recording (GIF creator)
- Console/network monitoring
- Element finding and clicking

**Workflows:** 50+ ready-to-use prompts in `tests/CHROME_WORKFLOWS.md`

**Example Usage:**
```
Open NomNom at http://localhost:5173 and test the barcode scanner with Nutella (3017620422003).
Verify product name and calories appear. Take a screenshot and check console for errors.
```

**Categories:**
- Barcode scanner testing (basic, multi-product, performance, error handling)
- Food logging workflows (daily logging, bulk scanning, edit/delete)
- Goal tracking & dashboard testing
- Error handling & edge cases
- Performance & network monitoring
- Creating documentation (GIFs, screenshots)

### Backend Tests
- **Unit Tests**: Service layer, utility functions
- **Integration Tests**: API endpoints, database operations
- **Test Framework**: pytest

### Frontend Tests
- **Unit Tests**: Utility functions, state management (Vitest)
- **Component Tests**: Form validation, UI interactions (Vitest + Testing Library)
- **E2E Tests**: Critical user flows via Playwright MCP

### Test Coverage Requirements

**Must Test:**
- ✅ Barcode scanning (success and failure)
- ✅ Manual food entry
- ✅ Food logging (add, edit, delete)
- ✅ Daily total calculations
- ✅ Goal setting and tracking
- ✅ User authentication
- ✅ Offline/cache behavior
- ✅ Error handling

**Test Data:**
- Nutella: `3017620422003` (539 kcal) - Complete data
- Coca-Cola: `5000112637588` (42 kcal) - Complete data
- Greek Yogurt: `8714100770221` (97 kcal) - Partial data
- Cheerios: `737628064502` (367 kcal) - Complete data

### Testing Documentation

- **`TESTING.md`** - Comprehensive guide (900+ lines) covering both testing approaches
- **`tests/README.md`** - Quick start guide with directory structure and examples
- **`tests/CHROME_WORKFLOWS.md`** - 50+ copy/paste test prompts for interactive testing
- **`tests/templates/`** - Test templates for creating new tests

## Security Considerations

- **User Data**: Encrypt sensitive data at rest
- **Authentication**: Secure password hashing (bcrypt/argon2), JWT token expiry
- **API Rate Limiting**: Prevent abuse of barcode lookup endpoints
- **Input Validation**: Sanitize all user inputs (barcode, food names, quantities)
- **CORS**: Configure proper CORS policies for frontend-backend communication

## Performance Considerations

- **Barcode Lookup**: Cache frequently scanned items in local DB
- **Image Processing**: Compress/resize images before upload (non-MVP)
- **Database Indexing**: Index barcode, user_id, consumed_at fields
- **API Response Time**: Optimize queries, use database connection pooling

## Deployment (Future)

- **Backend**: Docker container, deploy to AWS ECS/Fargate, Google Cloud Run, or DigitalOcean
- **Frontend**: Static hosting (Vercel, Netlify, Cloudflare Pages)
- **Database**: Managed PostgreSQL (AWS RDS, Google Cloud SQL, Supabase)
- **CI/CD**: GitHub Actions for automated testing and deployment

## Don't Repeat Work

- **Reuse Svelte Components**: Always check `/Users/dawiddutoit/projects/play/svelte` before building new UI components
- **Follow Svelte 5 Patterns**: See `/Users/dawiddutoit/projects/play/svelte/CLAUDE.md` for comprehensive Svelte 5 guidelines
- **Type Safety**: Use Zod schemas for runtime validation + TypeScript type inference
- **API-First Design**: Design API endpoints before implementing frontend features
- **Use Testing Infrastructure**: Leverage existing test helpers and fixtures in `tests/fixtures/`
- **Use OpenFoodFacts Documentation**: Complete API integration guide in `.claude/artifacts/2025-12-28/openfoodfacts/`

## Project Structure

**Complete file tree**: See `plan.md` lines 446-578 for detailed directory structure.

**Key directories**:
- `app/` - FastAPI application code
  - `api/v1/endpoints/` - REST API endpoints (users, foods, meals, templates, plans, shopping, dashboard)
  - `services/` - Business logic (food_lookup, meal_service, nutrition, shopping_service)
  - `schemas/` - Pydantic models for request/response
  - `db/` - MongoDB Motor client
- `scripts/` - Setup scripts (indexes, seed data, MongoDB import)
- `tests/` - Pytest tests with fixtures and E2E tests
- `frontend/` - SvelteKit app (to be created)
- `uploads/meals/` - Photo storage

**Implementation order**: See `plan.md` Critical Files section (lines 1154-1207) for creation sequence.

**When implementing features**:
1. ✅ Use `implement-*` skills for standard patterns (repository, CQRS, value objects)
2. ✅ Use `quality-verify-integration` after creating files to ensure they're connected
3. ✅ Use `util-manage-todo` to track multi-file changes

## How to Get Information

### OpenFoodFacts Data (MongoDB Dump)
**Location**: `.claude/artifacts/2025-12-28/openfoodfacts/`
- `OPENFOODFACTS_INTEGRATION.md` - Complete API reference (use for field mapping)
- `QUICK_REFERENCE.md` - One-page cheatsheet for daily coding
- `example_implementation.py` - Working Python code examples

**When to reference**:
- Need to understand OpenFoodFacts field names (e.g., `nutriments.energy-kcal_100g`)
- Building food transformation logic
- Understanding quality scores (Nutri-Score, NOVA, Eco-Score)

### Testing Workflows
**Location**: `tests/` and `TESTING.md`
- `TESTING.md` - Read for testing strategy overview
- `tests/CHROME_WORKFLOWS.md` - Copy/paste prompts for interactive testing
- `tests/fixtures/test_data.py` - Known barcodes (Nutella, Coke, Yogurt, Cheerios)

**When to test**:
1. ✅ Use `playwright-e2e-testing` skill to create new automated tests
2. ✅ Use `chrome-browser-automation` skill for interactive testing
3. ✅ Use `test-debug-failures` skill when tests fail

### Implementation Guidance
**Primary source**: `plan.md`
- Lines 44-334: MongoDB collection schemas
- Lines 446-578: Project structure
- Lines 582-1207: Phase-by-phase implementation steps
- Lines 1052-1150: Data flows and examples

**When implementing**:
1. ✅ Read `plan.md` for detailed code examples
2. ✅ Use `implement-*` skills for standard patterns
3. ✅ Use `quality-verify-integration` to ensure code is connected
4. ✅ Use `util-manage-todo` for multi-step features

### Svelte Components (Frontend)
**Location**: `/Users/dawiddutoit/projects/play/svelte`
- Browse `src/lib/components/` for reusable components
- Check `CLAUDE.md` in that repo for Svelte 5 patterns

**Reuse components**:
- Forms (formsnap + sveltekit-superforms)
- Cards, buttons, modals
- Charts (LayerChart)
- Icons (lucide-svelte)

## Success Criteria

**Backend Infrastructure:**
- ✅ MongoDB 8.0 running via Docker Compose
- ✅ OpenFoodFacts products collection (~3M items) imported
- ✅ All MongoDB indexes created for performance
- ✅ Two users (nyntjie, unit) seeded with goals
- [ ] FastAPI app running on http://localhost:8000
- [ ] Auto-generated OpenAPI docs available at /docs

**Food Management:**
- [ ] Barcode lookup works (custom_foods → products)
- [ ] Custom food items can be created and override OpenFoodFacts data
- [ ] Text search works across custom_foods and products
- [ ] Food endpoint returns consistent format

**Meal Features:**
- [ ] Meal templates can be created with embedded ingredients
- [ ] Meals can be logged with user splits (percentage-based)
- [ ] Photos can be uploaded and embedded in meal consumption
- [ ] Nutritional calculations work correctly for split meals

**Planning & Shopping:**
- [ ] Meal plans can be created for future dates
- [ ] Shopping lists can be generated from meal plans
- [ ] Items are aggregated and grouped correctly
- [ ] Manual shopping list creation works

**Dashboard & Analytics:**
- [ ] Daily totals aggregate correctly per user
- [ ] Goal comparison shows accurate progress
- [ ] Weekly overview displays trends
- [ ] Nutrient calculations match expected values

**Frontend:**
- [ ] SvelteKit app running on http://localhost:5173
- [ ] User-specific routes work (/nyntjie, /unit)
- [ ] Day planner displays meals correctly
- [ ] Add meal modal with user split selector works
- [ ] Barcode scanner integration functional
- [ ] Dashboard charts display correctly

**Testing:**
- [ ] Backend tests pass (pytest)
- [ ] E2E tests pass (Playwright MCP)
- [ ] Interactive testing workflows documented
- [ ] No console errors in browser

**Documentation:**
- ✅ CLAUDE.md updated with MongoDB architecture
- ✅ plan.md contains complete implementation details
- ✅ API endpoint documentation in plan.md
- [ ] OpenAPI docs auto-generated and accurate
- [ ] README.md updated with setup instructions
