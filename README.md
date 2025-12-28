# NomNom 🍽️

Calorie and nutrition tracking application for shared households with percentage-based meal splits.

## Features

- **Shared household meals** with percentage-based portion splits
- **Food barcode scanning** using local OpenFoodFacts database (~3M products)
- **Meal templates** (reusable recipes with multiple ingredients)
- **Custom food items** (manually override or create nutrition data)
- **Meal planning** (daily/weekly meal prep)
- **Shopping list generation** from planned meals
- **Goal tracking** with dashboard and progress visualization

## Technology Stack

- **Backend**: FastAPI (Python 3.13+)
- **Database**: MongoDB 8.0 (OpenFoodFacts + app data)
- **Frontend**: Svelte 5 (SvelteKit)
- **Deployment**: Docker

## Quick Start

### Prerequisites

- Python 3.13+
- Docker
- Node.js 18+ (for frontend)

### Backend Setup

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Start MongoDB
docker-compose up -d

# Import OpenFoodFacts database (first time only - ~20GB download, ~80GB disk)
./scripts/setup_mongodb.sh

# Create indexes and seed users
python scripts/create_indexes.py
python scripts/seed_users.py

# Run backend
python main.py
```

Backend runs on http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:5173

## Project Structure

See [CLAUDE.md](CLAUDE.md) for comprehensive development documentation.

## Users

- **nyntjie** - Default daily goals: 2000 cal, 150g protein, 250g carbs, 65g fat
- **unit** - Default daily goals: 2200 cal, 160g protein, 275g carbs, 70g fat

## Development

```bash
# Quality checks
ruff check .
ruff format .
mypy app/

# Run tests
pytest

# MongoDB admin
docker exec -it nomnom-mongodb mongosh
```

## Documentation

- [Plan](plan.md) - Complete implementation plan and database schema
- [CLAUDE.md](CLAUDE.md) - Development guidelines for Claude Code

## License

MIT
