# S.P.E.C.T.R.A.
**S**tellar **P**arameter **E**stimation and **C**alculation **T**ools for **R**esearch and **A**nalysis

S.P.E.C.T.R.A. is a modern desktop application for deriving stellar parameters — with a particular focus on stellar mass and age — from photometric and spectroscopic data. It combines 2D Bayesian isochrone fitting against pre-main-sequence evolutionary grids, mass–magnitude machine learning regression modeling, and general-purpose statistical/mathematical tools behind an intuitive graphical interface.

> **Note:** This project was previously developed under the name S.T.E.L.A.R. ("Stellar Type Examination and Analysis Resource"). All references have been updated to S.P.E.C.T.R.A.

---

## Key Features

## Key Features

- **2D Bayesian Isochrone Parameter Estimator** — derives stellar mass ($M_\odot$), age (Myr), and $1\text{-}\sigma$ uncertainties using a full 2D likelihood grid evaluation over the HR diagram combined with a Salpeter/Kroupa IMF prior ($P(M) \propto M^{-1.35}$ for $M \le 0.5$, $M^{-2.35}$ for $M > 0.5$). Supported models: Siess 2000 and BHAC15.
- **⭐ Primary Stellar Parameters Module** — derives multi-band photometric effective temperatures ($T_{\text{eff}}$), spectral types ($\text{SpT}$), surface gravities ($\log g$), bolometric magnitudes ($M_{\text{bol}}$), bolometric luminosities ($\log_{10}(L/L_\odot)$), and stellar radii ($R_*/R_\odot$) following **Bell et al. (2014, MNRAS 444, 1157; `stu1488.pdf`)** Section 3.2. Includes spectroscopic Equivalent Width (EW) analysis ($H\alpha$, $Li\,\text{I}$, $TiO$) for Pre-Main-Sequence (PMS) youth diagnostics and T Tauri activity classification (**CTTS**, **WTTS**, **Field**), alongside machine learning parameter regressors (*RandomForest*, *GradientBoosting*, *SVR*, *KNN*).
- **Goodness-of-Fit Statistical Suite** — computes comprehensive goodness-of-fit metrics ($R^2$, Adjusted $R^2$, RMSE, MAE, $\chi^2$, Reduced $\chi^2$) exported directly to module table outputs and embedded in interactive reports.
- **Automatic Luminosity Conversion** — automatically detects linear luminosity columns (`L`, `lum`, `L/Ls`, `Lsun`) and converts them to logarithmic scale $\log_{10}(L/L_\odot)$.
- **MADYS Models Repository Manager (`📦 Models Manager`)** — dedicated interactive dialog to inspect all 18+ MADYS evolutionary models, view installation status (🟢 Installed / ⚪ Not Installed), mass/age bounds, and download missing grids directly in the background.
- **Dynamic MADYS Model & Filter Engine** — dynamically updates valid mass boundaries, age slider ranges, and supported photometric filter lists (up to 127+ filters per model) upon selecting any model.
- **Interactive Web HTML Reports (`🌐 HTML Report`)** — generates standalone, interactive web reports with dark-themed layouts, embedded base64 distribution plots, Color-Magnitude Diagrams (CMD), Goodness-of-Fit cards, and per-star verbose calculation traces controlled by a `round-toggle` switch.
- **Mass–Magnitude Regression Modeling** — builds and compares multi-model regression pipelines (Linear, Ridge, Lasso, ElasticNet, Bayesian Ridge, SVR, Decision Trees, Random Forest, Gradient Boosting, AdaBoost, KNN) using `MADYS` isochrone grids, generating comprehensive performance reports and 4-panel diagnostic dashboards with flexible magnitude column matching (`Gmag`, `G`, `Jmag`, `J`, etc.).
- **Mathematical Modeling & Exploratory Analysis** — feature selection, missing data imputation (KNN, Iterative), correlation matrices, and Principal Component Analysis (PCA) for dataset exploration.
- **Modular Output Organization** — automatically structures generated files into dedicated subdirectories under `outputs/` (`isochrone_fitting/`, `mass_modeling/`, `primary_parameters/plots/`, `primary_parameters/tables/`, `primary_parameters/reports/`, `math_models/`).
- **Standardized GUI Component Architecture** — unified visual presentation across all 5 main tabs with standardized header cards, aligned action controls, and `round-toggle` verbose switches.
- **Thread-Safe Data & State Management** — centralized `DataManager` preventing race conditions and keeping dataset states consistent across GUI tabs.
- **Integrated Program Updates** — built-in **"Atualizar Programa"** dialog allowing one-click background updates directly from GitHub.
- **Cosmic Light & Dark Themes** — high-contrast cosmic color palettes tailored for research presentation ("Spectra Stellar Light" and "Spectra Deep Space Dark").

---

## Installation

Using **Conda** (or Mamba) is the recommended way to install S.P.E.C.T.R.A. across Windows, macOS, and Linux.

