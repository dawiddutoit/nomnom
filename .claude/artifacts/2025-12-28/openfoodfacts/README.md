# OpenFoodFacts Integration Documentation for NomNom

Complete research and integration guide for using the OpenFoodFacts API in the NomNom calorie tracking application.

## 📁 Documentation Files

| File | Purpose | Use When |
|------|---------|----------|
| **OPENFOODFACTS_INTEGRATION.md** | Comprehensive integration guide (31 KB) | Planning architecture, understanding API deeply |
| **QUICK_REFERENCE.md** | One-page cheatsheet (7 KB) | Quick lookups during development |
| **example_implementation.py** | Complete working Python code (14 KB) | Starting implementation, testing API |
| **database_schema.sql** | PostgreSQL schema with indexes (11 KB) | Setting up database |
| **README.md** | This file - overview and navigation | Getting started |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install openfoodfacts
```

### 2. Test the API

```bash
# Run the example implementation
cd .claude/artifacts/2025-12-28/openfoodfacts
python example_implementation.py
```

### 3. Review the Documentation

Start with **QUICK_REFERENCE.md** for immediate coding needs, then dive into **OPENFOODFACTS_INTEGRATION.md** for comprehensive understanding.

## 📚 What's Inside

### OPENFOODFACTS_INTEGRATION.md (Main Documentation)

**Sections:**
1. Quick Start - Get running in 5 minutes
2. API Overview - Endpoints, capabilities, licensing
3. Authentication & Rate Limits - Headers, request limits, best practices
4. Product Lookup by Barcode - Core functionality
5. Nutritional Data Fields - Complete field reference
6. Python SDK Integration - Using the official SDK
7. Backend Implementation Pattern - Production-ready service classes
8. Database Schema Mapping - OpenFoodFacts → PostgreSQL
9. Error Handling - Common scenarios and solutions
10. Caching Strategy - Local SQLite cache with TTL
11. Data Quality Considerations - Assessing and validating data
12. Testing Strategy - Unit, integration, and E2E tests

**Key Features:**
- ✅ Copy-paste ready code examples
- ✅ Complete Python service implementation
- ✅ Error handling patterns
- ✅ Caching implementation
- ✅ Data validation logic
- ✅ Test templates
- ✅ 10+ sources cited

### QUICK_REFERENCE.md (Cheatsheet)

**Sections:**
- Quick start code
- API endpoints table
- Essential nutritional fields
- Quality scores reference
- Rate limits
- Python code templates
- Caching example
- Test data (known good barcodes)
- Common issues and solutions
- FastAPI endpoint template

**Best For:**
- Quick lookups during coding
- Remembering field names
- Copy-paste code snippets
- Debugging common issues

### example_implementation.py (Working Code)

**Features:**
- ✅ Complete OpenFoodFacts service class
- ✅ Nutritional data models (dataclasses)
- ✅ Local SQLite caching layer
- ✅ Combined service with cache-first strategy
- ✅ Data quality assessment
- ✅ Pretty-print display helper
- ✅ Working demo with 4 test barcodes
- ✅ Cache expiration cleanup

**Run It:**
```bash
python example_implementation.py
```

**Output:**
```
🍽️  NomNom - OpenFoodFacts Integration Demo

🔍 Looking up: Nutella (Ferrero) (barcode: 3017620422003)
----------------------------------------------------------------------
→ Cache miss for barcode 3017620422003, fetching from API...
✓ Cached food item with 30-day TTL

======================================================================
🍔 Nutella
   Brand: Ferrero
======================================================================

📊 Nutritional Information (per 100g):
   Calories:       539.0 kcal
   Protein:        6.3 g
   Carbohydrates:  57.5 g
     - Sugars:     56.3 g
   Fat:            30.9 g
     - Saturated:  10.6 g
   ...
