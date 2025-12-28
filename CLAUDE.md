# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**NomNom** is a calorie and nutrition tracking application with the following core features:

- **Day Planner View**: Calendar-style interface showing daily food intake
- **Food Entry**: Quick food item logging via manual entry or barcode scanning
- **Barcode Recognition**: Camera-based barcode scanning with local DB caching
- **Future: Image Recognition**: Identify food from photos (non-MVP)
- **Nutritional Analysis**: Calculate calories and nutritional values
- **Multi-User Support**: Multiple users with personalized goals
- **Smart Suggestions**: AI-powered meal recommendations
- **Goal Tracking**: Dashboard comparing actual intake vs. goals

## Architecture

### Technology Stack

**Backend**:
- **Language**: Python 3.13+
- **Framework**: TBD (FastAPI recommended for API endpoints with automatic OpenAPI spec generation)
- **Database**: TBD (PostgreSQL recommended for production, SQLite for development)
- **ORM**: TBD (SQLAlchemy recommended)
- **Barcode API**: TBD (OpenFoodFacts API or similar)

**Frontend**:
- **Framework**: Svelte 5 (runes-based)
- **Component Source**: `/Users/dawiddutoit/projects/play/svelte` (component library for reuse)
- **Strategy**: Cherry-pick components from existing Svelte showcase library rather than building from scratch

**Integration Pattern**:
- Backend serves RESTful API endpoints
- Frontend consumes API via typed client functions
- OpenAPI/Swagger for API documentation and TypeScript type generation

### Data Flow

1. **Food Entry Path**:
   - User captures barcode via camera → Frontend sends barcode to backend
   - Backend checks local DB → If found, return cached data
   - If not found → Query external API (OpenFoodFacts) → Cache in DB → Return to frontend
   - User confirms/tags food item → Backend persists to user's food log

2. **Goal Tracking Path**:
   - User sets nutritional goals (calories, macros, etc.)
   - Daily intake aggregated from food log entries
   - Dashboard compares aggregated totals vs. goals

### Key Architectural Decisions

- **Backend Language**: Initially Python, but flexible - can switch to TypeScript/Node.js if it simplifies Svelte integration
- **Component Reuse**: Leverage existing Svelte showcase library (`/Users/dawiddutoit/projects/play/svelte`) for UI components
- **Mobile-First**: Designed for phone camera barcode scanning
- **Offline-First Consideration**: Local DB caching for previously scanned items

## Development Setup

### Prerequisites

- Python 3.13+
- Node.js 18+ or 20+ (for Svelte frontend)
- Virtual environment (`venv` or `uv`)

### Backend Setup

```bash
# Create and activate virtual environment
python3.13 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Run development server (once framework chosen)
# Example for FastAPI: uvicorn main:app --reload
```

### Frontend Setup

```bash
# Navigate to frontend directory (to be created)
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
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

## Code Standards

### Python Standards

- **Type Hints**: Use type hints for all function signatures
- **Async/Await**: Prefer async operations for I/O (database, API calls)
- **Error Handling**: Explicit error handling, fail-fast principle
- **Docstrings**: Concise one-liners for simple functions; detailed for complex logic
- **Naming**: snake_case for variables/functions, PascalCase for classes

### API Design

- **RESTful Endpoints**: Follow REST conventions
- **OpenAPI Spec**: Auto-generate from FastAPI (if chosen)
- **Versioning**: API versioning strategy (e.g., `/api/v1/`)
- **Response Format**: Consistent JSON response structure

```python
# Example response format
{
    "success": true,
    "data": {...},
    "error": null
}

# Error response
{
    "success": false,
    "data": null,
    "error": {
        "code": "BARCODE_NOT_FOUND",
        "message": "No food item found for barcode 123456789"
    }
}
```

### Database Schema (Conceptual)

**Users**:
- id, email, password_hash, created_at, updated_at

**UserGoals**:
- id, user_id, daily_calories, daily_protein, daily_carbs, daily_fat

**FoodItems**:
- id, barcode, name, brand, calories, protein, carbs, fat, fiber, sodium, etc.
- source (local/external API), created_at, updated_at

**FoodLog**:
- id, user_id, food_item_id, consumed_at, quantity, unit
- user_notes, tags

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

## Key Features to Implement (MVP)

### Phase 1: Core Infrastructure
- [ ] Backend framework setup (FastAPI recommended)
- [ ] Database setup with migrations
- [ ] User authentication (JWT-based)
- [ ] Basic API endpoints (CRUD for users, foods, logs)

### Phase 2: Food Database
- [ ] Barcode scanning integration (frontend camera API)
- [ ] Local food item database
- [ ] External API integration (OpenFoodFacts or similar)
- [ ] Caching strategy for scanned items

### Phase 3: User Experience
- [ ] Day planner view (calendar-style)
- [ ] Quick food entry UI
- [ ] Food detail view with nutritional info
- [ ] User goal setting

### Phase 4: Analytics & Insights
- [ ] Daily intake aggregation
- [ ] Dashboard with charts (calories, macros)
- [ ] Goal comparison visualization
- [ ] Smart suggestions (basic)

## Critical Decisions Needed

Before implementation, decide on:

1. **Backend Framework**: FastAPI (recommended), Flask, Django REST Framework?
2. **Database**: PostgreSQL (production), SQLite (development)?
3. **Authentication**: JWT, session-based, OAuth?
4. **Barcode API**: OpenFoodFacts (free, comprehensive), FatSecret, Nutritionix?
5. **Deployment**: Docker, serverless (AWS Lambda/Vercel), traditional VPS?
6. **Image Recognition**: External service (Google Vision API, Clarifai) or custom model?

## External API Considerations

### OpenFoodFacts API (Recommended)

- **Pros**: Free, open-source, 2.8M+ products, comprehensive nutritional data
- **Cons**: Data quality varies, may need validation/cleanup
- **Endpoint**: `https://world.openfoodfacts.org/api/v2/product/{barcode}.json`

### Alternative APIs

- **FatSecret**: Comprehensive, requires API key
- **Nutritionix**: Good coverage, commercial pricing
- **USDA FoodData Central**: Government data, highly accurate but limited to US foods

## Testing Strategy

### Backend Tests
- **Unit Tests**: Service layer, utility functions
- **Integration Tests**: API endpoints, database operations
- **Test Framework**: pytest

### Frontend Tests
- **Unit Tests**: Utility functions, state management (Vitest)
- **Component Tests**: Form validation, UI interactions (Vitest + Testing Library)
- **E2E Tests**: Critical user flows - scan barcode, log food, view dashboard (Playwright)

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
