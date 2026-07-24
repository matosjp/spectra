# User Manual — S.P.E.C.T.R.A.

This manual explains how to use each feature of the **S.P.E.C.T.R.A.** graphical user interface for stellar parameter estimation and data analysis.

> **Note:** For environment setup and installation procedures across different operating systems (Windows, macOS, Linux), please refer to the `README.md` file.

---

## Table of Contents

## Table of Contents

1. [Input Data Prerequisites (File Format & Required Columns)](#0-input-data-prerequisites-file-format--required-columns)
2. [Module Architecture & Functional Breakdown](#1-module-architecture--functional-breakdown)
3. [Launching the Application](#2-launching-the-application)
4. [Interface Overview](#3-interface-overview)
5. [Home Tab](#4-home-tab)
6. [Isochrone Fitting Tab](#5-isochrone-fitting-tab)
7. [Mass-Magnitude Modeling Tab](#6-mass-magnitude-modeling-tab)
8. [Mathematical Modeling Tab](#7-mathematical-modeling-tab)
9. [File Menu](#8-file-menu)
10. [Help Menu](#9-help-menu)
11. [Output Directory & File Locations](#10-output-directory--file-locations)
12. [Output Interpretation Guide (Tables & Plots)](#11-output-interpretation-guide-tables--plots)
13. [Known Limitations](#12-known-limitations)

---

## 0. Input Data Prerequisites (File Format & Required Columns)

> **CRITICAL — READ BEFORE LOADING YOUR DATA**

Before importing any dataset into S.P.E.C.T.R.A., ensure your input file meets the following specifications:

1. **File Format:** Your dataset **must be saved in `.csv` format** (comma-separated values). Proprietary or binary formats such as `.xlsx`, `.fits`, `.txt`, or `.tsv` must be exported/converted to `.csv` prior to loading.
2. **Pre-calculated Physical Parameters:** S.P.E.C.T.R.A. does not derive effective temperature ($\text{Teff}$) or luminosity ($\log L$) directly from raw fluxes or spectrum files. **Your input table must already contain pre-calculated values for temperature and luminosity**.
3. **Standard Column Naming Conventions:**
* **For Isochrone Fitting:** The dataset must contain columns named strictly **`Teff`** (Effective Temperature in Kelvin, $K$) and **`logL`** (Luminosity in $\log(L/L_\odot)$).
* **For Mass-Magnitude Modeling:** The dataset must contain a magnitude column named according to the pattern `<Filter>mag` corresponding to your chosen photometric filter (e.g., `Gmag`, `Vmag`, `Jmag`).
* **For Distance Corrections (Optional):** If distance correction is enabled, include a column named **`pc`** (distance in parsecs).
4. **Example Datasets:** To test the application and inspect the expected column structures, example tables are provided directly within the project at `isochrone_models/SIESS/` (e.g., `1myrZ002o.csv` and `3myrZ002o.csv`).


---

## 1. Module Architecture & Functional Breakdown

S.P.E.C.T.R.A. is organized into modular Python packages (`spectra/`), each responsible for a distinct step in the data pipeline:

* ### `spectra.interface`


Handles the GUI built on `ttkbootstrap`. It manages the primary application window (`App`), navigation sidebar, top menus, and responsive rendering of interactive tables and plots.
* ### `spectra.StarLocalization`


Contains the core astrophysical fitting engines. It reads stellar evolutionary grids (Siess 2000, BHAC15), maps observed stars onto the Hertzsprung–Russell (HR) diagram, performs 2D bilinear/multivariate interpolation across age-mass tracks, and calculates interpolative parameter uncertainties.
* ### `spectra.tools`


Houses the machine learning and statistical engines. It provides automated feature preprocessing, missing data imputation algorithms (KNN, Iterative), Principal Component Analysis (PCA) reduction, multi-model regression fitting (Linear, Ridge, Lasso, SVR, Decision Trees, Random Forest, Gradient Boosting, AdaBoost, KNN)[cite: 1], and automated regression performance evaluation.
* ### `spectra.paths`


Serves as the single source of truth for runtime pathing across the OS. It automatically initializes output folder hierarchies (`outputs/tables/`, `outputs/plots/`, `outputs/isocfit_outputs/`) and handles absolute path resolutions for external assets and models.
* ### `spectra.widgets`


Contains reusable GUI components, including progress monitoring windows, download managers (`ModelDownloadWindow`), session pickle state managers (`SessionManager`), and custom modal notification dialogs.

---

## 2. Launching the Application

Before running S.P.E.C.T.R.A., always activate your Conda environment from the terminal:

```bash
conda activate spectra
python main.py
```

### First-Run Data Download

Upon your first launch (or whenever local models are missing), a **"Downloading Stellar Models"** dialog will pop up. S.P.E.C.T.R.A. automatically fetches:

1. MADYS stellar evolutionary models (BHAC15, PARSEC, MIST) via the `madys` API.
2. The `isochrone_models/` directory (Siess 2000 & BHAC15 grids) via Google Drive download.

> *Download times depend on your internet bandwidth.* Once completed, the main window opens. Refer to `README.md` if the download fails.

---

## 3. Interface Overview

The interface consists of three primary regions:

1. **Top Menu Bar:** System utilities (**File** and **Help**).
2. **Sidebar (Left):** Navigation tabs corresponding to core workflows:
* `Home`
* `Isochrone Fitting`
* `Mass-Magnitude Modeling`
* `Mathematical Modeling`


3. **Main Display Area:** Interactive space where generated data tables, diagnostic charts, and regression summaries open in dedicated viewports.

> **Workflow Tip:** Loading a `.csv` via **Input Table** or **Open table** stores the dataset in global memory (`table_data`), making it immediately available across all sidebar tabs.

---

## 4. Home Tab

Displays application metadata, version information, software overview, and author credits. No configuration actions are required here.

---

## 5. Isochrone Fitting Tab

Maps stars onto Hertzsprung–Russell (HR) diagrams and derives individual stellar ages and masses by interpolating against evolutionary track grids (Siess 2000, BHAC15).

### Step-by-Step Guide:

1. **Isochrone Model:** Select the target evolutionary model grid (*Siess 2000* or *BHAC15*).
2. **Data Input:** Choose your input method:
* **Single Star:** Enter **Effective Temperature (K)** and **Luminosity (in log)** manually in the input boxes.
* **Multi-Star Table:** Click **Input Table** and select a `.csv` file with `Teff` and `logL` columns. *(Note: Table input overrides manual entries if both are supplied).*


3. **Verbose Toggle:**
* **Enabled:** Generates and saves individual HR diagram fit plots (PDFs) for every star in `outputs/isocfit_outputs/`.
* **Disabled:** Generates only the aggregate summary table and overview plot.


4. **Locate Stars:** Click to execute the grid interpolation pipeline. A progress bar tracks execution.
5. **View Results:**
* Click **Show Table** to inspect derived values (`Mass_calc`, `Age_calc`, uncertainties).
* Click **Result Plot** to render the summary HR diagram.



---

## 6. Mass-Magnitude Modeling Tab

Generates a specialized mass–magnitude relation model from MADYS isochrone grids and applies the trained machine learning pipeline to derive stellar masses from observed magnitudes.

### Step-by-Step Guide:

1. **Isochrone Model:** Choose the underlying grid (`bhac15`, `parsec`, or `mist`).
2. **Mass Range:** Set the minimum and maximum stellar mass limits (in $M_\odot$) for model construction.
3. **Isochrone Age:** Set the target age (in Myr) using the slider or numeric entry.
4. **Select Magnitude Filter:** Pick the photometric band matching your observed data (`G`, `G_BP`, `G_RP`, `U`, `B`, `V`, `I`, `J`, `H`, `K`).
5. **Build Model:** Click to train multiple regression algorithms in the background.
* **Model Report:** Opens a table comparing performance metrics across all evaluated regression models.
* **Model Report Plot:** Displays diagnostic plots for the top-performing model.


6. **Distance Correction (Optional):** Check the box to apply distance modulus corrections (requires a `pc` distance column in your dataset).
7. **Input Table:** Load your `.csv` dataset containing the relevant magnitude column (e.g., `Gmag`).
8. **Calculate Mass:** Apply the winning regression model to predict masses for your input stars.
* View outputs in **Show Table** (`Mass_calc`, `Mass_e`) or **Result Plot**.



> **Important:** You must click **Build Model** before running **Calculate Mass**.

---

## 7. Mathematical Modeling Tab

Provides exploratory data analysis (correlation matrices, feature importance, PCA reduction) and general-purpose regression modeling to predict any target column from remaining features.

### Step-by-Step Guide:

1. **Analyze:** Click to inspect the active table. Computes correlation matrices and populates numerical feature lists.
2. **Missing Imputation:** Choose how missing entries should be handled (`None`, `KNN`, `Iterative`).
> *Note: Avoid selecting `MICE` as it is currently experimental.*


3. **Select Target:** Choose the target column you wish to predict from the dropdown menu.
4. **Build Model:** Trains machine learning regressors and runs a Principal Component Analysis (PCA). Use **Model Report** and **Model Report Plot** to evaluate fit quality.
5. **Calculate:** Applies the model to add `<target>_calc` and `<target>_e` prediction columns to your table.

---

## 8. File Menu

* **Open table:** Loads a new `.csv` file into shared global memory (`table_data`).
* **Save session:** Exports the current application state, loaded tables, and trained model parameters to a binary `.pkl` (pickle) file.

---

## 9. Help Menu

* **Documentation:** Quick access to user documentation and guides.
* **About:** Displays application metadata, version history, license info, and author credits.
* **Dark Mode:** Toggles GUI themes between Light and Dark modes.

---

## 10. Output Directory & File Locations

All generated assets are saved in the `outputs/` folder at the project root:

| Folder Path | Description of Generated Content |
| --- | --- |
| `outputs/tables/` | Exported result spreadsheets (`_final_result_table.csv`, regression performance reports). |
| `outputs/plots/` | Diagnostic plots (HR diagram overview, correlation matrices, PCA plots, mass distribution charts). |
| `outputs/isocfit_outputs/` | Individual PDF fit charts for every star processed in *Verbose* mode. |

---


## 11. Output Interpretation Guide (Tables & Plots)

This section provides a reference for understanding the physical and statistical meaning of the output data generated by S.P.E.C.T.R.A.

---

### A. Results Table (`_final_result_table.csv`)

When a calculation or fitting process completes, the exported CSV table in `outputs/tables/` contains the following primary columns:

| Column | Description & Interpretation |
| :--- | :--- |
| **`Mass_calc`** | **Estimated Stellar Mass ($M_\odot$):** Derived stellar mass computed by the regression pipeline or by 2D grid interpolation. |
| **`Mass_e`** | **Mass Uncertainty ($M_\odot$):** Associated error margin of the mass estimate. Lower values indicate higher confidence in the fit. |
| **`Age_calc`** | **Derived Stellar Age (Myr):** Interpolated age obtained from the HR diagram grid (available in the *Isochrone Fitting* tab). |
| **`Age_e`** | **Age Uncertainty (Myr):** Error margin associated with the interpolated age. |
| **`<target>_calc` / `<target>_e`** | **Custom Target Prediction:** Estimated value and error for the custom target feature selected in the *Mathematical Modeling* tab. |

---

### B. Interpreting Visual Output Plots

Plots saved under `outputs/plots/` provide essential diagnostic insights into your dataset and model quality:

#### 1. Hertzsprung–Russell Diagram (`_hrd_complete.png` & PDFs in `isocfit_outputs/`)
* **Visual Inspection:** Observed stars (data points) are overlaid on the continuous theoretical tracks and isochrones ($\log L$ vs. $T_{\text{eff}}$).
* **Diagnostic Check:** Stars positioned far outside the grid boundaries indicate potential input data issues (erroneous $T_{\text{eff}}$ or $\log L$) or stars that fall outside the supported age/mass ranges of the chosen evolutionary model.

#### 2. Regression Diagnostic Reports (`_visual_report.png` / `Model Report Plot`)
The `_visual_report.png` provides a 4-panel diagnostic dashboard evaluating the statistical validity and performance of the trained regression model (e.g., **KNeighbors Regressor**):

1. **Top-Left (Actual vs. Predicted Target Values):**
   * **Metrics:** Displays $R^2$ score ($R^2 = 0.94$).
   * **Interpretation:** Measures prediction accuracy against the 1:1 ideal line. Points closely aligned along the diagonal indicate high predictive power.

2. **Top-Right (Residual Normality Histogram):**
   * **Metrics:** Shapiro-Wilk / Normality test ($p\text{-value} = 0.02$).
   * **Interpretation:** Checks if prediction errors follow a normal distribution centered at zero. A $p\text{-value} < 0.05$ flags departures from Gaussian normality.

3. **Bottom-Left (Residual Skedasticity):**
   * **Metrics:** Breusch-Pagan / Goldfeld-Quandt test ($p\text{-value} = 0.45$).
   * **Interpretation:** Evaluates variance consistency. A $p\text{-value} > 0.05$ confirms **homoscedasticity**, meaning error variance remains uniform across all prediction ranges.

4. **Bottom-Right (Influence Plot):**
   * **Metrics:** Studentized Residuals ($\hat{\sigma}$) vs. Leverage ($\hat{h}$).
   * **Interpretation:** Identifies influential data points and extreme outliers. Observations crossing the critical Cook's distance bounds (red dashed lines) or thresholds ($\pm 3$) disproportionately impact model fitting.

#### 3. Correlation Matrix (`_correlation_report.png`)
* **Color Scale (-1 to +1):** 
  * Values near **+1 (Blue/Dark)** represent strong positive linear correlation (features increase together).
  * Values near **-1 (Red/Warm)** represent strong inverse correlation.
  * Values near **0** indicate no linear relationship, helping identify which magnitudes/parameters most heavily influence mass prediction.

#### 4. Principal Component Analysis (`_pca_report.png`)
* **Explained Variance Ratio:** Measures how well the top principal components (PC1, PC2) capture the dataset's total variance. If PC1 + PC2 account for >80% of the variance, the feature set effectively captures the underlying physics with minimal noise redundancy.

---

## 12. Known Limitations

* **Session Restoration:** Isn't available yet.
* **MICE Imputation:** The MICE option in Mathematical Modeling is experimental and may raise terminal exceptions.
* **Training Subsampling:** To prevent memory overflow during grid searches and overfitting on dense isochrone grids, mass-magnitude model training caps input samples at 5,000 randomly selected points.