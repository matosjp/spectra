import statsmodels.api as sm
import scipy.stats as ss

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, BayesianRidge
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.neighbors import KNeighborsRegressor

import matplotlib.pyplot as plt
from ttkbootstrap.toast import ToastNotification

import numpy as np
import pandas as pd
import madys


import StarLocalization as sl


class FilterValues:
    def __init__(self):
        pass

    @staticmethod
    def filter_predict(mag, X, clust_dist):
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
        ph = np.nan_to_num(teff)
        k = []
        for i in range(len(ph)):
            if ph[i] is not None and ph[i] != 0:
                k.append(i)
        teff[k] = ph[k]

        row = {'mag': teff}

        ff = ~np.isnan(row['mag']) & (row['mag'] >= min(X)) & (row['mag'] <= max(X))
        df_row = pd.DataFrame(row)
        teff = df_row.loc[ff, 'mag'].values

        return teff, ff

    @staticmethod
    def filter_results(y, y_out, other=None):
        if other is not None:
            row = {'y': y,
                   'y_out': y_out,
                   'other': other}
        else:
            row = {'y': y,
                   'y_out': y_out}

        ff = ~np.isnan(row['y']) & (row['y'] > 0) & ~np.isnan(row['y_out']) & (row['y_out'] > 0)
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


def interpolmass(primarydataset, alldataiso=sl.readiso()):
    control_mass = None
    res = None
    nm = []
    data = primarydataset['Teff']
    ageiso = np.array([1.e4, 5.e4, 2.e5, 5.e5, 2.e6, 5.e6, 1.e7, 6e7, 1e8]) / 1e6
    massiso = np.array([.1, .2, .3, .4, .5, .6, .7, .8, .9, 1., 1.1, 1.2])
    ai = []
    mi = []
    for age in primarydataset['Age']:
        # Check if the age is present in ageiso
        if age in ageiso:
            # If found, get the index
            index = np.where(ageiso == age)[0][0]
            ai.append(index)
        else:
            ai.append(None)  # Append None if age not found in ageiso

    for mass in primarydataset['Mass']:
        # Check if the age is present in ageiso
        if mass in massiso:
            # If found, get the index
            index = np.where(massiso == mass)[0][0]
            mi.append(index)
        else:
            mi.append(None)  # Append None if mass not found in ageiso

    if len(ai) == 0 or len(mi) == 0:
        toast = ToastNotification(
            title='Stellar Mass Interpolation',
            message="Stellar mass(es) can't be derived",
            duration=5000,
            bootstyle='light'
        )
        toast.show_toast()

    else:
        nm = []
        xpd = []
        ypd = []
        t = data
        for x in range(len(t)):
            i = ai[x]
            j = mi[x]
            if j is not None:
                if j != 0 and j != 11:
                    xp = [alldataiso[i, 3, j - 1], alldataiso[i, 3, j], alldataiso[i, 3, j + 1]]
                    yp = [massiso[j - 1], massiso[j], massiso[j + 1]]
                    xpd.append(xp[1])
                    ypd.append(yp[1])
                elif j == 0:
                    xp = [alldataiso[i, 3, j], alldataiso[i, 3, j + 1], alldataiso[i, 3, j + 2]]
                    yp = [massiso[j], massiso[j + 1], massiso[j + 2]]
                    xpd.append(xp[0])
                    ypd.append(yp[0])
                else:
                    xp = [alldataiso[i, 3, j - 2], alldataiso[i, 3, j - 1], alldataiso[i, 3, j]]
                    yp = [massiso[j - 2], massiso[j - 1], massiso[j]]
                    xpd.append(xp[1])
                    ypd.append(yp[1])
                y = np.interp(t[x], xp, yp)
                nm.append(y)
            else:
                nm.append(np.nan)

    return nm


def fit(X, y, model_name):
    if model_name == 'Bayesian Regression':
        model = BayesianRidge()
        param_grid = {}
    elif model_name == 'Linear Regression':
        model = LinearRegression()
        param_grid = {}
    elif model_name == 'Ridge Regression':
        model = Ridge()
        param_grid = {'model__alpha': [0.1, 1.0, 10.0]}
    elif model_name == 'Lasso Regression':
        model = Lasso()
        param_grid = {'model__alpha': [0.1, 1.0, 10.0]}
    elif model_name == 'ElasticNet Regression':
        model = ElasticNet()
        param_grid = {'model__alpha': [0.1, 1.0, 10.0], 'model__l1_ratio': [0.1, 0.5, 0.9]}
    elif model_name == 'Support Vector Regressor':
        model = SVR()
        param_grid = {'model__kernel': ['linear', 'poly', 'rbf'], 'model__C': [0.1, 1.0, 10.0],
                      'model__epsilon': [0.001, 0.01, 0.1, 1.0, 10.0]}
    elif model_name == 'Decision Tree Regressor':
        model = DecisionTreeRegressor()
        param_grid = {'model__max_depth': [None, 10, 20]}
    elif model_name == 'Random Forest Regressor':
        model = RandomForestRegressor()
        param_grid = {'model__n_estimators': [50, 100, 200]}
    elif model_name == 'Gradient Boosting Regressor':
        model = GradientBoostingRegressor()
        param_grid = {'model__n_estimators': [50, 100, 200], 'model__learning_rate': [0.01, 0.1, 0.5]}
    elif model_name == 'AdaBoost Regressor':
        model = AdaBoostRegressor()
        param_grid = {'model__n_estimators': [50, 100, 200], 'model__learning_rate': [0.01, 0.1, 0.5]}
    elif model_name == 'KNeighbors Regressor':
        model = KNeighborsRegressor()
        param_grid = {'model__n_neighbors': [3, 5, 10]}
    else:
        raise ValueError(f"Unknown model name: {model_name}")

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', model)
    ])

    grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring='neg_mean_squared_error')
    grid_search.fit(X, y)
    return grid_search


