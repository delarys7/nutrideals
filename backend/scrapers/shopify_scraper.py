"""
Shopify Scraper Module for NutriDeals
Generic scraper for Shopify stores with strict blacklist, whey whitelist,
stock availability, compare_at_price (real promo) extraction, and French store localization.
"""

import time
import requests
from typing import List, Optional
from .base_scraper import BaseScraper, ScrapedProduct, ProductVariant

try:
    from core.protein_scorer import extract_or_estimate_protein_metrics
    from core.manufacturing_scorer import extract_or_estimate_manufacturing_metrics
    from core.health_scorer import extract_or_estimate_health_metrics
    from core.eco_scorer import extract_or_estimate_eco_metrics
except ImportError:
    from backend.core.protein_scorer import extract_or_estimate_protein_metrics
    from backend.core.manufacturing_scorer import extract_or_estimate_manufacturing_metrics
    from backend.core.health_scorer import extract_or_estimate_health_metrics
    from backend.core.eco_scorer import extract_or_estimate_eco_metrics


SHOPIFY_BRANDS = [
    {"name": "Nutrimuscle", "url": "https://www.nutrimuscle.com", "product_url_prefix": "https://www.nutrimuscle.com/products/"},
    {"name": "ESN", "url": "https://www.esn.com", "product_url_prefix": "https://www.esn.com/fr/products/"},
    {"name": "Inshape Nutrition", "url": "https://www.inshape-nutrition.com", "product_url_prefix": "https://www.inshape-nutrition.com/products/"},
    {"name": "Nutrimea", "url": "https://www.nutrimea.com", "product_url_prefix": "https://www.nutrimea.com/fr/products/"},
    {"name": "BioTech USA", "url": "https://shop.biotechusa.fr", "product_url_prefix": "https://shop.biotechusa.fr/products/"},
]


