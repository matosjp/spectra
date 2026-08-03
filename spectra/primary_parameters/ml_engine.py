"""
Supervised Machine Learning Engine for Primary Parameter Prediction.

Trains regressors (RandomForest, GradientBoosting, SVR, KNN) on empirical dwarf calibrations.
Predicts continuous Teff, SpT_num, and log g for target stars with partial/full colors.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.impute import SimpleImputer
from .calibrations import EmpiricalCalibrations
from .spt_encoder import decode_spt


class PrimaryParameterMLEngine:
    """
    ML Regressor Engine for predicting Teff, SpT, and log g from color vectors.
    """
    def __init__(self, algorithm: str = "RandomForest"):
        self.algorithm = algorithm
        self.calib = EmpiricalCalibrations()
        self.feature_cols = ['BP-RP', 'G-RP', 'B-V', 'V-K', 'J-H', 'H-K']
        self.imputer = SimpleImputer(strategy='mean')
        self.is_trained = False
        
        self._init_models()

    def _init_models(self):
        if self.algorithm == "RandomForest":
            self.model_teff = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model_spt = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model_logg = RandomForestRegressor(n_estimators=100, random_state=42)
        elif self.algorithm == "GradientBoosting":
            self.model_teff = GradientBoostingRegressor(random_state=42)
            self.model_spt = GradientBoostingRegressor(random_state=42)
            self.model_logg = GradientBoostingRegressor(random_state=42)
        elif self.algorithm == "KNN":
            self.model_teff = KNeighborsRegressor(n_neighbors=3)
            self.model_spt = KNeighborsRegressor(n_neighbors=3)
            self.model_logg = KNeighborsRegressor(n_neighbors=3)
        elif self.algorithm == "SVR":
            self.model_teff = SVR(C=1000.0)
            self.model_spt = SVR(C=100.0)
            self.model_logg = SVR(C=10.0)
        else:
            self.model_teff = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model_spt = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model_logg = RandomForestRegressor(n_estimators=100, random_state=42)

    def train_on_calibrations(self):
        """
        Trains ML models using the empirical dwarf calibration grid.
        """
        grid_df = self.calib.get_calibration_grid()
        X = grid_df[self.feature_cols].values
        X_imp = self.imputer.fit_transform(X)
        
        y_teff = grid_df['Teff'].values
        y_spt = grid_df['SpT_num'].values
        y_logg = grid_df['logg'].values
        
        self.model_teff.fit(X_imp, y_teff)
        self.model_spt.fit(X_imp, y_spt)
        self.model_logg.fit(X_imp, y_logg)
        self.is_trained = True

    def predict_star(self, colors_dict: Dict[str, float]) -> Dict[str, Any]:
        """
        Predicts Teff, SpT, and log g for a target star given a color dictionary.
        """
        if not self.is_trained:
            self.train_on_calibrations()
            
        vector = [colors_dict.get(c, np.nan) for c in self.feature_cols]
        X_test = np.array(vector).reshape(1, -1)
        X_test_imp = self.imputer.transform(X_test)
        
        pred_teff = float(self.model_teff.predict(X_test_imp)[0])
        pred_spt_num = float(self.model_spt.predict(X_test_imp)[0])
        pred_logg = float(self.model_logg.predict(X_test_imp)[0])
        
        return {
            'Teff_ml': round(pred_teff, 1),
            'SpT_num_ml': round(pred_spt_num, 2),
            'SpT_ml': decode_spt(pred_spt_num),
            'logg_ml': round(pred_logg, 2),
            'Algorithm': self.algorithm
        }
