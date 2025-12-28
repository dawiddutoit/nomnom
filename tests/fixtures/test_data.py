"""Test data fixtures for NomNom tests.

Contains known-good barcodes, test users, and expected nutritional data.
"""

from typing import TypedDict


class NutritionalData(TypedDict):
    """Nutritional information structure."""
    barcode: str
    name: str
    brand: str | None
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float | None
    sodium: float | None
    quality: str  # 'complete', 'partial', 'minimal'


class UserGoals(TypedDict):
    """User nutritional goals."""
    calories: int
    protein: int
    carbs: int
    fat: int


class TestUser(TypedDict):
    """Test user account."""
    email: str
    password: str
    goals: UserGoals


# Known-good barcodes from OpenFoodFacts
# These have been verified to return complete data
KNOWN_BARCODES: dict[str, NutritionalData] = {
    "nutella": {
        "barcode": "3017620422003",
        "name": "Nutella",
        "brand": "Ferrero",
        "calories": 539,
        "protein": 6.3,
        "carbs": 57.5,
        "fat": 30.9,
        "fiber": 0,
        "sodium": 0.0428,
        "quality": "complete"
    },
    "coca_cola": {
        "barcode": "5000112637588",
        "name": "Coca-Cola",
        "brand": "Coca-Cola",
        "calories": 42,
        "protein": 0,
        "carbs": 10.6,
        "fat": 0,
        "fiber": 0,
        "sodium": 0.01,
        "quality": "complete"
    },
    "greek_yogurt": {
        "barcode": "8714100770221",
        "name": "Greek Yogurt",
        "brand": "FAGE",
        "calories": 97,
        "protein": 10,
        "carbs": 4,
        "fat": 5,
        "fiber": None,
        "sodium": 0.05,
        "quality": "partial"
    },
    "cheerios": {
        "barcode": "737628064502",
        "name": "Cheerios",
        "brand": "General Mills",
        "calories": 367,
        "protein": 11.7,
        "carbs": 73.3,
        "fat": 5,
        "fiber": 10,
        "sodium": 0.58,
        "quality": "complete"
    }
}


# Test user accounts
TEST_USERS: dict[str, TestUser] = {
    "default": {
        "email": "test@nomnom.app",
        "password": "Test123!",
        "goals": {
            "calories": 2000,
            "protein": 150,
            "carbs": 200,
            "fat": 67
        }
    },
    "high_protein": {
        "email": "athlete@nomnom.app",
        "password": "Athlete123!",
        "goals": {
            "calories": 2500,
            "protein": 200,
            "carbs": 250,
            "fat": 83
        }
    },
    "low_carb": {
        "email": "keto@nomnom.app",
        "password": "Keto123!",
        "goals": {
            "calories": 1800,
            "protein": 120,
            "carbs": 50,
            "fat": 140
        }
    }
}


# Invalid/edge case barcodes for testing error handling
INVALID_BARCODES = {
    "not_found": "0000000000000",  # Doesn't exist in OpenFoodFacts
    "too_short": "123",  # Invalid format
    "too_long": "12345678901234567890",  # Invalid format
    "non_numeric": "ABC123XYZ",  # Invalid characters
}


# Sample food log entries for testing
SAMPLE_FOOD_LOG = [
    {
        "barcode": "737628064502",  # Cheerios
        "meal_type": "breakfast",
        "quantity": 1,
        "unit": "serving"
    },
    {
        "barcode": "8714100770221",  # Greek Yogurt
        "meal_type": "snack",
        "quantity": 150,
        "unit": "g"
    },
    {
        "barcode": "5000112637588",  # Coca-Cola
        "meal_type": "lunch",
        "quantity": 330,
        "unit": "ml"
    },
    {
        "barcode": "3017620422003",  # Nutella
        "meal_type": "snack",
        "quantity": 15,
        "unit": "g"
    }
]


def get_barcode(product_key: str) -> str:
    """Get barcode number for a known product."""
    return KNOWN_BARCODES[product_key]["barcode"]


def get_expected_calories(product_key: str) -> float:
    """Get expected calories for a known product."""
    return KNOWN_BARCODES[product_key]["calories"]


def get_test_user(user_key: str = "default") -> TestUser:
    """Get test user credentials and goals."""
    return TEST_USERS[user_key]
