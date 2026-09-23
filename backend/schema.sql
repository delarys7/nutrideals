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
    protein_percentage NUMERIC(5, 2),
    has_aminogram BOOLEAN DEFAULT FALSE,
    leucine_per_100g NUMERIC(5, 2),
    protein_score NUMERIC(4, 1),
    whey_type VARCHAR(50),
    is_grass_fed BOOLEAN DEFAULT FALSE,
    origin_country VARCHAR(100),
    extraction_process VARCHAR(100),
    chemical_free BOOLEAN DEFAULT TRUE,
    certifications JSONB DEFAULT '[]'::jsonb,
    has_coa BOOLEAN DEFAULT FALSE,
    third_party_testing BOOLEAN DEFAULT FALSE,
    manufacturing_score NUMERIC(4, 1),
    sweeteners JSONB DEFAULT '[]'::jsonb,
    additives_count INTEGER DEFAULT 0,
    is_clean_label BOOLEAN DEFAULT FALSE,
    health_score NUMERIC(4, 1),
    packaging_type VARCHAR(100),
    has_plastic_scoop BOOLEAN DEFAULT FALSE,
    supply_chain_transparency VARCHAR(100),
    eco_score NUMERIC(4, 1),
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
    compare_at_price NUMERIC(10, 2),
    weight_kg NUMERIC(10, 3),
    price_per_kg NUMERIC(10, 2),
    sku VARCHAR(100),
    available BOOLEAN DEFAULT TRUE,
    url TEXT,
    sweeteners JSONB DEFAULT '[]'::jsonb,
    additives_count INTEGER DEFAULT 0,
    health_score NUMERIC(4, 1),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_product_variant UNIQUE (product_id, title)
);

-- Ensure compare_at_price, protein score, manufacturing score, health score & eco score columns exist if schema already created
ALTER TABLE product_variants ADD COLUMN IF NOT EXISTS compare_at_price NUMERIC(10, 2);
ALTER TABLE product_variants ADD COLUMN IF NOT EXISTS sweeteners JSONB DEFAULT '[]'::jsonb;
ALTER TABLE product_variants ADD COLUMN IF NOT EXISTS additives_count INTEGER DEFAULT 0;
ALTER TABLE product_variants ADD COLUMN IF NOT EXISTS health_score NUMERIC(4, 1);
ALTER TABLE products ADD COLUMN IF NOT EXISTS protein_percentage NUMERIC(5, 2);
ALTER TABLE products ADD COLUMN IF NOT EXISTS has_aminogram BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS leucine_per_100g NUMERIC(5, 2);
ALTER TABLE products ADD COLUMN IF NOT EXISTS protein_score NUMERIC(4, 1);
ALTER TABLE products ADD COLUMN IF NOT EXISTS whey_type VARCHAR(50);
ALTER TABLE products ADD COLUMN IF NOT EXISTS is_grass_fed BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS origin_country VARCHAR(100);
ALTER TABLE products ADD COLUMN IF NOT EXISTS extraction_process VARCHAR(100);
ALTER TABLE products ADD COLUMN IF NOT EXISTS chemical_free BOOLEAN DEFAULT TRUE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS certifications JSONB DEFAULT '[]'::jsonb;
ALTER TABLE products ADD COLUMN IF NOT EXISTS has_coa BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS third_party_testing BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS manufacturing_score NUMERIC(4, 1);
ALTER TABLE products ADD COLUMN IF NOT EXISTS sweeteners JSONB DEFAULT '[]'::jsonb;
ALTER TABLE products ADD COLUMN IF NOT EXISTS additives_count INTEGER DEFAULT 0;
ALTER TABLE products ADD COLUMN IF NOT EXISTS is_clean_label BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS health_score NUMERIC(4, 1);
ALTER TABLE products ADD COLUMN IF NOT EXISTS packaging_type VARCHAR(100);
ALTER TABLE products ADD COLUMN IF NOT EXISTS has_plastic_scoop BOOLEAN DEFAULT FALSE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS supply_chain_transparency VARCHAR(100);
ALTER TABLE products ADD COLUMN IF NOT EXISTS eco_score NUMERIC(4, 1);

-- 4. Create Performance Indexes
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_url ON products(url);
CREATE INDEX IF NOT EXISTS idx_products_min_price_per_kg ON products(min_price_per_kg);
CREATE INDEX IF NOT EXISTS idx_products_protein_score ON products(protein_score);
CREATE INDEX IF NOT EXISTS idx_products_manufacturing_score ON products(manufacturing_score);
CREATE INDEX IF NOT EXISTS idx_products_health_score ON products(health_score);
CREATE INDEX IF NOT EXISTS idx_products_eco_score ON products(eco_score);

CREATE INDEX IF NOT EXISTS idx_variants_product_id ON product_variants(product_id);
CREATE INDEX IF NOT EXISTS idx_variants_price_per_kg ON product_variants(price_per_kg);

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
