# S.P.E.C.T.R.A. - Stellar Parameter Estimation and Calculation Tools for Research and Analysis
# Copyright (C) 2026  João Paulo Matos Dias Gomes, Maria Jaqueline Vasconcelos, Adriano Hoth Cerqueira
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact:
#   João Paulo Matos Dias Gomes — jpmdgomes.bf@gmail.com
#   Maria Jaqueline Vasconcelos — mjvasc@uesc.br
#   Adriano Hoth Cerqueira — hoth@uesc.br
#   Universidade Estadual de Santa Cruz (UESC), Ilhéus - BA, Brasil

import statsmodels.api as sm
import statsmodels.stats.api as sms
import scipy.stats as ss
import scipy.interpolate as interp

from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV, KFold, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, BayesianRidge
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor, ExtraTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.neighbors import KNeighborsRegressor

import matplotlib.pyplot as plt
import os
import missingno as msno
from ttkbootstrap.widgets import ToastNotification   
from statsmodels.graphics.tsaplots import plot_acf
import seaborn as sns

import numpy as np
import pandas as pd
import madys

from .StarLocalization import readiso
from .paths import TABLES_DIR, PLOTS_DIR


class FilterValues:
    def __init__(self):
        pass

    @staticmethod
    def filter_predict(mag, X, clust_dist):
        mag = np.array(mag, copy=True, dtype=float)
        ph = np.nan_to_num(mag)
        k = []
        for i in range(len(ph)):
            if ph[i] is not None and ph[i] != 0:
                k.append(i)
        mag[k] = -(5 * np.log10(clust_dist) - 5 - ph[k])

        row = {'mag': mag}

        ff = ~np.isnan(row['mag']) & (row['mag'] >= min(X)) & (row['mag'] <= max(X))
        df_row = pd.DataFrame(row)
        mag = df_row.loc[ff, 'mag'].values

        return mag, ff

    @staticmethod
    def filter_predict_un(mag, X):
        mag = np.array(mag, copy=True, dtype=float)
        ph = np.nan_to_num(mag)
        k = []
        for i in range(len(ph)):
            if ph[i] is not None and ph[i] != 0:
                k.append(i)
        mag[k] = ph[k]

        row = {'mag': mag}

        ff = ~np.isnan(row['mag']) & (row['mag'] >= min(X)) & (row['mag'] <= max(X))
        df_row = pd.DataFrame(row)
        mag = df_row.loc[ff, 'mag'].values

        return mag, ff

    @staticmethod
    def filter_predict_iso(teff, X):
        teff = np.array(teff, copy=True, dtype=float)
        ph = np.nan_to_num(teff)
        k = []
        for i in range(len(ph)):
            if ph[i] is not None and ph[i] != 0:
                k.append(i)
        teff[k] = ph[k]

        row = {'Teff': teff}

        ff = ~np.isnan(row['Teff']) & (row['Teff'] >= min(X)) & (row['Teff'] <= max(X))
        df_row = pd.DataFrame(row)
        teff = df_row.loc[ff, 'Teff'].values

        return teff, ff


    @staticmethod
    def filter_results(y, y_out, other=None):
        """
        Filters out invalid or missing values from the input data.

        Parameters:
            y (array-like): The input values to be filtered
            y_out (array-like): The output values to be filtered
            other (array-like, optional): Additional values to be filtered (default is None)

        Returns:
            tuple: A tuple containing the filtered values of y, y_out, and other (if provided)

        Notes:
            This function filters out rows with NaN values or values less than or equal to 0 in either y or y_out. If the other parameter is provided, it is also filtered accordingly. The filtered values are returned as a tuple.
        """
        if other is not None:
            row = {'y': y,
                   'y_out': y_out,
                   'other': other}
        else:
            row = {'y': y,
                   'y_out': y_out}

        ff = ~np.isnan(row['y']) & ~np.isnan(row['y_out'])
        df_row = pd.DataFrame(row)
        y = df_row.loc[ff, 'y'].values
        y_out = df_row.loc[ff, 'y_out'].values
        if other is not None:
            other = df_row.loc[ff, 'other'].values
        return y, y_out, other


