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
  isochrone data tables it depends on (see below).


## Installation

It's strongly recommended to install S.P.E.C.T.R.A. into an isolated virtual
environment rather than your system/base Python — this avoids version
conflicts with other projects (`madys`, `scikit-learn`, and `statsmodels` in
particular tend to pull in specific dependency versions) and makes it easy
to start clean if something goes wrong. Pick **one** of the two options
below.

```bash
git clone <this-repository-url>
cd spectra
```

### Option A — `venv` (built into Python)

```bash
python -m venv .venv

# activate it:
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate            # Windows (cmd.exe)
.venv\Scripts\Activate.ps1        # Windows (PowerShell)

pip install --upgrade pip
pip install -r requirements.txt
```

### Option B — conda / mamba

```bash
conda create -n spectra python=3.11
conda activate spectra

pip install -r requirements.txt
```
### Requirements

- Python 3.9+
- A Python distribution with **Tk** support (`tkinter`). This ships with
  Python on Windows/macOS; on Linux you typically need the system package:
  ```bash
  sudo apt install python3-tk        # Debian/Ubuntu
  sudo dnf install python3-tkinter   # Fedora
  ```
  If you're using a **conda** environment, install it via conda instead so
  it's linked correctly inside the env: `conda install tk`.


`requirements.txt`:
```
ttkbootstrap
Pillow
numpy
pandas
scipy
scikit-learn
statsmodels
matplotlib
seaborn
missingno
madys
gdown
```

`madys` additionally depends on the TAP Gaia Query package (`tap`), which
should be installed *before* `madys` to avoid pulling in an unrelated PyPI
package of the same name:

```bash
pip install git+https://github.com/mfouesneau/tap.git
pip install madys
```

(`ttkbootstrap`, `madys`, and `gdown` aren't on the default conda channels,
so `pip install` inside the activated conda environment is the simplest
path — just make sure the environment is activated first, so packages land
inside it rather than your base environment.)

---

Once dependencies are installed (in either environment), you can also
install S.P.E.C.T.R.A. itself as a package:

```bash
pip install .
```

Remember to activate the same environment (`source .venv/bin/activate` or
`conda activate spectra`) every time before running the app in a new
terminal session — see below.

## Running the application

```bash
python main.py
```

On the **first launch** — or any time the relevant local data is
missing — a small "Downloading Stellar Models" window appears and fetches
whichever of the following isn't yet present:

- The BHAC15, PARSEC, and MIST models via
  `madys.ModelHandler.download_model(model_name)`. A flag file,
  `.stelar_models_downloaded`, is written to the project root once this
  succeeds so subsequent launches skip it. Delete this flag file to force
  a re-download.
- The `isochrone_models/` folder (Siess 2000 and BHAC15 evolutionary-track
  and isochrone data tables), pulled via `gdown` from
  [this shared Google Drive folder](https://drive.google.com/drive/folders/1KE3X647EJJtYFjv3pknPge02R2Rf92MR?usp=sharing).
  This one is checked by folder presence rather than a flag file — delete
  or empty `isochrone_models/` to force a re-download.

Both downloads can take a while depending on your connection and run
independently of each other, so if only one is missing, only that one is
fetched.

## 📖 Documentation & User Manual

For detailed step-by-step instructions on operating SPECTRA, please refer to the official [User Manual](Manual.md). The manual covers:
* Input dataset formatting and CSV structure requirements.
* Complete walkthroughs for Isochrone Fitting (`IsocFit`) and Mass-Magnitude Modeling (RMM).
* Parameter tuning and feature selection in the Mathematical Modeling tab.
* Interpretation and export of output diagnostic plots and tables.

## Project structure

```
project-root/
├── main.py                # entry point (imports from the spectra package)
├── setup.py                # packaging metadata
├── icon.png                 # application icon
├── requirements.txt           # Python dependencies
├── README.md                   # this file
├── spectra/                       # the installable package
│   ├── __init__.py
│   ├── paths.py                      # single source of truth for every runtime path (outputs/, isochrone_models/, etc.)
│   ├── interface.py                   # main GUI (App, Sidebar, TopMenu)
│   ├── tools.py                         # regression models, math/statistical tools
│   ├── StarLocalization.py                # isochrone/evolutionary-track reading & HR-diagram fitting
│   └── widgets.py                           # reusable widgets (SessionManager, AboutWindow, ModelDownloadWindow, BusyWindow, SizeNotifier)
├── external/
│   └── themes.json                            # custom ttkbootstrap theme definitions (light/dark)
├── isochrone_models/
│   ├── SIESS/
│   │   ├── Grid/OV02/                            # Siess 2000 evolutionary tracks
│   │   └── Isoc/                                  # Siess 2000 isochrone tables
│   └── BAHC15/
│       ├── Grid/BWeLM/                            # BHAC15 evolutionary tracks
│       └── Isoc/                                   # BHAC15 isochrone tables
└── outputs/
    ├── tables/                                      # exported result tables (CSV)
    ├── plots/                                         # regression/correlation/PCA/HRD-summary report images
    └── isocfit_outputs/                                 # per-star HR-diagram fit plots (saved when requested)
```

> **Note:** `main.py`, `setup.py`, `icon.png`, and the `external/`,
> `isochrone_models/`, and `outputs/` directories stay at the project root —
> only the application's Python modules live inside the `spectra/` package.
> The `external/` and `isochrone_models/` directories (and their contents)
> are required at runtime but are not tracked in this upload — see *Known
> Issues* below. `outputs/` and its subfolders **are** created automatically
> on startup (via `spectra/paths.py`), so you don't need to create those
> yourself.

## Known issues / setup gaps

- `external/themes.json` must exist before startup; there is currently no
  fallback if it's missing.
- The exact `model_grid` identifiers MADYS expects for
  `madys.ModelHandler.download_model()` haven't been confirmed against a
  live install — if the first-run download reports failures, see
  *Troubleshooting* below.
- Building a Mass-Magnitude model caps the training data fed into
  `RegressionReport` at 5,000 randomly-sampled points
  (`Sidebar.MAX_TRAINING_SAMPLES` in `interface.py`) to keep the SVR/grid-search
  step from exhausting memory on the full isochrone grid (which defaults to
  `n_steps=[1000, 1000]`, i.e. up to ~1,000,000 points). This trades a bit of
  training-set size for the model actually finishing — see *Troubleshooting*
  if you want to tune it.

## Troubleshooting

**"Model Download" warning listing `list index out of range` for one or
more models.** This means `madys.ModelHandler.download_model(model_name)`
didn't recognize the short name (`bhac15`, `parsec`, `mist`) passed to it —
MADYS expects an exact `model_grid` identifier, which may differ from the
family name. The warning dialog now also prints whatever
`madys.ModelHandler.available()` reports, so you can read off the correct
identifier(s) from there and update `REQUIRED_MODELS` in `spectra/paths.py`
accordingly. You can also check this directly:
```bash
python -c "import madys; madys.ModelHandler.available()"
```
Until this is fixed, isochrone fitting features that depend on the failed
model(s) won't work, but the rest of the app is unaffected — dismissing the
warning lets you continue.


## Authors

+ João Paulo Matos Dias Gomes — jpmdgomes.bf@gmail.com
+ Maria Jaqueline Vasconcelos — mjvasc@uesc.br
+ Adriano Hoth Cerqueira — hoth@uesc.br

## License

Not yet specified.