# S.P.E.C.T.R.A.
**S**tellar **P**arameter **E**stimation and **C**alculation **T**ools for **R**esearch and **A**nalysis

S.P.E.C.T.R.A. is a desktop application for deriving stellar parameters — with a
particular focus on stellar mass — from photometric and spectroscopic data. It
combines isochrone fitting against evolutionary-track grids, mass-magnitude
regression modeling, and general-purpose statistical/mathematical tools behind
a single graphical interface.

> This project was previously developed under the name S.T.E.L.A.R.
> ("Stellar Type Examination and Analysis Resource"). All references have
> been renamed to S.P.E.C.T.R.A.

## Features

- **Isochrone Fitting** — locate stars on a Hertzsprung–Russell (HR) diagram
  and interpolate their age and mass against pre-main-sequence evolutionary
  models (Siess 2000, BHAC15).
- **Mass–Magnitude Modeling** — fit and evaluate multiple regression models
  (linear, ridge, lasso, elastic net, Bayesian ridge, SVR, decision trees,
  random forest, gradient boosting, AdaBoost, KNN, ...) to derive a
  mass–magnitude relationship, complete with an automatically generated
  regression report and diagnostic plots.
- **Mathematical Modeling** — general feature-selection, PCA, and
  correlation/statistical analysis tools for exploring a dataset before or
  after parameter fitting.
- **HR Diagram plotting** — visualize fitted stars against evolutionary
  tracks and isochrones, with results saved as image files.
- **First-run data download** — on first launch, S.P.E.C.T.R.A. automatically
  downloads the MADYS stellar evolutionary models and the Siess 2000/BHAC15
  isochrone data tables it depends on.

---

## Installation

Using **Conda** (or Mamba) is the recommended and unified way to install S.P.E.C.T.R.A. across all operating systems. It handles Python, `tkinter` GUI support, and system-level dependencies automatically without compilation errors.

### 1. Clone the repository
```bash
git clone <this-repository-url>
cd spectra

```

### 2. Create the environment

Create the Conda environment using the provided `spectra.yml` configuration:

```bash
conda env create -f spectra.yml

```

### 3. Activate the environment

```bash
conda activate spectra

```

---

### Operating System Specific Configuration

#### macOS / Linux

On Unix-based systems, you can optionally add the project folder to your PATH environment variables so S.P.E.C.T.R.A. can be configured globally:

```bash
# Get the full absolute path of the repository
rota=$(pwd)

# For ZSH users (default shell on macOS):
echo "export SPECTRA=$rota:\$PATH" >> ~/.zshrc
source ~/.zshrc

# For BASH users (default shell on most Linux distributions):
echo "export SPECTRA=$rota:\$PATH" >> ~/.bashrc
source ~/.bashrc

```

#### Windows

On Windows, open **Anaconda Prompt** or **PowerShell** and navigate to the project directory:

```cmd
cd path\to\spectra
conda env create -f spectra.yml
conda activate spectra

```

---

## Running the Application

Always ensure your Conda environment is activated before launching:

```bash
conda activate spectra
python main.py

```

### First-Run Data Download

On the **first launch** — or any time the relevant local data is missing — a small "Downloading Stellar Models" window appears and fetches whichever of the following isn't yet present:

* The BHAC15, PARSEC, and MIST models via
`madys.ModelHandler.download_model(model_name)`. A flag file,
`.stelar_models_downloaded`, is written to the project root once this
succeeds so subsequent launches skip it.
* The `isochrone_models/` folder (Siess 2000 and BHAC15 evolutionary-track
and isochrone data tables), pulled via `gdown` from Google Drive.

Both downloads can take a while depending on your connection and run independently of each other.

---

## Documentation & User Manual

For detailed step-by-step instructions on operating S.P.E.C.T.R.A., please refer to the official [User Manual](Manual.md). The manual covers:

* Input dataset formatting and CSV structure requirements.
* Complete walkthroughs for Isochrone Fitting (`IsocFit`) and Mass-Magnitude Modeling (RMM).
* Parameter tuning and feature selection in the Mathematical Modeling tab.
* Interpretation and export of output diagnostic plots and tables.

---

## Project Structure

```
project-root/
├── main.py                 # entry point (imports from the spectra package)
├── setup.py                # packaging metadata
├── pyproject.toml          # build and dependency specifications
├── spectra.yml             # Conda environment definition
├── icon.png                # application icon
├── requirements.txt        # Python dependencies list
├── README.md               # this file
├── spectra/                # the installable package
│   ├── __init__.py
│   ├── paths.py            # single source of truth for runtime paths
│   ├── interface.py        # main GUI (App, Sidebar, TopMenu)
│   ├── tools.py            # regression models, math/statistical tools
│   ├── StarLocalization.py # isochrone/HR-diagram fitting
│   └── widgets.py          # reusable widgets
├── external/
│   └── themes.json         # custom ttkbootstrap theme definitions
├── isochrone_models/       # evolutionary-track data
└── outputs/                # exported result tables and plots

```

---

## Known Issues / Setup Gaps

* `external/themes.json` must exist before startup; there is currently no fallback if it's missing.
* Building a Mass-Magnitude model caps the training data fed into `RegressionReport` at 5,000 randomly-sampled points (`Sidebar.MAX_TRAINING_SAMPLES` in `interface.py`) to keep the SVR/grid-search step from exhausting memory on the full isochrone grid and avoid an overfitted model.

---

## Authors

* João Paulo Matos Dias Gomes — jpmdgomes.bf@gmail.com
* Maria Jaqueline Vasconcelos — mjvasc@uesc.br
* Adriano Hoth Cerqueira — hoth@uesc.br

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.