class MagCorrector:
    """
    Class for correcting magnitudes and handling extinction.
    """

    def __init__(self):
        pass

    def non_null_indices(mag):
        """
        Get indices of non-null or non-zero magnitudes.

        Parameters:
            magnitudes (list or numpy.ndarray): List of magnitudes.

        Returns:
            list: Indices of non-null or non-zero magnitudes.
        """
        mag = np.nan_to_num(mag)
        k = []
        for i in range(len(mag)):
            if mag[i] is not None and mag[i] != 0:
                k.append(i)
        return k

    def ext_cor(self, mag, ra, dec, par, color, clust_dist, l=None, b=None, d=None, ext_map='leike', error=False):
        """
        Correct the magnitude magnitudes by the extinction, computed the reddening/extinction in a custom band,
        given the position of a star using MADYS function.

        Args:
            ra (float or numpy array, optional): Right ascension of the star(s) [deg].
            dec (float or numpy array, optional): Declination of the star(s) [deg].
            l (float or numpy array, optional): Galactic longitude of the star(s) [deg].
            b (float or numpy array, optional): Galactic latitude of the star(s) [deg].
            par (float or numpy array, optional): Parallax of the star(s) [mas].
            d (float or numpy array, optional): Distance of the star(s) [pc].
            ext_map (str, optional): Extinction map to be used: 'leike' or 'stilism'. Default: 'leike'.
            color (str, optional): Band for reddening/extinction. Default: 'B-V'.
            error (bool, optional): Compute uncertainty. Default: False.

        Returns:
            mag - mag_extinction: Magnitude correction by extinction.
        """

        mag = self.abs_cor(mag, clust_dist)
        mag_extinction = self.ext(ra=ra, dec=dec, par=par, color=color)
        return mag - mag_extinction

    def ext(self, ra, dec, par, color):
        """
        Computes the reddening/extinction in a custom band, given the position of a star using MADYS function.

        Args:
            ra (float or numpy array, optional): Right ascension of the star(s) [deg].
            dec (float or numpy array, optional): Declination of the star(s) [deg].
            l (float or numpy array, optional): Galactic longitude of the star(s) [deg].
            b (float or numpy array, optional): Galactic latitude of the star(s) [deg].
            par (float or numpy array, optional): Parallax of the star(s) [mas].
            d (float or numpy array, optional): Distance of the star(s) [pc].
            ext_map (str, optional): Extinction map to be used: 'leike' or 'stilism'. Default: 'leike'.
            color (str, optional): Band for reddening/extinction. Default: 'B-V'.
            error (bool, optional): Compute uncertainty. Default: False.

        Returns:
            ext (float or numpy array): Best estimate of reddening/extinction for each star.
            err (float or numpy array): Uncertainty on the estimate if error=True.
        """
        mag_extinction = madys.SampleObject.interstellar_ext(ra=ra, dec=dec, par=par, color=color)
        return mag_extinction

    def abs_cor(mag, clust_dist):
        """
        Converts apparent magnitudes into absolute magnitudes.

        Args:
            app_mag (float, list, or numpy array): Input apparent magnitude.
            clust_dist (float): Cluster distance.

        Returns:
            abs_mag (float, list, or numpy array): Absolute magnitude(s).
        """
        ph = np.nan_to_num(mag)
        k = []
        for i in range(len(ph)):
            if ph[i] is not None and ph[i] != 0:
                k.append(i)
        mag[k] = -(5 * np.log10(clust_dist) - 5 - ph[k])
        return mag, k


