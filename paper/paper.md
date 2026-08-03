---
title: 'SPECTRA: Stellar Parameter Estimation and Calculation Tools for Research and Analysis'
tags:
  - Python
  - astronomy
  - astrophysics
  - stellar evolution
  - isochrones
  - machine learning
authors:
  - name: João Paulo Almeida da Silva Matos
    orcid: 0009-0000-2586-2801
    corresponding: true
    affiliation: 1, 2
  - name: Maria Jaqueline Vasconcelos
    orcid: 0000-0003-1672-4866
    affiliation: 2
  - name: Adriano Hoth Cerqueira
    orcid: 0000-0003-3708-1564
    affiliation: 2
affiliations:
  - name: Department of Physics, São Paulo State University (UNESP), Institute of Biosciences, Humanities and Exact Sciences, São José do Rio Preto, SP, 15054-000, Brazil
    index: 1
  - name: Laboratório de Astrofísica Teórica e Observacional, Universidade Estadual de Santa Cruz (UESC), Ilhéus, Brasil
    index: 2
date: 16 July 2026
bibliography: paper.bib
---

# Summary

Determining fundamental stellar parameters — such as mass, age, luminosity, effective temperature ($T_{\text{eff}}$), radius, and distance — is central to observational and theoretical astrophysics [@serenelli_weighing_2021]. Interior stellar structure [@baraffe_new_2015], rotation [@vasconcelos2022], magnetic field generation [@charbonneau2014], for example, are mass dependent processes. **SPECTRA**[^1] (*Stellar Parameter Estimation and Calculation Tools for Research and Analysis*, v1.2.0) is an open-source Python tool designed to optimize and automate stellar mass determination and diagnostic modeling for stars in clusters, with a particular focus on young, low-mass stars.

The software integrates data preprocessing, missing data imputation via $k$-Nearest Neighbors ($k$-NN) and iterative techniques, 2D Bayesian isochrone fitting (`IsocFit`), primary stellar parameters derivation (`Primary Parameters`), machine-learning regression modeling (`Mass-Magnitude Modeling`), and interactive visualization tools [@baraffe_new_2015; @serenelli_weighing_2021].

[^1]: The development of this software and its underlying research framework were initiated and primarily executed at the Universidade Estadual de Santa Cruz (UESC), with final updates and infrastructure migration supported by the Universidade Estadual Paulista (UNESP).

# Statement of need

In Astrophysics, estimating the mass of single stars outside binary systems depends heavily on theoretical stellar evolution models and mass-luminosity or mass-magnitude relations (MLR/MMR) [@benedict_solar_2016; @serenelli_weighing_2021]. Taking advantage of age and metallicity homogeneity of stars belonging to clusters, isochrone or stellar track fitting on color magnitude diagrams proves to be a useful tool to obtain simultaneously stellar ages and mass. However, it depends on a well defined main sequence, on high quality data and on the age of the cluster. Clusters with ages $\le 100$ Myr have a great number of pre main sequence (PMS) stars that lie above the main sequence making the fitting more difficult. Moreover, PMS stars exhibit high observational uncertainties due to differential interstellar extinction, age dispersion, and incomplete data vectors [@herczeg__empirical_2015]. Differences between stellar models also affect the final results. Stellar structure and evolutionary models differ in the adopted input physics and this impact the isochrone fitting results [@lebreton_2014]. On the other hand, MLR or MMR uses photometric and spectroscopic data for systems that can provide direct mass values as, for example, double-lined eclipsing binary systems. These relations are model independent. Using MLR/MMR requires goodness-of-fit methods that can be statistical in nature or that can rely on the use of machine learning techniques. `SPECTRA` uses both isochrone fitting and MMR relations to calculate mass values of stars belonging to stellar clusters.


`SPECTRA` addresses these challenges by offering a unified, user-friendly desktop application built with `ttkbootstrap`. It enables researchers and educators to:

1.  Automatically preprocess, filter, and impute incomplete photometric datasets using simple or machine-learning imputation strategies ($k$-NN, Iterative/MICE).
2.  Execute 2D Bayesian posterior probability calculations across theoretical evolutionary grids (e.g., Siess et al. 2000; BHAC15) via `IsocFit` with Salpeter/Kroupa IMF priors [@baraffe_new_2015].
3.  Derive primary physical parameters — including effective temperature ($T_{\text{eff}}$), spectral type ($\text{SpT}$), surface gravity ($\log g$), bolometric luminosity ($\log_{10}(L/L_\odot)$) and stellar radius ($R_*/R_\odot$) via Bell et al. (2014) — alongside spectroscopic Equivalent Width (EW) $H\alpha, Li\,\text{I}, TiO$ Pre-Main-Sequence (PMS) youth diagnostics and T Tauri activity classification (**CTTS**, **WTTS**, **Field**).
4.  Train, optimize (via Grid Search and $K$-fold cross-validation), and statistically evaluate machine learning regression algorithms (e.g., Random Forests, Support Vector Regressors, Gradient Boosting, $k$-NN) to construct semi-empirical mass-magnitude relations using dynamic MADYS model/filter repositories.
5.  Generate Goodness-of-Fit statistical metrics ($R^2$, Adjusted $R^2$, RMSE, MAE, $\chi^2$, Reduced $\chi^2$) and export standalone, dark-themed interactive HTML web reports with per-star calculation traces.



