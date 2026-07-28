---
title: 'SPECTRA: Stellar Parameter Estimation and Calculation Tools for Research and Analysis'
tags:
  - Python
  - astronomy
  - astrophysics
  - stellar evolution
  - isochrones
  - machine learning
  - Bayesian statistics
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
date: 28 July 2026
bibliography: paper.bib
---

# Summary

Determining fundamental stellar parameters — such as mass, age, luminosity, effective temperature ($T_{\text{eff}}$), radius, and distance — is central to observational and theoretical astrophysics [@serenelli_weighing_2021]. Interior stellar structure [@baraffe_new_2015], rotation [@vasconcelos2022], and magnetic field generation [@charbonneau2014] are mass- and age-dependent processes. **SPECTRA**[^1] (*Stellar Parameter Estimation and Calculation Tools for Research and Analysis*, v1.1.0) is an open-source Python desktop application designed to optimize and automate stellar mass and age determination and diagnostic modeling for stars in clusters, with a particular focus on pre-main-sequence (PMS) and low-mass stars.

The software integrates thread-safe data state management (`spectra.state`), missing data imputation via $k$-Nearest Neighbors ($k$-NN) and iterative techniques, 2D Bayesian posterior isochrone fitting (`spectra.bayesian`), machine-learning regression modeling (`spectra.tools`), and interactive diagnostic visualization tools [@baraffe_new_2015; @serenelli_weighing_2021].

[^1]: The development of this software and its underlying research framework were initiated and primarily executed at the Universidade Estadual de Santa Cruz (UESC), with final updates and infrastructure migration supported by the Universidade Estadual Paulista (UNESP).

# Statement of need

In Astrophysics, estimating the mass and age of single stars outside binary systems depends heavily on theoretical stellar evolution models and mass-luminosity or mass-magnitude relations (MLR/MMR) [@benedict_solar_2016; @serenelli_weighing_2021]. Taking advantage of age and metallicity homogeneity of stars belonging to clusters, isochrone or stellar track fitting on color magnitude and HR diagrams proves to be a powerful tool to obtain simultaneously stellar ages and mass. However, clusters with ages $\le 100$ Myr have a great number of pre-main-sequence stars that lie above the main sequence, exhibiting high observational uncertainties due to differential interstellar extinction, age dispersion, and incomplete data vectors [@herczeg__empirical_2015]. Differences between theoretical input physics in models (e.g., Siess et al. 2000 vs. BHAC15) also introduce systematic variances [@lebreton_2014].

`SPECTRA` addresses these challenges by offering a unified, user-friendly desktop application built with `ttkbootstrap`. It enables researchers and educators to:

1.  Automatically preprocess, filter, convert linear luminosity units ($L/L_\odot \rightarrow \log_{10} L$), and impute incomplete photometric datasets.
2.  Perform 2D Bayesian posterior probability inference over theoretical evolutionary grids (Siess et al. 2000; BHAC15) to calculate marginal expected values and $1\text{-}\sigma$ uncertainties for both mass ($M_\odot$) and age (Myr) [@baraffe_new_2015].
3.  Train, optimize (via Grid Search and $K$-fold cross-validation), and statistically evaluate machine learning regression algorithms (e.g., Random Forests, Support Vector Regressors, $k$-NN, Bayesian Ridge) to construct semi-empirical mass-magnitude relations.
4.  Organize, inspect, and export publication-ready tables (`_final_result_table.csv`) and diagnostic visual figures (`Mass Plot`, `Age Plot`, `HR Diagram Plot`, and 4-panel regression dashboards).

# State of the field

Several computational tools exist within the astronomical ecosystem for stellar parameter estimation and cluster analysis:

*  Machine learning tools applied to stellar parameter derivation, such as CARMENES transfer-learning routines [@bello-garcia_carmenes_2023], target specific spectral types ($M$ dwarfs) rather than open clusters.
*  Empirical relations based on low-mass field binaries [@benedict_solar_2016; @mann_how_2019] provide benchmarks for main-sequence objects, but lack integrated GUI workflows for cluster-wide missing-data imputation, 2D Bayesian posterior estimation, and pre-main-sequence fits.