def interpolmass(primarydataset, model):
    """
    Bayesian Isochrone Parameter Estimator (Mass, Age, and 1-sigma uncertainties).
    Uses full 2D likelihood evaluation over the HR diagram and a Salpeter/Kroupa IMF prior.
    """
    teffs = np.array(primarydataset['Teff'], copy=True, dtype=float)
    if 'logL' in primarydataset:
        logls = np.array(primarydataset['logL'], copy=True, dtype=float)
        # Se os valores forem todos positivos e a mediana > 0.05 (Luminosidade linear L em vez de log10(L)), converte para log10(L)
        valid_l = logls[~np.isnan(logls)]
        if len(valid_l) > 0 and np.all(valid_l > 0) and np.median(valid_l) > 0.05:
            logls = np.log10(np.maximum(1e-10, logls))
    elif 'L' in primarydataset:
        logls = np.log10(np.maximum(1e-10, np.array(primarydataset['L'], copy=True, dtype=float)))
    else:
        raise KeyError("Coluna de luminosidade ('logL' ou 'L') não encontrada.")

    e_teffs = np.array(primarydataset['e_Teff'], copy=True, dtype=float) if 'e_Teff' in primarydataset else np.full(len(teffs), np.nan)
    e_logls = np.array(primarydataset['e_logL'], copy=True, dtype=float) if 'e_logL' in primarydataset else np.full(len(logls), np.nan)

    alldataiso = readiso(model)

    if model == "Siess 2000":
        at = 3  # Teff
        al = 1  # L (linear)
        am = 4  # Mass
        ageiso = np.array([1.e4, 5.e4, 2.e5, 5.e5, 2.e6, 5.e6, 1.e7, 3e7, 6e7, 1e8]) / 1e6
        is_logl_in_table = False
    elif model == "BHAC15":
        at = 1  # Teff
        al = 2  # logL
        am = 0  # Mass
        ageiso = np.array([1.e6, 2.e6, 5.e6, 1.e7, 2.e7, 5.e7, 8.e7, 1.e8, 1.2e8, 2e8]) / 1e6
        is_logl_in_table = True
    else:
        raise ValueError(f"Modelo desconhecido: {model}")

    log_ageiso = np.log10(ageiso)

    # 1. Extração dos nós válidos da grade do modelo
    points = []
    teff_list = []
    logl_list = []

    for i in range(len(ageiso)):
        log_a = log_ageiso[i]
        for j in range(alldataiso.shape[2]):
            t = alldataiso[i, at, j]
            l_val = alldataiso[i, al, j]
            m = alldataiso[i, am, j]

            if t > 0 and not np.isnan(t) and not np.isnan(l_val) and m > 0:
                l_log = l_val if is_logl_in_table else (np.log10(l_val) if l_val > 0 else np.nan)
                if not np.isnan(l_log):
                    points.append((m, log_a))
                    teff_list.append(t)
                    logl_list.append(l_log)

    points = np.array(points)
    teff_arr = np.array(teff_list)
    logl_arr = np.array(logl_list)

    # 2. Construção dos Interpoladores 2D na malha (Massa, log10(Idade))
    interp_teff = interp.LinearNDInterpolator(points, teff_arr)
    interp_logl = interp.LinearNDInterpolator(points, logl_arr)
    near_teff = interp.NearestNDInterpolator(points, teff_arr)
    near_logl = interp.NearestNDInterpolator(points, logl_arr)

    # 3. Grade de Avaliação Bayesiana (150x150)
    m_min, m_max = points[:, 0].min(), points[:, 0].max()
    log_a_min, log_a_max = points[:, 1].min(), points[:, 1].max()

    m_grid = np.linspace(m_min, m_max, 150)
    log_a_grid = np.linspace(log_a_min, log_a_max, 150)
    M_mesh, A_mesh = np.meshgrid(m_grid, log_a_grid)
    mesh_points = np.column_stack([M_mesh.ravel(), A_mesh.ravel()])

    t_pred = interp_teff(mesh_points).reshape(M_mesh.shape)
    l_pred = interp_logl(mesh_points).reshape(M_mesh.shape)

    # Máscara dos pontos válidos estritamente dentro da envoltória convexa (convex hull) dos dados do modelo
    valid_hull = ~np.isnan(t_pred) & ~np.isnan(l_pred)

    # Prior Salpeter / Kroupa IMF
    imf_prior = np.where(M_mesh <= 0.5, M_mesh**(-1.35), M_mesh**(-2.35))

    calc_masses = []
    calc_ages = []
    calc_mass_errs = []
    calc_age_errs = []

    for x in range(len(teffs)):
        t_obs = teffs[x]
        l_obs = logls[x]

        if np.isnan(t_obs) or np.isnan(l_obs) or t_obs <= 0:
            calc_masses.append(np.nan)
            calc_ages.append(np.nan)
            calc_mass_errs.append(np.nan)
            calc_age_errs.append(np.nan)
            continue

        sig_t = e_teffs[x] if not np.isnan(e_teffs[x]) and e_teffs[x] > 0 else max(50.0, 0.03 * t_obs)
        sig_l = e_logls[x] if not np.isnan(e_logls[x]) and e_logls[x] > 0 else 0.08

        # Se o ponto estiver ligeiramente fora do convex hull, avalia o vizinho mais próximo na borda
        active_mask = valid_hull
        t_eval = t_pred
        l_eval = l_pred

        if not np.any(active_mask):
            t_eval = near_teff(mesh_points).reshape(M_mesh.shape)
            l_eval = near_logl(mesh_points).reshape(M_mesh.shape)
            active_mask = np.ones(M_mesh.shape, dtype=bool)

        chi2 = np.full(M_mesh.shape, np.inf)
        chi2[active_mask] = ((t_eval[active_mask] - t_obs) / sig_t)**2 + ((l_eval[active_mask] - l_obs) / sig_l)**2

        min_chi2 = np.min(chi2[active_mask]) if np.any(active_mask) else 0.0

        log_lik = np.full(M_mesh.shape, -np.inf)
        log_lik[active_mask] = -0.5 * (chi2[active_mask] - min_chi2)

        lik = np.zeros(M_mesh.shape)
        lik[active_mask] = np.exp(log_lik[active_mask])

        post = lik * imf_prior
        z = np.sum(post)

        if z <= 0 or np.isnan(z):
            calc_masses.append(np.nan)
            calc_ages.append(np.nan)
            calc_mass_errs.append(np.nan)
            calc_age_errs.append(np.nan)
            continue

        post_norm = post / z

        # Momentos Posteriores
        mean_m = np.sum(M_mesh * post_norm)
        var_m = np.sum((M_mesh - mean_m)**2 * post_norm)
        std_m = np.sqrt(max(0.0, var_m))

        mean_log_a = np.sum(A_mesh * post_norm)
        var_log_a = np.sum((A_mesh - mean_log_a)**2 * post_norm)
        std_log_a = np.sqrt(max(0.0, var_log_a))

        mean_age = 10**mean_log_a
        std_age = mean_age * np.log(10) * std_log_a

        calc_masses.append(float(mean_m))
        calc_ages.append(float(mean_age))
        calc_mass_errs.append(float(std_m))
        calc_age_errs.append(float(std_age))

    return calc_masses, calc_ages, calc_mass_errs, calc_age_errs