# State of the field

Several computational tools exist within the astronomical ecosystem for stellar parameter estimation and cluster analysis:

*  Machine learning tools applied to stellar parameter derivation, such as CARMENES transfer-learning routines [@bello-garcia_carmenes_2023], target specific spectral types ($M$ dwarfs) rather than open clusters.
*  Empirical relations based on low-mass field binaries [@benedict_solar_2016; @mann_how_2019] provide benchmarks for main-sequence objects, but lack integrated GUI workflows for cluster-wide missing-data imputation and pre-main-sequence fits.



`SPECTRA` fills this gap by combining GUI-driven visual diagnostics (e.g., Hertzsprung-Russell and diagnostic residual plots), automated missing-data imputation, and a model-ranking framework based on goodness-of-fit metrics ($RMSE$, $MAE$, $R^2$, and $AIC$).

# Software design and workflow

`SPECTRA` is written in Python 3 and relies on core packages including `numpy`, `pandas`, `scikit-learn`, `statsmodels`, `scipy`, and `ttkbootstrap` for user interface rendering [@gomes_determinacao_2024]. The application's architecture decouples GUI control logic from heavy computational backends, providing a modular design structured around four main analytical pathways.

\autoref{fig:workflow} illustrates the high-level execution flow and operational logic of `SPECTRA`:

