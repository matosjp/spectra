"""
Spectroscopic Feature Processing & T Tauri Activity Classifier for SPECTRA.

Processes Equivalent Widths (H-alpha, Li I 6708Å, TiO, VO indices) based on:
- Millan-Valderrama et al. (2026, MNRAS)
- White & Basri (2003, ApJ 582, 1109)
"""

import numpy as np
import pandas as pd
from typing import Dict, Any
from .spt_encoder import encode_spt

# White & Basri (2003) H-alpha EW threshold (in Angstroms) for CTTS vs WTTS accretion
CTTS_HA_THRESHOLDS = {
    'K': 3.0,    # K0-K7: EW(Halpha) >= 3Å -> CTTS
    'M0-M2': 10.0, # M0-M2: EW(Halpha) >= 10Å -> CTTS
    'M3-M5': 20.0, # M3-M5: EW(Halpha) >= 20Å -> CTTS
    'M6-M9': 40.0, # M6-M9: EW(Halpha) >= 40Å -> CTTS
}


def classify_t_tauri(ew_halpha: float, spt_str: str = "M0V") -> str:
    """
    Classifies a star as CTTS (Classical T Tauri Star) or WTTS (Weak-lined T Tauri Star)
    based on H-alpha equivalent width (in emission, positive EW in Å) and Spectral Type.
    """
    if ew_halpha is None or np.isnan(ew_halpha) or ew_halpha <= 0:
        return "Field Star / Non-Accreting"
        
    spt_num = encode_spt(spt_str) if spt_str else 70.0
    if spt_num is None:
        spt_num = 70.0  # Default to M0
        
    # Determine threshold
    if spt_num < 70.0:  # K-type or earlier
        thresh = 3.0
    elif 70.0 <= spt_num < 73.0:  # M0-M2
        thresh = 10.0
    elif 73.0 <= spt_num < 76.0:  # M3-M5
        thresh = 20.0
    else:  # M6+
        thresh = 40.0
        
    if ew_halpha >= thresh:
        return "CTTS (Classical T Tauri)"
    else:
        return "WTTS (Weak-lined T Tauri)"


def process_spectroscopic_ews(row: pd.Series) -> Dict[str, Any]:
    """
    Extracts spectroscopic features from catalog columns (EW_Halpha, EW_Li, TiO_index, VO_index).
    """
    ew_ha = row.get('EW_Halpha', row.get('EW_HA', row.get('Halpha_EW', np.nan)))
    ew_li = row.get('EW_Li', row.get('EW_Li6708', row.get('Li_EW', np.nan)))
    tio_idx = row.get('TiO_index', row.get('TiO', np.nan))
    spt_str = row.get('SpT_phot', row.get('SpT', 'M0V'))
    
    ttauri_class = classify_t_tauri(ew_ha, spt_str)
    pms_indicator = (float(ew_li) > 0.1) if (not pd.isna(ew_li)) else None
    
    return {
        'EW_Halpha': ew_ha,
        'EW_Li': ew_li,
        'TiO_index': tio_idx,
        'T_Tauri_Class': ttauri_class,
        'PMS_Youth_Indicator': pms_indicator
    }


def estimate_spectroscopic_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies spectroscopic feature extraction and T Tauri classification to a dataset.
    """
    res_df = df.copy()
    classes = []
    youth = []
    
    for _, row in res_df.iterrows():
        info = process_spectroscopic_ews(row)
        classes.append(info['T_Tauri_Class'])
        youth.append(info['PMS_Youth_Indicator'])
        
    res_df['T_Tauri_Class'] = classes
    res_df['PMS_Youth_Indicator'] = youth
    return res_df