def fit(X, y, model_name):
    """
    Fits a machine learning model to the input data and performs hyperparameter tuning using GridSearchCV.

    Parameters:
        X (array-like): The input features
        y (array-like): The target variable
        model_name (str): The name of the machine learning model to use (e.g. 'Bayesian Regression', 'Linear Regression', etc.)

    Returns:
        GridSearchCV: A GridSearchCV object containing the best-performing model and its hyperparameters

    Notes:
        This function creates a pipeline with a StandardScaler and the specified machine learning model, and then performs hyperparameter tuning using GridSearchCV. The best-performing model is returned.
    """
    if model_name == 'Bayesian Regression':
        model = BayesianRidge()
        param_grid = {'model__alpha_1': [1e-6, 1e-5, 1e-4, 1e-3],
                      'model__alpha_2': [1e-6, 1e-5, 1e-4, 1e-3],
                      'model__lambda_1': [1e-6, 1e-5, 1e-4, 1e-3],
                      'model__lambda_2': [1e-6, 1e-5, 1e-4, 1e-3],
                      'model__compute_score': [True, False],
                      'model__fit_intercept': [True, False]}
    elif model_name == 'Linear Regression':
        model = LinearRegression()
        param_grid = {'model__fit_intercept': [True, False],
                      'model__positive': [True, False]}
    elif model_name == 'ElasticNet Regression':
        model = ElasticNet()
        param_grid = {'model__alpha': [0.01, 0.1, 0.5, 1.0],
                      'model__l1_ratio': [0.01, 0.1, 0.5, 1.0],
                      'model__fit_intercept': [True, False],
                      'model__positive': [True, False],
                      'model__precompute': [True, False],
                      'model__selection': ['cyclic', 'random']}

    elif model_name == 'Support Vector Regressor':
        model = SVR()
        param_grid = {'model__C': [0.01, 0.1, 1, 10],
                      'model__epsilon': [0.01, 0.1, 0.5, 1],
                      'model__kernel': ['linear', 'rbf', 'sigmoid']}

    elif model_name == 'Decision Tree Regressor':
        model = DecisionTreeRegressor()
        param_grid = {'model__max_depth': [1, 2, 7, 12, 15, 20],
                      'model__min_samples_split': [2, 7, 10],
                      'model__min_samples_leaf': [2, 7, 10]}

    elif model_name == 'Random Forest Regressor':
        model = RandomForestRegressor()
        param_grid = {'model__n_estimators': [100],
                      'model__max_depth': [1, 2, 7, 12, 15, 20],
                      'model__min_samples_split': [2, 7, 10],
                      'model__min_samples_leaf': [2, 7, 10]}

    elif model_name == 'Gradient Boosting Regressor':
        model = GradientBoostingRegressor()
        param_grid = {'model__loss': ['squared_error'],
                      'model__learning_rate': [0.01, 0.1, 0.5, 1.],
                      'model__n_estimators': [100],
                      'model__subsample': [0.7, 0.8, 0.9, 1.0],
                      'model__max_depth': [1, 2, 7, 12, 15, 20]}

    elif model_name == 'AdaBoost Regressor':
        model = AdaBoostRegressor()
        param_grid = {'model__n_estimators': [100],
                      'model__learning_rate': [0.01, 0.1, 0.5, 1.0],
                      'model__loss': ['square']}

    elif model_name == 'KNeighbors Regressor':
        model = KNeighborsRegressor()
        param_grid = {'model__n_neighbors': [3, 5, 7, 9, 12],
                      'model__weights': ['uniform', 'distance']}
    else:
        raise ValueError(f"Unknown model name: {model_name}")

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', model)
    ])

    grid_search = GridSearchCV(pipeline, param_grid, cv=min(len(X), 3), scoring='neg_mean_squared_error', n_jobs=-1)
    grid_search.fit(X, y)
    return grid_search


def calculate_aic(n, mse, k):
    """
    Calculates the Akaike information criterion (AIC) for a given model.

    Parameters:
        n (int): The number of samples
        mse (float): The mean squared error of the model
        k (int): The number of parameters in the model

    Returns:
        float: The AIC value

    Notes:
        The AIC is a measure of the relative quality of a model for a given set of data. It takes into account both the goodness of fit and the complexity of the model.
    """
    aic = n * np.log(mse) + 2 * k
    return aic


def normalize_metrics(metrics):
    """
    Normalizes a set of metrics to have values between 0 and 1.

    Parameters:
        metrics (dict): A dictionary of metrics, where each key is a metric name and each value is a list of metric values

    Returns:
        dict: A dictionary of normalized metrics, where each key is a metric name and each value is a list of normalized metric values

    Notes:
        This function normalizes each metric by subtracting the minimum value and dividing by the range of values. This allows for fair comparison of metrics with different scales.
    """
    normalized_metrics = {}
    for metric, values in metrics.items():
        max_val = np.max(values)
        min_val = np.min(values)
        normalized_metrics[metric] = [(val - min_val) / (max_val - min_val) for val in values]
    return normalized_metrics


def weighted_score(normalized_metrics):
    """
    Calculates a weighted score based on a set of normalized metrics.

    Parameters:
        normalized_metrics (dict): A dictionary of normalized metrics, where each key is a metric name and each value is a list of normalized metric values

    Returns:
        list: A list of weighted scores, where each score is a weighted sum of the normalized metrics

    Notes:
        This function uses a set of predefined weights to calculate a weighted score for each set of metrics. The weights are: RMSE (0.25), MAE (0.25), R2 (0.25), and AIC (0.25).
    """
    weights = {
        'rmse': 1.,
        'mae': 1.,
        'r2': 1.,
        'aic': 1.,
    }
    total_scores = []
    for i in range(len(normalized_metrics['rmse'])):
        score = ((weights['rmse'] * normalized_metrics['rmse'][i] +
                  weights['mae'] * normalized_metrics['mae'][i] +
                  weights['r2'] * (1 - normalized_metrics['r2'][i]) +  # Invert R2 because higher is better
                  weights['aic'] * normalized_metrics['aic'][i]))

        total_scores.append(score)
    return total_scores


