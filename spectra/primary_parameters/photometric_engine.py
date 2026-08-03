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


def calculate_stu1488_luminosity(
    teff: float,
    row: pd.Series,
    extinction_av: float = 0.0,
    m_bol_sun: float = 4.755
) -> Tuple[float, float, float]:
    """
    Calculates logarithmic bolometric luminosity log10(L/Lsun), M_bol, and radius (R/Rsun)
    following Bell et al. (2014, MNRAS 444, 1157; stu1488.pdf) Section 3.2.

    Formulas from Bell et al. (2014):
      DM = 5 * log10(d_pc) - 5  (or 15 - 5 * log10(parallax_mas))
      m_0 = m_obs - A_lambda
      M_lambda = m_0 - DM
      BC_lambda = calib_engine.get_bc_g_from_teff(teff)  (or BC_V)
      M_bol = M_lambda + BC_lambda
      log10(L/Lsun) = 0.4 * (M_bol_sun - M_bol)
      log10(R/Rsun) = 0.5 * log10(L/Lsun) - 2 * log10(teff / 5770.0)
    """
    if teff is None or np.isnan(teff):
        return np.nan, np.nan, np.nan

    # 1. Distance Modulus (DM)
    d_pc = row.get('d_pc', row.get('dist_pc', row.get('distance', row.get('dist', np.nan))))
    plx_mas = row.get('parallax', row.get('plx', row.get('Plx', np.nan)))

    if not pd.isna(d_pc) and float(d_pc) > 0:
        dm = 5.0 * np.log10(float(d_pc)) - 5.0
    elif not pd.isna(plx_mas) and float(plx_mas) > 0:
        dm = 15.0 - 5.0 * np.log10(float(plx_mas))
    else:
        return np.nan, np.nan, np.nan

    # 2. Photometric band and Extinction
    g_col = row.get('Gmag', row.get('G', np.nan))
    v_col = row.get('Vmag', row.get('V', np.nan))

    if not pd.isna(g_col):
        m_obs = float(g_col)
        a_lam = EXTINCTION_RATIOS['G'] * extinction_av
        m_abs = m_obs - a_lam - dm
        bc = calib_engine.get_bc_g_from_teff(teff)
    elif not pd.isna(v_col):
        m_obs = float(v_col)
        a_lam = EXTINCTION_RATIOS['V'] * extinction_av
        m_abs = m_obs - a_lam - dm
        bc = calib_engine.get_bc_v_from_teff(teff)
    else:
        return np.nan, np.nan, np.nan

    # 3. Bolometric Absolute Magnitude & Luminosity (Bell et al. 2014, Eq. 2 & 3)
    m_bol = m_abs + bc
    log_l = 0.4 * (m_bol_sun - m_bol)

    # 4. Stellar Radius (Stefan-Boltzmann law)
    log_r = 0.5 * log_l - 2.0 * np.log10(teff / 5770.0)

    return round(float(log_l), 3), round(float(m_bol), 3), round(float(10**log_r), 3)


def estimate_photometric_parameters(row: pd.Series, extinction_av: float = 0.0) -> Dict[str, Any]:
    """
    Estimates Teff, SpT, log g, logL, Mbol, and Radius for a single star using multi-band photometry.
    """
    colors = derive_unreddened_colors(row, extinction_av)
    teff_estimates = []
    
    for cname, cval in colors.items():
        t = calib_engine.get_teff_from_color(cname, cval)
        if t is not None and not np.isnan(t):
            teff_estimates.append(t)
            
    if not teff_estimates:
        return {
            'Teff_phot': np.nan, 'SpT_phot': 'Unknown', 'logg_phot': np.nan,
            'logL_phot': np.nan, 'Mbol_phot': np.nan, 'Radius_phot': np.nan,
            'Av_used': extinction_av
        }
        
    teff_mean = float(np.mean(teff_estimates))
    spt_str = calib_engine.get_spt_from_teff(teff_mean)
    logg_val = float(calib_engine.interp_logg_from_teff(teff_mean))
    
    log_l, m_bol, radius = calculate_stu1488_luminosity(teff_mean, row, extinction_av)
    
    return {
        'Teff_phot': round(teff_mean, 1),
        'SpT_phot': spt_str,
        'logg_phot': round(logg_val, 2),
        'logL_phot': log_l,
        'Mbol_phot': m_bol,
        'Radius_phot': radius,
        'Av_used': extinction_av
    }


def estimate_photometric_dataset(df: pd.DataFrame, extinction_av: float = 0.0) -> pd.DataFrame:
    """
    Processes a complete pandas DataFrame and appends Teff_phot, SpT_phot, logg_phot, logL_phot, Mbol_phot, Radius_phot columns.
    """
    res_df = df.copy()
    teffs, spts, loggs, logls, mbols, radii = [], [], [], [], [], []
    
    for _, row in res_df.iterrows():
        est = estimate_photometric_parameters(row, extinction_av)
        teffs.append(est['Teff_phot'])
        spts.append(est['SpT_phot'])
        loggs.append(est['logg_phot'])
        logls.append(est['logL_phot'])
        mbols.append(est['Mbol_phot'])
        radii.append(est['Radius_phot'])
        
    res_df['Teff_phot'] = teffs
    res_df['SpT_phot'] = spts
    res_df['logg_phot'] = loggs
    res_df['logL_phot'] = logls
    res_df['Mbol_phot'] = mbols
    res_df['Radius_phot'] = radii
    return res_df