def calculate_aic(n, mse, k):
    aic = n * np.log(mse) + 2 * k
    return aic


def normalize_metrics(metrics):
    normalized_metrics = {}
    for metric, values in metrics.items():
        max_val = np.max(values)
        min_val = np.min(values)
        normalized_metrics[metric] = [(val - min_val) / (max_val - min_val) for val in values]
    return normalized_metrics


def weighted_score(normalized_metrics):
    weights = {
        'rmse': 0.35,
        'mae': 0.25,
        'r2': 0.30,
        'aic': 0.10
    }
    total_scores = []
    for i in range(len(normalized_metrics['rmse'])):
        score = (weights['rmse'] * normalized_metrics['rmse'][i] +
                 weights['mae'] * normalized_metrics['mae'][i] +
                 weights['r2'] * (1 - normalized_metrics['r2'][i]) +  # Invert R2 because higher is better
                 weights['aic'] * normalized_metrics['aic'][i])
        total_scores.append(score)
    return total_scores


def RegressionReport(X, y):
    models = {
        'Bayesian Regression': BayesianRidge(),
        'Linear Regression': LinearRegression(),
        'Ridge Regression': Ridge(),
        'Lasso Regression': Lasso(),
        'ElasticNet Regression': ElasticNet(),
        'Support Vector Regressor': SVR(),
        'Decision Tree Regressor': DecisionTreeRegressor(),
        'Random Forest Regressor': RandomForestRegressor(),
        'Gradient Boosting Regressor': GradientBoostingRegressor(),
        'AdaBoost Regressor': AdaBoostRegressor(),
        'KNeighbors Regressor': KNeighborsRegressor()
    }

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    report = []
    metrics = {'rmse': [], 'mae': [], 'r2': [], 'aic': []}
    for model_name in models.keys():
        grid_search = fit(X_train, y_train, model_name)
        best_model = grid_search.best_estimator_
        y_pred = best_model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # Calculate AIC
        n = len(y_test)
        k = best_model.named_steps['model'].coef_.shape[0] if hasattr(best_model.named_steps['model'],
                                                                      'coef_') else len(
            best_model.named_steps['model'].get_params())
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
    # print(tabulate(report_df, headers='keys', tablefmt='psql'))
    report = report_df
    # Return the best model based on the weighted score
    best_model = report_df.loc[report_df['Score'].idxmin()]['Model']
    model = fit(X, y, best_model).best_estimator_

    return best_model, model, report


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
            leverage_values = np.linspace(0.001, 1, 1000)

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
                 linestyle='-.', label="D$_{crit}$")
        plt.plot(d1x, -d1y, marker='none', color='#c3121e',
                 linestyle='-.')

        plt.scatter(lev, st_res, color='#7570b3')
        plt.axhline(-3, color='#e7298a', linestyle=':')
        plt.axhline(3, color='#e7298a', linestyle=':')
        plt.axhline(0, color='grey', linestyle='--')
        plt.axvline(0, color='grey', linestyle='--')
        plt.legend(loc='best')
        plt.xlabel('Leverage ($\hat{h}$)')
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
        plt.ylabel('$\sqrt{Standardized~ Residuals}$')
        plt.title('Scale-Location Plot')
        plt.grid(True)
        plt.tick_params(direction='in')

        if save_file:
            plt.savefig('_statistical_results.png')
        elif isinstance(save_file, str):
            plt.savefig(save_file)
        plt.close(fig)
        plt.close()


class ResultDisplay:
    def __init__(self, x, y, yerr, method):
        self.x = x
        self.y = y
        self.yerr = yerr
        self.method = method

    def res_plot(self, save_file=False):
        x, y, yerr = FilterValues.filter_results(self.x, self.y, self.yerr)
        fig = plt.figure(figsize=(12, 8))
        plt.plot(x, y, marker="^", color='#7570b3', alpha=0.6,
                 label="Calculated masses", linestyle='')
        plt.errorbar(x, y, yerr=yerr, capsize=5, fmt='^', ecolor='gray', alpha=0.6)
        if self.method == 'MMR':
            plt.xlabel('Magnitude (mag)')
            plt.title('Mass-Magnitude Relationship Results')
            plt.xlim(np.min(x) - 0.05, np.max(x) + 0.05)

        else:
            plt.xlabel('Effective Temperature (K)')
            plt.xlim(2500, 4350)
            plt.title('Isocrhone Fitting Results')

        plt.ylabel('Predicted Values (M/M$_\odot$)')
        plt.legend(loc="best")

        plt.grid(True)
        plt.tight_layout()
        plt.ylim(0, 1.45)
        plt.tick_params(axis='both', which='major', labelsize=10)
        plt.tick_params(direction='in')

        if save_file:
            plt.savefig(
                '_mass_results_display.png', dpi=300)
        elif isinstance(save_file, str):
            plt.savefig(save_file)
        plt.close(fig)
        plt.close()