def RegressionReport(X, y):
    """
    Generates a comprehensive report for regression models.

    Parameters:
        X (pd.DataFrame): The feature data
        y (pd.Series): The target variable

    Returns:
        tuple: A tuple containing the best model, the trained model object, and a report dataframe

    Notes:
        This function performs the following steps:
        1. Splits the data into training and testing sets
        2. Trains and evaluates multiple regression models using grid search
        3. Calculates various metrics (RMSE, MAE, R2, AIC) for each model
        4. Normalizes the metrics and calculates a weighted score for each model
        5. Selects the best model based on the weighted score
        6. Generates a visual report with plots for actual vs predicted values, residuals distribution, skedasticity, and influence plot
        7. Saves the report to a CSV file and returns the best model, trained model object, and report dataframe
    """
    models = {
        'Bayesian Regression': BayesianRidge(),
        'Linear Regression': LinearRegression(),
        'ElasticNet Regression': ElasticNet(),
        'Support Vector Regressor': SVR(),
        'Decision Tree Regressor': DecisionTreeRegressor(),
        'Random Forest Regressor': RandomForestRegressor(),
        'Gradient Boosting Regressor': GradientBoostingRegressor(),
        'AdaBoost Regressor': AdaBoostRegressor(),
        'KNeighbors Regressor': KNeighborsRegressor()
    }
    # Split the data

    report = []
    metrics = {'rmse': [], 'mae': [], 'r2': [], 'aic': []}
    if len(X)>3:
        X_train, X_test, y_train, y_test = train_test_split(X,
                                                            y,
                                                            test_size=0.1,
                                                            random_state=42)

        for model_name in models.keys():
            grid_search = fit(X_train, y_train, model_name)
            best_model = grid_search.best_estimator_

            y_pred = best_model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            n = len(y_test)
            k = best_model.named_steps['model'].coef_.shape[0] if hasattr(best_model.named_steps['model'],
                                                                          'coef_') else len(best_model.named_steps['model'].get_params())
            aic = calculate_aic(n, mse, k)

            metrics['rmse'].append(rmse)
            metrics['mae'].append(mae)
            metrics['r2'].append(r2)
            metrics['aic'].append(aic)

            report.append({
                'Model': model_name,
                'RMSE': rmse,
                'MAE': mae,
                'R2': r2,
                'AIC': aic,
                'Best Params': grid_search.best_params_
            })

        # Normalize metrics
        normalized_metrics = normalize_metrics(metrics)

        # Calculate weighted scores
        scores = weighted_score(normalized_metrics)

        for i, model_report in enumerate(report):
            model_report['Score'] = scores[i]

        report_df = pd.DataFrame(report)
        report = report_df
        report.to_csv(os.path.join(TABLES_DIR, 'Regression_model_report.csv'), index=None)
        # Return the best model based on the weighted score
        best_model = report_df.loc[report_df['Score'].idxmin()]['Model']
        model = fit(X, y, best_model).best_estimator_

        ols = sm.OLS(y_test, sm.add_constant(X_test)).fit()
        res = ols.resid
        sth = ols.get_influence().summary_frame()
        st_res = sth['student_resid']
        lev = sth['hat_diag']
        rsqueared = ols.rsquared

        pred_test = model.predict(X_test)

        xyrange = np.linspace(min(y), max(y), 14)
        xyrange = [round(x, 1) for x in xyrange]

        plt.figure(figsize=(15, 15),
                   tight_layout=True)

        # Actual vs Predicted
        plt.subplot(2, 2, 1)
        plt.scatter(y_test, pred_test, facecolor='#9370db', label='Test Prediction')
        plt.plot([y_test.min(), y_test.max()],
                 [y_test.min(), y_test.max()],
                 color='black',
                 linestyle='dashed',
                 lw=2, label='Ideal')
        plt.xlabel('Actual Target Values')
        plt.ylabel('Predicted Target Values')
        if rsqueared <= 0.75:
            corr = 'Weakly correlated'
        else:
            corr = 'Strongly correlated'
        plt.title(fr'{best_model} ({corr}, R$^2$={rsqueared:.2f})')
        plt.legend(loc='best')
        plt.tick_params(direction='in')
        plt.xticks(xyrange)
        plt.yticks(xyrange)
        plt.grid(True)

        # Residuals distribution (normality)
        plt.subplot(2, 2, 2)
        norm_p_value = ss.jarque_bera(res).pvalue
        if norm_p_value <= 0.05:
            norm = 'Not normal'
        else:
            norm = 'Normal'
        sns.histplot(res,
                     kde=True,
                     color='#9370db')
        plt.title(f'Normality of residuals ({norm}, P-value={norm_p_value:.2f})')
        plt.xlabel('Residuals')
        plt.grid(True)
        plt.tick_params(direction='in')

        plt.subplot(2, 2, 3)
        # Skedasticity (Residuals vs Predicted)
        line = sm.OLS(abs(res), sm.add_constant(pred_test)).fit()
        test_pred = line.predict(sm.add_constant(pred_test))
        ske_p_value = sms.het_breuschpagan(res, ols.model.exog)[1]
        if ske_p_value <= 0.05:
            ske = 'Heteroskedastic'
        else:
            ske = 'Homoskedastic'
        plt.scatter(pred_test,
                    abs(res),
                    facecolor='#9370db')
        plt.axhline(y=test_pred[0],
                    color='k',
                    linestyle='dashed',
                    label='Symmetry line')
        plt.xlabel('Predicted Values of Validation Data')
        plt.ylabel('Residuals')
        plt.title(f'Skedasticity of Residuals ({ske}, P-value={ske_p_value:.2f})')
        plt.grid(True)
        plt.xticks(xyrange)
        plt.legend(loc='best')
        plt.tick_params(direction='in')

        plt.subplot(2, 2, 4)

        # add cook's distance to plot
        cutoff = 4 / (len(pred_test) - 2)

        d_curves = ResultsAnalyzer.calculate_theoretical_curves(fixed_cooks_distance_values=[cutoff])

        d1x = d_curves[cutoff]['leverage']
        d1y = d_curves[cutoff]['studentized_residuals']

        plt.plot(d1x, d1y, marker='none', color='#c3121e',
                 linestyle='-.', label=r"D$_{crit}$")
        plt.plot(d1x, -d1y, marker='none', color='#c3121e',
                 linestyle='-.')

        plt.scatter(lev, st_res, facecolor='#9370db')
        plt.axhline(-3, color='k', linestyle=':')
        plt.axhline(3, color='k', linestyle=':', label=r'$\hat{\sigma}_{crit}$')
        plt.axhline(0, color='grey', linestyle='--')
        plt.legend(loc='best')
        plt.grid(True)
        plt.xlabel(r'Leverage ($\hat{h}$)')
        plt.ylabel(r'Studentinized Residuals ($\hat{\sigma}$)')
        plt.title('Influence Plot')
        plt.xlim([min(lev), max(lev)])
        plt.ylim(-3.5, 3.5)

        plt.savefig(os.path.join(PLOTS_DIR, '_visual_report.png'), dpi=300)

        return best_model, model, report
    else:
        # Not enough samples to fit/validate a model. No Tk widgets are
        # created here (this function may run on a background thread) —
        # the caller is responsible for surfacing this to the user.
        return None, None, None