`SPECTRA` fills this gap by combining GUI-driven visual diagnostics (e.g., Hertzsprung-Russell and diagnostic residual plots), automated missing-data imputation, 2D Bayesian parameter inference, and a model-ranking framework based on goodness-of-fit metrics ($RMSE$, $MAE$, $R^2$, and $AIC$).

# Software design and workflow

`SPECTRA` is written in Python 3 and relies on core scientific packages including `numpy`, `pandas`, `scipy`, `scikit-learn`, `statsmodels`, and `ttkbootstrap` [@gomes_determinacao_2024]. The application's architecture decouples GUI control logic from heavy computational backends, providing a modular design structured around thread-safe state management (`DataManager` in `spectra.state`) and specialized analytical modules.

\autoref{fig:workflow} illustrates the high-level execution flow and operational logic of `SPECTRA`:

![Execution workflow and modular architecture of `SPECTRA`.](spectra_app_workflow.png){#fig:workflow}

### Execution Pipeline & Module Description

1. **Initialization & Environment Setup:** Upon launching `main.py`, `SPECTRA` performs an automated verification check. If local theoretical evolutionary grids (e.g., Siess et al. 2000; BHAC15) or model weights are missing, the system automatically fetches and caches them to ensure reproducible execution [@baraffe_new_2015].

2. **Core Analytical Workflows:** From the primary desktop window, users can direct multi-catalog photometry (e.g., *Gaia* DR3, TESS) into three specialized processing modules [@babusiaux_gaia_2023; @stassun_revised_2019; @paegert_tess_2021]:

   * **2D Bayesian Isochrone Fitting Module (`spectra.bayesian`):** Evaluates a full 2D likelihood $\chi^2$ over the HR diagram space:
     $$\chi^2 = \left(\frac{T_{\text{eff}, \text{obs}} - T_{\text{eff}, \text{grid}}}{\sigma_T}\right)^2 + \left(\frac{\log L_{\text{obs}} - \log L_{\text{grid}}}{\sigma_L}\right)^2$$
     combined with a Salpeter/Kroupa Initial Mass Function (IMF) prior ($P(M) \propto M^{-1.35}$ for $M \le 0.5 M_\odot$, $M^{-2.35}$ for $M > 0.5 M_\odot$). Marginal posterior moments yield the expected values and physical $1\text{-}\sigma$ uncertainties for both stellar mass ($\hat{M}, \sigma_M$) and age ($\hat{t}, \sigma_t$).

   * **Mass-Magnitude Modeling Module (`spectra.tools`):** Builds semi-empirical relations by training candidate regression algorithms (e.g., $k$-NN, Random Forests, Support Vector Regressors, Bayesian Linear Regression) over theoretical stellar grids. Hyperparameters are optimized via $K$-fold cross-validation and Grid Search. Candidate models are evaluated and automatically ranked using a normalized multi-metric score $S$:
     $$S = \hat{\mathcal{M}} \cdot \mathcal{P}^T$$
     where $\hat{\mathcal{M}}$ represents the min-max normalized metrics matrix and $\mathcal{P}$ corresponds to a unit vector, assigning equal relative importance to $RMSE$, $MAE$, $(1-R^2)$, and $AIC$.

   * **Mathematical Modeling Module:** Provides advanced preprocessing, dataset filtering, missing attribute imputation (e.g., $k$-NN and iterative stochastic techniques), feature correlation analysis, Principal Component Analysis (PCA), and residual diagnostic checks (homoscedasticity and normality of errors).

3. **Output Artifact Generation:** All generated diagnostics—including annotated HR diagrams, individual mass/age plots (`Mass Plot`, `Age Plot`), statistical summary tables (`_final_result_table.csv`), regression report logs, and diagnostic residual plots—are automatically organized and saved in the localized `outputs/` repository for direct export into publications.

# Research impact & empirical case study

The practical effectiveness of `SPECTRA` was validated through a comprehensive study of young stellar clusters covering distinct evolutionary stages: Orion Nebula Cluster (ONC, ~1 Myr) [@hillenbrand_stellar_1997], Upper Scorpius (~5–11 Myr) [@pecaut_revised_2012; @rebull_rotation_2018], $h$ Persei / NGC 869 (~13 Myr), Pleiades (~112 Myr) [@dahm_reexamining_2015; @lodieu_5d_2019; @gossage_age_2018], and NGC 2516 (~150 Myr).

### Methodological Validation
Using a control sample of isolated eclipsing binary stars from @benedict_solar_2016, `SPECTRA`'s $k$-NN regression model derived from the BHAC15 isochrone grid [@baraffe_new_2015] achieved high predictive accuracy ($R^2 = 0.96$, $P_{\text{skedasticity}} = 0.12$) with a median residual uncertainty of $3.8\%$.

### Cluster Analysis Results

* **Young PMS Clusters (ONC & Upper Scorpius):** For clusters rich in pre-main-sequence objects with significant age dispersion [@hillenbrand_stellar_1997; @pecaut_revised_2012], 2D Bayesian `IsocFit` successfully identified low-mass PMS objects and derived simultaneous ages, whereas $k$-NN regression provided robust mass estimates with less dependency on bolometric corrections [@pecaut_intrinsic_2013].

* **Well-Defined Main-Sequence Clusters (Pleiades & NGC 2516):** On clusters with established main sequences [@lodieu_5d_2019], $k$-NN RMM modeling using *Gaia* $G$-band and $V$-band absolute magnitudes yielded near-perfect alignment with literature values ($R^2 > 0.99$, $RMSE < 0.01 M_\odot$), demonstrating superior performance over traditional isochrone grid edge-effects.

\autoref{fig:pleiades_comp} illustrates a comparative evaluation of mass estimates derived by `SPECTRA` for member stars of the Pleiades cluster using both the grid-interpolation method (`IsocFit - BHAC15`, left panels) and the machine-learning Mass-Magnitude relation (`KNN - BHAC15`, right panels), benchmarked against literature values from TESS V8.2 [@stassun_revised_2019], [@lodieu_5d_2019], and [@delfosse_accurate_2000], [@benedict_solar_2016].

![Comparison of stellar mass estimates for the Pleiades cluster obtained via `IsocFit` (left column) and `KNN - BHAC15` (right column) against reference datasets from TESS V8.2, Lodieu et al. (2019), and Delfosse et al. (2000). The dashed line represents the ideal 1:1 identity relation.](ple_results_report.png){#fig:pleiades_comp}

As shown in \autoref{fig:pleiades_comp}, the `IsocFit - BHAC15` method exhibits greater dispersion around the 1:1 identity line, particularly for stars with $M > 0.7 M_\odot$. This behavior is attributed to the convergence of evolutionary tracks near the Zero-Age Main Sequence (ZAMS) at the age of the Pleiades (~112 Myr), which creates localized degeneracies during grid minimization[@gomes_determinacao_2024]. Conversely, the semi-empirical `KNN - BHAC15` model demonstrates exceptional predictive stability, showing near-perfect alignment ($R^2 \approx 1.0$) when cross-validated against the photometrically derived masses of @lodieu_5d_2019. When benchmarked against empirical binary masses from @benedict_solar_2016, the $k$-NN model reproduces stellar masses with minimal bias up to the applicability threshold of the empirical $K$-band relation ($M \lesssim 0.75 M_\odot$) [@gomes_determinacao_2024].

A more detailed astrophysical discussion and complete parameter catalogues derived for each cluster will be presented in a forthcoming paper (Gomes et al., in prep.).

By reducing manual preprocessing time and providing rigorous statistical diagnostic reports, `SPECTRA` supports both observational research in stellar rotation/dynamics and undergraduate/graduate instruction in stellar astrophysics [@gomes_determinacao_2024].

# AI usage disclosure

No generative AI tools were used in the algorithmic development or code implementation of the `SPECTRA` package.

# Acknowledgements

The primary development, algorithmic design, and empirical cluster validations of `SPECTRA` were conducted at the Laboratório de Astrofísica Teórica e Observacional (LATO) at the Universidade Estadual de Santa Cruz (UESC), whose financial and structural support during the initial phases of this research was fundamental. The primary author also acknowledges the current institutional support provided by the Universidade Estadual Paulista (UNESP) during the final stages and preparation of this software manuscript, as well as the entire open-source Python scientific community. The work of MJV and AHC is partially funded by the UESC's projects 2023.0003119-74 and 2025.0033125-91. 

# References