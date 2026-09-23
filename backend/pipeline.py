"""
NutriDeals Main Scraping Orchestrator
Executes all brand scrapers (Shopify + Prozis) with strict Whey filtering,
displays clean summary, and persists validated dataset into Supabase.
"""

import sys
import time
from typing import List, Dict, Any
from scrapers.base_scraper import ScrapedProduct
from scrapers.shopify_scraper import ShopifyScraper, SHOPIFY_BRANDS
from scrapers.custom_scraper import ProzisScraper
from core.database import init_db, SessionLocal, save_scraped_products, clear_products


class NutriDealsPipeline:
    """
    Orchestrates web scraping collection across all supplement brands
    and handles automatic Supabase database persistence.
    """

    def __init__(self):
        self.products: List[ScrapedProduct] = []

    def run(self, save_to_db: bool = True, purge_old: bool = True) -> List[ScrapedProduct]:
        """
        Executes full scraping pipeline.
        """
        start_time = time.time()
        print("=" * 70)
        print("     NUTRIDEALS - COMPLEMENTS ALIMENTAIRES (STRICT WHEY PIPELINE)     ")
        print("=" * 70)

        # 1. Run Shopify Scrapers
        print("\n--- Phase 1: Scraping Shopify Stores (Whey powders only) ---")
        for brand in SHOPIFY_BRANDS:
            try:
                scraper = ShopifyScraper(brand_name=brand["name"], base_url=brand["url"])
                brand_products = scraper.scrape()
                self.products.extend(brand_products)
            except Exception as e:
                print(f"[{brand['name']}] Error running scraper: {e}")

        # 2. Run Prozis Custom Scraper
        print("\n--- Phase 2: Scraping Custom Stores (Prozis Whey powders) ---")
        try:
            prozis_scraper = ProzisScraper(max_products=25)
            prozis_products = prozis_scraper.scrape()
            self.products.extend(prozis_products)
        except Exception as e:
            print(f"[Prozis] Error running scraper: {e}")

        elapsed = time.time() - start_time
        print("\n" + "=" * 70)
        print(f" Scraping finished in {elapsed:.2f} seconds.")
        print("=" * 70)

        self.display_summary()

        # 3. Persist into Supabase
        if save_to_db and self.products:
            print("\n--- Phase 3: Persisting Data to Supabase PostgreSQL ---")
            try:
                init_db()
                session = SessionLocal()

                if purge_old:
                    clear_products(session)

                prod_count, var_count = save_scraped_products(session, self.products)
                session.close()
                print(f"[Supabase Ingestion] Successfully saved {prod_count} clean whey products and {var_count} variants!")
            except Exception as e:
                print(f"[Supabase Ingestion] Failed to save products to database: {e}")

        return self.products

    def display_summary(self):
        """
        Prints a clean structured table summary of scraped metrics per brand.
        """
        if not self.products:
            print("\nNo products scraped.")
            return

        brand_stats: Dict[str, Dict[str, Any]] = {}

        for p in self.products:
            b = p.brand
            if b not in brand_stats:
                brand_stats[b] = {
                    "product_count": 0,
                    "variant_count": 0,
                    "min_prices": [],
                    "min_pkg_prices": [],
                    "scores": []
                }
            
            brand_stats[b]["product_count"] += 1
            brand_stats[b]["variant_count"] += len(p.variants)

            if p.min_price > 0:
                brand_stats[b]["min_prices"].append(p.min_price)
            if p.min_price_per_kg and p.min_price_per_kg > 0:
                brand_stats[b]["min_pkg_prices"].append(p.min_price_per_kg)
            if p.protein_score is not None:
                brand_stats[b]["scores"].append(p.protein_score)

        print("\n" + "-" * 90)
        print(f"{'Marque':<18} | {'Produits Whey':<14} | {'Variantes':<10} | {'Prix Min':<12} | {'Prix/kg Min':<12} | {'Score Protéique Moy':<18}")
        print("-" * 90)

        total_prods = 0
        total_vars = 0

        for brand, stats in sorted(brand_stats.items()):
            p_count = stats["product_count"]
            v_count = stats["variant_count"]
            total_prods += p_count
            total_vars += v_count

            min_p = f"{min(stats['min_prices']):.2f} €" if stats["min_prices"] else "N/A"
            min_pkg = f"{min(stats['min_pkg_prices']):.2f} €/kg" if stats["min_pkg_prices"] else "N/A"
            avg_score = f"{sum(stats['scores'])/len(stats['scores']):.1f} / 10" if stats["scores"] else "N/A"

            print(f"{brand:<18} | {p_count:<14} | {v_count:<10} | {min_p:<12} | {min_pkg:<12} | {avg_score:<18}")

        print("-" * 90)
        print(f"{'TOTAL GLOBAL WHEY':<18} | {total_prods:<14} | {total_vars:<10} | {'-':<12} | {'-':<12} | {'-':<18}")
        print("-" * 90 + "\n")


if __name__ == "__main__":
    pipeline = NutriDealsPipeline()
    results = pipeline.run(save_to_db=True, purge_old=True)
