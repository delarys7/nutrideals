'use client';

import React from 'react';
import { Sparkles, Package, Dumbbell } from 'lucide-react';

interface HeaderProps {
  totalProducts: number;
  totalVariants: number;
  bestPriceKg: number | null;
}

export const Header: React.FC<HeaderProps> = ({
  totalProducts,
  totalVariants,
  bestPriceKg,
}) => {
  return (
    <header className="border-b border-gray-800 bg-[#0F1623]/90 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          
          {/* Logo & Tagline */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Dumbbell className="w-5 h-5 text-slate-950 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-xl font-black tracking-tight text-white">
                  Nutri<span className="text-emerald-400">Deals</span>
                </h1>
                <span className="px-2 py-0.5 text-[10px] font-extrabold uppercase rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  v2.0
                </span>
              </div>
              <p className="text-xs text-gray-400 font-medium">
                Comparateur de Whey & Score Protéique en temps réel
              </p>
            </div>
          </div>

          {/* Quick Metrics KPI Bar */}
          <div className="flex items-center space-x-4 text-xs">
            <div className="flex items-center space-x-2 bg-gray-900/80 px-3.5 py-2 rounded-xl border border-gray-800">
              <Package className="w-4 h-4 text-emerald-400" />
              <div>
                <span className="text-gray-400 font-medium">Offres : </span>
                <span className="font-bold text-white">{totalProducts} produits ({totalVariants} var.)</span>
              </div>
            </div>

            {bestPriceKg && (
              <div className="hidden md:flex items-center space-x-2 bg-emerald-950/40 px-3.5 py-2 rounded-xl border border-emerald-800/50">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <div>
                  <span className="text-emerald-300/80 font-medium">Meilleur Prix/kg : </span>
                  <span className="font-extrabold text-emerald-400">{bestPriceKg.toFixed(2)} €/kg</span>
                </div>
              </div>
            )}
          </div>

        </div>
      </div>
    </header>
  );
};