### 1. Clone the repository
```bash
git clone https://github.com/matosjp/spectra.git
cd spectra
```

### 2. Create and activate the Conda environment

```bash
conda env create -f spectra.yml
conda activate spectra
```

---

## Running the Application

### Graphical User Interface (GUI Mode)
Ensure your Conda environment is active before launching:

```bash
conda activate spectra
python main.py
```

### Command-Line Interface (Text Mode & Batch Pipeline)
S.P.E.C.T.R.A. can be executed headlessly from the terminal for automated batch processing across multiple open clusters:

1. **2D Isochrone Fitting (`isocfit`)**:
```bash
python main.py isocfit --input cluster_data.csv --model "BHAC15" --html
```

2. **Mass-Magnitude Machine Learning (`rmm`)**:
```bash
python main.py rmm --input cluster_data.csv --model "bhac15" --filter "G" --age 100 --distance 136.2 --html
```

3. **⭐ Primary Parameters Derivation (`primary`)**:
```bash
python main.py primary --input cluster_data.csv --av 0.3 --distance 412 --html
```

4. **Automated Batch Multi-Cluster Pipeline (`batch`)**:
```bash
# Process a folder of cluster CSV files
python main.py batch --dir path/to/clusters/ --module isocfit --model "Siess 2000"

# Or execute a multi-job JSON pipeline configuration
python main.py batch --config batch_clusters_config.json
```

### First-Run Data Download

On first launch (or if model tables are missing), S.P.E.C.T.R.A. automatically downloads:
* **BHAC15, PARSEC, and MIST models** via `madys.ModelHandler`.
* **Siess 2000 & BHAC15 evolutionary tracks** (`isochrone_models/` folder) via `gdown`.

---

## Documentation & User Manual

For step-by-step operational instructions, please consult the official [User Manual](Manual.md). It covers:
* Input CSV formatting requirements.
* Complete workflows for Isochrone Fitting, ⭐ Primary Parameters, Mass-Magnitude Modeling, and Mathematical Modeling.
* Interpretation of 2D Bayesian posterior probabilities, $1\text{-}\sigma$ uncertainties, Goodness-of-Fit stats, and diagnostic plots.

---

## Project Structure

```
spectra-root/
├── main.py                 # Application entry point
├── setup.py                # Setuptools packaging metadata
├── pyproject.toml          # PEP 621 build specification
├── spectra.yml             # Conda environment definition file
├── Manual.md               # Detailed User Manual
├── README.md               # Project overview
├── generate_test_dataset.py# Synthetic test dataset generator script
├── example_primary_params_dataset.csv # Example test dataset
├── spectra/                # Core Python package
│   ├── __init__.py         # Package metadata and version definition (v1.2.0)
│   ├── state.py            # DataManager: Thread-safe dataset state management
│   ├── bayesian.py         # 2D Bayesian Isochrone Parameter Estimator
│   ├── StarLocalization.py # Isochrone table loader with caching & HRD plotting
│   ├── tools.py            # Regression report, ML engines, Goodness-of-Fit stats & HTML reports
│   ├── widgets.py          # Custom UI dialogs (UpdateWindow, AboutWindow, BusyWindow)
│   ├── interface.py        # Main GUI window (App, Sidebar, TopMenu, Standardized Tab Views)
│   ├── paths.py            # Centralized path definitions and modular outputs management
│   └── primary_parameters/ # Primary Parameters Engine Package
│       ├── __init__.py
│       ├── calibrations.py # Empirical Dwarf Color-Teff-SpT-BC Calibrations (Pecaut & Mamajek 2013)
│       ├── spt_encoder.py  # Spectral Type Numerical Encoder / Decoder
│       ├── photometric_engine.py # Photometric Teff, SpT, log g & Bell et al. (2014) logL/Radius derivation
│       ├── spectroscopic_engine.py # EW Halpha, Li I, TiO index & T Tauri Activity Classifier
│       └── ml_engine.py    # Machine Learning Multi-Parameter Regressors
├── external/
│   └── themes.json         # Custom Light and Dark theme definitions
├── isochrone_models/       # Evolutionary-track data tables
└── outputs/                # Structured output directory by module
    ├── isochrone_fitting/  # Isochrone fitting tables and PDF star plots
    ├── mass_modeling/      # Mass-Magnitude ML tables & diagnostic dashboards
    ├── primary_parameters/ # Primary Parameters outputs
    │   ├── plots/          # Distribution plots & Gaia CMD figures
    │   ├── tables/         # Derived catalog CSV & Goodness-of-Fit statistics
    │   └── reports/        # Standalone interactive HTML reports
    └── math_models/        # General mathematical & PCA outputs
```

---

## Authors

* **João Paulo Matos Dias Gomes** — jpmdgomes.bf@gmail.com
* **Maria Jaqueline Vasconcelos** — mjvasc@uesc.br
* **Adriano Hoth Cerqueira** — hoth@uesc.br

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.