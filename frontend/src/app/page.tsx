'use client';

import React, { useEffect, useState, useMemo } from 'react';
import { Search, Filter, Sparkles } from 'lucide-react';
import { supabase, Product } from '../lib/supabase';
import { Header } from '../components/Header';
import { ProductTable } from '../components/ProductTable';

const BRANDS = [
  'Tous',
  'Nutrimuscle',
  'ESN',
  'Prozis',
  'Inshape Nutrition',
  'BioTech USA',
  'Nutrimea',
];

export default function HomePage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedBrand, setSelectedBrand] = useState<string>('Tous');

  // Fetch data from Supabase with API fallback
  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      try {
        // Attempt 1: Fetch via Supabase JS Client
        const { data: supaData, error } = await supabase
          .from('products')
          .select('*, product_variants(*)')
          .eq('category', 'whey')
          .order('min_price_per_kg', { ascending: true, nullsFirst: false });

        if (!error && supaData && supaData.length > 0) {
          setProducts(supaData as Product[]);
          setIsLoading(false);
          return;
        }

        // Attempt 2: Fallback to Next.js API Route (direct DB connection)
        const res = await fetch('/api/products');
        const json = await res.json();

        if (json.success && json.data) {
          setProducts(json.data as Product[]);
        }
      } catch (err) {
        console.error('Error loading NutriDeals products:', err);
      } finally {
        setIsLoading(false);
      }
    }

    loadData();
  }, []);

  // Filtered Products
  const filteredProducts = useMemo(() => {
    return products.filter((product) => {
      // Brand filter
      if (selectedBrand !== 'Tous' && product.brand.toLowerCase() !== selectedBrand.toLowerCase()) {
        return false;
      }

      // Search filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const matchesTitle = product.title.toLowerCase().includes(query);
        const matchesBrand = product.brand.toLowerCase().includes(query);
        return matchesTitle || matchesBrand;
      }

      return true;
    });
  }, [products, selectedBrand, searchQuery]);

  // Calculated Metrics
  const totalVariantsCount = useMemo(() => {
    return products.reduce((acc, p) => acc + (p.product_variants?.length || 0), 0);
  }, [products]);

  const bestPriceKg = useMemo(() => {
    const validPrices = products
      .map((p) => p.min_price_per_kg)
      .filter((p): p is number => p !== null && p !== undefined && p > 0);
    return validPrices.length > 0 ? Math.min(...validPrices) : null;
  }, [products]);

  return (
    <div className="min-h-screen bg-[#0B0F17] text-gray-100 flex flex-col font-sans">
      
      {/* Header Bar */}
      <Header
        totalProducts={products.length}
        totalVariants={totalVariantsCount}
        bestPriceKg={bestPriceKg}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Search & Filter Controls Panel */}
        <section className="glass-panel rounded-2xl p-6 border border-gray-800 space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            
            {/* Search Input */}
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-emerald-400" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Rechercher une whey, isolat, ou marque (ex: Native, Nutrimuscle, Prozis)..."
                className="w-full pl-10 pr-4 py-3 bg-[#111827] border border-gray-800 rounded-xl text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors"
              />
            </div>

            {/* Quick Helper Badge */}
            <div className="flex items-center space-x-2 text-xs text-gray-400 bg-gray-900/80 px-3 py-2 rounded-xl border border-gray-800">
              <Sparkles className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span>{filteredProducts.length} offre(s) affichée(s)</span>
            </div>
          </div>

          {/* Brand Filter Buttons */}
          <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-gray-800/80">
            <div className="flex items-center space-x-1 text-xs text-gray-400 mr-2 font-medium">
              <Filter className="w-3.5 h-3.5 text-emerald-400" />
              <span>Marques :</span>
            </div>

            {BRANDS.map((brand) => {
              const isSelected = selectedBrand === brand;
              return (
                <button
                  key={brand}
                  onClick={() => setSelectedBrand(brand)}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                    isSelected
                      ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 shadow-md shadow-emerald-500/20 font-bold'
                      : 'bg-gray-800/80 hover:bg-gray-700 text-gray-300 border border-gray-700/80'
                  }`}
                >
                  {brand}
                </button>
              );
            })}
          </div>
        </section>

        {/* Products Table Section */}
        <section>
          <ProductTable products={filteredProducts} isLoading={isLoading} />
        </section>

      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800/80 bg-[#0A0D14] py-6 text-center text-xs text-gray-500">
        <p>NutriDeals © 2026 - Comparateur intelligent automatisé de compléments alimentaires.</p>
      </footer>

    </div>
  );
}