class ShopifyScraper(BaseScraper):
    """
    Generic Scraper for Shopify stores with strict filtering, French store localization, and browser session handling.
    """

    def __init__(self, brand_name: str, base_url: str, product_url_prefix: Optional[str] = None):
        super().__init__(brand_name=brand_name, base_url=base_url)
        self.product_url_prefix = product_url_prefix or f"{self.base_url}/products/"

    def fetch_data(self) -> List[dict]:
        """
        Fetch all products from Shopify endpoint using pagination and session headers.
        """
        all_products = []
        page = 1
        
        session = requests.Session()
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        })

        while True:
            url = f"{self.base_url}/products.json?limit=250&page={page}"
            products = []
            
            for attempt in range(3):
                try:
                    response = session.get(url, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        products = data.get("products", [])
                        break
                    elif response.status_code == 429:
                        time.sleep(1.5 * (attempt + 1))
                    else:
                        break
                except Exception as e:
                    time.sleep(1)

            if not products:
                break

            all_products.extend(products)
            if len(products) < 250:
                break

            page += 1

        return all_products

    def parse_products(self, raw_items: List[dict]) -> List[ScrapedProduct]:
        """
        Parses Shopify raw products array into ScrapedProduct objects,
        extracting prices, compare_at_price (real promos), stock status, and weight.
        """
        parsed_products = []

        for item in raw_items:
            title = item.get("title", "").strip()
            handle = item.get("handle", "")
            tags = [str(t) for t in item.get("tags", [])]
            body_html = item.get("body_html", "") or ""

            # Apply strict Whey validation & Blacklist
            if not self.is_valid_whey_product(title, description=body_html, tags=tags):
                continue

            # Generate French localized product URL
            product_url = f"{self.product_url_prefix}{handle}" if handle else self.base_url
            
            # Extract image
            images = item.get("images", [])
            image_url = images[0].get("src") if images else None

            category = "whey"

            raw_variants = item.get("variants", [])
            variants: List[ProductVariant] = []

            for var in raw_variants:
                var_id = str(var.get("id"))
                var_title = var.get("title", "Default").strip()
                
                # Reject if variant title itself contains blacklisted term
                if self.is_blacklisted(var_title):
                    continue

                # Extract Price
                try:
                    price = float(var.get("price", 0.0))
                except (ValueError, TypeError):
                    price = 0.0

                # Extract Compare At Price (Real Promo)
                compare_at_price = None
                raw_compare = var.get("compare_at_price")
                if raw_compare:
                    try:
                        parsed_cap = float(raw_compare)
                        if parsed_cap > price:
                            compare_at_price = parsed_cap
                    except (ValueError, TypeError):
                        pass

                # Extract Weight in KG
                weight_kg = None
                grams = var.get("grams")
                if grams and float(grams) > 0:
                    weight_kg = round(float(grams) / 1000.0, 3)
                
                if not weight_kg:
                    weight_kg = self.parse_weight_in_kg(var_title)
                if not weight_kg:
                    weight_kg = self.parse_weight_in_kg(title)

                # Filter out small samples or 0-weight items (require weight >= 0.35kg if weight is parsed)
                if weight_kg and weight_kg < self.MIN_WEIGHT_KG:
                    continue

                price_per_kg = self.calculate_price_per_kg(price, weight_kg)
                sku = var.get("sku")
                available = bool(var.get("available", True))
                var_url = f"{product_url}?variant={var_id}" if var_id else product_url

                variants.append(
                    ProductVariant(
                        id=var_id,
                        title=var_title,
                        flavor=var_title if var_title != "Default Title" else None,
                        price=price,
                        compare_at_price=compare_at_price,
                        weight_kg=weight_kg,
                        price_per_kg=price_per_kg,
                        sku=sku,
                        available=available,
                        url=var_url
                    )
                )

            if variants:
                # Extract & calculate Protein Score metrics
                protein_metrics = extract_or_estimate_protein_metrics(
                    title=title,
                    description=body_html,
                    brand=self.brand_name
                )

                # Extract & calculate Manufacturing Score metrics
                mfg_metrics = extract_or_estimate_manufacturing_metrics(
                    title=title,
                    description=body_html,
                    brand=self.brand_name
                )

                # Extract & calculate Health Score metrics
                health_metrics = extract_or_estimate_health_metrics(
                    title=title,
                    description=body_html,
                    brand=self.brand_name
                )

                # Extract & calculate Eco Score metrics
                eco_metrics = extract_or_estimate_eco_metrics(
                    title=title,
                    description=body_html,
                    brand=self.brand_name
                )

                parsed_products.append(
                    ScrapedProduct(
                        brand=self.brand_name,
                        title=title,
                        url=product_url,
                        image_url=image_url,
                        category=category,
                        variants=variants,
                        protein_percentage=protein_metrics["protein_percentage"],
                        has_aminogram=protein_metrics["has_aminogram"],
                        leucine_per_100g=protein_metrics["leucine_per_100g"],
                        protein_score=protein_metrics["protein_score"],
                        whey_type=mfg_metrics["whey_type"],
                        is_grass_fed=mfg_metrics["is_grass_fed"],
                        origin_country=mfg_metrics["origin_country"],
                        extraction_process=mfg_metrics["extraction_process"],
                        chemical_free=mfg_metrics["chemical_free"],
                        certifications=mfg_metrics["certifications"],
                        has_coa=mfg_metrics["has_coa"],
                        third_party_testing=mfg_metrics["third_party_testing"],
                        manufacturing_score=mfg_metrics["manufacturing_score"],
                        sweeteners=health_metrics["sweeteners"],
                        additives_count=health_metrics["additives_count"],
                        is_clean_label=health_metrics["is_clean_label"],
                        health_score=health_metrics["health_score"],
                        packaging_type=eco_metrics["packaging_type"],
                        has_plastic_scoop=eco_metrics["has_plastic_scoop"],
                        supply_chain_transparency=eco_metrics["supply_chain_transparency"],
                        eco_score=eco_metrics["eco_score"],
                    )
                )

        return parsed_products
