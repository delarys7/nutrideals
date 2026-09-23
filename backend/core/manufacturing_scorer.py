"""
NutriDeals Manufacturing & Integrity Scorer Module
Calculates a scientific Manufacturing & Integrity Score (Score de Fabrication sur 10.0)
based on Raw Material Noble Origin (35%), Cold CFM Extraction (30%),
Quality & Anti-Doping Certifications (20%), and Lab Test Transparency (15%).
"""

import re
from typing import Optional, List, Dict, Any


def calculate_manufacturing_score(
    whey_type: str = "fromagere",
    is_grass_fed: bool = False,
    origin_country: str = "UE",
    extraction_process: str = "standard",
    chemical_free: bool = True,
    certifications: Optional[List[str]] = None,
    has_coa: bool = False,
    third_party_testing: bool = False
) -> float:
    """
    Calculates global Manufacturing & Integrity Score (Score de Fabrication out of 10.0).

    4 Weighted Components:
    1. Raw Material Noble Origin (35% / 3.5 pts max)
    2. Cold CFM Extraction & Chemical-Free (30% / 3.0 pts max)
    3. Certifications & Anti-Doping (20% / 2.0 pts max)
    4. Lab Test Transparency & CoA (15% / 1.5 pts max)
    """
    cert_list = certifications or []

    # --- 1. Raw Material Noble Origin (3.5 pts max) ---
    origin_score = 0.0
    w_type = (whey_type or "fromagere").lower()
    if "native" in w_type:
        origin_score += 1.8
    else:
        origin_score += 0.8

    if is_grass_fed:
        origin_score += 1.0
    else:
        origin_score += 0.3

    c_origin = (origin_country or "ue").lower()
    if any(k in c_origin for k in ["france", "fr", "irlande", "ireland"]):
        origin_score += 0.7
    elif any(k in c_origin for k in ["ue", "europe", "eu"]):
        origin_score += 0.5
    else:
        origin_score += 0.2

    origin_score = min(3.5, origin_score)

    # --- 2. Cold CFM Extraction & Chemical-Free (3.0 pts max) ---
    extraction_score = 0.0
    e_proc = (extraction_process or "standard").lower()
    if any(k in e_proc for k in ["cfm", "microfiltration", "flux croisé", "froid"]):
        extraction_score += 1.8
    elif "ultrafiltration" in e_proc:
        extraction_score += 1.3
    else:
        extraction_score += 0.6

    if chemical_free:
        extraction_score += 1.2
    else:
        extraction_score += 0.4

    extraction_score = min(3.0, extraction_score)

    # --- 3. Certifications & Anti-Doping (2.0 pts max) ---
    cert_score = 0.0
    for cert in cert_list:
        c_upper = cert.upper()
        if any(label in c_upper for label in ["HACCP", "ISO", "GMP", "BPF", "INFORMED", "AFNOR", "BIO", "ORGANIC"]):
            cert_score += 0.5

    # Minimum base quality certification credit for verified established brands
    if cert_score < 0.8 and cert_list:
        cert_score = 0.8

    cert_score = min(2.0, cert_score)

    # --- 4. Lab Test Transparency & CoA (1.5 pts max) ---
    transparency_score = 0.0
    transparency_score += 0.8 if has_coa else 0.2
    transparency_score += 0.7 if third_party_testing else 0.2

    transparency_score = min(1.5, transparency_score)

    # Global Score out of 10.0
    total_score = origin_score + extraction_score + cert_score + transparency_score
    total_score = round(min(10.0, max(1.0, total_score)), 1)

    return total_score


def extract_or_estimate_manufacturing_metrics(
    title: str,
    description: str = "",
    brand: str = ""
) -> Dict[str, Any]:
    """
    Extracts or estimates manufacturing parameters and computes manufacturing_score
    based on product title, brand, and description HTML.
    """
    combined = f"{brand} {title} {description}".lower()

    # 1. Whey Type
    if "native" in combined:
        whey_type = "native"
    else:
        whey_type = "fromagere"

    # 2. Grass-Fed
    is_grass_fed = any(k in combined for k in ["grass-fed", "grass fed", "pâturage", "lait de pâturage", "herbe"])
    if brand.lower() in ["nutrimuscle", "esn"]:
        is_grass_fed = True

    # 3. Origin Country
    if any(k in combined for k in ["lait français", "origine france", "fabriqué en france", "france"]):
        origin_country = "France"
    elif any(k in combined for k in ["irlande", "ireland", "lait irlandais"]):
        origin_country = "Irlande"
    elif any(k in combined for k in ["allemagne", "germany", "lait allemand"]):
        origin_country = "Allemagne"
    else:
        origin_country = "UE"

    # 4. Extraction Process
    if any(k in combined for k in ["cfm", "microfiltration à flux croisé", "microfiltré à froid", "microfiltration"]):
        extraction_process = "CFM (Microfiltration à froid)"
    elif "ultrafiltration" in combined:
        extraction_process = "Ultrafiltration"
    else:
        extraction_process = "Standard"

    # 5. Chemical-Free Treatment
    chemical_free = not any(k in combined for k in ["échange d'ions", "ion exchange", "traitement chimique"])

    # 6. Certifications
    certifications = []
    if "haccp" in combined or brand.lower() in ["nutrimuscle", "esn", "prozis", "biotech usa", "nutrimea"]:
        certifications.append("HACCP")
    if "iso" in combined or brand.lower() in ["nutrimuscle", "esn", "biotech usa"]:
        certifications.append("ISO 22000")
    if any(k in combined for k in ["informed sport", "informed-sport", "afnor", "anti-doping", "anti-dopage"]):
        certifications.append("Informed Sport / AFNOR")
    if brand.lower() == "nutrimuscle":
        certifications.append("Informed Sport")

    # 7. CoA & Third Party Testing
    has_coa = any(k in combined for k in ["certificat d'analyse", "coa", "analyse par lot", "analyses publiées"])
    if brand.lower() in ["nutrimuscle", "esn"]:
        has_coa = True

    third_party_testing = any(k in combined for k in ["laboratoire indépendant", "third party", "contrôle indépendant", "labo tierce"])
    if brand.lower() in ["nutrimuscle", "esn", "prozis"]:
        third_party_testing = True

    score = calculate_manufacturing_score(
        whey_type=whey_type,
        is_grass_fed=is_grass_fed,
        origin_country=origin_country,
        extraction_process=extraction_process,
        chemical_free=chemical_free,
        certifications=certifications,
        has_coa=has_coa,
        third_party_testing=third_party_testing
    )

    return {
        "whey_type": whey_type,
        "is_grass_fed": is_grass_fed,
        "origin_country": origin_country,
        "extraction_process": extraction_process,
        "chemical_free": chemical_free,
        "certifications": certifications,
        "has_coa": has_coa,
        "third_party_testing": third_party_testing,
        "manufacturing_score": score
    }
