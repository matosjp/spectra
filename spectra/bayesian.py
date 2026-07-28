"""
S.P.E.C.T.R.A. - Bayesian Isochrone Parameter Estimator Module
Copyright (C) 2026 João Paulo Matos Dias Gomes, Maria Jaqueline Vasconcelos, Adriano Hoth Cerqueira

Provides 2D Bayesian posterior probability estimation over the HR Diagram, calculating expected
stellar masses (Msun), ages (Myr), and 1-sigma uncertainties using Salpeter/Kroupa IMF priors.
"""

from typing import Tuple, List, Dict, Any, Optional, Union
import numpy as np
import pandas as pd
import scipy.interpolate as interp

from spectra.StarLocalization import readiso


# Cache for 2D Interpolator MeshGrids to avoid recomputing identical grids
_GRID_CACHE: Dict[str, Tuple[Any, Any, Any, Any, Any, Any, Any]] = {}


def _get_interpolator_grid(model: str) -> Tuple[Any, Any, Any, Any, Any, Any, Any]:
    """
    Builds or retrieves cached 2D interpolator mesh grids for a given isochrone model.

    Args:
        model (str): Name of the isochrone model ('Siess 2000' or 'BHAC15').

    Returns:
        Tuple containing (M_mesh, A_mesh, t_pred, l_pred, valid_hull, near_teff, near_logl).
    """
    if model in _GRID_CACHE:
        return _GRID_CACHE[model]

    alldataiso = readiso(model)

    if model == "Siess 2000":
        at, al, am = 3, 1, 4
        ageiso = np.array([1.e4, 5.e4, 2.e5, 5.e5, 2.e6, 5.e6, 1.e7, 3e7, 6e7, 1e8]) / 1e6
        is_logl = False
    elif model == "BHAC15":
        at, al, am = 1, 2, 0
        ageiso = np.array([1.e6, 2.e6, 5.e6, 1.e7, 2.e7, 5.e7, 8.e7, 1.e8, 1.2e8, 2e8]) / 1e6
        is_logl = True
    else:
        raise ValueError(f"Unknown isochrone model: {model}")

    log_ageiso = np.log10(ageiso)

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
                l_log = l_val if is_logl else (np.log10(l_val) if l_val > 0 else np.nan)
                if not np.isnan(l_log):
                    points.append((m, log_a))
                    teff_list.append(t)
                    logl_list.append(l_log)

    points = np.array(points)
    teff_arr = np.array(teff_list)
    logl_arr = np.array(logl_list)

    interp_teff = interp.LinearNDInterpolator(points, teff_arr)
    interp_logl = interp.LinearNDInterpolator(points, logl_arr)
    near_teff = interp.NearestNDInterpolator(points, teff_arr)
    near_logl = interp.NearestNDInterpolator(points, logl_arr)

    m_min, m_max = points[:, 0].min(), points[:, 0].max()
    log_a_min, log_a_max = points[:, 1].min(), points[:, 1].max()

    m_grid = np.linspace(m_min, m_max, 150)
    log_a_grid = np.linspace(log_a_min, log_a_max, 150)
    M_mesh, A_mesh = np.meshgrid(m_grid, log_a_grid)
    mesh_points = np.column_stack([M_mesh.ravel(), A_mesh.ravel()])

    t_pred = interp_teff(mesh_points).reshape(M_mesh.shape)
    l_pred = interp_logl(mesh_points).reshape(M_mesh.shape)
    valid_hull = ~np.isnan(t_pred) & ~np.isnan(l_pred)

    grid_data = (M_mesh, A_mesh, t_pred, l_pred, valid_hull, near_teff, near_logl)
    _GRID_CACHE[model] = grid_data
    return grid_data


def interpolmass(
    primarydataset: Union[pd.DataFrame, Dict[str, Any]],
    model: str
) -> Tuple[List[float], List[float], List[float], List[float]]:
    """
    2D Bayesian Isochrone Parameter Estimator (Mass, Age, and 1-sigma uncertainties).

    Evaluates full 2D likelihood over the HR diagram using a Salpeter/Kroupa IMF prior:
        P(M) ~ M^(-1.35) for M <= 0.5 Msun
        P(M) ~ M^(-2.35) for M > 0.5 Msun

    Args:
        primarydataset (Union[pd.DataFrame, Dict[str, Any]]): Input dataset containing 'Teff' and 'logL' (or 'L').
        model (str): Isochrone model name ('Siess 2000' or 'BHAC15').

    Returns:
        Tuple[List[float], List[float], List[float], List[float]]:
            (calculated_masses, calculated_ages, mass_uncertainties, age_uncertainties)
    """
    teffs = np.array(primarydataset['Teff'], copy=True, dtype=float)
    if 'logL' in primarydataset:
        logls = np.array(primarydataset['logL'], copy=True, dtype=float)
        valid_l = logls[~np.isnan(logls)]
        if len(valid_l) > 0 and np.all(valid_l > 0) and np.median(valid_l) > 0.05:
            logls = np.log10(np.maximum(1e-10, logls))
    elif 'L' in primarydataset:
        logls = np.log10(np.maximum(1e-10, np.array(primarydataset['L'], copy=True, dtype=float)))
    else:
        raise KeyError("Luminosity column ('logL' or 'L') not found in dataset.")

    e_teffs = np.array(primarydataset['e_Teff'], copy=True, dtype=float) if 'e_Teff' in primarydataset else np.full(len(teffs), np.nan)
    e_logls = np.array(primarydataset['e_logL'], copy=True, dtype=float) if 'e_logL' in primarydataset else np.full(len(logls), np.nan)

    M_mesh, A_mesh, t_pred, l_pred, valid_hull, near_teff, near_logl = _get_interpolator_grid(model)
    mesh_points = np.column_stack([M_mesh.ravel(), A_mesh.ravel()])

    # IMF Prior: Salpeter (M > 0.5) / Kroupa low-mass (M <= 0.5)
    imf_prior = np.where(M_mesh <= 0.5, M_mesh**(-1.35), M_mesh**(-2.35))

    calc_masses: List[float] = []
    calc_ages: List[float] = []
    calc_mass_errs: List[float] = []
    calc_age_errs: List[float] = []

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

        # Marginal Posterior Moments
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
