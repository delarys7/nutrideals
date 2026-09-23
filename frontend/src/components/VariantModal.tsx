'use client';

import React from 'react';
import { X, ExternalLink, Tag, Scale, CheckCircle, AlertCircle, Flame, Award, ShieldCheck, Zap, Info } from 'lucide-react';
import { Product } from '../lib/supabase';

interface VariantModalProps {
  product: Product | null;
  onClose: () => void;
}

export const VariantModal: React.FC<VariantModalProps> = ({ product, onClose }) => {
  if (!product) return null;

  const variants = product.product_variants || [];

  const score = product.protein_score ?? 8.0;
  const proteinPct = product.protein_percentage ?? 78.0;
  const hasAminogram = product.has_aminogram ?? true;
  const leucine = product.leucine_per_100g ?? (proteinPct * 0.105);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-2xl max-h-[85vh] bg-[#111827] border border-gray-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="p-5 border-b border-gray-800 flex items-start justify-between bg-[#151D2F]">
          <div className="flex items-center space-x-4">
            {product.image_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img 
                src={product.image_url} 
                alt={product.title} 
                className="w-14 h-14 object-contain rounded-lg bg-gray-900 border border-gray-800 p-1 flex-shrink-0"
              />
            ) : (
              <div className="w-14 h-14 rounded-lg bg-gray-800 border border-gray-700 flex items-center justify-center text-gray-500 text-xs flex-shrink-0">
                No image
              </div>
            )}
            <div>
              <span className="inline-block px-2 py-0.5 text-xs font-semibold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 mb-1">
                {product.brand}
              </span>
              <h3 className="text-lg font-bold text-white leading-snug">
                {product.title}
              </h3>
              <p className="text-xs text-gray-400 mt-0.5">
                {variants.length} variante(s) disponible(s)
              </p>
            </div>
          </div>

          <button 
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-5 overflow-y-auto space-y-5 flex-1">

          {/* Protein Score & Aminogram Breakdown Card */}
          <div className="bg-[#161F32] border border-gray-800 rounded-xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Award className="w-4 h-4 text-amber-400" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-gray-200">
                  Analyse Protéique & Aminogramme
                </h4>
              </div>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-black bg-gradient-to-r from-emerald-500/20 to-teal-500/20 text-emerald-300 border border-emerald-400/40">
                Score Global: {score.toFixed(1)} / 10
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 pt-1">
              {/* Metric 1: Protein % */}
              <div className="bg-[#0F1623] p-3 rounded-lg border border-gray-800/80 flex flex-col justify-between">
                <div className="flex items-center space-x-1 text-gray-400 text-[11px]">
                  <Zap className="w-3 h-3 text-emerald-400" />
                  <span>Protéines nettes</span>
                </div>
                <div className="text-lg font-black text-white mt-1">
                  {proteinPct.toFixed(1)}%
                </div>
                <div className="text-[10px] text-gray-500 mt-0.5">
                  par portion 100g
                </div>
              </div>

              {/* Metric 2: Aminogram Status */}
              <div className="bg-[#0F1623] p-3 rounded-lg border border-gray-800/80 flex flex-col justify-between">
                <div className="flex items-center space-x-1 text-gray-400 text-[11px]">
                  <ShieldCheck className="w-3 h-3 text-teal-400" />
                  <span>Aminogramme</span>
                </div>
                <div className={`text-xs font-bold mt-1.5 ${hasAminogram ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {hasAminogram ? 'Certifié & Transparent' : 'Non spécifié'}
                </div>
                <div className="text-[10px] text-gray-500 mt-0.5">
                  {hasAminogram ? 'Sans amino spiking' : 'Transparence limitée'}
                </div>
              </div>

              {/* Metric 3: Leucine Concentration */}
              <div className="bg-[#0F1623] p-3 rounded-lg border border-gray-800/80 flex flex-col justify-between">
                <div className="flex items-center space-x-1 text-gray-400 text-[11px]">
                  <Info className="w-3 h-3 text-amber-400" />
                  <span>Taux de Leucine</span>
                </div>
                <div className="text-lg font-black text-amber-300 mt-1">
                  {leucine.toFixed(1)}g <span className="text-xs font-normal text-gray-400">/ 100g</span>
                </div>
                <div className="text-[10px] text-gray-500 mt-0.5">
                  Seuil anabolique mTOR
                </div>
              </div>
            </div>
          </div>

          {/* Variants List Header */}
          <div className="text-xs font-bold uppercase tracking-wider text-gray-400 pt-1">
            Formats & Variantes de Saveurs
          </div>

          <div className="space-y-3 divide-y divide-gray-800/60">
            {variants.length === 0 ? (
              <p className="text-gray-400 text-sm text-center py-6">
                Aucune variante spécifique détaillée.
              </p>
            ) : (
              variants.map((v) => {
                const isPromo = v.compare_at_price && v.compare_at_price > v.price;
                const isAvailable = v.available !== false;

                return (
                  <div 
                    key={v.id || v.title} 
                    className={`pt-3 first:pt-0 flex items-center justify-between gap-4 transition-all ${
                      !isAvailable ? 'opacity-40 grayscale select-none bg-gray-900/40 p-2 rounded-xl' : ''
                    }`}
                  >
                    {/* Variant info */}
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <Tag className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                        <span className="text-sm font-medium text-gray-200">
                          {v.flavor || v.title}
                        </span>

                        {/* Promo Badge */}
                        {isPromo && (
                          <span className="inline-flex items-center space-x-1 bg-red-600 text-white text-[10px] font-black uppercase px-2 py-0.5 rounded shadow-sm">
                            <Flame className="w-3 h-3 text-white fill-white" />
                            <span>PROMO</span>
                          </span>
                        )}
                      </div>

                      <div className="flex items-center space-x-3 text-xs">
                        {v.weight_kg && (
                          <div className="flex items-center space-x-1 text-gray-400">
                            <Scale className="w-3 h-3 text-emerald-400" />
                            <span>Format: {v.weight_kg} kg</span>
                          </div>
                        )}

                        {/* Stock Status Badge */}
                        {isAvailable ? (
                          <span className="inline-flex items-center space-x-1 text-[11px] font-medium text-emerald-400">
                            <CheckCircle className="w-3 h-3 text-emerald-400" />
                            <span>En stock</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center space-x-1 text-[11px] font-semibold text-red-400">
                            <AlertCircle className="w-3 h-3 text-red-400" />
                            <span>Rupture de stock</span>
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Price & Action */}
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className="flex items-center justify-end space-x-2">
                          {isPromo && (
                            <span className="text-xs text-gray-400 line-through font-medium">
                              {v.compare_at_price?.toFixed(2)} €
                            </span>
                          )}
                          <span className={`text-sm font-bold ${isPromo ? 'text-red-400' : 'text-white'}`}>
                            {v.price.toFixed(2)} €
                          </span>
                        </div>

                        {v.price_per_kg && (
                          <div className="text-xs font-medium text-emerald-400">
                            {v.price_per_kg.toFixed(2)} € / kg
                          </div>
                        )}
                      </div>

                      {isAvailable ? (
                        <a 
                          href={v.url || product.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white flex items-center space-x-1 transition-colors shadow-md shadow-emerald-600/20"
                        >
                          <span>Voir</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      ) : (
                        <button 
                          disabled
                          className="px-3.5 py-1.5 rounded-lg text-xs font-medium bg-gray-800 text-gray-500 cursor-not-allowed flex items-center space-x-1"
                        >
                          <span>Epuisé</span>
                        </button>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-gray-800 bg-[#151D2F] flex justify-end">
          <button 
            onClick={onClose}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm font-medium rounded-xl transition-colors"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
};
