# User Manual — S.P.E.C.T.R.A. (v1.1.0)

This manual provides detailed instructions for using the **S.P.E.C.T.R.A.** graphical user interface for stellar parameter estimation, 2D Bayesian Isochrone Fitting, machine learning mass–magnitude modeling, and exploratory data analysis.

> **Note:** For environment setup and installation procedures across different operating systems (Windows, macOS, Linux), please refer to the `README.md` file.

---

## Table of Contents

1. [Input Data Prerequisites (File Format & Required Columns)](#1-input-data-prerequisites-file-format--required-columns)
2. [Module Architecture & Functional Breakdown](#2-module-architecture--functional-breakdown)
3. [Launching the Application](#3-launching-the-application)
4. [Interface Overview](#4-interface-overview)
5. [Home Tab](#5-home-tab)
6. [Isochrone Fitting Tab (2D Bayesian Estimator)](#6-isochrone-fitting-tab-2d-bayesian-estimator)
7. [Mass-Magnitude Modeling Tab](#7-mass-magnitude-modeling-tab)
8. [Mathematical Modeling Tab](#8-mathematical-modeling-tab)
9. [File & Help Menus](#9-file--help-menus)
10. [Updating the Application ("Atualizar Programa")](#10-updating-the-application-atualizar-programa)
11. [Output Directory & File Locations](#11-output-directory--file-locations)
12. [Output Interpretation Guide (Tables & Plots)](#12-output-interpretation-guide-tables--plots)
13. [Troubleshooting & Frequently Asked Questions](#13-troubleshooting--frequently-asked-questions)

---

## 1. Input Data Prerequisites (File Format & Required Columns)

> **CRITICAL — READ BEFORE LOADING YOUR DATA**

Before importing any dataset into S.P.E.C.T.R.A., ensure your input file meets the following specifications:

1. **File Format:** Your dataset **must be saved in `.csv` format** (comma-separated values). Proprietary or binary formats such as `.xlsx`, `.fits`, `.txt`, or `.tsv` must be exported/converted to `.csv` prior to loading.
2. **Pre-calculated Physical Parameters:** S.P.E.C.T.R.A. does not derive effective temperature ($T_{\text{eff}}$) or luminosity ($\log L$) directly from raw fluxes or spectrum files. **Your input table must already contain pre-calculated values for temperature and luminosity**.
3. **Standard Column Naming Conventions:**
   * **For Isochrone Fitting:** The dataset must contain columns named **`Teff`** (Effective Temperature in Kelvin, $K$) and **`logL`** (Luminosity in $\log_{10}(L/L_\odot)$).
   * **Automatic Linear Luminosity Conversion:** If your CSV uses a linear luminosity column (`L`, `lum`, `L/Ls`, `Lsun`), S.P.E.C.T.R.A. automatically detects it and converts the values to $\log_{10}(L/L_\odot)$.
   * **For Mass-Magnitude Modeling:** The dataset must contain a magnitude column named according to the pattern `<Filter>mag` corresponding to your chosen photometric filter (e.g., `Gmag`, `Vmag`, `Jmag`).
   * **For Distance Corrections (Optional):** If distance correction is enabled, include a column named **`pc`** (distance in parsecs).
4. **Example Datasets:** Example test tables are provided directly within the project at `isochrone_models/SIESS/` (e.g., `3myrZ002o.csv`).

---

## 2. Module Architecture & Functional Breakdown

S.P.E.C.T.R.A. is organized into modular Python packages (`spectra/`), each responsible for a distinct layer in the data processing pipeline:

* ### `spectra.state` (`DataManager`)
  Provides a thread-safe, centralized data manager (`DataManager`) that holds active memory datasets. Prevents race conditions during background calculations and keeps tables in sync across tabs.

* ### `spectra.bayesian` (`2D Bayesian Estimator`)
  Houses the core 2D Bayesian parameter inference engine (`interpolmass`). Computes joint likelihoods across the HR diagram, applies Salpeter/Kroupa Initial Mass Function (IMF) priors, and calculates expected values and $1\text{-}\sigma$ posterior uncertainties for Mass ($M_\odot$) and Age (Myr).

* ### `spectra.StarLocalization`
  Loads and parses isochrone evolutionary grids (Siess 2000, BHAC15) with in-memory caching (`_ISO_CACHE`), maps observed stars onto the HR diagram, and generates publication-ready Hertzsprung–Russell plots.

* ### `spectra.tools`
  Contains machine learning regression engines (`MathModels`, `RegressionReport`, `fit`, `ResultDisplay`). Performs missing data imputation (KNN, Iterative), PCA reduction, multi-model regression fitting, and diagnostic plotting.

* ### `spectra.widgets`
  Contains reusable GUI components, progress windows (`BusyWindow`), update managers (`UpdateWindow`), model download managers (`ModelDownloadWindow`), and modal notifications.

* ### `spectra.interface`
  Main GUI module built on `ttkbootstrap`. Manages the primary application window (`App`), navigation sidebar, menus, and responsive viewports.

* ### `spectra.paths`
  Single source of truth for absolute file paths and automatic creation of output directories (`outputs/tables/`, `outputs/plots/`, `outputs/isocfit_outputs/`).

---

## 3. Launching the Application

Activate your Conda environment from the terminal before starting S.P.E.C.T.R.A.:

```bash
conda activate spectra
python main.py
```

### First-Run Data Download

Upon your first launch, a **"Downloading Stellar Models"** dialog will appear. S.P.E.C.T.R.A. automatically fetches:
1. MADYS stellar evolutionary models (BHAC15, PARSEC, MIST).
2. The `isochrone_models/` directory (Siess 2000 & BHAC15 grids).

---

## 4. Interface Overview

The interface consists of three primary regions:

1. **Top Menu Bar:** System utilities (**File** and **Help**).
2. **Sidebar (Left):** Navigation tabs corresponding to core workflows:
   * `Home`
   * `Isochrone Fitting`
   * `Mass-Magnitude Modeling`
   * `Mathematical Modeling`
3. **Main Display Area:** Interactive space organized into structured cards (`ttk.Labelframe`) containing action controls, data tables, and diagnostic plots.

---

## 5. Home Tab

Displays software description, version status (**v1.1.0**), author credits, and quick links to documentation and program updates.

---

## 6. Isochrone Fitting Tab (2D Bayesian Estimator)

Derives individual stellar masses ($M_\odot$), ages (Myr), and $1\text{-}\sigma$ uncertainties using a 2D Bayesian Posterior probability calculation across theoretical evolutionary tracks.

### Step-by-Step Guide:

1. **Isochrone Model:** Select the target evolutionary grid (*Siess 2000* or *BHAC15*).
2. **Data Input:**
   * **Single Star:** Enter **Effective Temperature (K)** and **Luminosity (in log)** manually.
   * **Multi-Star Table:** Click **Input Table** and select a `.csv` file containing `Teff` and `logL` (or `L`) columns.
3. **Verbose Toggle:**
   * **Enabled:** Saves individual HR diagram fit plots (PDFs) for every star in `outputs/isocfit_outputs/`.
   * **Disabled:** Generates summary tables and main diagnostic plots.
4. **Locate Stars:** Click to execute the 2D Bayesian estimation pipeline.
5. **View & Export Results:**
   * **`📊 Show Table`**: Opens the calculated table containing `Mass_calc`, `Mass_e`, `Age_calc (Myr)`, and `Age_e (Myr)`.
   * **`📈 Mass Plot`**: Renders calculated Mass ($M_\odot$) vs. $T_{\text{eff}}$ with $1\text{-}\sigma$ error bars.
   * **`⏳ Age Plot`**: Renders calculated Age (Myr) vs. $T_{\text{eff}}$ with $1\text{-}\sigma$ error bars.
   * **`🌌 HRD Plot`**: Generates and displays the Hertzsprung–Russell diagram with observed stars overlaid on theoretical tracks.

---

## 7. Mass-Magnitude Modeling Tab

Constructs mass–magnitude relationships from MADYS evolutionary grids using machine learning regressors and calculates stellar masses from observed magnitudes.

### MADYS Models Repository Manager (`📦 Models Manager`):
- **Interactive Manager Dialog**: Clicking **`📦 Models Manager`** opens a dedicated window displaying all 18+ MADYS evolutionary grids (`bhac15`, `parsec`, `mist`, `baraffe15`, `baraffe98`, `siess2000`, `ames-cond`, `atmo2020`, etc.).
- **Installation Status & One-Click Download**: Shows real-time status badges (🟢 **Installed** or ⚪ **Not Installed**), mass/age bounds, and allows downloading any missing model grid from Zenodo in the background with a single click.

### Dynamic MADYS Model & Filter Engine:
- **Dynamic Parameter & Filter Bounds**: Selecting any model automatically updates valid mass boundaries, age slider ranges, and exact supported photometric filters.
- **Interactive HTML Report (`🌐 HTML Report`)**: Clicking **`🌐 HTML Report`** generates a modern, standalone interactive web report (`outputs/spectra_regression_report.html`) complete with dark mode styling, responsive performance charts ($R^2$ scores, RMSE errors), metadata summaries, and full regression model metrics tables, automatically opening it in the user's default browser.

### Step-by-Step Guide:

1. **Isochrone Model:** Select any grid from the dynamic dropdown (`bhac15`, `parsec`, `mist`, `baraffe15`, `siess2000`, etc.).
2. **Mass & Age Range:** Review or adjust minimum/maximum mass limits ($M_\odot$) and cluster age (Myr).
3. **Select Filter:** Choose any supported photometric band (`G`, `BP`, `RP`, `V`, `J`, `H`, `Ks`, etc.).
4. **Build Model:** Click to train and evaluate multiple regression algorithms.
   * **Model Report:** Displays comparison table ($R^2$, RMSE, MAE, AIC) for all models.
   * **Model Report Plot:** Opens 4-panel diagnostic dashboard for the winning model.
5. **Input Table:** Load observed CSV table with magnitude column (e.g., `Gmag`).
6. **Calculate Mass:** Predicts masses (`Mass_calc`, `Mass_e`).
7. **View Results:** Inspect via **`📊 Show Table`** or **`📈 Result Plot`**.

---

153: 
154: ---
155: 
156: ## 8. Primary Stellar Parameters Module (`⭐ Primary Parameters` Tab)
157: 
158: Derives fundamental physical parameters for stars across multi-band photometry and spectroscopic indices.
159: 
160: ### Physical Derivations & Methodology:
161: 1. **Multi-Band Photometry & Extinction ($A_V$)**:
   - Dereddens multi-color magnitudes (Gaia $G, BP, RP$, 2MASS $J, H, K$, Johnson $V, B$) using Cardelli extinction laws ($A_V$).
   - Derives effective temperature ($T_{\text{eff}}$), spectral type ($\text{SpT}$), and surface gravity ($\log g$) using empirical dwarf calibrations (Pecaut & Mamajek 2013).
2. **Bolometric Luminosity ($\log_{10}(L/L_\odot)$) & Stellar Radius ($R_*/R_\odot$)** (Bell et al. 2014 / `stu1488.pdf`):
   - Computes distance modulus $\text{DM} = 5 \log_{10}(d_{\text{pc}}) - 5$ (or from paralax $\varpi_{\text{mas}}$).
   - Derives absolute bolometric magnitude $M_{\text{bol}} = M_{\lambda} + \text{BC}_{\lambda}(T_{\text{eff}})$.
   - Calculates bolometric luminosity $\log_{10}(L_*/L_\odot) = 0.4 [M_{\text{bol},\odot} - M_{\text{bol}}]$ (where $M_{\text{bol},\odot} = 4.755\text{ mag}$).
   - Computes stellar radius $R_*/R_\odot$ via Stefan-Boltzmann relation $\log_{10}(R_*/R_\odot) = 0.5 \log_{10}(L_*/L_\odot) - 2 \log_{10}(T_{\text{eff}}/5770\text{ K})$.
3. **Spectroscopic Features & T Tauri Activity Classification**:
   - Analyzes Equivalent Widths (EW) of $H\alpha$ ($6563\text{ Å}$), $Li\,\text{I}$ ($6708\text{ Å}$), and $TiO$ bandhead index.
   - Classifies stars into **Classical T Tauri Stars (CTTS)** (strong accretion emission $H\alpha \ge 10\text{ Å}$), **Weak-lined T Tauri Stars (WTTS)** (chromospheric emission $2 \le H\alpha < 10\text{ Å}$ and young $Li\,\text{I} \ge 0.1\text{ Å}$), or **Field Stars**.
4. **Machine Learning Parameter Regressors**:
   - Trains multi-output regressors (*RandomForest*, *GradientBoosting*, *SVR*, *KNN*) to predict parameters directly from color indices.
5. **Goodness-of-Fit Statistical Suite**:
   - Computes $R^2$, Adjusted $R^2$, RMSE, MAE, $\chi^2$, and Reduced $\chi^2$ metrics saved to `outputs/primary_parameters/tables/primary_params_gof_stats.csv`.
6. **Interactive Web HTML Report (`🌐 HTML Report`)**:
   - Generates standalone, dark-themed HTML reports (`outputs/primary_parameters/reports/primary_params_report.html`) containing base64 distribution plots, Color-Magnitude Diagrams (CMD), Goodness-of-Fit cards, and an optional per-star step-by-step trace card (`round-toggle` switch).

---

## 9. Mathematical Modeling Tab

Provides general-purpose statistical analysis, missing data imputation, PCA reduction, and multi-feature regression modeling.

### Step-by-Step Guide:

1. **`🔍 Analyze Features`**: Click to compute correlation matrices and populate feature lists.
2. **Missing Imputation:** Select missing data strategy (`None`, `KNN`, `Iterative`).
3. **Select Target:** Choose target variable to predict from dropdown.
4. **Build Model:** Trains machine learning pipeline and computes PCA components.
5. **Calculate:** Generates `<Target>_calc` and `<Target>_e` prediction columns.

---

## 10. File & Help Menus

* **File -> Open table:** Opens a CSV file into shared memory (`DataManager`).
* **File -> Save session:** Exports application state to binary `.pkl` file.
* **Help -> About:** Displays license, software details, and update option.
* **Help -> Dark Mode:** Toggles between Light ("Spectra Stellar Light") and Dark ("Spectra Deep Space Dark") themes.

---

## 11. Updating the Application ("Atualizar Programa")

S.P.E.C.T.R.A. includes an integrated update manager:

1. Click **`🔄 Atualizar Programa`** in the Help menu or About window.
2. The system checks the remote GitHub repository and pulls updates automatically in a background thread.
3. If new updates are installed, a notification prompts you to restart the application.

---

## 12. Output Directory & File Locations

All output files are organized into dedicated subfolders under `outputs/`:

| Folder Path | Description of Generated Content |
| --- | --- |
| `outputs/isochrone_fitting/` | Bayesian 2D fit tables (`_final_result_table.csv`) and PDF star localization plots. |
| `outputs/mass_modeling/` | Mass-Magnitude regression reports (`Regression_model_report.csv`) and 4-panel diagnostic dashboards. |
| `outputs/primary_parameters/plots/` | $T_{\text{eff}}$ distribution histograms, Gaia Color-Magnitude Diagrams (CMD), and T Tauri activity charts. |
| `outputs/primary_parameters/tables/` | Derived primary parameters catalog (`primary_params_catalog.csv`) and Goodness-of-Fit metrics (`primary_params_gof_stats.csv`). |
| `outputs/primary_parameters/reports/` | Standalone interactive HTML reports (`primary_params_report.html`). |
| `outputs/math_models/` | General statistical regression tables and PCA component matrices. |

---

## 13. Output Interpretation Guide (Tables & Plots)

### Primary CSV Columns (`primary_params_catalog.csv` & `_final_result_table.csv`)

| Column Name | Physical Meaning & Statistical Interpretation |
| :--- | :--- |
| **`Teff_phot`** | **Photometric Effective Temperature ($K$):** Multi-band color weighted effective temperature. |
| **`SpT_phot`** | **Derived Spectral Type:** Empirical spectral classification (e.g., `G2V`, `M1.5V`, `A0V`). |
| **`logg_phot`** | **Surface Gravity ($\log g$):** Derived stellar surface gravity in $\text{dex} (\text{cm/s}^2)$. |
| **`logL_phot`** | **Bolometric Luminosity ($\log_{10}(L/L_\odot)$):** Luminosity derived via Bell et al. (2014; `stu1488.pdf`) Section 3.2. |
| **`Mbol_phot`** | **Absolute Bolometric Magnitude ($M_{\text{bol}}$):** Bolometric magnitude derived from dereddened magnitude and distance modulus. |
| **`Radius_phot`** | **Stellar Radius ($R_*/R_\odot$):** Stellar radius calculated via Stefan-Boltzmann relation. |
| **`T_Tauri_Class`** | **Activity Classification:** Spectroscopic PMS activity class (`CTTS`, `WTTS`, or `Field`). |
| **`Mass_calc`** | **Estimated Stellar Mass ($M_\odot$):** Expected mass value ($\hat{M}$) derived from 2D Bayesian posterior distribution or machine learning regression. |
| **`Mass_e`** | **Mass Uncertainty ($M_\odot$):** $1\text{-}\sigma$ Bayesian posterior standard deviation ($\sigma_M$) or model RMSE. |
| **`Age_calc (Myr)`** | **Derived Stellar Age (Myr):** Expected age ($\hat{t}$) in millions of years derived from 2D Bayesian posterior distribution. |
| **`Age_e (Myr)`** | **Age Uncertainty (Myr):** $1\text{-}\sigma$ Bayesian posterior standard deviation ($\sigma_t$) in millions of years. |

---

## 14. Troubleshooting & Frequently Asked Questions

* **Q: Why did my age result show in decimals?**
  * **A:** All ages in S.P.E.C.T.R.A. are expressed in **Myr (Millions of Years)**. An age of `3.0` corresponds to $3\text{ Myr}$ ($3.000.000\text{ years}$).
* **Q: How does the software handle linear vs. logarithmic luminosity?**
  * **A:** S.P.E.C.T.R.A. automatically converts linear luminosity columns (`L`, `lum`, `L/Ls`) into $\log_{10}(L/L_\odot)$ upon loading.
* **Q: How do I calculate bolometric luminosity if I only have distance/parallax?**
  * **A:** Provide `d_pc` (distance in pc) or `parallax` (in mas) alongside `Gmag` or `Vmag` in your CSV. The Primary Parameters module automatically computes $\log_{10}(L/L_\odot)$, $M_{\text{bol}}$, and $R_*/R_\odot$ following Bell et al. (2014).
* **Q: How do I revert to a previous working version?**
  * **A:** Use Git tags: `git checkout v1.0.0-stable` returns to the baseline version, while `git checkout v1.1.0-refactored` selects the current refactored release.