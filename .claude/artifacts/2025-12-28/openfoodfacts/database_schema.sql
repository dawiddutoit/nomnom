-- NomNom Database Schema for OpenFoodFacts Integration
-- PostgreSQL DDL for food items and user food log
--
-- Usage:
--   psql -U nomnom_user -d nomnom_db -f database_schema.sql

-- ============================================================================
-- Food Items Table (Cached from OpenFoodFacts)
-- ============================================================================

CREATE TABLE IF NOT EXISTS food_items (
    -- Primary identification
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    barcode VARCHAR(50) UNIQUE NOT NULL,

    -- Basic product info
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),

    -- Nutritional values (per 100g/100ml)
    -- All required fields from OpenFoodFacts
    calories DECIMAL(10, 2) NOT NULL DEFAULT 0,  -- kcal
    protein DECIMAL(10, 2) NOT NULL DEFAULT 0,   -- g
    carbs DECIMAL(10, 2) NOT NULL DEFAULT 0,     -- g
    fat DECIMAL(10, 2) NOT NULL DEFAULT 0,       -- g

    -- Optional nutritional fields
    fiber DECIMAL(10, 2),                        -- g
    sodium DECIMAL(10, 2),                       -- g
    sugar DECIMAL(10, 2),                        -- g
    saturated_fat DECIMAL(10, 2),                -- g

    -- Extended nutritional fields (optional)
    trans_fat DECIMAL(10, 2),                    -- g
    monounsaturated_fat DECIMAL(10, 2),          -- g
    polyunsaturated_fat DECIMAL(10, 2),          -- g
    cholesterol DECIMAL(10, 2),                  -- mg

    -- Vitamins (optional)
    vitamin_a DECIMAL(10, 2),                    -- μg
    vitamin_c DECIMAL(10, 2),                    -- mg
    vitamin_d DECIMAL(10, 2),                    -- μg
    vitamin_b12 DECIMAL(10, 2),                  -- μg

    -- Minerals (optional)
    calcium DECIMAL(10, 2),                      -- mg
    iron DECIMAL(10, 2),                         -- mg
    potassium DECIMAL(10, 2),                    -- mg
    magnesium DECIMAL(10, 2),                    -- mg

    -- Product metadata
    categories TEXT[],                           -- Array of category strings
    ingredients TEXT,                            -- Full ingredient list
    allergens TEXT[],                            -- Array of allergen strings
    serving_size VARCHAR(50),                    -- e.g., "15 g", "250 ml"

    -- Quality scores
    nutriscore_grade CHAR(1),                    -- a, b, c, d, e
    nova_group SMALLINT,                         -- 1, 2, 3, 4
    ecoscore_grade CHAR(1),                      -- a, b, c, d, e

    -- Images
    image_url TEXT,                              -- Product image URL

    -- Data provenance and quality
    source VARCHAR(50) DEFAULT 'openfoodfacts',  -- Data source
    data_quality VARCHAR(20),                    -- 'complete', 'partial', 'minimal'

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_nutriscore CHECK (nutriscore_grade IN ('a', 'b', 'c', 'd', 'e') OR nutriscore_grade IS NULL),
    CONSTRAINT valid_nova CHECK (nova_group BETWEEN 1 AND 4 OR nova_group IS NULL),
    CONSTRAINT valid_ecoscore CHECK (ecoscore_grade IN ('a', 'b', 'c', 'd', 'e') OR ecoscore_grade IS NULL),
    CONSTRAINT valid_data_quality CHECK (data_quality IN ('complete', 'partial', 'minimal', 'unknown') OR data_quality IS NULL),
    CONSTRAINT positive_nutrition CHECK (
        calories >= 0 AND
        protein >= 0 AND
        carbs >= 0 AND
        fat >= 0
    )
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Primary lookup by barcode (already unique, but explicit index)
CREATE INDEX IF NOT EXISTS idx_food_items_barcode ON food_items(barcode);

-- Full-text search on product name
CREATE INDEX IF NOT EXISTS idx_food_items_name_search
    ON food_items USING gin(to_tsvector('english', name));

-- Search by brand
CREATE INDEX IF NOT EXISTS idx_food_items_brand ON food_items(brand);

-- Filter by data quality
CREATE INDEX IF NOT EXISTS idx_food_items_quality ON food_items(data_quality);

-- Filter by last sync date (for cache invalidation)
CREATE INDEX IF NOT EXISTS idx_food_items_last_synced ON food_items(last_synced_at);

-- Partial index for incomplete data (data that needs refresh)
CREATE INDEX IF NOT EXISTS idx_food_items_incomplete
    ON food_items(barcode)
    WHERE data_quality IN ('partial', 'minimal');

-- ============================================================================
-- Users Table (for multi-user support)
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================================================
-- User Goals Table (nutritional targets)
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Daily nutritional goals
    daily_calories DECIMAL(10, 2) NOT NULL,
    daily_protein DECIMAL(10, 2),
    daily_carbs DECIMAL(10, 2),
    daily_fat DECIMAL(10, 2),
    daily_fiber DECIMAL(10, 2),
    daily_sodium DECIMAL(10, 2),

    -- Goal metadata
    goal_type VARCHAR(50),  -- 'weight_loss', 'maintenance', 'muscle_gain', 'custom'
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Only one active goal per user
    CONSTRAINT unique_active_goal_per_user UNIQUE (user_id, active)
        WHERE active = TRUE
);

