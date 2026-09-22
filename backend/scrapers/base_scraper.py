"""
Base Scraper Architecture for NutriDeals
Standardized interface, Pydantic models, strict blacklist filtering, and category classification.
"""

from abc import ABC, abstractmethod
import re
from typing import List, Optional
from pydantic import BaseModel, Field


# Category taxonomy for NutriDeals supplement engine
VALID_CATEGORIES = [
    "whey",
    "creatine",
    "pre_workout",
    "electrolytes",
    "creme_de_riz",
    "citrulline",
    "glycerol",
    "multivitamines"
]


class ProductVariant(BaseModel):
    id: Optional[str] = None
    title: str
    flavor: Optional[str] = None
    price: float
    weight_kg: Optional[float] = None
    price_per_kg: Optional[float] = None
    sku: Optional[str] = None
    available: bool = True
    url: Optional[str] = None


class ScrapedProduct(BaseModel):
    brand: str
    title: str
    url: str
    image_url: Optional[str] = None
    category: str = "whey"
    variants: List[ProductVariant] = Field(default_factory=list)
    min_price: float = 0.0
    min_price_per_kg: Optional[float] = None


class BaseScraper(ABC):
    """
    Abstract Base Scraper establishing template method and strict filtering rules.
    """

    # 1. Strict Blacklist for Non-Supplements, Apparel, and Solid Snacks
    BLACK_LIST_KEYWORDS = [
        # Apparel & Accessories
        "leggings", "legging", "shorts", "short", "t-shirt", "tshirt", "shirt",
        "hoodie", "fleece", "jacket", "women", "men", "shaker", "pillbox", "strap",
        "belt", "gourde", "serviette", "ceinture", "bande", "casquette", "sac",
        "bottle", "mug", "cup", "ebook", "livre", "pantalon", "boite-a-pilules",
        "chaussettes", "gants", "towel", "bag", "beanie", "socks",
        # Solid Snacks, Food & Spreads
        "bar", "barre", "bars", "crispy", "cookie", "cookies", "snack", "snacks",
        "peanut butter", "peanut", "beurre", "spread", "tartiner", "pancake", "pancakes",
        "wafer", "sauce", "syrup", "drip", "crunchy", "pâte", "oat", "avena", "farine",
        "porridge", "brownie", "pudding", "cold brew", "starterkit", "box", "pack",
        "muesli", "granola", "chips", "biscuit", "cake", "bread", "pain", "jam"
    ]

    # 2. Whitelist Keywords specifically for Whey & Protein powders
    WHEY_KEYWORDS = [
        "whey", "isolate", "isolat", "hydrolysat", "hydrolyzed", "clear whey",
        "native whey", "casein", "caséine", "protimuscle", "musclewhey",
        "blend protein", "milk protein", "protéine d'oeuf", "proteine d'oeuf",
        "soy protein", "protéine de soja"
    ]

    # Minimum threshold weight for bulk tubs/bags (rejects 30g sachets or samples)
    MIN_WEIGHT_KG = 0.35  # 350 grams

    def __init__(self, brand_name: str, base_url: str):
        self.brand_name = brand_name
        self.base_url = base_url.rstrip("/")

    @classmethod
    def is_blacklisted(cls, text: str) -> bool:
        """
        Checks if text contains any blacklisted term.
        """
        if not text:
            return False
        clean_text = text.lower()
        for term in cls.BLACK_LIST_KEYWORDS:
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, clean_text):
                return True
        return False

    @classmethod
    def is_valid_whey_product(cls, title: str, description: str = "", tags: Optional[List[str]] = None) -> bool:
        """
        Validates that a product is strictly a whey/protein powder supplement
        and not an accessory, snack, or non-whey supplement.
        """
        combined = f"{title} {description} {' '.join(tags or [])}".lower()

        # Reject if blacklisted term found
        if cls.is_blacklisted(combined):
            return False

        # Reject if missing whey keywords
        has_whey_kw = any(re.search(r'\b' + re.escape(kw) + r'\b', combined) for kw in cls.WHEY_KEYWORDS)
        return has_whey_kw

    @staticmethod
    def parse_weight_in_kg(text: Optional[str]) -> Optional[float]:
        """
        Parses weight strings into float kg (e.g., '1000g', '2.27kg', '900 g').
        """
        if not text:
            return None
        
        match = re.search(
            r'(\d+(?:[\.,]\d+)?)\s*(kg|kilo|kilos|g|gramme|grammes|grams|lb|lbs)\b',
            text,
            re.IGNORECASE
        )
        if match:
            val_str, unit = match.groups()
            val = float(val_str.replace(',', '.'))
            unit = unit.lower()
            if unit in ['g', 'gramme', 'grammes', 'grams']:
                return round(val / 1000.0, 3)
            elif unit in ['lb', 'lbs']:
                return round(val * 0.453592, 3)
            else:
                return round(val, 3)
        return None

    @staticmethod
    def detect_category(title: str, tags: Optional[List[str]] = None) -> str:
        """
        Categorizes supplement product according to NutriDeals taxonomy.
        Currently focuses on whey variants, expandable to creatine, pre-workout, etc.
        """
        combined = (title + " " + " ".join(tags or [])).lower()
        
        if "creatine" in combined or "créatine" in combined:
            return "creatine"
        elif "pre-workout" in combined or "preworkout" in combined or "booster" in combined:
            return "pre_workout"
        elif "electrolytes" in combined or "électrolytes" in combined:
            return "electrolytes"
        elif "creme de riz" in combined or "crème de riz" in combined or "rice cream" in combined:
            return "creme_de_riz"
        elif "citrulline" in combined:
            return "citrulline"
        elif "glycerol" in combined or "glycérol" in combined:
            return "glycerol"
        elif "multivitamin" in combined or "multivitamines" in combined:
            return "multivitamines"
        
        # Default active target category
        return "whey"

    @staticmethod
    def calculate_price_per_kg(price: float, weight_kg: Optional[float]) -> Optional[float]:
        """Calculates price per kg (€/kg)."""
        if price and weight_kg and weight_kg > 0:
            return round(price / weight_kg, 2)
        return None

    @abstractmethod
    def fetch_data() -> List[dict]:
        """Fetch raw products/data from target source."""
        pass

    @abstractmethod
    def parse_products(self, raw_items: List[dict]) -> List[ScrapedProduct]:
        """Parse raw items into standardized ScrapedProduct objects."""
        pass

    def scrape(self) -> List[ScrapedProduct]:
        """
        Template method executing standard scraping lifecycle.
        """
        print(f"[{self.brand_name}] Starting whey scraping from {self.base_url}...")
        raw_data = self.fetch_data()
        products = self.parse_products(raw_data)

        # Post-process min prices and filter invalid variants/products
        valid_products = []
        for prod in products:
            if not prod.variants:
                continue

            # Ensure min price calculation
            valid_prices = [v.price for v in prod.variants if v.price > 0]
            if valid_prices:
                prod.min_price = min(valid_prices)
            
            valid_pkg = [v.price_per_kg for v in prod.variants if v.price_per_kg and v.price_per_kg > 0]
            if valid_pkg:
                prod.min_price_per_kg = min(valid_pkg)

            valid_products.append(prod)

        print(f"[{self.brand_name}] Scraped {len(valid_products)} clean whey products with {sum(len(p.variants) for p in valid_products)} total variants.")
        return valid_products
