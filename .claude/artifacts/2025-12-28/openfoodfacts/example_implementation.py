"""
OpenFoodFacts Integration Example for NomNom

Complete working example showing how to integrate OpenFoodFacts API
into the NomNom calorie tracking application.

Usage:
    python example_implementation.py
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Optional
import json
import sqlite3
import openfoodfacts


# ============================================================================
# Data Models
# ============================================================================


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
    data_quality: str = "unknown"  # complete, partial, minimal


# ============================================================================
# OpenFoodFacts Service
# ============================================================================


class OpenFoodFactsService:
    """Service for interacting with OpenFoodFacts API."""

    def __init__(self, user_agent: str = "NomNom/1.0 (contact@nomnom.app)"):
        self.api = openfoodfacts.API(user_agent=user_agent)

    def get_food_by_barcode(self, barcode: str) -> Optional[FoodItem]:
        """
        Fetch food item by barcode.

        Args:
            barcode: Product barcode (EAN-13, UPC-A, etc.)

        Returns:
            FoodItem if found, None otherwise
        """
        try:
            product = self.api.product.get(
                barcode,
                fields=[
                    "code",
                    "product_name",
                    "brands",
                    "nutriments",
                    "categories",
                    "ingredients_text",
                    "allergens",
                    "serving_size",
                    "nutriscore_grade",
                    "nova_group",
                    "image_url",
                ],
            )

            if not product or "product_name" not in product:
                return None

            food_item = self._parse_product(product)
            food_item.data_quality = self._assess_data_quality(food_item)
            return food_item

        except Exception as e:
            print(f"❌ OpenFoodFacts API error: {e}")
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
            saturated_fat=nutriments.get("saturated-fat_100g"),
        )

        # Parse categories (comma-separated string)
        categories_str = product.get("categories", "")
        categories = (
            [c.strip() for c in categories_str.split(",")]
            if categories_str
            else []
        )

        # Parse allergens (comma-separated string with en: prefix)
        allergens_str = product.get("allergens", "")
        allergens = (
            [a.replace("en:", "").strip() for a in allergens_str.split(",")]
            if allergens_str
            else []
        )

        # Get first brand if multiple
        brands_str = product.get("brands", "")
        brand = brands_str.split(",")[0].strip() if brands_str else None

        return FoodItem(
            barcode=product.get("code", ""),
            name=product.get("product_name", "Unknown"),
            brand=brand,
            nutrition=nutrition,
            categories=categories,
            ingredients=product.get("ingredients_text"),
            allergens=allergens,
            serving_size=product.get("serving_size"),
            nutriscore_grade=product.get("nutriscore_grade"),
            nova_group=product.get("nova_group"),
            image_url=product.get("image_url"),
        )

    def _assess_data_quality(self, food_item: FoodItem) -> str:
        """
        Assess data completeness and quality.

        Returns:
            'complete', 'partial', or 'minimal'
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


# ============================================================================
# Caching Layer
# ============================================================================


