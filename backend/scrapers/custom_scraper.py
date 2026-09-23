"""
Custom Scraper Module for NutriDeals
Prozis Scraper with French localization (fr/fr), Schema.org stock verification,
and in-memory sitemap decompression.
"""

import gzip
import os
import re
import requests
import xml.etree.ElementTree as ET
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
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


class ProzisScraper(BaseScraper):
    """
    Custom Scraper for Prozis targeting Whey supplements strictly,
    localized for Prozis France (fr/fr) with accurate Schema.org stock parsing.
    """

    SITEMAP_GZ_URL = "https://www.prozis.com/fr/fr/sitemap_products.gz"
    FALLBACK_SITEMAP_GZ_URL = "https://www.prozis.com/be/fr/sitemap_products.gz"
    LOCAL_FALLBACK_PATH = os.path.join(
        os.path.dirname(__file__), "..", "..", "sitemaps", "prozis_sitemap_products"
    )

    def __init__(self, max_products: int = 35):
        super().__init__(brand_name="Prozis", base_url="https://www.prozis.com/fr/fr")
        self.max_products = max_products

    def fetch_data(self) -> List[str]:
        """
        Downloads .gz sitemap into memory, decompresses, and parses XML URLs.
        Applies strict Blacklist and Whey Whitelist filters.
        Ensures all generated URLs target the French store (fr/fr).
        """
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7"
        }

        xml_bytes = None

        # 1. Try French sitemap .gz URL
        for sitemap_url in [self.SITEMAP_GZ_URL, self.FALLBACK_SITEMAP_GZ_URL]:
            try:
                response = requests.get(sitemap_url, headers=headers, timeout=15)
                if response.status_code == 200:
                    xml_bytes = gzip.decompress(response.content)
                    print(f"[{self.brand_name}] Downloaded and decompressed sitemap (.gz) in memory ({len(xml_bytes)} bytes).")
                    break
            except Exception as e:
                print(f"[{self.brand_name}] Web download failed for {sitemap_url} ({e}).")

        # 2. Local fallback if in-memory download fails
        if not xml_bytes and os.path.exists(self.LOCAL_FALLBACK_PATH):
            try:
                with open(self.LOCAL_FALLBACK_PATH, "rb") as f:
                    xml_bytes = f.read()
                print(f"[{self.brand_name}] Loaded local fallback sitemap file ({len(xml_bytes)} bytes).")
            except Exception as ex:
                print(f"[{self.brand_name}] Error loading local fallback: {ex}")

        if not xml_bytes:
            print(f"[{self.brand_name}] Error: No sitemap data available.")
            return []

        # Parse XML & localize URLs for Prozis France (fr/fr)
        urls = []
        try:
            root = ET.fromstring(xml_bytes)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            for u in root.findall("sm:url", ns):
                loc = u.find("sm:loc", ns)
                if loc is not None and loc.text:
                    link = loc.text.strip()

                    # Force Prozis France locale URL
                    link_fr = link.replace("/be/fr/", "/fr/fr/").replace("/pt/pt/", "/fr/fr/").replace("/es/es/", "/fr/fr/")
                    if not link_fr.startswith("https://www.prozis.com/fr/fr/"):
                        link_fr = link_fr.replace("https://www.prozis.com/", "https://www.prozis.com/fr/fr/")

                    # Apply strict Whey validation & Blacklist on link slug
                    if self.is_valid_whey_product(link_fr):
                        urls.append(link_fr)
        except Exception as err:
            print(f"[{self.brand_name}] Error parsing XML sitemap: {err}")

        # Limit count for pipeline performance
        if self.max_products and len(urls) > self.max_products:
            urls = urls[:self.max_products]

        return urls

    def _fetch_product_details(self, session: requests.Session, url: str) -> Optional[ScrapedProduct]:
        """
        Fetches single Prozis product page and extracts meta properties, promos, and accurate stock status.
        """
        try:
            res = session.get(url, timeout=8)
            if res.status_code != 200:
                return None

            html = res.text
            
            # Extract meta tags
            raw_title_m = re.findall(r'<meta property="og:title" content="(.*?)"', html)
            price_m = re.findall(r'<meta property="product:price:amount" content="(.*?)"', html)
            img_m = re.findall(r'<meta property="og:image" content="(.*?)"', html)

            if not raw_title_m:
                return None

            # Clean Title
            raw_title = raw_title_m[0]
            clean_title = raw_title.split("-")[0].strip() if "-" in raw_title else raw_title

            # Validate Title against Whey & Blacklist
            if not self.is_valid_whey_product(clean_title):
                return None

            # Parse Price
            price = 0.0
            if price_m:
                try:
                    price = float(price_m[0].replace(",", "."))
                except ValueError:
                    price = 0.0

            # Extract Compare At Price (Strikethrough Promo Price)
            compare_at_price = None
            strikethrough = re.findall(r'class="[^"]*old-price[^"]*"[^>]*>(\d+[\.,]\d{2})', html)
            if not strikethrough:
                strikethrough = re.findall(r'<del[^>]*>(\d+[\.,]\d{2})', html)
            if strikethrough:
                try:
                    parsed_cap = float(strikethrough[0].replace(",", "."))
                    if parsed_cap > price:
                        compare_at_price = parsed_cap
                except ValueError:
                    pass

            image_url = img_m[0] if img_m else None

            # Parse Weight
            weight_kg = self.parse_weight_in_kg(raw_title)
            if not weight_kg:
                slug = url.split("/")[-1]
                weight_kg = self.parse_weight_in_kg(slug.replace("-", " "))

            # Enforce minimum weight threshold
            if weight_kg and weight_kg < self.MIN_WEIGHT_KG:
                return None

            # Accurate Stock status via Schema.org microdata (InStock vs OutOfStock)
            if "schema.org/OutOfStock" in html or "OutOfStock" in html:
                available = False
            elif "schema.org/InStock" in html or "InStock" in html:
                available = True
            else:
                # Default to True if page loaded with HTTP 200 and no explicit out of stock indicator
                available = True

            price_per_kg = self.calculate_price_per_kg(price, weight_kg)
            category = "whey"

            variant = ProductVariant(
                title=clean_title,
                price=price,
                compare_at_price=compare_at_price,
                weight_kg=weight_kg,
                price_per_kg=price_per_kg,
                available=available,
                url=url
            )

            protein_metrics = extract_or_estimate_protein_metrics(
                title=clean_title,
                description=html,
                brand=self.brand_name
            )

            mfg_metrics = extract_or_estimate_manufacturing_metrics(
                title=clean_title,
                description=html,
                brand=self.brand_name
            )

            health_metrics = extract_or_estimate_health_metrics(
                title=clean_title,
                description=html,
                brand=self.brand_name
            )

            eco_metrics = extract_or_estimate_eco_metrics(
                title=clean_title,
                description=html,
                brand=self.brand_name
            )

            return ScrapedProduct(
                brand=self.brand_name,
                title=clean_title,
                url=url,
                image_url=image_url,
                category=category,
                variants=[variant],
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
        except Exception as e:
            return None

    def parse_products(self, raw_items: List[str]) -> List[ScrapedProduct]:
        """
        Fetches individual Prozis product pages concurrently to extract metadata.
        """
        products = []
        session = requests.Session()
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7"
        })

        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_url = {
                executor.submit(self._fetch_product_details, session, url): url 
                for url in raw_items
            }
            for future in as_completed(future_to_url):
                prod = future.result()
                if prod:
                    products.append(prod)

        return products
