"""
Base Scraper Architecture for NutriDeals
Standardized interface, Pydantic models, strict 100% Pure Whey filtering rules,
and <= 4kg reference price filtering.
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
    compare_at_price: Optional[float] = None
    weight_kg: Optional[float] = None
    price_per_kg: Optional[float] = None
    sku: Optional[str] = None
    available: bool = True
    url: Optional[str] = None
    sweeteners: List[str] = Field(default_factory=list)
    additives_count: int = 0
    health_score: Optional[float] = None


class ScrapedProduct(BaseModel):
    brand: str
    title: str
    url: str
    image_url: Optional[str] = None
    category: str = "whey"
    variants: List[ProductVariant] = Field(default_factory=list)
    min_price: float = 0.0
    min_price_per_kg: Optional[float] = None
    protein_percentage: Optional[float] = None
    has_aminogram: bool = False
    leucine_per_100g: Optional[float] = None
    protein_score: Optional[float] = None
    whey_type: Optional[str] = "fromagere"
    is_grass_fed: bool = False
    origin_country: Optional[str] = "UE"
    extraction_process: Optional[str] = "Standard"
    chemical_free: bool = True
    certifications: List[str] = Field(default_factory=list)
    has_coa: bool = False
    third_party_testing: bool = False
    manufacturing_score: Optional[float] = None
    sweeteners: List[str] = Field(default_factory=list)
    additives_count: int = 0
    is_clean_label: bool = False
    health_score: Optional[float] = None
    packaging_type: Optional[str] = "pot_plastique_standard"
    has_plastic_scoop: bool = True
    supply_chain_transparency: Optional[str] = "local_ue"
    eco_score: Optional[float] = None


class BaseScraper(ABC):
    """
    Abstract Base Scraper establishing template method and strict 100% Pure Whey filtering rules.
    """

    # 1. Strict Blacklist for Non-Supplements, Apparel, Snacks, Gainers, Caseins & Non-Whey
    BLACK_LIST_KEYWORDS = [
        # Apparel & Accessories
        "leggings", "legging", "shorts", "short", "t-shirt", "tshirt", "shirt",
        "hoodie", "fleece", "jacket", "women", "men", "shaker", "pillbox", "strap",
        "belt", "gourde", "serviette", "ceinture", "bande", "casquette", "sac",
        "bottle", "mug", "cup", "ebook", "livre", "pantalon", "boite-a-pilules",
        "chaussettes", "gants", "towel", "bag", "beanie", "socks",
        # Solid Snacks, Food, Spreads, Drinks & Meals
        "bar", "barre", "bars", "crispy", "cookie", "cookies", "snack", "snacks",
        "peanut butter", "peanut", "beurre", "spread", "tartiner", "pancake", "pancakes",
        "wafer", "sauce", "syrup", "drip", "crunchy", "pâte", "oat", "oats", "oatmeal",
        "avena", "avoine", "farine", "porridge", "brownie", "pudding", "cold brew",
        "starterkit", "box", "pack", "duo", "muesli", "granola", "chips", "biscuit",
        "cake", "bread", "pain", "jam", "butter", "nutchoc", "kaffee", "coffee",
        "chocolat chaud", "hot chocolate", "latte", "flexpresso", "gélules", "gélule", 
        "capsules", "capsule", "caps", "fibre", "fiber",
        # Gainers & Mass Formula
        "gainer", "hard gainer", "lean gainer", "musclemasse",
        # Caséines & Non-Whey Proteins
        "casein", "caséine", "micellar", "micellaire", "milk protein", "pure milk",
        "egg", "musclewhegg", "oeuf", "soja", "soy", "matcha",
        # Other Non-Whey Supplements
        "amino", "bcaa", "creatine", "créatine", "collagène", "collagen", "peptistrong"
    ]

    # 2. Strict Whitelist Keywords for 100% Pure Whey
    WHEY_KEYWORDS = [
        "whey", "isolate", "isolat", "hydrolysat", "hydrolyzed", "clear whey", "native whey"
    ]

    # Minimum threshold weight for bulk tubs/bags (rejects 30g sachets or samples)
    MIN_WEIGHT_KG = 0.35  # 350 grams

    # Maximum reference weight for main card price/kg calculation (excludes >4kg bulk wholesale formats)
    MAX_REFERENCE_WEIGHT_KG = 4.0  # 4 kg

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
        Validates that a product is strictly 100% Pure Whey.
        """
        combined = f"{title} {description} {' '.join(tags or [])}".lower()

        # 1. Reject immediately if any blacklisted term is found
        if cls.is_blacklisted(combined):
            return False

        # 2. Require at least one whitelist Whey keyword
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
        """Categorizes supplement product. Default is 'whey'."""
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
        Filters reference min_price and min_price_per_kg exclusively for variants <= 4.0 kg.
        """
        print(f"[{self.brand_name}] Starting 100% Pure Whey scraping from {self.base_url}...")
        raw_data = self.fetch_data()
        products = self.parse_products(raw_data)

        valid_products = []
        for prod in products:
            if not prod.variants:
                continue

            # Reference variants for main card (<= 4.0 kg)
            ref_variants = [
                v for v in prod.variants 
                if v.price > 0 and (v.weight_kg is None or v.weight_kg <= self.MAX_REFERENCE_WEIGHT_KG)
            ]

            if not ref_variants:
                # Fallback to all variants if all are > 4kg
                ref_variants = [v for v in prod.variants if v.price > 0]

            if ref_variants:
                prod.min_price = min(v.price for v in ref_variants)
                ref_pkg = [v.price_per_kg for v in ref_variants if v.price_per_kg and v.price_per_kg > 0]
                if ref_pkg:
                    prod.min_price_per_kg = min(ref_pkg)

            valid_products.append(prod)

        print(f"[{self.brand_name}] Scraped {len(valid_products)} 100% pure whey products with {sum(len(p.variants) for p in valid_products)} total variants.")
        return valid_products
