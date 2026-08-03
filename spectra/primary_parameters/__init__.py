"""
Primary Stellar Parameters Module (`spectra.primary_parameters`).
Provides algorithms for determining Teff, Spectral Type, log g, extinction (Av),
and T Tauri star classification (CTTS/WTTS).
"""

from .spt_encoder import encode_spt, decode_spt
from .calibrations import EmpiricalCalibrations
from .photometric_engine import estimate_photometric_parameters, estimate_photometric_dataset
from .spectroscopic_engine import process_spectroscopic_ews, classify_t_tauri, estimate_spectroscopic_dataset
from .ml_engine import PrimaryParameterMLEngine

__all__ = [
    'encode_spt',
    'decode_spt',
    'EmpiricalCalibrations',
    'estimate_photometric_parameters',
    'estimate_photometric_dataset',
    'process_spectroscopic_ews',
    'classify_t_tauri',
    'estimate_spectroscopic_dataset',
    'PrimaryParameterMLEngine',
]