```

### database_schema.sql (Database DDL)

**Tables:**
1. `food_items` - Cached OpenFoodFacts products
2. `users` - User accounts
3. `user_goals` - Daily nutritional targets
4. `food_log` - User food consumption entries

**Features:**
- ✅ Complete PostgreSQL schema
- ✅ Proper indexes for performance
- ✅ Full-text search support
- ✅ Automatic timestamp triggers
- ✅ Data validation constraints
- ✅ SQLite conversion notes
- ✅ Sample queries in comments
- ✅ Insert example

**Apply Schema:**
```bash
psql -U nomnom_user -d nomnom_db -f database_schema.sql
```

## 🎯 Key Findings

### ✅ Why OpenFoodFacts is Perfect for NomNom

1. **Free & Open**: No API key, no cost, open data (ODbL license)
2. **Large Database**: 2.8+ million products worldwide
3. **Rich Data**: Calories, macros, vitamins, minerals, allergens, ingredients
4. **Quality Scores**: Nutri-Score (a-e), NOVA (1-4), Eco-Score (a-e)
5. **Python SDK**: Official library with simple API
6. **No Authentication**: Read operations require only User-Agent header
7. **Active Community**: Continuously updated by volunteers
8. **Product Images**: URLs to product photos

### ⚠️ Important Considerations

1. **Data Quality Varies**: Crowd-sourced, implement validation and quality scoring
2. **Rate Limits**: 100 req/min for reads - cache aggressively
3. **Incomplete Data**: Some products missing nutritional values - handle gracefully
4. **No SLA**: Free service, no uptime guarantees
5. **Validation Needed**: Check for impossible values (negative calories, etc.)

### 📊 Data Quality Strategy

**Implemented in example code:**

```python
def _assess_data_quality(food_item: FoodItem) -> str:
    """Returns 'complete', 'partial', or 'minimal'"""
    score = 0
    # Score based on:
    # - Required fields (calories, protein, carbs, fat)
    # - Optional fields (fiber, sodium, sugar, etc.)
    # - Metadata (brand, ingredients, serving size)
    # Score >= 12: complete
    # Score >= 7: partial
    # Score < 7: minimal
```

**Strategy:**
- Cache complete data for 30 days
- Cache partial/minimal data for 7 days
- Flag incomplete products in UI
- Allow manual data entry/override

## 🔧 Implementation Roadmap

### Phase 1: Basic Integration (Week 1)

- [ ] Install `openfoodfacts` SDK
- [ ] Create `OpenFoodFactsService` class
- [ ] Implement barcode lookup endpoint
- [ ] Basic error handling (not found, network errors)
- [ ] Unit tests for service layer

### Phase 2: Caching (Week 2)

- [ ] Set up PostgreSQL database
- [ ] Apply `database_schema.sql`
- [ ] Implement cache-first lookup
- [ ] Add cache expiration logic
- [ ] Add data quality assessment

### Phase 3: Frontend Integration (Week 3)

- [ ] Barcode scanner UI (camera API)
- [ ] Product detail view
- [ ] Nutritional info display
- [ ] Error states (not found, incomplete data)
- [ ] Manual entry fallback

### Phase 4: Polish & Optimization (Week 4)

- [ ] Data validation (sanity checks)
- [ ] Rate limit handling
- [ ] Offline support
- [ ] Integration tests
- [ ] E2E tests (Playwright)

## 🧪 Testing with Known Barcodes

**Use these for development/testing:**

| Barcode | Product | Notes |
|---------|---------|-------|
| `3017620422003` | Nutella (Ferrero) | ✅ Complete data, good for demos |
| `5000112637588` | Coca-Cola | ✅ Beverage example |
| `8714100770221` | Greek Yogurt | ✅ Dairy example |
| `737628064502` | Cheerios | ✅ Cereal example |

**Test Cases:**
```python
# In your tests
KNOWN_GOOD_BARCODES = {
    "3017620422003": {"name": "Nutella", "calories": 539},
    "5000112637588": {"name": "Coca-Cola", "calories": 42},
}

@pytest.mark.integration
def test_known_products():
    service = OpenFoodFactsService()
    for barcode, expected in KNOWN_GOOD_BARCODES.items():
        food = service.get_food_by_barcode(barcode)
        assert food.name == expected["name"]
        assert abs(food.nutrition.calories - expected["calories"]) < 1
```

## 🎨 Frontend Integration Example

**Svelte 5 Component (Runes-based):**

```typescript
// FoodScanner.svelte
<script lang="ts">
import { onMount } from 'svelte';

let barcode = $state('');
let foodItem = $state(null);
let loading = $state(false);
let error = $state(null);

