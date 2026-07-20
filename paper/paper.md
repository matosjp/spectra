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
  - name: João Paulo Matos Dias Gomes
    orcid: 0009-0000-2586-2801
    corresponding: true
    affiliation: 1, 2
  - name: Maria Jaqueline Vasconcelos
    affiliation: 2
  - name: Adriano Hoth Cerqueira
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

Determining fundamental stellar parameters—such as mass, age, luminosity, effective temperature ($T_{\text{eff}}$), radius, and distance—is central to observational and theoretical astrophysics [@serenelli_weighing_2021]. **SPECTRA** (*Stellar Parameter Estimation and Calculation Tools for Research and Analysis*, v2024.12.15t) is an open-source Python tool designed to optimize and automate stellar mass determination and diagnostic modeling for stars in clusters, with a particular focus on young, low-mass stars.

*Note: The development of this software and its underlying research framework were initiated and primarily executed at the Universidade Estadual de Santa Cruz (UESC), with final updates and infrastructure migration supported by the Universidade Estadual Paulista (UNESP).*

The software integrates data preprocessing, missing data imputation via $k$-Nearest Neighbors ($k$-NN) and iterative techniques, theoretical isochrone fitting (`IsocFit`), machine-learning regression modeling (`Mass-Magnitude Modeling`), and interactive visualization tools [@baraffe_new_2015; @serenelli_weighing_2021].

# Statement of need

In Astrophysics, estimating the mass of single stars outside binary systems relies heavily on theoretical stellar evolution models and mass-luminosity or mass-magnitude relations (MLR/MMR) [@benedict_solar_2016; @serenelli_weighing_2021]. Taking advantage of age and metallicity homogeneity of stars belonging to clusters, isochrone or stellar track fitting on color magnitude diagrams prove to be an useful tool to obtain simultaneously stellar ages and mass. However, it depends on a well defined main sequence which in turn depends on high quality data and on the age of the cluster. Younger clusters have a great number of pre main sequence (PMS) stars that lie above the main sequence making the fitting more difficult. Moreover, PMS stars exhibit high observational uncertainties due to differential interstellar extinction, age dispersion, and incomplete data vectors [@herczeg__empirical_2015].

`SPECTRA` addresses these challenges by offering a unified, user-friendly desktop application built with `ttkbootstrap`. It enables researchers and educators to:
1. Automatically preprocess, filter, and impute incomplete photometric datasets.
2. Execute automated local interpolation over theoretical evolutionary grids (e.g., Siess et al. 2000; BHAC15) via `IsocFit` [@baraffe_new_2015].
3. Train, optimize (via Grid Search and $K$-fold cross-validation), and statistically evaluate machine learning regression algorithms (e.g., Random Forests, Support Vector Regressors, $k$-NN) to construct semi-empirical mass-magnitude relations.

# State of the field

Several computational tools exist within the astronomical ecosystem for stellar parameter estimation and cluster analysis:
* Machine learning tools applied to stellar parameter derivation, such as CARMENES transfer-learning routines [@bello-garcia_carmenes_2023], target specific spectral types ($M$ dwarfs) rather than open clusters.
* Empirical relations based on low-mass field binaries [@benedict_solar_2016; @mann_how_2019] provide benchmarks for main-sequence objects, but lack integrated GUI workflows for cluster-wide missing-data imputation and pre-main-sequence fits.

`SPECTRA` fills this gap by combining GUI-driven visual diagnostics (e.g., Hertzsprung-Russell and diagnostic residual plots), automated missing-data imputation, and a model-ranking framework based on goodness-of-fit metrics ($RMSE$, $MAE$, $R^2$, and $AIC$).

# Software design and workflow

`SPECTRA` is written in Python and relies on core packages including `numpy`, `pandas`, `scikit-learn`, `statsmodels`, and `ttkbootstrap`. Its execution pipeline consists of three primary modules:

1. **Preprocessing & Imputation:** Filters multi-catalog photometry (e.g., *Gaia* DR3, TESS) and handles missing attributes via $k$-NN and iterative imputation [@gaia_collaboration_gaia_2023; @stassun_revised_2019; @paegert_tess_2021].
2. **Isochrone Fitting (`IsocFit`):** Computes local distance minimization on theoretical grids:
   $$\delta = \sqrt{(T_{\text{eff}} - T_{\text{eff},0})^2 + (L - L_0)^2}$$
   followed by linear interpolation across neighboring tracks.
3. **Machine Learning RMM:** Trains candidate regressors and ranks them using a normalized scoring metric $S = \hat{\mathcal{M}} \cdot \mathcal{P}^T$, where weights $\mathcal{P} = [0.35, 0.25, 0.30, 0.10]$ reflect $RMSE$, $MAE$, $(1-R^2)$, and $AIC$ respectively.

# Research impact & empirical case study

The practical effectiveness of `SPECTRA` was validated through a comprehensive study of young stellar clusters covering distinct evolutionary stages: Orion Nebula Cluster (ONC, ~1 Myr) [@hillenbrand_stellar_1997], Upper Scorpius (~5–11 Myr) [@pecaut_revised_2012; @rebull_rotation_2018], $h$ Persei / NGC 869 (~13 Myr), Pleiades (~112 Myr) [@dahm_reexamining_2015; @lodieu_5d_2019; @gossage_age_2018], and NGC 2516 (~150 Myr).

### Methodological Validation
Using a control sample of isolated eclipsing binary stars from @benedict_solar_2016, `SPECTRA`'s $k$-NN regression model derived from the BHAC15 isochrone grid [@baraffe_new_2015] achieved high predictive accuracy ($R^2 = 0.96$, $P_{\text{skedasticity}} = 0.12$) with a median residual uncertainty of $3.8\%$.

### Cluster Analysis Results
* **Young PMS Clusters (ONC & Upper Scorpius):** For clusters rich in pre-main-sequence objects with significant age dispersion [@hillenbrand_stellar_1997; @pecaut_revised_2012], `IsocFit` successfully identified low-mass PMS objects, whereas $k$-NN regression provided robust mass estimates with less dependency on bolometric corrections [@pecaut_intrinsic_2013].
* **Well-Defined Main-Sequence Clusters (Pleiades & NGC 2516):** On clusters with established main sequences [@lodieu_5d_2019], $k$-NN RMM modeling using *Gaia* $G$-band and $V$-band absolute magnitudes yielded near-perfect alignment with literature values ($R^2 > 0.99$, $RMSE < 0.01 M_\odot$), demonstrating superior performance over traditional isochrone grid edge-effects.

By reducing manual preprocessing time and providing rigorous statistical diagnostic reports, `SPECTRA` supports both observational research in stellar rotation/dynamics and undergraduate/graduate instruction in stellar astrophysics.

# AI usage disclosure

No generative AI tools were used in the algorithmic development or code implementation of the `SPECTRA` package.

# Acknowledgements

The primary development, algorithmic design, and empirical cluster validations of `SPECTRA` were conducted at the Laboratório de Astrofísica Teórica e Observacional (LATO) at the Universidade Estadual de Santa Cruz (UESC), whose financial and structural support during the initial phases of this research was fundamental. The primary author also acknowledges the current institutional support provided by the Universidade Estadual Paulista (UNESP) during the final stages and preparation of this software manuscript, as well as the entire open-source Python scientific community.

# References