class ResultsAnalyzer:

    def __init__(self, calculated_masses, ctrl_masses):
        self.y_out = calculated_masses
        self.y = ctrl_masses

    @staticmethod
    def calculate_theoretical_curves(fixed_cooks_distance_values, num_params=1):
        """
        Calculate theoretical curves for fixed values of Cook's distance.

        Args:
            leverage (array-like): Leverage values for each observation.
            studentized_residuals (array-like): Studentized residuals for each observation.
            fixed_cooks_distance_values (array-like): Fixed values of Cook's distance.
            num_params (int): Number of parameters in the model.

        Returns:
            dict: Dictionary containing the calculated theoretical curves for each fixed Cook's distance value.
        """
        theoretical_curves = {}

        for fixed_cook_distance in fixed_cooks_distance_values:
            # Calculate leverage for each observation
            leverage_values = np.linspace(0.001, 0.999, 1000)

            # Calculate the corresponding studentized residuals using the formula

            studentized_residuals_values = fixed_cook_distance / (leverage_values * (1 - leverage_values) / num_params)
            studentized_residuals_values = np.sqrt(studentized_residuals_values)

            theoretical_curves[fixed_cook_distance] = {
                'leverage': leverage_values,
                'studentized_residuals': studentized_residuals_values
            }

        return theoretical_curves

    @staticmethod
    def trend_line(self, x, y, d=4):

        # Perform linear regression to determine the trend line
        z = np.polyfit(x, y, d)
        p = np.poly1d(z)
        return p(sorted(x))

    def reg_diag(self, save_file=None):
        ph = FilterValues.filter_results(self.y, self.y_out)
        y = ph[0]
        y_out = ph[1]
        ols = sm.OLS(y, sm.add_constant(y_out)).fit()
        res = ols.resid
        sth = ols.get_influence().summary_frame()
        st_res = sth['student_resid']
        lev = sth['hat_diag']
        std_residuals = sth['standard_resid']
        cooks_d = sth['cooks_d']

        if len(y_out) == len(res):
            res = ols.resid
        else:
            res = y_out - y

        # Create a figure with subplots for diagnostic plots
        fig = plt.figure(tight_layout=True, figsize=(24, 16))

        # Residuals vs Leverage (Influence Plot)
        plt.subplot(2, 2, 4)

        # add cook's distance to plot
        cutoff = 4 / (len(y_out) - 2)

        d_curves = self.calculate_theoretical_curves(fixed_cooks_distance_values=[cutoff])

        d1x = d_curves[cutoff]['leverage']
        d1y = d_curves[cutoff]['studentized_residuals']

        plt.plot(d1x, d1y, marker='none', color='#c3121e',
                 linestyle='-.', label=r"D$_{crit}$")
        plt.plot(d1x, -d1y, marker='none', color='#c3121e',
                 linestyle='-.')

        plt.scatter(lev, st_res, color='#7570b3')
        plt.axhline(-3, color='#e7298a', linestyle=':')
        plt.axhline(3, color='#e7298a', linestyle=':')
        plt.axhline(0, color='grey', linestyle='--')
        plt.axvline(0, color='grey', linestyle='--')
        plt.legend(loc='best')
        plt.xlabel(r'Leverage ($\hat{h}$)')
        plt.ylabel('Studentinized Residuals')
        plt.title('Influence Plot')
        plt.xlim([min(lev), max(lev)])
        plt.ylim(-3.5, 3.5)

        # Residuals vs Fitted values (Regression Plot)
        plt.subplot(2, 2, 1)

        plt.scatter(y_out, res, color='#7570b3')
        plt.axhline(0, color='grey', linestyle='--')
        plt.axvline(0, color='grey', linestyle='--')
        plt.xlabel('Fitted Values')
        plt.ylabel('Residuals')
        plt.title('Residuals vs Fitted Values')

        if std_residuals.size <= 500:
            # Shapiro-Wilk test for normality
            shapiro_test_stat, norm_p_value = ss.shapiro(std_residuals)
            norm = 'Shapiro-Wilk'
        else:
            # Jarque-Bera test for normality
            norm_p_value = ss.jarque_bera(std_residuals).pvalue
            norm = 'Jarque-Bera'

        plt.subplot(2, 2, 2)
        x = ss.norm.rvs(0, size=len(std_residuals))
        q2 = sm.ProbPlot(x).sample_quantiles
        q1 = sm.ProbPlot(std_residuals).sample_quantiles
        plt.plot(q2, q1, marker='o', alpha=0.5,
                 markersize=10, linestyle='', color='#7570b3')
        plt.axline((-2, -2), slope=1, color='black', linestyle='dashed')
        plt.xlabel('Theoretical Quantiles')
        plt.ylabel('Standardized Residuals')
        plt.title(f'Normal Q-Q Plot ({norm} P-value={norm_p_value:.4f})')

        # Scale-Location Plot (Square root of standardized residuals vs Fitted values)
        plt.subplot(2, 2, 3)

        sqrt_std_residuals = np.sqrt(abs(std_residuals))

        plt.scatter(y_out, sqrt_std_residuals, color='#7570b3')
        plt.axhline(0, color='grey', linestyle='--')
        plt.axvline(0, color='grey', linestyle='--')
        plt.axhline(np.sqrt(3), color='#e7298a', linestyle=':')
        plt.xlabel('Fitted Values')
        plt.ylabel(r'$\sqrt{Standardized~ Residuals}$')
        plt.title('Scale-Location Plot')
        plt.grid(True)
        plt.tick_params(direction='in')

        if save_file:
            plt.savefig(os.path.join(PLOTS_DIR, '_statistical_results.png'), dpi=300)
        elif isinstance(save_file, str):
            plt.savefig(save_file, dpi=300)
        plt.close(fig)
        plt.close()


