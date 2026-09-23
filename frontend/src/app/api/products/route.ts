import { NextResponse } from 'next/server';
import { Pool } from 'pg';

const connectionString = process.env.DATABASE_URL;

export async function GET() {
  if (!connectionString) {
    return NextResponse.json({ success: false, error: 'DATABASE_URL is missing' }, { status: 500 });
  }

  const pool = new Pool({
    connectionString,
    ssl: { rejectUnauthorized: false }
  });

  try {
    const query = `
      SELECT 
        p.id,
        p.brand,
        p.title,
        p.url,
        p.image_url,
        p.category,
        p.min_price::float as min_price,
        p.min_price_per_kg::float as min_price_per_kg,
        p.protein_percentage::float as protein_percentage,
        p.has_aminogram,
        p.leucine_per_100g::float as leucine_per_100g,
        p.protein_score::float as protein_score,
        p.created_at,
        p.updated_at,
        COALESCE(
          json_agg(
            json_build_object(
              'id', v.id,
              'product_id', v.product_id,
              'variant_external_id', v.variant_external_id,
              'title', v.title,
              'flavor', v.flavor,
              'price', v.price::float,
              'compare_at_price', v.compare_at_price::float,
              'weight_kg', v.weight_kg::float,
              'price_per_kg', v.price_per_kg::float,
              'sku', v.sku,
              'available', v.available,
              'url', v.url
            )
          ) FILTER (WHERE v.id IS NOT NULL), '[]'
        ) as product_variants
      FROM products p
      LEFT JOIN product_variants v ON p.id = v.product_id
      WHERE p.category = 'whey'
      GROUP BY p.id
      ORDER BY p.min_price_per_kg ASC NULLS LAST
    `;

    const result = await pool.query(query);
    await pool.end();

    return NextResponse.json({ success: true, count: result.rowCount, data: result.rows });
  } catch (error: any) {
    console.error('[API Products Error]:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
