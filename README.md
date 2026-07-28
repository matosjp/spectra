# S.P.E.C.T.R.A.
**S**tellar **P**arameter **E**stimation and **C**alculation **T**ools for **R**esearch and **A**nalysis

S.P.E.C.T.R.A. is a modern desktop application for deriving stellar parameters — with a particular focus on stellar mass and age — from photometric and spectroscopic data. It combines 2D Bayesian isochrone fitting against pre-main-sequence evolutionary grids, mass–magnitude machine learning regression modeling, and general-purpose statistical/mathematical tools behind an intuitive graphical interface.

> **Note:** This project was previously developed under the name S.T.E.L.A.R. ("Stellar Type Examination and Analysis Resource"). All references have been updated to S.P.E.C.T.R.A.

---

## Key Features

- **2D Bayesian Isochrone Parameter Estimator** — derives stellar mass ($M_\odot$), age (Myr), and $1\text{-}\sigma$ uncertainties using a full 2D likelihood grid evaluation over the HR diagram combined with a Salpeter/Kroupa IMF prior ($P(M) \propto M^{-1.35}$ for $M \le 0.5$, $M^{-2.35}$ for $M > 0.5$). Supported models: Siess 2000 and BHAC15.
- **Automatic Luminosity Conversion** — automatically detects linear luminosity columns (`L`, `lum`, `L/Ls`, `Lsun`) and converts them to logarithmic scale $\log_{10}(L/L_\odot)$.
- **Mass–Magnitude Regression Modeling** — builds and compares multi-model regression pipelines (Linear, Ridge, Lasso, ElasticNet, Bayesian Ridge, SVR, Decision Trees, Random Forest, Gradient Boosting, AdaBoost, KNN) using `MADYS` isochrone grids, generating comprehensive performance reports and 4-panel diagnostic dashboards.
- **Mathematical Modeling & Exploratory Analysis** — feature selection, missing data imputation (KNN, Iterative), correlation matrices, and Principal Component Analysis (PCA) for dataset exploration.
- **Dedicated Output Plots** — interactive viewports and high-resolution export for **`📈 Mass Plot`**, **`⏳ Age Plot`**, and **`🌌 HR Diagram Plot`**.
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

Ensure your Conda environment is active before launching:

```bash
conda activate spectra
python main.py
```

### First-Run Data Download

On first launch (or if model tables are missing), S.P.E.C.T.R.A. automatically downloads:
* **BHAC15, PARSEC, and MIST models** via `madys.ModelHandler`.
* **Siess 2000 & BHAC15 evolutionary tracks** (`isochrone_models/` folder) via `gdown`.

---

## Documentation & User Manual

For step-by-step operational instructions, please consult the official [User Manual](Manual.md). It covers:
* Input CSV formatting requirements.
* Complete workflows for Isochrone Fitting, Mass-Magnitude Modeling, and Mathematical Modeling.
* Interpretation of 2D Bayesian posterior probabilities, $1\text{-}\sigma$ uncertainties, and diagnostic plots.

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
├── spectra/                # Core Python package
│   ├── __init__.py         # Package metadata and version definition (v1.1.0)
│   ├── state.py            # [NEW] DataManager: Thread-safe dataset state management
│   ├── bayesian.py         # [NEW] 2D Bayesian Isochrone Parameter Estimator
│   ├── StarLocalization.py # Isochrone table loader with caching & HRD plotting
│   ├── tools.py            # Regression report, ML models, and result visualization
│   ├── widgets.py          # Custom UI dialogs (UpdateWindow, AboutWindow, BusyWindow)
│   ├── interface.py        # Main GUI window (App, Sidebar, TopMenu, Tab Views)
│   └── paths.py            # Centralized path definitions and directory creation
├── external/
│   └── themes.json         # Custom Light and Dark theme definitions
├── isochrone_models/       # Evolutionary-track data tables
└── outputs/                # Exported CSV tables and diagnostic plot figures
```

---

## Authors

* **João Paulo Matos Dias Gomes** — jpmdgomes.bf@gmail.com
* **Maria Jaqueline Vasconcelos** — mjvasc@uesc.br
* **Adriano Hoth Cerqueira** — hoth@uesc.br

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.