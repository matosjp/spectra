"""
Synthetic Test Dataset Generator for S.P.E.C.T.R.A. Primary Parameters Module.

Generates realistic photometric (Gaia G, BP, RP; 2MASS J, H, K; Johnson V, B)
and spectroscopic (EW_Halpha, EW_Li, TiO_index) data for diverse stellar types
(Solar twin, CTTS, WTTS, M dwarf, A/F star).
"""

import pandas as pd
import numpy as np
import os

def create_synthetic_spectra_dataset() -> pd.DataFrame:
    stars_data = [
        # StarID, Gmag, BPmag, RPmag, Jmag, Hmag, Kmag, Vmag, Bmag, EW_Halpha, EW_Li, TiO_index, True_Type
        {
            'Star_ID': 'SPECTRA_001_SunLike',
            'Gmag': 14.65,
            'BPmag': 15.00,
            'RPmag': 14.36,
            'Jmag': 13.50,
            'Hmag': 13.24,
            'Kmag': 13.19,
            'Vmag': 14.82,
            'Bmag': 15.45,
            'd_pc': 100.0,
            'parallax': 10.0,
            'EW_Halpha': -1.20,  # Absorption
            'EW_Li': 0.02,
            'TiO_index': 0.98,
            'Notes': 'G2V Solar Twin (Standard)'
        },
        {
            'Star_ID': 'SPECTRA_002_CTTS',
            'Gmag': 13.40,
            'BPmag': 14.22,
            'RPmag': 12.62,
            'Jmag': 11.20,
            'Hmag': 10.56,
            'Kmag': 10.34,
            'Vmag': 13.80,
            'Bmag': 14.95,
            'd_pc': 140.0,
            'parallax': 7.14,
            'EW_Halpha': 28.50,  # Strong accretion emission
            'EW_Li': 0.52,      # Young lithium
            'TiO_index': 0.72,
            'Notes': 'M1.5V Classical T Tauri Star (CTTS)'
        },
        {
            'Star_ID': 'SPECTRA_003_WTTS',
            'Gmag': 12.85,
            'BPmag': 13.43,
            'RPmag': 12.25,
            'Jmag': 11.32,
            'Hmag': 10.89,
            'Kmag': 10.74,
            'Vmag': 13.15,
            'Bmag': 14.10,
            'd_pc': 140.0,
            'parallax': 7.14,
            'EW_Halpha': 4.20,   # Moderate chromospheric emission
            'EW_Li': 0.41,      # Young lithium
            'TiO_index': 0.85,
            'Notes': 'K7V Weak-lined T Tauri Star (WTTS)'
        },
        {
            'Star_ID': 'SPECTRA_004_MDwarf',
            'Gmag': 16.20,
            'BPmag': 17.28,
            'RPmag': 15.12,
            'Jmag': 13.25,
            'Hmag': 12.61,
            'Kmag': 12.39,
            'Vmag': 16.80,
            'Bmag': 18.25,
            'd_pc': 15.0,
            'parallax': 66.67,
            'EW_Halpha': 8.10,   # Flares/Chromosphere
            'EW_Li': 0.05,
            'TiO_index': 0.45,  # Strong TiO band
            'Notes': 'M3.5V Cool Low-Mass Dwarf'
        },
        {
            'Star_ID': 'SPECTRA_005_AStar',
            'Gmag': 10.25,
            'BPmag': 10.24,
            'RPmag': 10.25,
            'Jmag': 10.25,
            'Hmag': 10.25,
            'Kmag': 10.25,
            'Vmag': 10.25,
            'Bmag': 10.25,
            'd_pc': 60.0,
            'parallax': 16.67,
            'EW_Halpha': -14.50, # Deep Balmer absorption
            'EW_Li': 0.00,
            'TiO_index': 1.00,
            'Notes': 'A0V Hot Star'
        },
        {
            'Star_ID': 'SPECTRA_006_FStar',
            'Gmag': 11.80,
            'BPmag': 12.01,
            'RPmag': 11.59,
            'Jmag': 11.20,
            'Hmag': 11.05,
            'Kmag': 11.01,
            'Vmag': 11.95,
            'Bmag': 12.39,
            'd_pc': 50.0,
            'parallax': 20.0,
            'EW_Halpha': -6.80,
            'EW_Li': 0.12,
            'TiO_index': 0.99,
            'Notes': 'F5V Intermediate Dwarf'
        },
    ]
    
    df = pd.DataFrame(stars_data)
    return df

if __name__ == "__main__":
    df = create_synthetic_spectra_dataset()
    out_path = os.path.abspath(os.path.join(os.getcwd(), "example_primary_params_dataset.csv"))
    df.to_csv(out_path, index=False)
    print(f"Generated test dataset at: {out_path}")
    print(df[['Star_ID', 'Gmag', 'BPmag', 'RPmag', 'EW_Halpha', 'EW_Li', 'Notes']])