class ResultDisplay:
    """
    Displays and plots the results of mass prediction models.

    Attributes:
        x (array-like): The input values (e.g. magnitudes or effective temperatures)
        y (array-like): The predicted masses
        yerr (array-like): The errors associated with the predicted masses
        method (str): The method used for prediction ('MMR', 'ISO', or 'MOD')
        feature_name (str, optional): Name of feature for x-axis label.
        target_name (str, optional): Name of target variable.

    Methods:
        res_plot(save_file=False): Plots the results and saves the figure to a file if specified.
    """
    def __init__(self, x, y, yerr, method, feature_name=None, target_name=None):
        self.x = x
        self.y = y
        self.yerr = yerr
        self.method = method
        self.feature_name = feature_name
        self.target_name = target_name

    def res_plot(self, save_file=False):
        """
        Plots the results of prediction models.
        """
        x, y, yerr = FilterValues.filter_results(self.x, self.y, self.yerr)
        fig = plt.figure(figsize=(12, 8))
        label_text = f"Calculated {self.target_name}" if self.target_name else "Calculated values"
        plt.plot(x, y, marker="^", color='#7570b3', alpha=0.6,
                 label=label_text, linestyle='')
        plt.errorbar(x, y, yerr=yerr, capsize=5, fmt='^', ecolor='gray', alpha=0.6)

        if self.method == 'MMR':
            plt.xlabel('Magnitude (mag)')
            plt.title('Mass-Magnitude Relationship Results')
            if len(x) > 0:
                plt.xlim(np.min(x) - 0.05, np.max(x) + 0.05)

        elif self.method == 'ISO':
            plt.xlabel('Effective Temperature (K)')
            if len(x) > 0:
                plt.xlim(np.min(x) - 50, np.max(x) + 50)
            plt.gca().invert_xaxis()
            targ_title = self.target_name if self.target_name else 'Mass'
            plt.title(f'Isochrone Fitting Results ({targ_title})')

        else:
            xlabel = self.feature_name if self.feature_name else 'Observed / Feature'
            targ_label = self.target_name if self.target_name else 'Target'
            plt.xlabel(xlabel)
            plt.title(f'Mathematical Modeling Results ({targ_label})')
            if len(x) > 0:
                x_min, x_max = np.min(x), np.max(x)
                margin = (x_max - x_min) * 0.05 if x_max != x_min else 1.0
                plt.xlim(x_min - margin, x_max + margin)

        ylabel = f'Calculated {self.target_name}' if self.target_name else r'Predicted Values'
        plt.ylabel(ylabel)
        plt.legend(loc="best")

        plt.grid(True)
        plt.tight_layout()
        if len(y) > 0 and np.max(y) > 0:
            plt.ylim(0, np.max(y) * 1.15)
        else:
            plt.ylim(0, 1.45)
        plt.tick_params(axis='both', which='major', labelsize=10)
        plt.tick_params(direction='in')

        if save_file is True:
            plt.savefig(
                os.path.join(PLOTS_DIR, '_results_display.png'), dpi=300)
        elif isinstance(save_file, str):
            plt.savefig(save_file, dpi=300)
        plt.close(fig)
        plt.close()

