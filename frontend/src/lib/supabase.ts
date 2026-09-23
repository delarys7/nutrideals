import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://bcgpssoeyjykrxrvgyjt.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.placeholder';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export interface ProductVariant {
  id: string;
  product_id: string;
  variant_external_id?: string;
  title: string;
  flavor?: string;
  price: number;
  compare_at_price?: number;
  weight_kg?: number;
  price_per_kg?: number;
  sku?: string;
  available: boolean;
  url?: string;
}

export interface Product {
  id: string;
  brand: string;
  title: string;
  url: string;
  image_url?: string;
  category: string;
  min_price: number;
  min_price_per_kg?: number;
  protein_percentage?: number;
  has_aminogram?: boolean;
  leucine_per_100g?: number;
  protein_score?: number;
  whey_type?: string;
  is_grass_fed?: boolean;
  origin_country?: string;
  extraction_process?: string;
  chemical_free?: boolean;
  certifications?: string[];
  has_coa?: boolean;
  third_party_testing?: boolean;
  manufacturing_score?: number;
  sweeteners?: string[];
  additives_count?: number;
  is_clean_label?: boolean;
  health_score?: number;
  packaging_type?: string;
  has_plastic_scoop?: boolean;
  supply_chain_transparency?: string;
  eco_score?: number;
  created_at?: string;
  updated_at?: string;
  product_variants?: ProductVariant[];
}
