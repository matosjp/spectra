"""
Central, single-source-of-truth path definitions for S.P.E.C.T.R.A.

Every path here is resolved to an ABSOLUTE path once, at import time,
based on the working directory the app was launched from (PROJECT_ROOT).
Every other module should import the paths it needs from here instead of
recomputing os.getcwd() or relying on os.chdir() — that pattern is what
caused output files (plots, tables) to sometimes land outside outputs/,
and to sometimes be unreadable right after being written, depending on
what order features were used in and what the current working directory
happened to be at that moment.
"""
import os

# Derive absolute project root from file location regardless of current working directory
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(_CURRENT_DIR).lower() == 'spectra':
    PROJECT_ROOT = os.path.dirname(_CURRENT_DIR)
else:
    PROJECT_ROOT = _CURRENT_DIR

# --- outputs/ organized by module --------------------------------------
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, 'outputs')

# Module-specific output roots
ISOCHRONE_OUTPUTS_DIR = os.path.join(OUTPUTS_DIR, 'isochrone_fitting')
MASS_MODELING_OUTPUTS_DIR = os.path.join(OUTPUTS_DIR, 'mass_modeling')
PRIMARY_PARAMS_OUTPUTS_DIR = os.path.join(OUTPUTS_DIR, 'primary_parameters')
MATH_MODELS_OUTPUTS_DIR = os.path.join(OUTPUTS_DIR, 'math_models')

# Primary Parameters Subfolders
PRIMARY_PARAMS_PLOTS_DIR = os.path.join(PRIMARY_PARAMS_OUTPUTS_DIR, 'plots')
PRIMARY_PARAMS_TABLES_DIR = os.path.join(PRIMARY_PARAMS_OUTPUTS_DIR, 'tables')
PRIMARY_PARAMS_REPORTS_DIR = os.path.join(PRIMARY_PARAMS_OUTPUTS_DIR, 'reports')

# Legacy / Global paths
TABLES_DIR = os.path.join(OUTPUTS_DIR, 'tables')
PLOTS_DIR = os.path.join(OUTPUTS_DIR, 'plots')
ISOCFIT_DIR = ISOCHRONE_OUTPUTS_DIR
RML_DIR = MASS_MODELING_OUTPUTS_DIR
STATS_DIR = MATH_MODELS_OUTPUTS_DIR
SAMPLES_DIR = os.path.join(PROJECT_ROOT, 'samples')
CACHE_DIR = os.path.join(PROJECT_ROOT, '.cache')

# --- external data / config -------------------------------------------
EXTERNAL_DIR = os.path.join(PROJECT_ROOT, 'external')
THEMES_PATH = os.path.join(EXTERNAL_DIR, 'themes.json')
ICON_PATH = os.path.join(PROJECT_ROOT, 'icon.png')
ISOCHRONE_MODELS_DIR = os.path.join(PROJECT_ROOT, 'isochrone_models')

# --- first-run switch ---------------------------------------------------
MODELS_FLAG_FILE = os.path.join(PROJECT_ROOT, '.stelar_models_downloaded')
REQUIRED_MODELS = ["bhac15_p0.00"]
ISOCHRONE_MODELS_URL = 'https://drive.google.com/drive/folders/1KE3X647EJJtYFjv3pknPge02R2Rf92MR?usp=sharing'

def ensure_directories_exist() -> None:
    """Ensures that all necessary application output directories exist on disk."""
    for _dir in (
        OUTPUTS_DIR, TABLES_DIR, PLOTS_DIR, ISOCFIT_DIR,
        ISOCHRONE_OUTPUTS_DIR, MASS_MODELING_OUTPUTS_DIR,
        PRIMARY_PARAMS_OUTPUTS_DIR, MATH_MODELS_OUTPUTS_DIR,
        PRIMARY_PARAMS_PLOTS_DIR, PRIMARY_PARAMS_TABLES_DIR, PRIMARY_PARAMS_REPORTS_DIR
    ):
        os.makedirs(_dir, exist_ok=True)

# Make sure every output directory exists up front upon import
ensure_directories_exist()
ensure_directories = ensure_directories_exist