"""
Photometric Primary Parameter Estimation Engine for SPECTRA.

Computes Teff, SpT, log g, and extinction Av from multi-color photometry (Gaia, 2MASS, Johnson).
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from .calibrations import EmpiricalCalibrations
from .spt_encoder import decode_spt

# Extinction ratios A_lambda / A_V (Cardelli / Gaia DR3)
EXTINCTION_RATIOS = {
    'G': 0.84,
    'BP': 1.08,
    'RP': 0.63,
    'V': 1.00,
    'B': 1.32,
    'J': 0.282,
    'H': 0.175,
    'K': 0.112,
}

calib_engine = EmpiricalCalibrations()


def derive_unreddened_colors(row: pd.Series, extinction_av: float = 0.0) -> Dict[str, float]:
    """
    Computes intrinsic unreddened colors for a star row given extinction Av.
    """
    colors = {}
    
    # Identify column names
    g_col = 'Gmag' if 'Gmag' in row else ('G' if 'G' in row else None)
    bp_col = 'BPmag' if 'BPmag' in row else ('BP' if 'BP' in row else None)
    rp_col = 'RPmag' if 'RPmag' in row else ('RP' if 'RP' in row else None)
    j_col = 'Jmag' if 'Jmag' in row else ('J' if 'J' in row else None)
    h_col = 'Hmag' if 'Hmag' in row else ('H' if 'H' in row else None)
    k_col = 'Kmag' if 'Kmag' in row else ('K' if 'K' in row else ('Ksmag' if 'Ksmag' in row else None))
    v_col = 'Vmag' if 'Vmag' in row else ('V' if 'V' in row else None)
    b_col = 'Bmag' if 'Bmag' in row else ('B' if 'B' in row else None)

    # Compute dereddened magnitudes
    def _dered(col, key):
        if col and not pd.isna(row[col]):
            return row[col] - (EXTINCTION_RATIOS.get(key, 1.0) * extinction_av)
        return None

    g_0 = _dered(g_col, 'G')
    bp_0 = _dered(bp_col, 'BP')
    rp_0 = _dered(rp_col, 'RP')
    j_0 = _dered(j_col, 'J')
    h_0 = _dered(h_col, 'H')
    k_0 = _dered(k_col, 'K')
    v_0 = _dered(v_col, 'V')
    b_0 = _dered(b_col, 'B')

    if bp_0 is not None and rp_0 is not None:
        colors['BP-RP'] = bp_0 - rp_0
    if g_0 is not None and rp_0 is not None:
        colors['G-RP'] = g_0 - rp_0
    if b_0 is not None and v_0 is not None:
        colors['B-V'] = b_0 - v_0
    if v_0 is not None and k_0 is not None:
        colors['V-K'] = v_0 - k_0
    if j_0 is not None and h_0 is not None:
        colors['J-H'] = j_0 - h_0
    if h_0 is not None and k_0 is not None:
        colors['H-K'] = h_0 - k_0

    return colors


def estimate_photometric_parameters(row: pd.Series, extinction_av: float = 0.0) -> Dict[str, Any]:
    """
    Estimates Teff, SpT, and log g for a single star using multi-band photometry.
    """
    colors = derive_unreddened_colors(row, extinction_av)
    teff_estimates = []
    
    for cname, cval in colors.items():
        t = calib_engine.get_teff_from_color(cname, cval)
        if t is not None and not np.isnan(t):
            teff_estimates.append(t)
            
    if not teff_estimates:
        return {'Teff_phot': np.nan, 'SpT_phot': 'Unknown', 'logg_phot': np.nan, 'Av_used': extinction_av}
        
    teff_mean = float(np.mean(teff_estimates))
    spt_str = calib_engine.get_spt_from_teff(teff_mean)
    logg_val = float(calib_engine.interp_logg_from_teff(teff_mean))
    
    return {
        'Teff_phot': round(teff_mean, 1),
        'SpT_phot': spt_str,
        'logg_phot': round(logg_val, 2),
        'Av_used': extinction_av
    }


def estimate_photometric_dataset(df: pd.DataFrame, extinction_av: float = 0.0) -> pd.DataFrame:
    """
    Processes a complete pandas DataFrame and appends Teff_phot, SpT_phot, logg_phot columns.
    """
    res_df = df.copy()
    teffs, spts, loggs = [], [], []
    
    for _, row in res_df.iterrows():
        est = estimate_photometric_parameters(row, extinction_av)
        teffs.append(est['Teff_phot'])
        spts.append(est['SpT_phot'])
        loggs.append(est['logg_phot'])
        
    res_df['Teff_phot'] = teffs
    res_df['SpT_phot'] = spts
    res_df['logg_phot'] = loggs
    return res_df