class FoodItemCache:
    """Local SQLite cache for food items."""

    def __init__(self, db_path: str = "food_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize SQLite cache database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cached_foods (
                barcode TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """
        )
        conn.commit()
        conn.close()

    def get(self, barcode: str) -> Optional[dict]:
        """Get cached food item if not expired."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT data FROM cached_foods WHERE barcode = ? AND expires_at > ?",
            (barcode, datetime.now().isoformat()),
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
        return None

    def set(self, barcode: str, food_item: FoodItem, ttl_days: int = 30):
        """Cache food item with expiration."""
        conn = sqlite3.connect(self.db_path)
        expires_at = datetime.now() + timedelta(days=ttl_days)

        # Convert FoodItem to dict for JSON serialization
        data = asdict(food_item)

        conn.execute(
            """
            INSERT OR REPLACE INTO cached_foods (barcode, data, expires_at)
            VALUES (?, ?, ?)
            """,
            (barcode, json.dumps(data), expires_at.isoformat()),
        )
        conn.commit()
        conn.close()

    def clear_expired(self):
        """Remove expired cache entries."""
        conn = sqlite3.connect(self.db_path)
        result = conn.execute(
            "DELETE FROM cached_foods WHERE expires_at <= ?",
            (datetime.now().isoformat(),),
        )
        deleted_count = result.rowcount
        conn.commit()
        conn.close()
        return deleted_count


# ============================================================================
# Combined Service with Caching
# ============================================================================


class CachedOpenFoodFactsService:
    """OpenFoodFacts service with local caching."""

    def __init__(
        self,
        user_agent: str = "NomNom/1.0 (contact@nomnom.app)",
        cache_path: str = "food_cache.db",
    ):
        self.api_service = OpenFoodFactsService(user_agent=user_agent)
        self.cache = FoodItemCache(cache_path)

    def get_food_by_barcode(self, barcode: str) -> Optional[FoodItem]:
        """
        Get food from cache or API.

        Args:
            barcode: Product barcode

        Returns:
            FoodItem if found (from cache or API), None otherwise
        """
        # Check cache first
        cached_data = self.cache.get(barcode)
        if cached_data:
            print(f"✓ Cache hit for barcode {barcode}")
            return self._dict_to_food_item(cached_data)

        print(f"→ Cache miss for barcode {barcode}, fetching from API...")

        # Fetch from API
        food_item = self.api_service.get_food_by_barcode(barcode)

        # Cache result if found
        if food_item:
            # Use shorter TTL for incomplete data
            ttl = 7 if food_item.data_quality == "minimal" else 30
            self.cache.set(barcode, food_item, ttl_days=ttl)
            print(f"✓ Cached food item with {ttl}-day TTL")

        return food_item

    def _dict_to_food_item(self, data: dict) -> FoodItem:
        """Convert cached dict back to FoodItem."""
        nutrition_data = data["nutrition"]
        nutrition = NutritionalData(**nutrition_data)

        return FoodItem(
            barcode=data["barcode"],
            name=data["name"],
            brand=data["brand"],
            nutrition=nutrition,
            categories=data["categories"],
            ingredients=data["ingredients"],
            allergens=data["allergens"],
            serving_size=data["serving_size"],
            nutriscore_grade=data["nutriscore_grade"],
            nova_group=data["nova_group"],
            image_url=data["image_url"],
            data_quality=data["data_quality"],
        )


# ============================================================================
# Display Helper
# ============================================================================


def display_food_item(food_item: FoodItem):
    """Pretty print food item details."""
    print("\n" + "=" * 70)
    print(f"🍔 {food_item.name}")
    if food_item.brand:
        print(f"   Brand: {food_item.brand}")
    print("=" * 70)

    print(f"\n📊 Nutritional Information (per 100g):")
    print(f"   Calories:       {food_item.nutrition.calories:.1f} kcal")
    print(f"   Protein:        {food_item.nutrition.protein:.1f} g")
    print(f"   Carbohydrates:  {food_item.nutrition.carbs:.1f} g")
    if food_item.nutrition.sugar is not None:
        print(f"     - Sugars:     {food_item.nutrition.sugar:.1f} g")
    print(f"   Fat:            {food_item.nutrition.fat:.1f} g")
    if food_item.nutrition.saturated_fat is not None:
        print(f"     - Saturated:  {food_item.nutrition.saturated_fat:.1f} g")
    if food_item.nutrition.fiber is not None:
        print(f"   Fiber:          {food_item.nutrition.fiber:.1f} g")
    if food_item.nutrition.sodium is not None:
        print(f"   Sodium:         {food_item.nutrition.sodium * 1000:.1f} mg")

    if food_item.serving_size:
        print(f"\n📏 Serving Size: {food_item.serving_size}")

    if food_item.allergens:
        print(f"\n⚠️  Allergens: {', '.join(food_item.allergens)}")

    if food_item.nutriscore_grade:
        grade_emoji = {
            "a": "🟢",
            "b": "🟡",
            "c": "🟠",
            "d": "🟠",
            "e": "🔴",
        }
        emoji = grade_emoji.get(food_item.nutriscore_grade, "⚪")
        print(
            f"\n{emoji} Nutri-Score: {food_item.nutriscore_grade.upper()} (a=best, e=worst)"
        )

    if food_item.nova_group:
        nova_desc = {
            1: "Unprocessed or minimally processed",
            2: "Processed culinary ingredients",
            3: "Processed foods",
            4: "Ultra-processed foods",
        }
        print(
            f"🏭 NOVA Group: {food_item.nova_group} ({nova_desc.get(food_item.nova_group, 'Unknown')})"
        )

    quality_emoji = {
        "complete": "✅",
        "partial": "⚠️",
        "minimal": "❌",
    }
    emoji = quality_emoji.get(food_item.data_quality, "❓")
    print(
        f"\n{emoji} Data Quality: {food_item.data_quality.upper()}"
    )

    if food_item.categories:
        print(f"\n🏷️  Categories: {', '.join(food_item.categories[:3])}")

    print("=" * 70 + "\n")


# ============================================================================
# Demo Usage
# ============================================================================


def main():
    """Demo the OpenFoodFacts integration."""
    print("🍽️  NomNom - OpenFoodFacts Integration Demo\n")

    # Initialize service with caching
    service = CachedOpenFoodFactsService()

    # Example barcodes to test
    test_barcodes = [
        ("3017620422003", "Nutella (Ferrero)"),
        ("5000112637588", "Coke (Coca-Cola)"),
        ("8714100770221", "Greek Yogurt (Milner)"),
        ("invalid_barcode", "Invalid Barcode Test"),
    ]

    for barcode, description in test_barcodes:
        print(f"\n🔍 Looking up: {description} (barcode: {barcode})")
        print("-" * 70)

        food_item = service.get_food_by_barcode(barcode)

        if food_item:
            display_food_item(food_item)
        else:
            print(f"❌ Product not found for barcode: {barcode}\n")

    # Clean up expired cache entries
    print("\n🧹 Cleaning up expired cache entries...")
    deleted = service.cache.clear_expired()
    print(f"   Deleted {deleted} expired entries")

    print("\n✅ Demo complete!")


if __name__ == "__main__":
    main()
