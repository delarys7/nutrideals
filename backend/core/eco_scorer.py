"""
NutriDeals Eco Scorer Module
Calculates a scientific Éco-Score (sur 10.0)
based on Packaging & Plastic Scoop Policy (60%) and Supply Chain Transparency & Carbon Footprint (40%).
"""

import re
from typing import Optional, List, Dict, Any


def calculate_eco_score(
    packaging_type: str = "pot_plastique_standard",
    has_plastic_scoop: bool = True,
    supply_chain_transparency: str = "local_ue"
) -> float:
    """
    Calculates global Éco-Score out of 10.0.

    2 Weighted Components:
    1. Packaging & Plastic Scoop Policy (60% / 6.0 pts max)
    2. Supply Chain & Carbon Footprint (40% / 4.0 pts max)
    """
    pkg = (packaging_type or "pot_plastique_standard").lower()

    # --- 1. Packaging & Scoop Policy (6.0 pts max) ---
    pkg_score = 0.0
    if any(k in pkg for k in ["sachet_recyclable", "sachet recyclable", "kraft", "pouch_mono", "mono-matériau"]):
        pkg_score = 3.5
    elif any(k in pkg for k in ["pot_rpet", "rpet", "plastique recyclé"]):
        pkg_score = 3.0
    elif any(k in pkg for k in ["sachet", "pouch", "doypack"]):
        pkg_score = 2.5
    elif any(k in pkg for k in ["pot_plastique_standard", "pehd", "pet"]):
        pkg_score = 1.5
    else:
        pkg_score = 0.8

    # Plastic scoop policy credit (2.5 max vs 0.5 for systematic plastic scoop)
    if not has_plastic_scoop:
        scoop_score = 2.5
    else:
        scoop_score = 0.5

    packaging_total = min(6.0, pkg_score + scoop_score)

    # --- 2. Supply Chain & Carbon Footprint (4.0 pts max) ---
    sc = (supply_chain_transparency or "local_ue").lower()
    if any(k in sc for k in ["circuit_court_france", "france", "local_france"]):
        chain_score = 4.0
    elif any(k in sc for k in ["local_ue", "ue", "europe", "allemagne"]):
        chain_score = 3.0
    else:
        chain_score = 1.0

    # Global Score out of 10.0
    total_score = packaging_total + chain_score
    total_score = round(min(10.0, max(1.0, total_score)), 1)

    return total_score


def extract_or_estimate_eco_metrics(
    title: str,
    description: str = "",
    brand: str = ""
) -> Dict[str, Any]:
    """
    Extracts or estimates eco parameters and computes eco_score
    based on product title, brand, and description HTML.
    """
    combined = f"{brand} {title} {description}".lower()

    # 1. Packaging type
    if any(k in combined for k in ["sachet recyclable", "kraft", "doypack recyclable", "mono-matériau"]):
        packaging_type = "sachet_recyclable"
    elif any(k in combined for k in ["rpet", "pot recyclé", "plastique 100% recyclé"]):
        packaging_type = "pot_rpet"
    elif any(k in combined for k in ["sachet", "pouch", "bag", "doypack"]):
        packaging_type = "sachet_recyclable" if brand.lower() in ["esn", "nutrimuscle"] else "sachet_standard"
    else:
        if brand.lower() in ["nutrimuscle", "nutrimea"]:
            packaging_type = "pot_rpet"
        else:
            packaging_type = "pot_plastique_standard"

    # 2. Plastic scoop policy
    has_plastic_scoop = not any(k in combined for k in ["sans cuillère", "sans scoop", "pas de cuillère", "eco scoop", "cuillère bois"])
    if brand.lower() in ["nutrimuscle", "esn"]:
        # ESN and Nutrimuscle stopped including mandatory plastic scoops in every bag
        has_plastic_scoop = False

    # 3. Supply chain transparency
    if any(k in combined for k in ["lait français", "fabriqué en france", "circuit court"]):
        supply_chain_transparency = "circuit_court_france"
    elif any(k in combined for k in ["fabriqué en europe", "lait ue", "origine ue"]):
        supply_chain_transparency = "local_ue"
    else:
        if brand.lower() in ["nutrimuscle", "inshape nutrition", "nutrimea"]:
            supply_chain_transparency = "circuit_court_france"
        elif brand.lower() in ["esn", "prozis"]:
            supply_chain_transparency = "local_ue"
        else:
            supply_chain_transparency = "mondial_opaque"

    score = calculate_eco_score(
        packaging_type=packaging_type,
        has_plastic_scoop=has_plastic_scoop,
        supply_chain_transparency=supply_chain_transparency
    )

    return {
        "packaging_type": packaging_type,
        "has_plastic_scoop": has_plastic_scoop,
        "supply_chain_transparency": supply_chain_transparency,
        "eco_score": score
    }
