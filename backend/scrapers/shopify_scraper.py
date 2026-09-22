"""
Shopify Scraper Module for NutriDeals
Generic scraper for Shopify stores with strict blacklist, whey whitelist, and weight validation.
"""

import requests
from typing import List, Optional
from .base_scraper import BaseScraper, ScrapedProduct, ProductVariant


SHOPIFY_BRANDS = [
    {"name": "Nutrimuscle", "url": "https://www.nutrimuscle.com"},
    {"name": "ESN", "url": "https://www.esn.com"},
    {"name": "Décathlon", "url": "https://www.decathlon.com"},
    {"name": "Inshape Nutrition", "url": "https://www.inshape-nutrition.com"},
    {"name": "Nutrimea", "url": "https://www.nutrimea.com"},
    {"name": "BioTech USA", "url": "https://shop.biotechusa.com"},
]


class ShopifyScraper(BaseScraper):
    """
    Generic Scraper for Shopify stores with strict filtering.
    """

    def fetch_data(self) -> List[dict]:
        """
        Fetch all products from Shopify endpoint using pagination.
        """
        all_products = []
        page = 1
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json"
        }

        while True:
            url = f"{self.base_url}/products.json?limit=250&page={page}"
            try:
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code != 200:
                    print(f"[{self.brand_name}] Warning: Received status {response.status_code} on page {page}")
                    break
                
                data = response.json()
                products = data.get("products", [])
                if not products:
                    break

                all_products.extend(products)
                if len(products) < 250:
                    break

                page += 1
            except Exception as e:
                print(f"[{self.brand_name}] Error fetching page {page}: {e}")
                break

        return all_products

    def parse_products(self, raw_items: List[dict]) -> List[ScrapedProduct]:
        """
        Parses Shopify raw products array into ScrapedProduct objects,
        applying strict blacklist and whey whitelist rules.
        """
        parsed_products = []

        for item in raw_items:
            title = item.get("title", "").strip()
            handle = item.get("handle", "")
            product_type = item.get("product_type", "")
            tags = [str(t) for t in item.get("tags", [])]
            body_html = item.get("body_html", "") or ""

            # Apply strict Whey validation & Blacklist
            if not self.is_valid_whey_product(title, description=body_html, tags=tags):
                continue

            product_url = f"{self.base_url}/products/{handle}" if handle else self.base_url
            
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
                        weight_kg=weight_kg,
                        price_per_kg=price_per_kg,
                        sku=sku,
                        available=available,
                        url=var_url
                    )
                )

            if variants:
                parsed_products.append(
                    ScrapedProduct(
                        brand=self.brand_name,
                        title=title,
                        url=product_url,
                        image_url=image_url,
                        category=category,
                        variants=variants
                    )
                )

        return parsed_products