class MathModels:
    """
    A class for mathematical modeling and feature selection.

    This class provides methods for selecting the most important features from a dataset and generating correlation plots.

    Attributes:
        None

    Methods:
        select_features(table_data, target): Selects the most important features from a dataset using correlation analysis and random forest feature importance.
        correlation_plot(data): Generates a correlation plot for a given dataset, including a missing data matrix and a correlation matrix.
    """
    def __init__(self):
        pass
    @staticmethod
    def correlation_plot(data):
        """
       Generates a correlation plot for a given dataset, including a missing data matrix and a correlation matrix.

       Parameters:
           data (pd.DataFrame): The input dataset.

       Returns:
           None

       Notes:
           This function performs the following steps:
           1. Filters the input data to exclude non-numeric columns.
           2. Creates a heatmap of missing data in the filtered dataset.
           3. Drops rows with all missing values from the filtered dataset.
           4. Computes the Pearson correlation matrix of the filtered dataset.
           5. Creates a heatmap of the correlation matrix.
           6. Saves the plot to a file named '_correlation_report.png' in the current working directory.

       The resulting plot consists of two subplots:
           - Top subplot: Missing data matrix, where green cells indicate missing values.
           - Bottom subplot: Correlation matrix, where purple cells indicate strong positive correlations and white cells indicate weak or negative correlations.
        """

        data_filtered = data.select_dtypes(exclude='object')
        plt.figure(figsize=(8, 12),
                   tight_layout=True)

        plt.subplot(2,1,1)
        sns.heatmap(data_filtered.isna().transpose(),
                    cmap="Greens",
                    cbar_kws={'label': 'Missing Data'})
        plt.tick_params(direction='in')
        plt.title('Missing Data Matrix')

        plt.subplot(2,1,2)
        data_filtered = data_filtered.dropna(axis=0, how='all')
        corr_matrix = data_filtered.corr()
        sns.heatmap(corr_matrix,
                    annot=False,
                    cmap='Purples',
                    cbar_kws={'label': 'Pearson Correlation'},
                    linewidths=1.)
        plt.tick_params(direction='in')
        plt.title('Correlation Matrix')


        plt.savefig(os.path.join(PLOTS_DIR, '_correlation_report.png'), dpi=300)


    @staticmethod
    def select_features(table_data, target):
        """
        Selects the most important features from a dataset using correlation analysis and random forest feature importance.

        Parameters:
            table_data (pd.DataFrame): The input dataset containing features and target variable.
            target (str): The name of the target variable in the dataset.

        Returns:
            list: A list of selected feature names with importance greater than or equal to 0.1.

        Notes:
            This function performs the following steps:
            1. Computes the correlation matrix of the input dataset.
            2. Selects features with absolute correlation greater than or equal to 0.75.
            3. Splits the data into training and testing sets.
            4. Scales the data using StandardScaler.
            5. Trains a random forest regressor on the scaled data.
            6. Computes the feature importance using the random forest regressor.
            7. Plots the feature importance using a bar chart.
            8. Selects features with importance greater than or equal to 0.1.
        """

        corr_matrix = table_data.corr()
        upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        selected_features = [column for column in upper_tri.columns if any(abs(upper_tri[column]) >= 0.75)]

        if target in selected_features:
            selected_features.remove(target)

        X = table_data[selected_features]
        y = table_data[target]
        X_train, X_test, y_train, y_test = train_test_split(X,
                                                            y,
                                                            test_size=0.3,
                                                            random_state=42)
        ss = StandardScaler()
        X_train_scaled = ss.fit_transform(X_train)
        X_test_scaled = ss.transform(X_test)
        y_train = np.array(y_train)

        rfc_1 = RandomForestRegressor()
        rfc_1.fit(X_train_scaled, y_train)
        rfc_1.score(X_train_scaled, y_train)

        feats = {}

        for feature, importance in zip(X.columns,
                                       rfc_1.feature_importances_):
            feats[feature] = importance
        importances = pd.DataFrame.from_dict(feats,
                                             orient='index').rename(columns={0: 'Gini-Importance'})
        importances = importances.sort_values(by='Gini-Importance',
                                              ascending=False)
        importances = importances.reset_index()
        importances = importances.rename(columns={'index': 'Features'})
        sns.set(font_scale=5)
        sns.set(style="whitegrid",
                color_codes=True,
                font_scale=1.7)

        plt.figure(figsize=(12, 8),
                   tight_layout=True)

        sns.barplot(x=importances['Gini-Importance'],
                    y=importances['Features'],
                    data=importances,
                    color='#7570b3')
        plt.axvline(x=0.1, color='red')
        plt.xlabel('Importance', fontsize=25, weight='bold')
        plt.ylabel('Features', fontsize=25, weight='bold')
        plt.title('Feature Importance', fontsize=25, weight='bold')
        plt.grid(True)

        plt.savefig(os.path.join(PLOTS_DIR, '_pca_report.png'), dpi=300)
        selected_features = importances[importances['Gini-Importance'] >= 0.1]['Features'].tolist()

        return selected_features