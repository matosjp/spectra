"""
Spectral Type Continuous Numerical Encoder & Decoder for SPECTRA.

Scale mapping:
  O0V .. O9V   = 10.0 .. 19.0
  B0V .. B9V   = 20.0 .. 29.0
  A0V .. A9V   = 30.0 .. 39.0
  F0V .. F9V   = 40.0 .. 49.0
  G0V .. G9V   = 50.0 .. 59.0
  K0V .. K9V   = 60.0 .. 69.0
  M0V .. M9V   = 70.0 .. 79.0
  L0V .. L9V   = 80.0 .. 89.0
  T0V .. T9V   = 90.0 .. 99.0
  Y0V .. Y9V   = 100.0 .. 109.0
"""

import re
from typing import Tuple, Union

SPECTRAL_CLASSES = {
    'O': 10.0,
    'B': 20.0,
    'A': 30.0,
    'F': 40.0,
    'G': 50.0,
    'K': 60.0,
    'M': 70.0,
    'L': 80.0,
    'T': 90.0,
    'Y': 100.0
}

REV_CLASSES = {int(v // 10): k for k, v in SPECTRAL_CLASSES.items()}


def encode_spt(spt_str: str) -> float:
    """
    Encodes a spectral type string (e.g. 'G2V', 'M3.5V', 'K5') into a continuous float.
    Returns 52.0 for 'G2V', 73.5 for 'M3.5V'. Returns None if unparseable.
    """
    if not spt_str or not isinstance(spt_str, str):
        return None
    
    clean = spt_str.strip().upper()
    match = re.search(r'([OBAFGKLTY])\s*([0-9]+(?:\.[0-9]+)?)', clean)
    if not match:
        return None
    
    sp_class = match.group(1)
    subclass = float(match.group(2))
    
    base_val = SPECTRAL_CLASSES.get(sp_class, 50.0)
    return base_val + subclass


def decode_spt(num_val: float, luminosity_class: str = "V") -> str:
    """
    Decodes a continuous numerical float back to a formatted Spectral Type string (e.g. 52.0 -> 'G2V').
    """
    if num_val is None or num_val != num_val:
        return "Unknown"
    
    class_idx = int(num_val // 10)
    subclass = num_val % 10
    
    sp_class = REV_CLASSES.get(class_idx, 'G')
    
    # Format subclass cleanly
    if abs(subclass - round(subclass)) < 1e-3:
        sub_str = f"{int(round(subclass))}"
    else:
        sub_str = f"{subclass:.1f}"
        
    return f"{sp_class}{sub_str}{luminosity_class}"
