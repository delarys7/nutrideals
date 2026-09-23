"""
Database Module for NutriDeals
SQLAlchemy ORM models, database connection pool, and robust upsert functions for Supabase.
"""

import uuid
from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Boolean,
    Integer,
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    JSON,
    text
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

try:
    from scrapers.base_scraper import ScrapedProduct, ProductVariant as PydanticVariant
    from core.config import DATABASE_URL
except ImportError:
    from backend.scrapers.base_scraper import ScrapedProduct, ProductVariant as PydanticVariant
    from backend.core.config import DATABASE_URL

# SQLAlchemy Engine & Session Factory
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ProductDB(Base):
    """
    SQLAlchemy Model for products table.
    """
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    url = Column(String, nullable=False, unique=True, index=True)
    image_url = Column(String, nullable=True)
    category = Column(String(50), default="whey", index=True)
    min_price = Column(Numeric(10, 2), default=0.00)
    min_price_per_kg = Column(Numeric(10, 2), nullable=True, index=True)
    protein_percentage = Column(Numeric(5, 2), nullable=True)
    has_aminogram = Column(Boolean, default=False)
    leucine_per_100g = Column(Numeric(5, 2), nullable=True)
    protein_score = Column(Numeric(4, 1), nullable=True, index=True)
    whey_type = Column(String(50), nullable=True)
    is_grass_fed = Column(Boolean, default=False)
    origin_country = Column(String(100), nullable=True)
    extraction_process = Column(String(100), nullable=True)
    chemical_free = Column(Boolean, default=True)
    certifications = Column(JSONB, default=[])
    has_coa = Column(Boolean, default=False)
    third_party_testing = Column(Boolean, default=False)
    manufacturing_score = Column(Numeric(4, 1), nullable=True, index=True)
    sweeteners = Column(JSONB, default=[])
    additives_count = Column(Integer, default=0)
    is_clean_label = Column(Boolean, default=False)
    health_score = Column(Numeric(4, 1), nullable=True, index=True)
    packaging_type = Column(String(100), nullable=True)
    has_plastic_scoop = Column(Boolean, default=False)
    supply_chain_transparency = Column(String(100), nullable=True)
    eco_score = Column(Numeric(4, 1), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    variants = relationship("ProductVariantDB", back_populates="product", cascade="all, delete-orphan")


class ProductVariantDB(Base):
    """
    SQLAlchemy Model for product_variants table.
    """
    __tablename__ = "product_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_external_id = Column(String(100), nullable=True)
    title = Column(String(255), nullable=False)
    flavor = Column(String(100), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    compare_at_price = Column(Numeric(10, 2), nullable=True)
    weight_kg = Column(Numeric(10, 3), nullable=True)
    price_per_kg = Column(Numeric(10, 2), nullable=True, index=True)
    sku = Column(String(100), nullable=True)
    available = Column(Boolean, default=True)
    url = Column(String, nullable=True)
    sweeteners = Column(JSONB, default=[])
    additives_count = Column(Integer, default=0)
    health_score = Column(Numeric(4, 1), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("ProductDB", back_populates="variants")

    __table_args__ = (
        UniqueConstraint("product_id", "title", name="uq_product_variant"),
    )


def init_db():
    """
    Initializes database tables in Supabase PostgreSQL if they do not exist.
    """
    print("[Database] Initializing Supabase schema tables...")
    Base.metadata.create_all(bind=engine)
    # Ensure compare_at_price, protein score, manufacturing score, health score & eco score columns exist
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE product_variants ADD COLUMN IF NOT EXISTS compare_at_price NUMERIC(10, 2);"))
        conn.execute(text("ALTER TABLE product_variants ADD COLUMN IF NOT EXISTS sweeteners JSONB DEFAULT '[]'::jsonb;"))
        conn.execute(text("ALTER TABLE product_variants ADD COLUMN IF NOT EXISTS additives_count INTEGER DEFAULT 0;"))
        conn.execute(text("ALTER TABLE product_variants ADD COLUMN IF NOT EXISTS health_score NUMERIC(4, 1);"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS protein_percentage NUMERIC(5, 2);"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS has_aminogram BOOLEAN DEFAULT FALSE;"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS leucine_per_100g NUMERIC(5, 2);"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS protein_score NUMERIC(4, 1);"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS whey_type VARCHAR(50);"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS is_grass_fed BOOLEAN DEFAULT FALSE;"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS origin_country VARCHAR(100);"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS extraction_process VARCHAR(100);"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS chemical_free BOOLEAN DEFAULT TRUE;"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS certifications JSONB DEFAULT '[]'::jsonb;"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS has_coa BOOLEAN DEFAULT FALSE;"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS third_party_testing BOOLEAN DEFAULT FALSE;"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS manufacturing_score NUMERIC(4, 1);"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS sweeteners JSONB DEFAULT '[]'::jsonb;"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS additives_count INTEGER DEFAULT 0;"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS is_clean_label BOOLEAN DEFAULT FALSE;"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS health_score NUMERIC(4, 1);"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS packaging_type VARCHAR(100);"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS has_plastic_scoop BOOLEAN DEFAULT FALSE;"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS supply_chain_transparency VARCHAR(100);"))
        conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS eco_score NUMERIC(4, 1);"))
        conn.commit()
    print("[Database] Schema tables initialized successfully.")


def clear_products(session: Session, category: Optional[str] = None):
    """
    Clears products from Supabase database using TRUNCATE TABLE products CASCADE;.
    """
    print("[Database] Executing TRUNCATE TABLE products CASCADE; in Supabase...")
    session.execute(text("TRUNCATE TABLE products CASCADE;"))
    session.commit()
    print("[Database] Database truncate complete.")


def save_scraped_products(session: Session, scraped_products: List[ScrapedProduct]) -> Tuple[int, int]:
    """
    Persists scraped product models into Supabase PostgreSQL.
    Uses UPSERT logic based on product URL and variant title to prevent duplicate errors.
    Returns (saved_products_count, saved_variants_count).
    """
    if not scraped_products:
        return 0, 0

    saved_products_count = 0
    saved_variants_count = 0

    try:
        for sp in scraped_products:
            # Check if product exists by URL
            existing_prod = session.query(ProductDB).filter(ProductDB.url == sp.url).first()

            if existing_prod:
                # Update existing product metadata
                existing_prod.brand = sp.brand
                existing_prod.title = sp.title
                existing_prod.image_url = sp.image_url
                existing_prod.category = sp.category
                existing_prod.min_price = sp.min_price
                existing_prod.min_price_per_kg = sp.min_price_per_kg
                existing_prod.protein_percentage = sp.protein_percentage
                existing_prod.has_aminogram = sp.has_aminogram
                existing_prod.leucine_per_100g = sp.leucine_per_100g
                existing_prod.protein_score = sp.protein_score
                existing_prod.whey_type = sp.whey_type
                existing_prod.is_grass_fed = sp.is_grass_fed
                existing_prod.origin_country = sp.origin_country
                existing_prod.extraction_process = sp.extraction_process
                existing_prod.chemical_free = sp.chemical_free
                existing_prod.certifications = sp.certifications
                existing_prod.has_coa = sp.has_coa
                existing_prod.third_party_testing = sp.third_party_testing
                existing_prod.manufacturing_score = sp.manufacturing_score
                existing_prod.sweeteners = sp.sweeteners
                existing_prod.additives_count = sp.additives_count
                existing_prod.is_clean_label = sp.is_clean_label
                existing_prod.health_score = sp.health_score
                existing_prod.packaging_type = sp.packaging_type
                existing_prod.has_plastic_scoop = sp.has_plastic_scoop
                existing_prod.supply_chain_transparency = sp.supply_chain_transparency
                existing_prod.eco_score = sp.eco_score
                existing_prod.updated_at = datetime.utcnow()
                prod_obj = existing_prod
            else:
                # Create new product
                prod_obj = ProductDB(
                    brand=sp.brand,
                    title=sp.title,
                    url=sp.url,
                    image_url=sp.image_url,
                    category=sp.category,
                    min_price=sp.min_price,
                    min_price_per_kg=sp.min_price_per_kg,
                    protein_percentage=sp.protein_percentage,
                    has_aminogram=sp.has_aminogram,
                    leucine_per_100g=sp.leucine_per_100g,
                    protein_score=sp.protein_score,
                    whey_type=sp.whey_type,
                    is_grass_fed=sp.is_grass_fed,
                    origin_country=sp.origin_country,
                    extraction_process=sp.extraction_process,
                    chemical_free=sp.chemical_free,
                    certifications=sp.certifications,
                    has_coa=sp.has_coa,
                    third_party_testing=sp.third_party_testing,
                    manufacturing_score=sp.manufacturing_score,
                    sweeteners=sp.sweeteners,
                    additives_count=sp.additives_count,
                    is_clean_label=sp.is_clean_label,
                    health_score=sp.health_score,
                    packaging_type=sp.packaging_type,
                    has_plastic_scoop=sp.has_plastic_scoop,
                    supply_chain_transparency=sp.supply_chain_transparency,
                    eco_score=sp.eco_score,
                )
                session.add(prod_obj)
                session.flush()  # Generate prod_obj.id
                saved_products_count += 1

            # Sync Variants
            existing_variants = {v.title: v for v in prod_obj.variants}

            for v in sp.variants:
                if v.title in existing_variants:
                    # Update variant
                    var_obj = existing_variants[v.title]
                    var_obj.variant_external_id = v.id
                    var_obj.flavor = v.flavor
                    var_obj.price = v.price
                    var_obj.compare_at_price = v.compare_at_price
                    var_obj.weight_kg = v.weight_kg
                    var_obj.price_per_kg = v.price_per_kg
                    var_obj.sku = v.sku
                    var_obj.available = v.available
                    var_obj.url = v.url
                    var_obj.sweeteners = v.sweeteners
                    var_obj.additives_count = v.additives_count
                    var_obj.health_score = v.health_score
                    var_obj.updated_at = datetime.utcnow()
                else:
                    # Insert new variant
                    var_obj = ProductVariantDB(
                        product_id=prod_obj.id,
                        variant_external_id=v.id,
                        title=v.title,
                        flavor=v.flavor,
                        price=v.price,
                        compare_at_price=v.compare_at_price,
                        weight_kg=v.weight_kg,
                        price_per_kg=v.price_per_kg,
                        sku=v.sku,
                        available=v.available,
                        url=v.url,
                        sweeteners=v.sweeteners,
                        additives_count=v.additives_count,
                        health_score=v.health_score,
                    )
                    session.add(var_obj)
                    saved_variants_count += 1

        session.commit()
        print(f"[Database] Successfully persisted {len(scraped_products)} products into Supabase.")
        return len(scraped_products), saved_variants_count

    except Exception as e:
        session.rollback()
        print(f"[Database] Error persisting products: {e}")
        raise e
