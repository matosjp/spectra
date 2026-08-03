"""
Unit Tests for SPECTRA Primary Parameters Module (spectra.primary_parameters).
"""

import unittest
import pandas as pd
import numpy as np

from spectra.primary_parameters.spt_encoder import encode_spt, decode_spt
from spectra.primary_parameters.calibrations import EmpiricalCalibrations
from spectra.primary_parameters.photometric_engine import estimate_photometric_parameters, estimate_photometric_dataset
from spectra.primary_parameters.spectroscopic_engine import classify_t_tauri, process_spectroscopic_ews
from spectra.primary_parameters.ml_engine import PrimaryParameterMLEngine


def test_spt_encoding_decoding():
    assert encode_spt('G2V') == 52.0
    assert encode_spt('M3.5V') == 73.5
    assert decode_spt(52.0) == 'G2V'
    assert decode_spt(73.5) == 'M3.5V'
    print("test_spt_encoding_decoding: PASSED")


def test_empirical_calibrations():
    calib = EmpiricalCalibrations()
    teff_sun = calib.get_teff_from_spt('G2V')
    assert 5700 <= teff_sun <= 5850
    spt_sun = calib.get_spt_from_teff(5770)
    assert 'G2' in spt_sun
    print("test_empirical_calibrations: PASSED")


def test_photometric_engine():
    row = pd.Series({'BPmag': 15.0, 'RPmag': 14.36, 'Gmag': 14.65})
    res = estimate_photometric_parameters(row, extinction_av=0.0)
    assert 'Teff_phot' in res
    assert res['Teff_phot'] > 3000
    print("test_photometric_engine: PASSED")


def test_spectroscopic_engine():
    assert classify_t_tauri(15.0, 'M0V') == "CTTS (Classical T Tauri)"
    assert classify_t_tauri(5.0, 'M0V') == "WTTS (Weak-lined T Tauri)"
    row = pd.Series({'EW_Halpha': 25.0, 'SpT_phot': 'M3V', 'EW_Li': 0.45})
    res = process_spectroscopic_ews(row)
    assert res['T_Tauri_Class'] == "CTTS (Classical T Tauri)"
    assert res['PMS_Youth_Indicator'] is True
    print("test_spectroscopic_engine: PASSED")


def test_ml_engine():
    engine = PrimaryParameterMLEngine(algorithm="RandomForest")
    engine.train_on_calibrations()
    colors = {'BP-RP': 0.64, 'G-RP': 0.33}
    pred = engine.predict_star(colors)
    assert 'Teff_ml' in pred
    assert 5000 <= pred['Teff_ml'] <= 6500
    print("test_ml_engine: PASSED")


if __name__ == "__main__":
    test_spt_encoding_decoding()
    test_empirical_calibrations()
    test_photometric_engine()
    test_spectroscopic_engine()
    test_ml_engine()
    print("ALL 5 UNIT TESTS PASSED!")
