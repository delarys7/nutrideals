"""
Custom Scraper Module for NutriDeals
Prozis Scraper with strict whey filtering, blacklist checking, and memory decompression.
"""

import gzip
import os
import re
import requests
import xml.etree.ElementTree as ET
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base_scraper import BaseScraper, ScrapedProduct, ProductVariant


class ProzisScraper(BaseScraper):
    """
    Custom Scraper for Prozis targeting Whey supplements strictly.
    """

    SITEMAP_GZ_URL = "https://www.prozis.com/be/fr/sitemap_products.gz"
    LOCAL_FALLBACK_PATH = os.path.join(
        os.path.dirname(__file__), "..", "..", "sitemaps", "prozis_sitemap_products"
    )

    def __init__(self, max_products: int = 30):
        super().__init__(brand_name="Prozis", base_url="https://www.prozis.com")
        self.max_products = max_products

    def fetch_data(self) -> List[str]:
        """
        Downloads .gz sitemap into memory, decompresses, and parses XML URLs.
        Applies strict Blacklist and Whey Whitelist filters.
        """
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        xml_bytes = None
        try:
            response = requests.get(self.SITEMAP_GZ_URL, headers=headers, timeout=15)
            if response.status_code == 200:
                xml_bytes = gzip.decompress(response.content)
                print(f"[{self.brand_name}] Downloaded and decompressed sitemap (.gz) in memory ({len(xml_bytes)} bytes).")
            else:
                print(f"[{self.brand_name}] Web fetch status {response.status_code}. Using local sitemap fallback...")
        except Exception as e:
            print(f"[{self.brand_name}] Web download failed ({e}). Using local sitemap fallback...")

        # Local fallback if in-memory download fails
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

        # Parse XML
        urls = []
        try:
            root = ET.fromstring(xml_bytes)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            for u in root.findall("sm:url", ns):
                loc = u.find("sm:loc", ns)
                if loc is not None and loc.text:
                    link = loc.text.strip()
                    # Apply strict Whey validation & Blacklist on link slug
                    if self.is_valid_whey_product(link):
                        urls.append(link)
        except Exception as err:
            print(f"[{self.brand_name}] Error parsing XML sitemap: {err}")

        # Limit count for pipeline performance
        if self.max_products and len(urls) > self.max_products:
            urls = urls[:self.max_products]

        return urls

    def _fetch_product_details(self, session: requests.Session, url: str) -> Optional[ScrapedProduct]:
        """
        Fetches single Prozis product page and extracts meta properties.
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

            image_url = img_m[0] if img_m else None

            # Parse Weight
            weight_kg = self.parse_weight_in_kg(raw_title)
            if not weight_kg:
                slug = url.split("/")[-1]
                weight_kg = self.parse_weight_in_kg(slug.replace("-", " "))

            # Enforce minimum weight threshold
            if weight_kg and weight_kg < self.MIN_WEIGHT_KG:
                return None

            price_per_kg = self.calculate_price_per_kg(price, weight_kg)
            category = "whey"

            variant = ProductVariant(
                title=clean_title,
                price=price,
                weight_kg=weight_kg,
                price_per_kg=price_per_kg,
                available=True,
                url=url
            )

            return ScrapedProduct(
                brand=self.brand_name,
                title=clean_title,
                url=url,
                image_url=image_url,
                category=category,
                variants=[variant]
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