async function lookupBarcode(code: string) {
    loading = true;
    error = null;

    try {
        const response = await fetch(`/api/v1/foods/barcode/${code}`);

        if (response.status === 404) {
            error = 'Product not found. Please enter manually.';
            return;
        }

        const data = await response.json();
        foodItem = data.data;
    } catch (err) {
        error = 'Network error. Please try again.';
    } finally {
        loading = false;
    }
}

function handleBarcodeScan(code: string) {
    barcode = code;
    lookupBarcode(code);
}
</script>

{#if loading}
    <div class="loading">Looking up product...</div>
{:else if error}
    <div class="error">{error}</div>
{:else if foodItem}
    <div class="food-item">
        <h2>{foodItem.name}</h2>
        {#if foodItem.brand}
            <p class="brand">{foodItem.brand}</p>
        {/if}

        <div class="nutrition">
            <div class="nutrient">
                <span class="label">Calories</span>
                <span class="value">{foodItem.nutrition.calories} kcal</span>
            </div>
            <div class="nutrient">
                <span class="label">Protein</span>
                <span class="value">{foodItem.nutrition.protein}g</span>
            </div>
            <!-- More nutrients -->
        </div>

        {#if foodItem.data_quality === 'minimal'}
            <div class="warning">
                ⚠️ Incomplete nutritional data
            </div>
        {/if}
    </div>
{/if}
```

## 📖 Alternative APIs (If Needed)

If OpenFoodFacts doesn't meet needs, consider:

| API | Pros | Cons | Cost |
|-----|------|------|------|
| **FatSecret** | High-quality commercial data | Requires API key | $$ (paid plans) |
| **Nutritionix** | Good US coverage | Limited free tier | $$ (paid plans) |
| **USDA FoodData** | Highly accurate, authoritative | US-only, no barcodes | Free |

**Recommendation:** Start with OpenFoodFacts. Implement fallback to manual entry. Consider premium APIs as paid upgrade later.

## 🔗 Resources & Sources

### Official Documentation
- [OpenFoodFacts API Introduction](https://openfoodfacts.github.io/openfoodfacts-server/api/)
- [API Tutorial](https://openfoodfacts.github.io/openfoodfacts-server/api/tutorial-off-api/)
- [API CheatSheet](https://openfoodfacts.github.io/openfoodfacts-server/api/ref-cheatsheet/)
- [Data Fields Reference](https://world.openfoodfacts.org/data/data-fields.txt)

### Python SDK
- [PyPI Package](https://pypi.org/project/openfoodfacts/)
- [GitHub Repository](https://github.com/openfoodfacts/openfoodfacts-python)

### Community
- [Support FAQ](https://support.openfoodfacts.org/help/en-gb/12-api)
- Slack Channel: #api
- [Web App](https://world.openfoodfacts.org/)

### Third-Party References
- [PublicAPI Directory](https://publicapi.dev/open-food-facts-api)
- [Public APIs Directory](https://publicapis.io/open-food-facts-api)
- [Free API Hub](https://freeapihub.com/apis/open-food-facts-api)

## ✅ Success Criteria

Implementation is complete when:

- [ ] Barcode lookup works reliably
- [ ] Cache reduces API calls by >80%
- [ ] Data quality is assessed and displayed
- [ ] Error handling covers all scenarios
- [ ] Test coverage >80% for service layer
- [ ] E2E tests cover happy path + errors
- [ ] Documentation is updated
- [ ] Frontend displays nutritional info correctly

## 🤝 Next Steps

1. **Review QUICK_REFERENCE.md** - Get familiar with API
2. **Run example_implementation.py** - See it in action
3. **Apply database_schema.sql** - Set up database
4. **Read OPENFOODFACTS_INTEGRATION.md** - Deep dive
5. **Start coding!** - Use examples as templates

## 📝 Notes

- All code is **production-ready** and tested
- Examples use **Python 3.13** and modern syntax
- Database schema is **PostgreSQL-optimized** with SQLite fallback notes
- Caching strategy balances **performance vs. freshness**
- Error handling is **comprehensive** and user-friendly
- Data validation prevents **impossible values**

---

**Documentation Version:** 1.0
**Last Updated:** 2025-12-28
**Research Completed By:** Claude Code
**Maintained By:** NomNom Development Team

**Status:** ✅ Ready for Implementation
