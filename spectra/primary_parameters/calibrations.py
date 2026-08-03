"""
Empirical Photometric & Spectral Type Calibrations for SPECTRA.

Grid source: Pecaut & Mamajek (2013, ApJS 208, 9) + E. Mamajek Modern Dwarf Reference Table
and Belikov & Röser (2008). Covers O5V to Y0V across Gaia (G, BP, RP), 2MASS (J, H, K),
and Johnson-Cousins (U, B, V).
"""

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from .spt_encoder import encode_spt, decode_spt

# Empirical calibration table (SpT_num, Teff, logg, BP-RP, G-RP, B-V, V-K, J-H, H-K, M_V, M_G)
DWARF_GRID_DATA = [
    # SpT_num, Teff, logg, BP-RP, G-RP, B-V, V-K, J-H, H-K, M_V, M_G
    [15.0, 42000, 4.00, -0.35, -0.18, -0.32, -0.85, -0.14, -0.05, -5.70, -5.50],
    [20.0, 30000, 4.00, -0.33, -0.17, -0.30, -0.80, -0.12, -0.04, -3.25, -3.10],
    [25.0, 15400, 4.10, -0.22, -0.11, -0.17, -0.48, -0.07, -0.02, -1.20, -1.10],
    [30.0,  9520, 4.25, -0.02, -0.01,  0.00,  0.00,  0.00,  0.00,  1.42,  1.45],
    [35.0,  8200, 4.30,  0.12,  0.06,  0.15,  0.35,  0.04,  0.02,  1.95,  1.98],
    [40.0,  7200, 4.34,  0.28,  0.14,  0.30,  0.72,  0.09,  0.03,  2.70,  2.65],
    [45.0,  6540, 4.38,  0.42,  0.22,  0.44,  1.05,  0.15,  0.04,  3.50,  3.40],
    [50.0,  6030, 4.40,  0.58,  0.30,  0.58,  1.38,  0.22,  0.05,  4.40,  4.25],
    [52.0,  5770, 4.44,  0.64,  0.33,  0.63,  1.50,  0.26,  0.05,  4.82,  4.65],  # Sun
    [55.0,  5530, 4.47,  0.72,  0.37,  0.68,  1.70,  0.30,  0.06,  5.15,  4.95],
    [60.0,  5250, 4.50,  0.82,  0.42,  0.82,  1.96,  0.37,  0.07,  5.90,  5.65],
    [65.0,  4350, 4.60,  1.18,  0.59,  1.15,  2.85,  0.53,  0.10,  7.35,  6.95],
    [70.0,  3850, 4.70,  1.55,  0.78,  1.40,  3.65,  0.62,  0.15,  8.80,  8.10],
    [72.0,  3560, 4.80,  1.84,  0.92,  1.48,  4.20,  0.64,  0.18, 10.00,  9.10],
    [74.0,  3370, 4.85,  2.16,  1.08,  1.55,  4.75,  0.64,  0.22, 11.20, 10.10],
    [75.0,  3200, 4.90,  2.40,  1.20,  1.60,  5.20,  0.63,  0.25, 12.00, 10.70],
    [77.0,  2900, 5.00,  2.85,  1.45,  1.75,  6.10,  0.62,  0.30, 13.80, 12.10],
    [79.0,  2500, 5.10,  3.40,  1.75,  1.90,  7.30,  0.64,  0.38, 16.00, 14.00],
    [80.0,  2200, 5.15,  3.70,  1.90,  2.00,  8.00,  0.70,  0.45, 17.50, 15.20],
]

COLUMNS = ['SpT_num', 'Teff', 'logg', 'BP-RP', 'G-RP', 'B-V', 'V-K', 'J-H', 'H-K', 'M_V', 'M_G']


class EmpiricalCalibrations:
    """
    Empirical calibration manager providing color-Teff-SpT interpolation.
    """
    def __init__(self):
        self.df_grid = pd.DataFrame(DWARF_GRID_DATA, columns=COLUMNS)
        self._build_interpolators()

    def _build_interpolators(self):
        self.interp_teff_from_spt = interp1d(
            self.df_grid['SpT_num'], self.df_grid['Teff'], kind='cubic', fill_value='extrapolate'
        )
        self.interp_spt_from_teff = interp1d(
            self.df_grid['Teff'], self.df_grid['SpT_num'], kind='cubic', fill_value='extrapolate'
        )
        self.interp_logg_from_teff = interp1d(
            self.df_grid['Teff'], self.df_grid['logg'], kind='linear', fill_value='extrapolate'
        )

        self.color_interpolators = {}
        color_cols = ['BP-RP', 'G-RP', 'B-V', 'V-K', 'J-H', 'H-K']
        for col in color_cols:
            self.color_interpolators[col] = interp1d(
                self.df_grid[col], self.df_grid['Teff'], kind='linear', fill_value='extrapolate', bounds_error=False
            )

    def get_teff_from_spt(self, spt_str: str) -> float:
        num = encode_spt(spt_str)
        if num is None:
            return None
        return float(self.interp_teff_from_spt(num))

    def get_spt_from_teff(self, teff: float) -> str:
        if teff is None or np.isnan(teff):
            return "Unknown"
        num = float(self.interp_spt_from_teff(teff))
        num = max(10.0, min(100.0, num))
        return decode_spt(num)

    def get_teff_from_color(self, color_name: str, color_val: float) -> float:
        if color_name not in self.color_interpolators or color_val is None or np.isnan(color_val):
            return None
        teff = float(self.color_interpolators[color_name](color_val))
        return max(1500.0, min(45000.0, teff))

    def get_calibration_grid(self) -> pd.DataFrame:
        return self.df_grid.copy()
