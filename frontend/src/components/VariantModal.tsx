'use client';

import React from 'react';
import { X, ExternalLink, Tag, Scale, CheckCircle, AlertCircle, Flame, Award, ShieldCheck, Zap, Info, Factory, FileCheck, MapPin } from 'lucide-react';
import { Product } from '../lib/supabase';

interface VariantModalProps {
  product: Product | null;
  onClose: () => void;
}

export const VariantModal: React.FC<VariantModalProps> = ({ product, onClose }) => {
  if (!product) return null;

  const variants = product.product_variants || [];

  // Protein Metrics
  const pScore = product.protein_score ?? 8.0;
  const proteinPct = product.protein_percentage ?? 78.0;
  const hasAminogram = product.has_aminogram ?? true;
  const leucine = product.leucine_per_100g ?? (proteinPct * 0.105);

  // Manufacturing Metrics
  const mScore = product.manufacturing_score ?? 7.0;
  const wheyType = product.whey_type || 'fromagere';
  const isGrassFed = product.is_grass_fed ?? false;
  const originCountry = product.origin_country || 'UE';
  const extractionProcess = product.extraction_process || 'CFM (Microfiltration à froid)';
  const chemicalFree = product.chemical_free ?? true;
  const certs = product.certifications || ['HACCP', 'ISO 22000'];
  const hasCoA = product.has_coa ?? false;
  const thirdPartyTesting = product.third_party_testing ?? false;

  // Health Metrics
  const hScore = product.health_score ?? 6.0;
  const sweeteners = product.sweeteners || [];
  const additivesCount = product.additives_count ?? 0;
  const isCleanLabel = product.is_clean_label ?? false;

  // Eco Metrics
  const eScore = product.eco_score ?? 6.0;
  const packagingType = product.packaging_type || 'pot_plastique_standard';
  const hasPlasticScoop = product.has_plastic_scoop ?? true;
  const supplyChain = product.supply_chain_transparency || 'local_ue';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-4xl max-h-[90vh] bg-[#111827] border border-gray-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
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
              <div className="flex items-center space-x-2 mb-1">
                <span className="inline-block px-2 py-0.5 text-xs font-semibold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  {product.brand}
                </span>
                <a 
                  href={product.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-1 text-xs text-emerald-400 hover:text-emerald-300 font-semibold"
                >
                  <span>Visiter la fiche marchand</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <h3 className="text-lg font-bold text-white leading-snug">
                {product.title}
              </h3>
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

          {/* 4 QUAD SCORES BREAKDOWN CARDS */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            {/* Card 1: Score Protéique */}
            <div className="bg-[#161F32] border border-gray-800 rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Award className="w-4 h-4 text-amber-400" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-gray-200">
                    Score Protéique
                  </h4>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-black bg-gradient-to-r from-emerald-500/20 to-teal-500/20 text-emerald-300 border border-emerald-400/40">
                  {pScore.toFixed(1)} / 10
                </span>
              </div>

              <div className="space-y-2 text-xs text-gray-300">
                <div className="flex justify-between items-center p-2 rounded-lg bg-[#0F1623] border border-gray-800/80">
                  <span className="text-gray-400 flex items-center space-x-1">
                    <Zap className="w-3 h-3 text-emerald-400" />
                    <span>Taux de protéines net</span>
                  </span>
                  <span className="font-bold text-white">{proteinPct.toFixed(1)}%</span>
                </div>

                <div className="flex justify-between items-center p-2 rounded-lg bg-[#0F1623] border border-gray-800/80">
                  <span className="text-gray-400 flex items-center space-x-1">
                    <ShieldCheck className="w-3 h-3 text-teal-400" />
                    <span>Aminogramme</span>
                  </span>
                  <span className={`font-semibold ${hasAminogram ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {hasAminogram ? 'Certifié & Transparent' : 'Non spécifié'}
                  </span>
                </div>

                <div className="flex justify-between items-center p-2 rounded-lg bg-[#0F1623] border border-gray-800/80">
                  <span className="text-gray-400 flex items-center space-x-1">
                    <Info className="w-3 h-3 text-amber-400" />
                    <span>Concentration Leucine</span>
                  </span>
                  <span className="font-bold text-amber-300">{leucine.toFixed(1)}g / 100g</span>
                </div>
              </div>
            </div>

            {/* Card 2: Score de Fabrication & Intégrité */}
            <div className="bg-[#161F32] border border-gray-800 rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-indigo-400" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-gray-200">
                    Score de Fabrication
                  </h4>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-black bg-gradient-to-r from-indigo-500/20 to-blue-500/20 text-indigo-300 border border-indigo-400/40">
                  {mScore.toFixed(1)} / 10
                </span>
              </div>

              <div className="space-y-2 text-xs text-gray-300">
                <div className="flex justify-between items-center p-2 rounded-lg bg-[#0F1623] border border-gray-800/80">
                  <span className="text-gray-400 flex items-center space-x-1">
                    <Factory className="w-3 h-3 text-indigo-400" />
                    <span>Matière Première</span>
                  </span>
                  <span className="font-bold text-white capitalize">
                    {wheyType === 'native' ? 'Whey Native' : 'Whey Fromagère'} {isGrassFed && '🌱 (Herbe)'}
                  </span>
                </div>

                <div className="flex justify-between items-center p-2 rounded-lg bg-[#0F1623] border border-gray-800/80">
                  <span className="text-gray-400 flex items-center space-x-1">
                    <MapPin className="w-3 h-3 text-blue-400" />
                    <span>Origine & Procédé</span>
                  </span>
                  <span className="font-bold text-blue-300">
                    {originCountry} • {extractionProcess.includes('CFM') ? 'CFM à froid' : 'Standard'}
                  </span>
                </div>

                <div className="flex justify-between items-center p-2 rounded-lg bg-[#0F1623] border border-gray-800/80">
                  <span className="text-gray-400 flex items-center space-x-1">
                    <FileCheck className="w-3 h-3 text-emerald-400" />
                    <span>Certifications & CoA</span>
                  </span>
                  <span className="font-semibold text-emerald-300">
                    {certs.length > 0 ? certs.join(', ') : 'Standards EU'}
                  </span>
                </div>
              </div>
            </div>

            {/* Card 3: Score Santé & Composition */}
            <div className="bg-[#161F32] border border-gray-800 rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Zap className="w-4 h-4 text-lime-400" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-gray-200">
                    Score Santé
                  </h4>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-black bg-gradient-to-r from-lime-500/20 to-emerald-500/20 text-lime-300 border border-lime-400/40">
                  {hScore.toFixed(1)} / 10
                </span>
              </div>

              <div className="space-y-2 text-xs text-gray-300">
                <div className="flex justify-between items-center p-2 rounded-lg bg-[#0F1623] border border-gray-800/80">
                  <span className="text-gray-400 flex items-center space-x-1">
                    <Zap className="w-3 h-3 text-lime-400" />
                    <span>Édulcorants</span>
                  </span>
                  <span className="font-bold text-white capitalize">
                    {sweeteners.length > 0 ? sweeteners.join(', ').replace(/_/g, ' ') : 'Sans Édulcorant (Nature)'}
                  </span>
                </div>

                <div className="flex justify-between items-center p-2 rounded-lg bg-[#0F1623] border border-gray-800/80">
                  <span className="text-gray-400 flex items-center space-x-1">
                    <Info className="w-3 h-3 text-amber-400" />
                    <span>Additifs & Texturants</span>
                  </span>
                  <span className={`font-semibold ${additivesCount === 0 ? 'text-emerald-400 font-bold' : 'text-amber-300'}`}>
                    {additivesCount === 0 ? '0 additif (Formule pure)' : `${additivesCount} additif(s)`}
                  </span>
                </div>

                <div className="flex justify-between items-center p-2 rounded-lg bg-[#0F1623] border border-gray-800/80">
                  <span className="text-gray-400 flex items-center space-x-1">
                    <CheckCircle className="w-3 h-3 text-emerald-400" />
                    <span>Label Propreté</span>
                  </span>
                  <span className={`font-semibold ${isCleanLabel ? 'text-emerald-300' : 'text-gray-400'}`}>
                    {isCleanLabel ? 'Clean Label Certifié' : 'Formulation standard'}
                  </span>
                </div>
              </div>
            </div>

            {/* Card 4: Éco-Score & Empreinte */}
            <div className="bg-[#161F32] border border-gray-800 rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Factory className="w-4 h-4 text-teal-400" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-gray-200">
                    Éco-Score
                  </h4>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-black bg-gradient-to-r from-teal-500/20 to-emerald-500/20 text-teal-300 border border-teal-400/40">
                  {eScore.toFixed(1)} / 10
                </span>
              </div>

              <div className="space-y-2 text-xs text-gray-300">
                <div className="flex justify-between items-center p-2 rounded-lg bg-[#0F1623] border border-gray-800/80">
                  <span className="text-gray-400 flex items-center space-x-1">
                    <Factory className="w-3 h-3 text-teal-400" />
                    <span>Contenant / Packaging</span>
                  </span>
                  <span className="font-bold text-white capitalize">
                    {packagingType.replace(/_/g, ' ')}
                  </span>
                </div>

                <div className="flex justify-between items-center p-2 rounded-lg bg-[#0F1623] border border-gray-800/80">
                  <span className="text-gray-400 flex items-center space-x-1">
                    <Info className="w-3 h-3 text-emerald-400" />
                    <span>Politique Cuillère Plastique</span>
                  </span>
                  <span className={`font-semibold ${!hasPlasticScoop ? 'text-emerald-400 font-bold' : 'text-red-400'}`}>
                    {!hasPlasticScoop ? 'Eco Scoop / Sans Plastique' : 'Scoop Plastique Inclus'}
                  </span>
                </div>

                <div className="flex justify-between items-center p-2 rounded-lg bg-[#0F1623] border border-gray-800/80">
                  <span className="text-gray-400 flex items-center space-x-1">
                    <MapPin className="w-3 h-3 text-blue-400" />
                    <span>Traçabilité & Logistique</span>
                  </span>
                  <span className="font-semibold text-blue-300 capitalize">
                    {supplyChain.replace(/_/g, ' ')}
                  </span>
                </div>
              </div>
            </div>

          </div>

          {/* Variants List Header */}
          <div className="text-xs font-bold uppercase tracking-wider text-gray-400 pt-1">
            Formats & Variantes de Saveurs ({variants.length})
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

                const vHealthScore = v.health_score ?? hScore;
                const vSweeteners = v.sweeteners && v.sweeteners.length > 0 ? v.sweeteners : sweeteners;
                const vAdditives = v.additives_count ?? additivesCount;

                return (
                  <div 
                    key={v.id || v.title} 
                    className={`pt-3 first:pt-0 flex items-center justify-between gap-4 transition-all ${
                      !isAvailable ? 'opacity-50 grayscale select-none bg-gray-900/40 p-2 rounded-xl' : ''
                    }`}
                  >
                    {/* Variant info */}
                    <div className="space-y-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <Tag className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                        <span className="text-sm font-medium text-gray-200">
                          {v.flavor || v.title}
                        </span>

                        {/* Variant Health Score Badge */}
                        <span 
                          className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded-lg text-[10px] font-black border ${
                            vHealthScore >= 9.0 
                              ? 'bg-lime-950/90 text-lime-300 border-lime-500/50'
                              : vHealthScore >= 6.0
                              ? 'bg-lime-950/60 text-lime-300 border-lime-800/60'
                              : 'bg-amber-950/60 text-amber-400 border-amber-800/60'
                          }`}
                          title={`Score Santé de la variante: ${vHealthScore.toFixed(1)}/10 (${vSweeteners.length > 0 ? vSweeteners.join(', ') : 'Nature'}, ${vAdditives} additif(s))`}
                        >
                          <Zap className="w-2.5 h-2.5 text-lime-400" />
                          <span>Santé {vHealthScore.toFixed(1)}/10</span>
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

                    {/* Price & Action - Permanent Access Link */}
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

                      <a 
                        href={v.url || product.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white flex items-center space-x-1 transition-colors shadow-md shadow-emerald-600/20"
                      >
                        <span>Voir</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
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
