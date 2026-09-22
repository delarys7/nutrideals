-- ====================================================================
-- NutriDeals Supabase Schema
-- Relational model for supplement comparison engine (Whey, Creatine, etc.)
-- ====================================================================

-- 1. Enable UUID Extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create Products Table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    url TEXT NOT NULL UNIQUE,
    image_url TEXT,
    category VARCHAR(50) DEFAULT 'whey',
    min_price NUMERIC(10, 2) DEFAULT 0.00,
    min_price_per_kg NUMERIC(10, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Create Product Variants Table
CREATE TABLE IF NOT EXISTS product_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    variant_external_id VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    flavor VARCHAR(100),
    price NUMERIC(10, 2) NOT NULL,
    weight_kg NUMERIC(10, 3),
    price_per_kg NUMERIC(10, 2),
    sku VARCHAR(100),
    available BOOLEAN DEFAULT TRUE,
    url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_product_variant UNIQUE (product_id, title)
);

-- 4. Create Performance Indexes
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_url ON products(url);
CREATE INDEX IF NOT EXISTS idx_products_min_price_per_kg ON products(min_price_per_kg);

CREATE INDEX IF NOT EXISTS idx_variants_product_id ON product_variants(product_id);
CREATE INDEX IF NOT EXISTS idx_variants_price_per_kg ON product_variants(price_per_kg);
CREATE INDEX IF NOT EXISTS idx_variants_available ON product_variants(available);

-- 5. Auto-Update Timestamp Function & Triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_products_modtime ON products;
CREATE TRIGGER update_products_modtime
BEFORE UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_product_variants_modtime ON product_variants;
CREATE TRIGGER update_product_variants_modtime
BEFORE UPDATE ON product_variants
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
