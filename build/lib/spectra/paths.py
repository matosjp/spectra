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

PROJECT_ROOT = os.getcwd()

# --- outputs/ ---------------------------------------------------------
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, 'outputs')
TABLES_DIR = os.path.join(OUTPUTS_DIR, 'tables')
PLOTS_DIR = os.path.join(OUTPUTS_DIR, 'plots')
ISOCFIT_DIR = os.path.join(OUTPUTS_DIR, 'isocfit_outputs')

# --- external data / config -------------------------------------------
EXTERNAL_DIR = os.path.join(PROJECT_ROOT, 'external')
THEMES_PATH = os.path.join(EXTERNAL_DIR, 'themes.json')
ICON_PATH = os.path.join(PROJECT_ROOT, 'icon.png')
ISOCHRONE_MODELS_DIR = os.path.join(PROJECT_ROOT, 'isochrone_models')

# --- first-run switch ---------------------------------------------------
MODELS_FLAG_FILE = os.path.join(PROJECT_ROOT, '.stelar_models_downloaded')
REQUIRED_MODELS = ['bhac15', 'parsec', 'mist']
ISOCHRONE_MODELS_URL = 'https://drive.google.com/drive/folders/1KE3X647EJJtYFjv3pknPge02R2Rf92MR?usp=sharing'

# Make sure every output directory exists up front, regardless of which
# module/feature runs first.
for _dir in (OUTPUTS_DIR, TABLES_DIR, PLOTS_DIR, ISOCFIT_DIR):
    os.makedirs(_dir, exist_ok=True)