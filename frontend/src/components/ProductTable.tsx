'use client';

import React, { useState } from 'react';
import { ExternalLink, Layers, ArrowUpDown, CheckCircle2, PackageCheck, Flame, Award, Zap, ShieldCheck, Factory } from 'lucide-react';
import { Product } from '../lib/supabase';
import { VariantModal } from './VariantModal';

interface ProductTableProps {
  products: Product[];
  isLoading: boolean;
}

type SortField = 'price_per_kg' | 'protein_score' | 'manufacturing_score' | 'health_score' | 'eco_score';

export const ProductTable: React.FC<ProductTableProps> = ({ products, isLoading }) => {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [sortField, setSortField] = useState<SortField>('price_per_kg');
  const [sortAscending, setSortAscending] = useState<boolean>(true);

  // Sorting logic
  const sortedProducts = [...products].sort((a, b) => {
    if (sortField === 'protein_score') {
      const scoreA = a.protein_score ?? 0;
      const scoreB = b.protein_score ?? 0;
      return sortAscending ? scoreA - scoreB : scoreB - scoreA;
    } else if (sortField === 'manufacturing_score') {
      const scoreA = a.manufacturing_score ?? 0;
      const scoreB = b.manufacturing_score ?? 0;
      return sortAscending ? scoreA - scoreB : scoreB - scoreA;
    } else if (sortField === 'health_score') {
      const scoreA = a.health_score ?? 0;
      const scoreB = b.health_score ?? 0;
      return sortAscending ? scoreA - scoreB : scoreB - scoreA;
    } else if (sortField === 'eco_score') {
      const scoreA = a.eco_score ?? 0;
      const scoreB = b.eco_score ?? 0;
      return sortAscending ? scoreA - scoreB : scoreB - scoreA;
    } else {
      const valA = a.min_price_per_kg ?? 9999;
      const valB = b.min_price_per_kg ?? 9999;
      return sortAscending ? valA - valB : valB - valA;
    }
  });

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortAscending(!sortAscending);
    } else {
      setSortField(field);
      setSortAscending(field === 'price_per_kg' ? true : false); // Default desc for scores, asc for price
    }
  };

  return (
    <>
      <div className="w-full glass-panel rounded-2xl border border-gray-800 overflow-hidden shadow-xl">
        {/* Table Controls Header */}
        <div className="p-4 sm:p-6 border-b border-gray-800/80 bg-[#121927] flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <PackageCheck className="w-5 h-5 text-emerald-400" />
            <h2 className="text-base font-bold text-white">
              Tableau Comparatif (Whey & Protéines ≤ 4 kg)
            </h2>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-medium text-gray-400 mr-1">Trier par :</span>

            <button
              onClick={() => toggleSort('price_per_kg')}
              className={`flex items-center space-x-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg border transition-colors ${
                sortField === 'price_per_kg'
                  ? 'bg-emerald-950/80 text-emerald-300 border-emerald-500/50 shadow-sm shadow-emerald-500/20'
                  : 'bg-gray-800 hover:bg-gray-700 text-gray-300 border-gray-700'
              }`}
            >
              <ArrowUpDown className="w-3.5 h-3.5 text-emerald-400" />
              <span>Prix/kg {sortField === 'price_per_kg' ? (sortAscending ? '(Croissant)' : '(Décroissant)') : ''}</span>
            </button>

            <button
              onClick={() => toggleSort('protein_score')}
              className={`flex items-center space-x-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg border transition-colors ${
                sortField === 'protein_score'
                  ? 'bg-amber-950/80 text-amber-300 border-amber-500/50 shadow-sm shadow-amber-500/20'
                  : 'bg-gray-800 hover:bg-gray-700 text-gray-300 border-gray-700'
              }`}
            >
              <Award className="w-3.5 h-3.5 text-amber-400" />
              <span>Score Protéique {sortField === 'protein_score' ? (sortAscending ? '(Croissant)' : '(Décroissant)') : ''}</span>
            </button>

            <button
              onClick={() => toggleSort('manufacturing_score')}
              className={`flex items-center space-x-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg border transition-colors ${
                sortField === 'manufacturing_score'
                  ? 'bg-indigo-950/80 text-indigo-300 border-indigo-500/50 shadow-sm shadow-indigo-500/20'
                  : 'bg-gray-800 hover:bg-gray-700 text-gray-300 border-gray-700'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
              <span>Score Fabrication {sortField === 'manufacturing_score' ? (sortAscending ? '(Croissant)' : '(Décroissant)') : ''}</span>
            </button>

            <button
              onClick={() => toggleSort('health_score')}
              className={`flex items-center space-x-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg border transition-colors ${
                sortField === 'health_score'
                  ? 'bg-lime-950/80 text-lime-300 border-lime-500/50 shadow-sm shadow-lime-500/20'
                  : 'bg-gray-800 hover:bg-gray-700 text-gray-300 border-gray-700'
              }`}
            >
              <Zap className="w-3.5 h-3.5 text-lime-400" />
              <span>Score Santé {sortField === 'health_score' ? (sortAscending ? '(Croissant)' : '(Décroissant)') : ''}</span>
            </button>

            <button
              onClick={() => toggleSort('eco_score')}
              className={`flex items-center space-x-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg border transition-colors ${
                sortField === 'eco_score'
                  ? 'bg-teal-950/80 text-teal-300 border-teal-500/50 shadow-sm shadow-teal-500/20'
                  : 'bg-gray-800 hover:bg-gray-700 text-gray-300 border-gray-700'
              }`}
            >
              <Factory className="w-3.5 h-3.5 text-teal-400" />
              <span>Éco-Score {sortField === 'eco_score' ? (sortAscending ? '(Croissant)' : '(Décroissant)') : ''}</span>
            </button>
          </div>
        </div>

        {/* Table Content */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-gray-800 bg-[#0F1623] text-xs font-semibold text-gray-400 uppercase tracking-wider">
                <th scope="col" className="py-4 px-5">Produit & Marque</th>
                <th scope="col" className="py-4 px-3 text-center">Score Protéique</th>
                <th scope="col" className="py-4 px-3 text-center">Score Fabrication</th>
                <th scope="col" className="py-4 px-3 text-center">Score Santé</th>
                <th scope="col" className="py-4 px-3 text-center">Éco-Score</th>
                <th scope="col" className="py-4 px-4 text-right">Prix Min</th>
                <th scope="col" className="py-4 px-4 text-right">Prix / kg</th>
                <th scope="col" className="py-4 px-4 text-center">Variantes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60 bg-[#111827]/60 text-sm">
              {isLoading ? (
                // Skeleton Rows
                Array.from({ length: 6 }).map((_, idx) => (
                  <tr key={idx} className="animate-pulse">
                    <td className="py-4 px-6">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-gray-800 rounded-lg"></div>
                        <div className="space-y-2">
                          <div className="w-20 h-4 bg-gray-800 rounded"></div>
                          <div className="w-48 h-4 bg-gray-800 rounded"></div>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-6 text-center"><div className="w-16 h-6 bg-gray-800 rounded mx-auto"></div></td>
                    <td className="py-4 px-6 text-center"><div className="w-16 h-6 bg-gray-800 rounded mx-auto"></div></td>
                    <td className="py-4 px-6 text-center"><div className="w-14 h-5 bg-gray-800 rounded mx-auto"></div></td>
                    <td className="py-4 px-6 text-right"><div className="w-16 h-5 bg-gray-800 rounded ml-auto"></div></td>
                    <td className="py-4 px-6 text-right"><div className="w-20 h-6 bg-gray-800 rounded ml-auto"></div></td>
                    <td className="py-4 px-6 text-center"><div className="w-16 h-5 bg-gray-800 rounded mx-auto"></div></td>
                  </tr>
                ))
              ) : sortedProducts.length === 0 ? (
                // Empty State
                <tr>
                  <td colSpan={7} className="py-12 text-center text-gray-400">
                    <p className="text-base font-semibold text-gray-300">Aucun produit ne correspond à votre recherche.</p>
                    <p className="text-xs text-gray-500 mt-1">Essayez de modifier les filtres de recherche ou de marque.</p>
                  </td>
                </tr>
              ) : (
                sortedProducts.map((product) => {
                  const variants = product.product_variants || [];
                  const variantsCount = variants.length;
                  const isTopDeal = product.min_price_per_kg && product.min_price_per_kg <= 20.0;

                  // Promo check: check if any variant has a compare_at_price > price
                  const promoVariant = variants.find(
                    (v) => v.compare_at_price && v.compare_at_price > v.price
                  );
                  const hasPromo = Boolean(promoVariant);

                  // Availability check
                  const allOut = variants.length > 0 && variants.every((v) => v.available === false);

                  // Protein Score styling
                  const pScore = product.protein_score ?? 8.0;
                  let pScoreBadgeClass = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
                  if (pScore >= 9.0) {
                    pScoreBadgeClass = 'bg-gradient-to-r from-emerald-500/20 to-teal-500/20 text-emerald-300 border-emerald-400/50 glow-emerald';
                  } else if (pScore >= 8.0) {
                    pScoreBadgeClass = 'bg-teal-950/60 text-teal-300 border-teal-800/60';
                  } else if (pScore >= 7.0) {
                    pScoreBadgeClass = 'bg-blue-950/60 text-blue-300 border-blue-800/60';
                  } else {
                    pScoreBadgeClass = 'bg-amber-950/60 text-amber-300 border-amber-800/60';
                  }

                  // Manufacturing Score styling
                  const mScore = product.manufacturing_score ?? 7.0;
                  let mScoreBadgeClass = 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40';
                  if (mScore >= 8.0) {
                    mScoreBadgeClass = 'bg-gradient-to-r from-indigo-500/20 to-blue-500/20 text-indigo-300 border-indigo-400/50';
                  } else if (mScore >= 6.5) {
                    mScoreBadgeClass = 'bg-blue-950/60 text-blue-300 border-blue-800/60';
                  } else {
                    mScoreBadgeClass = 'bg-slate-800 text-slate-300 border-slate-700';
                  }

                  // Health Score styling
                  const hScore = product.health_score ?? 6.0;
                  let hScoreBadgeClass = 'bg-lime-500/20 text-lime-300 border-lime-500/40';
                  if (hScore >= 8.5) {
                    hScoreBadgeClass = 'bg-gradient-to-r from-lime-500/20 to-emerald-500/20 text-lime-300 border-lime-400/50 shadow-sm shadow-lime-500/20';
                  } else if (hScore >= 6.0) {
                    hScoreBadgeClass = 'bg-lime-950/60 text-lime-300 border-lime-800/60';
                  } else {
                    hScoreBadgeClass = 'bg-amber-950/60 text-amber-400 border-amber-800/60';
                  }

                  // Eco Score styling
                  const eScore = product.eco_score ?? 6.0;
                  let eScoreBadgeClass = 'bg-teal-500/20 text-teal-300 border-teal-500/40';
                  if (eScore >= 8.5) {
                    eScoreBadgeClass = 'bg-gradient-to-r from-teal-500/20 to-emerald-500/20 text-teal-300 border-teal-400/50 shadow-sm shadow-teal-500/20';
                  } else if (eScore >= 6.5) {
                    eScoreBadgeClass = 'bg-teal-950/60 text-teal-300 border-teal-800/60';
                  } else {
                    eScoreBadgeClass = 'bg-slate-800 text-slate-300 border-slate-700';
                  }

                  return (
                    <tr 
                      key={product.id}
                      className={`hover:bg-gray-800/40 transition-colors group relative ${
                        allOut ? 'opacity-75' : ''
                      }`}
                    >
                      {/* Brand & Product Title - FULLY CLICKABLE LINK (even when out of stock) */}
                      <td className="py-4 px-5 relative">
                        <a 
                          href={product.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center space-x-3 group/link hover:opacity-90 transition-opacity"
                        >
                          {/* Image Thumbnail with Floating PROMO Badge */}
                          <div className="relative flex-shrink-0">
                            {hasPromo && (
                              <span className="absolute -top-2 -left-2 z-10 inline-flex items-center space-x-0.5 bg-red-600 text-white text-[9px] font-black uppercase px-1.5 py-0.5 rounded-full shadow-lg shadow-red-600/50 border border-red-400 ring-2 ring-[#111827]">
                                <Flame className="w-2.5 h-2.5 fill-white" />
                                <span>PROMO</span>
                              </span>
                            )}

                            {product.image_url ? (
                              // eslint-disable-next-line @next/next/no-img-element
                              <img 
                                src={product.image_url} 
                                alt={product.title} 
                                className="w-12 h-12 object-contain rounded-lg bg-gray-900 border border-gray-800 p-1 group-hover/link:border-emerald-500/50 group-hover/link:scale-105 transition-all"
                              />
                            ) : (
                              <div className="w-12 h-12 rounded-lg bg-gray-800 border border-gray-700 flex items-center justify-center text-gray-500 text-[10px]">
                                Whey
                              </div>
                            )}
                          </div>

                          <div>
                            <div className="flex items-center space-x-2 mb-1">
                              <span className="inline-block px-2 py-0.5 text-[11px] font-bold rounded bg-gray-800 text-emerald-400 border border-emerald-500/20">
                                {product.brand}
                              </span>

                              {allOut && (
                                <span className="inline-block px-1.5 py-0.5 text-[10px] font-bold rounded bg-red-950/80 text-red-400 border border-red-800/80">
                                  Rupture
                                </span>
                              )}

                              {hasPromo && (
                                <span className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-black uppercase rounded bg-red-600/20 text-red-400 border border-red-500/30">
                                  PROMO
                                </span>
                              )}
                            </div>

                            <h3 className="font-semibold text-gray-100 group-hover/link:text-emerald-300 transition-colors line-clamp-1 flex items-center space-x-1">
                              <span>{product.title}</span>
                              <ExternalLink className="w-3 h-3 opacity-0 group-hover/link:opacity-100 text-emerald-400 transition-opacity flex-shrink-0" />
                            </h3>
                          </div>
                        </a>
                      </td>

                      {/* Score Protéique */}
                      <td className="py-4 px-3 text-center">
                        <button
                          onClick={() => setSelectedProduct(product)}
                          className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-xl text-xs font-black border transition-transform hover:scale-105 ${pScoreBadgeClass}`}
                          title="Cliquez pour voir le détail de l'analyse protéique et aminogramme"
                        >
                          <Award className="w-3.5 h-3.5 text-amber-400" />
                          <span>{pScore.toFixed(1)}</span>
                        </button>
                      </td>

                      {/* Score de Fabrication */}
                      <td className="py-4 px-3 text-center">
                        <button
                          onClick={() => setSelectedProduct(product)}
                          className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-xl text-xs font-black border transition-transform hover:scale-105 ${mScoreBadgeClass}`}
                          title="Cliquez pour voir l'analyse complète de fabrication et d'intégrité"
                        >
                          <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                          <span>{mScore.toFixed(1)}</span>
                        </button>
                      </td>

                      {/* Score Santé */}
                      <td className="py-4 px-3 text-center">
                        <button
                          onClick={() => setSelectedProduct(product)}
                          className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-xl text-xs font-black border transition-transform hover:scale-105 ${hScoreBadgeClass}`}
                          title="Cliquez pour voir la composition (édulcorants, additifs, clean label)"
                        >
                          <Zap className="w-3.5 h-3.5 text-lime-400" />
                          <span>{hScore.toFixed(1)}</span>
                        </button>
                      </td>

                      {/* Éco-Score */}
                      <td className="py-4 px-3 text-center">
                        <button
                          onClick={() => setSelectedProduct(product)}
                          className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-xl text-xs font-black border transition-transform hover:scale-105 ${eScoreBadgeClass}`}
                          title="Cliquez pour voir l'empreinte écologique (packaging, cuillère, origine)"
                        >
                          <Factory className="w-3.5 h-3.5 text-teal-400" />
                          <span>{eScore.toFixed(1)}</span>
                        </button>
                      </td>

                      {/* Taux Protéines % */}
                      <td className="py-4 px-6 text-center">
                        <div className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-lg bg-gray-800/80 border border-gray-700 text-xs font-bold text-gray-200">
                          <Zap className="w-3 h-3 text-emerald-400" />
                          <span>{product.protein_percentage ? `${product.protein_percentage.toFixed(0)}%` : '78%'}</span>
                        </div>
                      </td>

                      {/* Min Price */}
                      <td className="py-4 px-6 text-right">
                        <div className="flex flex-col items-end justify-center">
                          {promoVariant && promoVariant.compare_at_price && (
                            <span className="text-xs text-gray-400 line-through font-medium">
                              {promoVariant.compare_at_price.toFixed(2)} €
                            </span>
                          )}
                          <span className={`font-bold text-sm ${hasPromo ? 'text-red-400' : 'text-gray-200'}`}>
                            {product.min_price.toFixed(2)} €
                          </span>
                        </div>
                      </td>

                      {/* Best Price per KG */}
                      <td className="py-4 px-6 text-right">
                        {product.min_price_per_kg ? (
                          <div className="inline-flex flex-col items-end">
                            <span className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg text-xs font-extrabold ${
                              isTopDeal 
                                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 glow-emerald' 
                                : 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/60'
                            }`}>
                              {isTopDeal && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                              <span>{product.min_price_per_kg.toFixed(2)} € / kg</span>
                            </span>
                          </div>
                        ) : (
                          <span className="text-xs text-gray-500">N/A</span>
                        )}
                      </td>

                      {/* Variants */}
                      <td className="py-4 px-6 text-center">
                        <button
                          onClick={() => setSelectedProduct(product)}
                          className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 transition-colors"
                        >
                          <Layers className="w-3.5 h-3.5 text-emerald-400" />
                          <span>{variantsCount} variante(s)</span>
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Variant Modal Popup */}
      <VariantModal
        product={selectedProduct}
        onClose={() => setSelectedProduct(null)}
      />
    </>
  );
};
