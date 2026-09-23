"""
NutriDeals Protein Scorer Module
Calculates a scientific Protein Score (Score Protéique sur 10) for whey supplements
based on Protein Percentage (%), Aminogram Transparency, and Leucine Concentration (g/100g).
"""

import re
from typing import Optional, Dict, Any


def calculate_protein_score(
    protein_percentage: Optional[float],
    has_aminogram: bool,
    leucine_per_100g: Optional[float]
) -> float:
    """
    Calculates global Protein Score (Score Protéique out of 10.0).
    
    Weights:
    - 50% (5.0 pts max): Net Protein Rate (%)
    - 25% (2.5 pts max): Aminogram Transparency & Certification
    - 25% (2.5 pts max): Leucine Concentration (g/100g)
    """
    # 1. Net Protein Rate Component (5.0 pts max)
    prot_pct = protein_percentage if protein_percentage is not None and protein_percentage > 0 else 78.0
    prot_pct = min(100.0, max(0.0, prot_pct))
    
    # 90%+ protein reaches full 5.0 pts
    protein_score = min(5.0, (prot_pct / 90.0) * 5.0)

    # 2. Aminogram Transparency Component (2.5 pts max)
    # 2.5 pts if transparent/certified, 0.8 pts penalty if not specified (protects against amino spiking)
    aminogram_score = 2.5 if has_aminogram else 0.8

    # 3. Leucine Concentration Component (2.5 pts max)
    # If leucine is missing, estimate as ~10.5% of total protein percentage
    if leucine_per_100g is None or leucine_per_100g <= 0:
        estimated_leucine = prot_pct * 0.105
    else:
        estimated_leucine = leucine_per_100g
        
    # 10.0g/100g leucine reaches full 2.5 pts
    leucine_score = min(2.5, (estimated_leucine / 10.0) * 2.5)

    # Total score out of 10.0
    total_score = protein_score + aminogram_score + leucine_score
    total_score = round(min(10.0, max(1.0, total_score)), 1)
    
    return total_score


def extract_or_estimate_protein_metrics(
    title: str,
    description: str = "",
    brand: str = ""
) -> Dict[str, Any]:
    """
    Extracts or estimates protein_percentage, has_aminogram, leucine_per_100g,
    and calculates protein_score based on product metadata and description HTML.
    """
    combined_text = f"{brand} {title} {description}".lower()
    
    # --- 1. Extract Protein Percentage (%) ---
    protein_pct: Optional[float] = None
    
    # Search patterns like "85% de protéines", "85% protein", "85g de protéines pour 100g"
    pct_match = re.search(r'(\d{2}(?:[\.,]\d)?)\s*%\s*(?:de\s*)?protéine', combined_text)
    if not pct_match:
        pct_match = re.search(r'(\d{2}(?:[\.,]\d)?)\s*g\s*(?:de\s*)?protéines?\s*(?:pour\s*100g|\/100g)', combined_text)
    if not pct_match:
        pct_match = re.search(r'protéines?\s*:?\s*(\d{2}(?:[\.,]\d)?)\s*g', combined_text)
    if not pct_match:
        pct_match = re.search(r'(\d{2}(?:[\.,]\d)?)\s*%\s*d\'isolat', combined_text)
        
    if pct_match:
        try:
            parsed_pct = float(pct_match.group(1).replace(',', '.'))
            if 50.0 <= parsed_pct <= 98.0:
                protein_pct = parsed_pct
        except ValueError:
            pass

    # --- 2. Detect Aminogram Presence ---
    aminogram_keywords = [
        "aminogramme", "aminogram", "acides aminés", "amino acid", "profil aminé",
        "leucine", "bcaa", "eaa", "répartition en acides aminés", "qualité certifiée"
    ]
    has_aminogram = any(kw in combined_text for kw in aminogram_keywords)

    # Known brands with transparent complete aminograms published for all whey products
    transparent_brands = ["nutrimuscle", "esn", "biotech usa", "prozis", "nutrimea"]
    if any(tb in brand.lower() for tb in transparent_brands):
        has_aminogram = True

    # --- 3. Extract Leucine (g / 100g) ---
    leucine_per_100g: Optional[float] = None
    
    leucine_match = re.search(r'(?:l-)?leucine\s*:?\s*(\d+(?:[\.,]\d+)?)\s*g', combined_text)
    if leucine_match:
        try:
            parsed_leucine = float(leucine_match.group(1).replace(',', '.'))
            if 4.0 <= parsed_leucine <= 15.0:
                leucine_per_100g = parsed_leucine
        except ValueError:
            pass

    # --- 4. Fallback Estimates based on Product Category & Keywords ---
    title_lower = title.lower()
    
    if protein_pct is None:
        if "hydrolys" in title_lower or "native isolate" in title_lower or "isowhey" in title_lower:
            protein_pct = 89.0
        elif "isolate" in title_lower or "isolat" in title_lower:
            protein_pct = 85.0
        elif "clear whey" in title_lower or "clear isolate" in title_lower:
            protein_pct = 84.0
        elif "native" in title_lower:
            protein_pct = 82.0
        elif "concentrate" in title_lower or "concentré" in title_lower or "pure whey" in title_lower or "whey 80" in title_lower:
            protein_pct = 78.0
        else:
            protein_pct = 76.0

    if leucine_per_100g is None:
        leucine_per_100g = round(protein_pct * 0.105, 2)

    # Calculate Score
    score = calculate_protein_score(
        protein_percentage=protein_pct,
        has_aminogram=has_aminogram,
        leucine_per_100g=leucine_per_100g
    )

    return {
        "protein_percentage": round(protein_pct, 1),
        "has_aminogram": has_aminogram,
        "leucine_per_100g": round(leucine_per_100g, 2),
        "protein_score": score
    }