CREATE INDEX IF NOT EXISTS idx_user_goals_user_id ON user_goals(user_id);

-- ============================================================================
-- Food Log Table (user food consumption)
-- ============================================================================

CREATE TABLE IF NOT EXISTS food_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    food_item_id UUID NOT NULL REFERENCES food_items(id) ON DELETE CASCADE,

    -- Consumption details
    consumed_at TIMESTAMP NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,  -- Amount consumed
    unit VARCHAR(20) NOT NULL,         -- 'g', 'ml', 'serving', 'oz'

    -- Calculated nutritional values (denormalized for performance)
    -- These are calculated based on quantity and food_item nutrition
    total_calories DECIMAL(10, 2),
    total_protein DECIMAL(10, 2),
    total_carbs DECIMAL(10, 2),
    total_fat DECIMAL(10, 2),

    -- User notes and tags
    user_notes TEXT,
    tags TEXT[],                       -- ['breakfast', 'snack', 'homemade']
    meal_type VARCHAR(50),             -- 'breakfast', 'lunch', 'dinner', 'snack'

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_quantity CHECK (quantity > 0),
    CONSTRAINT valid_unit CHECK (unit IN ('g', 'ml', 'serving', 'oz', 'cup', 'tbsp', 'tsp'))
);

-- ============================================================================
-- Indexes for Food Log (Query Performance)
-- ============================================================================

-- Primary queries: user's recent food entries
CREATE INDEX IF NOT EXISTS idx_food_log_user_consumed
    ON food_log(user_id, consumed_at DESC);

-- Daily aggregation queries
CREATE INDEX IF NOT EXISTS idx_food_log_consumed_date
    ON food_log(user_id, DATE(consumed_at));

-- Filter by meal type
CREATE INDEX IF NOT EXISTS idx_food_log_meal_type
    ON food_log(meal_type);

-- Tag search (GIN index for array)
CREATE INDEX IF NOT EXISTS idx_food_log_tags
    ON food_log USING gin(tags);

-- ============================================================================
-- Triggers for Automatic Timestamp Updates
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for food_items
DROP TRIGGER IF EXISTS update_food_items_updated_at ON food_items;
CREATE TRIGGER update_food_items_updated_at
    BEFORE UPDATE ON food_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for users
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for user_goals
DROP TRIGGER IF EXISTS update_user_goals_updated_at ON user_goals;
CREATE TRIGGER update_user_goals_updated_at
    BEFORE UPDATE ON user_goals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for food_log
DROP TRIGGER IF EXISTS update_food_log_updated_at ON food_log;
CREATE TRIGGER update_food_log_updated_at
    BEFORE UPDATE ON food_log
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Sample Queries for Common Operations
-- ============================================================================

-- Get today's food intake for a user
COMMENT ON TABLE food_log IS
'Sample query - Today''s intake:
SELECT f.name, fl.quantity, fl.unit, fl.total_calories
FROM food_log fl
JOIN food_items f ON fl.food_item_id = f.id
WHERE fl.user_id = $1
  AND DATE(fl.consumed_at) = CURRENT_DATE
ORDER BY fl.consumed_at DESC;';

-- Daily calorie totals (last 7 days)
COMMENT ON COLUMN food_log.total_calories IS
'Sample query - Last 7 days calories:
SELECT DATE(consumed_at) AS date, SUM(total_calories) AS total
FROM food_log
WHERE user_id = $1
  AND consumed_at >= CURRENT_DATE - INTERVAL ''7 days''
GROUP BY DATE(consumed_at)
ORDER BY date DESC;';

-- Search food items by name
COMMENT ON INDEX idx_food_items_name_search IS
'Sample query - Search by name:
SELECT barcode, name, brand, calories, protein
FROM food_items
WHERE to_tsvector(''english'', name) @@ plainto_tsquery(''english'', $1)
ORDER BY name
LIMIT 20;';

-- ============================================================================
-- SQLite Alternative Schema (for development/testing)
-- ============================================================================

/*
If using SQLite instead of PostgreSQL, replace:

1. UUID with TEXT
2. DECIMAL(10, 2) with REAL
3. TEXT[] with TEXT (store as JSON: '["item1", "item2"]')
4. to_tsvector with FTS5 virtual table
5. gen_random_uuid() with a UUID library in application code
6. Triggers work the same way

Example SQLite conversion:

CREATE TABLE food_items (
    id TEXT PRIMARY KEY,
    barcode TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    ...
    categories TEXT,  -- JSON string: '["breakfast", "spreads"]'
    ...
);
*/

-- ============================================================================
-- Data Insertion Example
-- ============================================================================

/*
-- Insert sample food item (Nutella)
INSERT INTO food_items (
    barcode, name, brand, calories, protein, carbs, fat,
    fiber, sodium, sugar, saturated_fat,
    categories, allergens, serving_size,
    nutriscore_grade, nova_group, data_quality
) VALUES (
    '3017620422003',
    'Nutella',
    'Ferrero',
    539, 6.3, 57.5, 30.9,
    0, 0.0428, 56.3, 10.6,
    ARRAY['Spreads', 'Chocolate spreads', 'Hazelnut spreads'],
    ARRAY['milk', 'nuts', 'soybeans'],
    '15 g',
    'e',
    4,
    'complete'
);
*/