![Execution workflow and modular architecture of `SPECTRA`.](spectra_app_workflow.png){#fig:workflow}

### Execution Pipeline & Module Description

The structure of the code, the environment and the setup for running it, the models used and all the mathematical considerations are described in details in @gomes_determinacao_2024. However, for the sake of clarity, we will outline the main features here:

1. **Initialization & Environment Setup:** Upon launching `main.py`, `SPECTRA` performs an automated first-run verification check. If local theoretical evolutionary grids (e.g., Siess et al. 2000; BHAC15) or model weights are missing, the system automatically fetches and caches them to ensure reproducible offline execution [@baraffe_new_2015].

2. **Core Analytical Workflows:** From the primary desktop window, users can direct multi-catalog photometry (e.g., *Gaia* DR3, 2MASS, TESS) into four specialized processing modules [@babusiaux_gaia_2023; @stassun_revised_2019; @paegert_tess_2021]:

   * **2D Bayesian Isochrone Fitting Module (`IsocFit`):** Evaluates joint 2D likelihood distributions across theoretical evolutionary tracks over the HR diagram combined with a Salpeter/Kroupa Initial Mass Function (IMF) prior ($P(M) \propto M^{-1.35}$ for $M \le 0.5\,M_\odot$, $M^{-2.35}$ for $M > 0.5\,M_\odot$). Calculates expected stellar mass ($M_\odot$), age (Myr), and $1\text{-}\sigma$ posterior uncertainties.

   * **⭐ Primary Stellar Parameters Module:** Performs multi-band photometric dereddening ($A_V$), derives effective temperature ($T_{\text{eff}}$), spectral type ($\text{SpT}$), surface gravity ($\log g$), bolometric luminosity ($\log_{10}(L/L_\odot)$) and stellar radius ($R_*/R_\odot$) following Bell et al. (2014), processes spectroscopic Equivalent Widths ($H\alpha$, $Li\,\text{I}$, $TiO$) to classify Pre-Main-Sequence activity (**CTTS**, **WTTS**, **Field**), and trains machine-learning multi-parameter regressors.

   * **Mass-Magnitude Modeling Module (RMM):** Integrated with the interactive MADYS Models Repository Manager (`📦 Models Manager`), dynamically querying 18+ evolutionary models and up to 127+ filters per model. Builds semi-empirical relations by training candidate regression algorithms ($k$-NN, Random Forests, Support Vector Regressors, Gradient Boosting, Bayesian Ridge) over dynamic mass/age bounds. Candidate models are evaluated and automatically ranked using a normalized multi-metric score $S$:
     $$S = \hat{\mathcal{M}} \cdot \mathcal{P}^T$$
     where $\hat{\mathcal{M}}$ represents the min-max normalized metrics matrix and $\mathcal{P}$ corresponds to a unit vector, assigning equal relative importance to $RMSE$, $MAE$, $(1-R^2)$, and $AIC$ to compute the composite metric score via matrix multiplication.

   * **Mathematical Modeling Module:** Provides advanced preprocessing, dataset filtering, missing attribute imputation ($k$-NN and iterative stochastic techniques), feature correlation analysis, Principal Component Analysis (PCA), and residual diagnostic checks (homoscedasticity and normality of errors).

3. **Output Artifact Generation:** All generated diagnostics—including annotated HR/Color-Magnitude diagrams, statistical summary tables (`.csv`), regression report logs, Goodness-of-Fit metrics tables, standalone interactive HTML reports (`🌐 HTML Report`), and diagnostic residual plots—are automatically organized and saved under dedicated subfolders in the localized `outputs/` repository (`isochrone_fitting/`, `mass_modeling/`, `primary_parameters/`, `math_models/`) for direct export into publications.

# Research impact & empirical case study

The practical effectiveness of `SPECTRA` was validated through a comprehensive study of young stellar clusters covering distinct evolutionary stages: Orion Nebula Cluster (ONC, ~1 Myr) [@hillenbrand_stellar_1997], Upper Scorpius (~5–11 Myr) [@pecaut_revised_2012; @rebull_rotation_2018], $h$ Persei / NGC 869 (~13 Myr), Pleiades (~112 Myr) [@dahm_reexamining_2015; @lodieu_5d_2019; @gossage_age_2018], and NGC 2516 (~150 Myr).

### Methodological Validation
Using a control sample of isolated eclipsing binary stars from @benedict_solar_2016, `SPECTRA`'s $k$-NN regression model derived from the BHAC15 isochrone grid [@baraffe_new_2015] achieved high predictive accuracy ($R^2 = 0.96$, $P_{\text{skedasticity}} = 0.12$) with a median residual uncertainty of $3.8\%$.

### Cluster Analysis Results

* **Young PMS Clusters (ONC & Upper Scorpius):** For clusters rich in pre-main-sequence objects with significant age dispersion [@hillenbrand_stellar_1997; @pecaut_revised_2012], `IsocFit` successfully identified low-mass PMS objects, whereas $k$-NN regression provided robust mass estimates with less dependency on bolometric corrections [@pecaut_intrinsic_2013].

* **Well-Defined Main-Sequence Clusters (Pleiades & NGC 2516):** On clusters with established main sequences [@lodieu_5d_2019], $k$-NN RMM modeling using *Gaia* $G$-band and $V$-band absolute magnitudes yielded near-perfect alignment with literature values ($R^2 > 0.99$, $RMSE < 0.01 M_\odot$), demonstrating superior performance over traditional isochrone grid edge-effects.

\autoref{fig:pleiades_comp} illustrates a comparative evaluation of mass estimates derived by `SPECTRA` for member stars of the Pleiades cluster using both the traditional grid-interpolation method (`IsocFit - BHAC15`, left panels) and the machine-learning Mass-Magnitude relation (`KNN - BHAC15`, right panels), benchmarked against literature values from TESS V8.2 [@stassun_revised_2019], [@lodieu_5d_2019], and [@delfosse_accurate_2000], [@benedict_solar_2016].

![Comparison of stellar mass estimates for the Pleiades cluster obtained via `IsocFit` (left column) and `KNN - BHAC15` (right column) against reference datasets from TESS V8.2, Lodieu et al. (2019), and Delfosse et al. (2000). The dashed line represents the ideal 1:1 identity relation.](ple_results_report.png){#fig:pleiades_comp}

As shown in \autoref{fig:pleiades_comp}, the `IsocFit - BHAC15` method exhibits greater dispersion around the 1:1 identity line, particularly for stars with $M > 0.7 M_\odot$. This behavior is attributed to the convergence of evolutionary tracks near the Zero-Age Main Sequence (ZAMS) at the age of the Pleiades (~112 Myr), which creates localized degeneracies during grid minimization[@gomes_determinacao_2024]. Conversely, the semi-empirical `KNN - BHAC15` model demonstrates exceptional predictive stability, showing near-perfect alignment ($R^2 \approx 1.0$) when cross-validated against the photometrically derived masses of @lodieu_5d_2019. When benchmarked against empirical binary masses from @benedict_solar_2016, the $k$-NN model reproduces stellar masses with minimal bias up to the applicability threshold of the empirical $K$-band relation ($M \lesssim 0.75 M_\odot$) [@gomes_determinacao_2024].

A more detailed astrophysical discussion and complete parameter catalogues derived for each cluster will be presented in a forthcoming paper (Gomes et al., in prep.).

By reducing manual preprocessing time and providing rigorous statistical diagnostic reports, `SPECTRA` supports both observational research in stellar rotation/dynamics and undergraduate/graduate instruction in stellar astrophysics [@gomes_determinacao_2024].

# AI usage disclosure

No generative AI tools were used in the algorithmic development or code implementation of the `SPECTRA` package.

# Acknowledgements

The primary development, algorithmic design, and empirical cluster validations of `SPECTRA` were conducted at the Laboratório de Astrofísica Teórica e Observacional (LATO) at the Universidade Estadual de Santa Cruz (UESC), whose financial and structural support during the initial phases of this research was fundamental. The primary author also acknowledges the current institutional support provided by the Universidade Estadual Paulista (UNESP) during the final stages and preparation of this software manuscript, as well as the entire open-source Python scientific community. The work of MJV and AHC is partially funded by the UESC's projects 2023.0003119-74 and 2025.0033125-91. 

# References