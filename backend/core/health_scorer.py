"""
NutriDeals Health Scorer Module
Calculates a scientific Health Score (Score Santé sur 10.0)
based on Sweeteners (50%), Additives & Texturizers (30%), and Clean Label / Purity (20%).
"""

import re
from typing import Optional, List, Dict, Any


def calculate_health_score(
    sweeteners: Optional[List[str]] = None,
    additives_count: int = 0,
    is_clean_label: bool = False,
    is_unflavored: bool = False
) -> float:
    """
    Calculates global Health Score (Score Santé out of 10.0).

    3 Weighted Components:
    1. Édulcorants & Sweeteners (50% / 5.0 pts max)
    2. Additifs & Texturants (30% / 3.0 pts max)
    3. Clean Label & Pureté (20% / 2.0 pts max)
    """
    sw_list = [s.lower() for s in (sweeteners or [])]

    # --- 1. Édulcorants & Sweeteners (5.0 pts max) ---
    if is_unflavored or "sans_edulcorant" in sw_list or not sw_list:
        sweetener_score = 5.0
    elif all(s in ["stevia", "stévia", "thaumatine", "erythritol", "érythritol"] for s in sw_list):
        sweetener_score = 4.8
    elif any(s in ["stevia", "stévia", "thaumatine"] for s in sw_list) and any(s in ["sucralose", "acesulfame_k", "acésulfame_k"] for s in sw_list):
        sweetener_score = 3.5
    elif sw_list == ["sucralose"]:
        sweetener_score = 2.5
    elif any(s in ["acesulfame_k", "acésulfame_k", "aspartame", "saccharine"] for s in sw_list) and "sucralose" not in sw_list:
        sweetener_score = 2.0
    elif "sucralose" in sw_list and any(s in ["acesulfame_k", "acésulfame_k", "aspartame"] for s in sw_list):
        sweetener_score = 1.0
    else:
        sweetener_score = 1.5

    sweetener_score = min(5.0, max(0.5, sweetener_score))

    # --- 2. Additifs & Texturants (3.0 pts max) ---
    if additives_count <= 0:
        additives_score = 3.0
    elif additives_count == 1:
        additives_score = 2.0
    elif additives_count == 2:
        additives_score = 1.0
    else:
        additives_score = 0.2

    # --- 3. Clean Label & Pureté (2.0 pts max) ---
    clean_score = 0.0
    if is_clean_label:
        clean_score += 1.0
    else:
        clean_score += 0.4

    if is_unflavored or additives_count == 0:
        clean_score += 1.0
    else:
        clean_score += 0.4

    clean_score = min(2.0, clean_score)

    # Global Score out of 10.0
    total_score = sweetener_score + additives_score + clean_score
    total_score = round(min(10.0, max(1.0, total_score)), 1)

    return total_score


def extract_or_estimate_health_metrics(
    title: str,
    description: str = "",
    brand: str = ""
) -> Dict[str, Any]:
    """
    Extracts or estimates health & composition parameters and computes health_score
    based on product title, brand, and description HTML.
    """
    combined = f"{brand} {title} {description}".lower()

    is_unflavored = any(k in combined for k in ["nature", "unflavored", "sans arôme", "brut", "neutre"])

    # 1. Sweeteners detection
    sweeteners = []
    if is_unflavored or "sans édulcorant" in combined or "sans edulcorant" in combined or "0 édulcorant" in combined:
        sweeteners.append("sans_edulcorant")
    else:
        if "sucralose" in combined:
            sweeteners.append("sucralose")
        if any(k in combined for k in ["acésulfame", "acesulfame", "acésulfame-k", "acesulfame-k"]):
            sweeteners.append("acesulfame_k")
        if any(k in combined for k in ["stévia", "stevia", "rébaudioside"]):
            sweeteners.append("stevia")
        if "thaumatine" in combined:
            sweeteners.append("thaumatine")

        # Defaults by brand if not mentioned in text
        if not sweeteners:
            if brand.lower() == "nutrimuscle":
                sweeteners = ["stevia"]
            elif brand.lower() in ["esn", "prozis", "biotech usa"]:
                sweeteners = ["sucralose", "acesulfame_k"]
            else:
                sweeteners = ["sucralose"]

    # 2. Additives count detection
    additives = 0
    if is_unflavored:
        additives = 0
    else:
        additive_keywords = [
            "gomme de xanthane", "xanthan", "carraghénane", "carrageenan", "gomme guar", "guar",
            "carboxyméthylcellulose", "cmc", "dioxyde de titane", "silice", "anti-agglomérant",
            "arôme artificiel", "colorant"
        ]
        additives = sum(1 for kw in additive_keywords if kw in combined)

        # Brand estimates if text is minimal
        if additives == 0:
            if brand.lower() == "nutrimuscle":
                additives = 0
            elif brand.lower() in ["esn", "prozis"]:
                additives = 2
            else:
                additives = 1

    # 3. Clean Label detection
    is_clean_label = any(k in combined for k in ["clean label", "sans additif", "100% naturel", "sans sucralose", "sans arôme artificiel"])
    if brand.lower() == "nutrimuscle" or is_unflavored:
        is_clean_label = True

    score = calculate_health_score(
        sweeteners=sweeteners,
        additives_count=additives,
        is_clean_label=is_clean_label,
        is_unflavored=is_unflavored
    )

    return {
        "sweeteners": sweeteners,
        "additives_count": additives,
        "is_clean_label": is_clean_label,
        "health_score": score
    }


def extract_or_estimate_variant_health_metrics(
    variant_title: str,
    parent_health_metrics: Dict[str, Any],
    brand: str = ""
) -> Dict[str, Any]:
    """
    Computes variant-specific Health Score and composition metrics.
    For example: 'Nature' / 'Unflavored' variants receive 10.0/10 with 0 additives,
    while sweet flavored variants receive flavor-appropriate sweetener and additive scores.
    """
    v_clean = (variant_title or "").lower()

    # Unflavored / Nature variant detection
    if any(k in v_clean for k in ["nature", "unflavored", "sans arôme", "neutre", "brut", "flavor unflavored"]):
        sweeteners = ["sans_edulcorant"]
        additives_count = 0
        is_clean_label = True
        is_unflavored = True
        score = calculate_health_score(
            sweeteners=sweeteners,
            additives_count=additives_count,
            is_clean_label=is_clean_label,
            is_unflavored=is_unflavored
        )
        return {
            "sweeteners": sweeteners,
            "additives_count": additives_count,
            "health_score": score
        }

    # Default to parent product health metrics for flavored variants
    return {
        "sweeteners": parent_health_metrics.get("sweeteners", []),
        "additives_count": parent_health_metrics.get("additives_count", 0),
        "health_score": parent_health_metrics.get("health_score", 6.0)
    }

