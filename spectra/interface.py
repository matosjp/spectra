# S.P.E.C.T.R.A. - Stellar Parameter Estimation and Calculation Tools for Research and Analysis
# Copyright (C) 2026  João Paulo Matos Dias Gomes, Maria Jaqueline Vasconcelos, Adriano Hoth Cerqueira
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact:
#   João Paulo Matos Dias Gomes — jpmdgomes.bf@gmail.com
#   Maria Jaqueline Vasconcelos — mjvasc@uesc.br
#   Adriano Hoth Cerqueira — hoth@uesc.br
#   Universidade Estadual de Santa Cruz (UESC), Ilhéus - BA, Brasil

from traceback import print_tb

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import ToastNotification   
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import KNNImputer, IterativeImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import missingno as msno
import os
import sys
import io
import pandas as pd
import numpy as np
import webbrowser
import subprocess
import madys

try:
    from .state import DataManager
    from . import __version__
    from .StarLocalization import intpol, interp
    from .tools import (
        RegressionReport, MathModels, ResultDisplay, FilterValues, interpolmass,
        get_available_madys_models, get_madys_model_metadata, find_mag_column,
        generate_spectra_html_report, generate_primary_params_html_report, generate_primary_params_analysis
    )
    from .primary_parameters import estimate_photometric_dataset, estimate_spectroscopic_dataset, PrimaryParameterMLEngine
    from .widgets import SessionManager, AboutWindow, ModelDownloadWindow, BusyWindow, UpdateWindow, MadysModelManagerWindow
    from .paths import (
        PROJECT_ROOT, OUTPUTS_DIR, TABLES_DIR, PLOTS_DIR, ISOCFIT_DIR,
        RML_DIR, STATS_DIR, SAMPLES_DIR, CACHE_DIR,
        ensure_directories, THEMES_PATH, ICON_PATH, ISOCHRONE_MODELS_DIR, MODELS_FLAG_FILE,
        REQUIRED_MODELS, ISOCHRONE_MODELS_URL
    )
except (ImportError, ValueError):
    try:
        from spectra.state import DataManager
        from spectra import __version__
        from spectra.StarLocalization import intpol, interp
        from spectra.tools import (
            RegressionReport, MathModels, ResultDisplay, FilterValues, interpolmass,
            get_available_madys_models, get_madys_model_metadata, find_mag_column,
            generate_spectra_html_report, generate_primary_params_html_report, generate_primary_params_analysis
        )
        from spectra.primary_parameters import estimate_photometric_dataset, estimate_spectroscopic_dataset, PrimaryParameterMLEngine
        from spectra.widgets import SessionManager, AboutWindow, ModelDownloadWindow, BusyWindow, UpdateWindow, MadysModelManagerWindow
        from spectra.paths import (
            PROJECT_ROOT, OUTPUTS_DIR, TABLES_DIR, PLOTS_DIR, ISOCFIT_DIR,
            RML_DIR, STATS_DIR, SAMPLES_DIR, CACHE_DIR,
            ensure_directories, THEMES_PATH, ICON_PATH, ISOCHRONE_MODELS_DIR, MODELS_FLAG_FILE,
            REQUIRED_MODELS, ISOCHRONE_MODELS_URL
        )
    except (ImportError, ModuleNotFoundError):
        from state import DataManager
        from StarLocalization import intpol, interp
        from tools import (
            RegressionReport, MathModels, ResultDisplay, FilterValues, interpolmass,
            get_available_madys_models, get_madys_model_metadata, find_mag_column,
            generate_spectra_html_report, generate_primary_params_html_report, generate_primary_params_analysis
        )
        from primary_parameters import estimate_photometric_dataset, estimate_spectroscopic_dataset, PrimaryParameterMLEngine
        from widgets import SessionManager, AboutWindow, ModelDownloadWindow, BusyWindow, UpdateWindow, MadysModelManagerWindow
        from paths import (
            PROJECT_ROOT, OUTPUTS_DIR, TABLES_DIR, PLOTS_DIR, ISOCFIT_DIR,
            RML_DIR, STATS_DIR, SAMPLES_DIR, CACHE_DIR,
            ensure_directories, THEMES_PATH, ICON_PATH, ISOCHRONE_MODELS_DIR, MODELS_FLAG_FILE,
            REQUIRED_MODELS, ISOCHRONE_MODELS_URL
        )

# Global backward-compatibility wrapper for table_data
def _get_table_data():
    return DataManager.get_dataset()

# Kept for backwards compatibility with any code/notes referring to the old
# names; all now point at the single source of truth in paths.py.
setup_path = PROJECT_ROOT
default_pth = PROJECT_ROOT
table_output = TABLES_DIR
themes_path = THEMES_PATH

class App(ttk.Window):
    def __init__(self):
        super().__init__()
        self.target = tk.StringVar()
        self.title("S.P.E.C.T.R.A")
        self.geometry("960x650")
        self.minsize(900, 600)
        self.current_theme = 'light_theme'  # Default theme
        self.load_custom_theme(self.current_theme)
        self.dark_mode_var = tk.BooleanVar(value=True if self.current_theme == 'dark_theme' else False)

        # Hide the main window until the first-run model download (if any)
        # has finished, so the user isn't dropped into a half-ready app.
        self.withdraw()
        self.check_first_run_models()

    def check_first_run_models(self):
        """
        First opening switch: on first launch (or any time the relevant
        data is missing), download whichever of the following are absent
        before showing the main interface:
          - the MADYS stellar models (BHAC15, PARSEC, MIST) needed for
            isochrone fitting;
          - the Siess 2000 / BHAC15 evolutionary-track and isochrone data
            tables under isochrone_models/, fetched from Google Drive.
        Each piece is checked independently, so re-running after deleting
        just one of them only re-downloads that one.
        """
        models_ready = os.path.exists(MODELS_FLAG_FILE)
        isochrones_ready = (
            os.path.isdir(ISOCHRONE_MODELS_DIR) and len(os.listdir(ISOCHRONE_MODELS_DIR)) > 0
        )

        if models_ready and isochrones_ready:
            self.create_widgets()
            self.deiconify()
            return

        def _on_models_ready(failed):
            # Only mark the MADYS models as done if none of them failed;
            # the isochrone-data check is independent (folder presence),
            # so it doesn't need a separate flag file.
            failed_names = {name for name, _ in failed}
            if not models_ready and not (failed_names & set(REQUIRED_MODELS)):
                with open(MODELS_FLAG_FILE, 'w') as f:
                    f.write('\n'.join(REQUIRED_MODELS))
            self.create_widgets()
            self.deiconify()

        ModelDownloadWindow(
            self,
            models=[] if models_ready else REQUIRED_MODELS,
            on_complete=_on_models_ready,
            isochrone_url=None if isochrones_ready else ISOCHRONE_MODELS_URL,
            isochrone_dest=ISOCHRONE_MODELS_DIR,
        )

    def load_custom_theme(self, theme_name):
        if os.path.exists(THEMES_PATH):
            try:
                self.style.load_user_themes(THEMES_PATH)
            except Exception as e:
                print(f"Warning: Could not load custom theme file {THEMES_PATH}: {e}")

        if theme_name in self.style.theme_names():
            self.style.theme_use(theme_name)
        else:
            # Fallback configuration or manual switch if needed
            self.style.theme_use(theme_name)

    
    def change_app_style(self):
        # Determine the new theme based on the checkbutton state
        if self.dark_mode_var.get():
            new_theme = 'dark_theme'
        else:
            new_theme = 'light_theme'

        # Apply the theme safely
        if new_theme in self.style.theme_names():
            self.style.theme_use(new_theme)
        else:
            self.load_custom_theme(new_theme)
            
        # Keep your internal state tracking variable updated too
        self.current_theme = new_theme

        self.sidebar.refresh_sidebar()

    def update_program(self):
        """
        Open the update window to check for and apply updates.
        """
        UpdateWindow(self)

    def create_widgets(self):
        self.sidebar = Sidebar(self)
        self.sidebar.pack(side=LEFT, fill=Y)
        self.top_menu = TopMenu(self)
        self.top_menu.pack(side=TOP, fill=X)

    def show_result_plot(self, target_type='Mass'):
        tab1 = table_data
        if tab1 is None:
            messagebox.showinfo("Result Plot", "No data table loaded. Please open a CSV file first.")
            return

        method = self.sidebar.method
        feature_name = None
        target_name = None

        if method == 'MMR':
            targ = 'Mass'
            target_name = 'Mass'
            calc_col = 'Mass_calc'
            err_col = 'Mass_e'
            filter_col = f'{self.sidebar.selected_filter.get()}mag'
            if filter_col not in tab1.columns:
                messagebox.showinfo("Result Plot", f"Column '{filter_col}' not found in dataset.")
                return
            x = tab1[filter_col].values

        elif method == 'ISO':
            if 'Teff' not in tab1.columns:
                messagebox.showinfo("Result Plot", "Column 'Teff' not found in dataset.")
                return
            x = tab1['Teff'].values

            if target_type == 'Age':
                targ = 'Age'
                target_name = 'Age (Myr)'
                calc_col = 'Age_calc (Myr)'
                err_col = 'Age_e (Myr)'
            else:
                targ = 'Mass'
                target_name = 'Mass'
                calc_col = 'Mass_calc'
                err_col = 'Mass_e'

        else:
            targ = self.sidebar.target.get()
            target_name = targ
            calc_col = targ + '_calc'
            err_col = targ + '_e'
            selected_feats = self.sidebar.selected_features
            if isinstance(selected_feats, list) and len(selected_feats) == 1:
                feature_name = selected_feats[0]
                x = tab1[feature_name].values
            elif targ in tab1.columns:
                feature_name = f"Observed {targ}"
                x = tab1[targ].values
            else:
                feature_name = "Sample Index"
                x = np.arange(1, len(tab1) + 1)

        if calc_col not in tab1.columns or err_col not in tab1.columns:
            messagebox.showinfo("Result Plot", f"No calculation result available for target '{target_name or targ}'. Please run 'Locate Stars' or 'Calculate' first.")
            return

        y = tab1[calc_col].values
        yerr = tab1[err_col].values

        fra = ResultDisplay(x, y, yerr, method, feature_name=feature_name, target_name=target_name)
        if fra:
            fra.res_plot(save_file=True)

            plot_window = ttk.Toplevel(self)
            plot_window.title("Results Plot")

            photo = Image.open(os.path.join(PLOTS_DIR, '_results_display.png')).resize((800, 600))
            image_tk = ImageTk.PhotoImage(photo)

            image_label = ttk.Label(plot_window, image=image_tk)
            image_label.pack(padx=20, pady=20)

            image_label.image = image_tk
        else:
            messagebox.showinfo("Result Plot", "No result data available.")

    def show_hrd_plot(self):
        tab1 = table_data
        model = self.sidebar.iso_selected_model.get()

        if 'Mass_calc' in tab1.columns:
            plot_HRD(tab1, model)

            # Create a new Toplevel window
            plot_window = ttk.Toplevel(self)
            plot_window.title("Hertzpruntg-Russel Diagram Plot")

            # Load the image and scale it to fit the window
            photo = Image.open(os.path.join(PLOTS_DIR, '_hrd_complete.png')).resize((800, 600))
            image_tk = ImageTk.PhotoImage(photo)

            # Create a Label to display the image
            image_label = ttk.Label(plot_window, image=image_tk)
            image_label.pack(padx=20, pady=20)

            # Keep a reference to the image to prevent garbage collection
            image_label.image = image_tk

        else:
            messagebox.showinfo("Hertzpruntg-Russel Diagram Plot", "No result data available.")

    def show_report_plot(self):
        method = self.sidebar.method
        if method == 'MMR' or method == 'MOD':

            plot_window = ttk.Toplevel(self)
            plot_window.title("Mass-Magnitude Relationship Regression")

            # Load the image and scale it to fit the window
            photo = Image.open(os.path.join(PLOTS_DIR, '_visual_report.png')).resize((800, 600))
            image_tk = ImageTk.PhotoImage(photo)

            # Create a Label to display the image
            image_label = ttk.Label(plot_window, image=image_tk)
            image_label.pack(padx=20, pady=20)

            # Keep a reference to the image to prevent garbage collection
            image_label.image = image_tk

        else:
            messagebox.showinfo("Regression Model Analysis Plot", "No result data available.")

    def show_table(self):
        tab1 = table_data

        table_window = tk.Toplevel(self)
        table_window.title("Final Result Table")
        table_window.geometry('1280x720')

        table_text = ttk.Treeview(table_window, columns=tab1.columns, show='headings')

        table_text["columns"] = list(tab1.columns)
        table_text["show"] = "headings"

        for col in table_text["columns"]:
            table_text.heading(col, text=col)
            table_text.column(col, anchor="center")

        for index, row in tab1.iterrows():
            table_text.insert("", "end", values=list(row))

        table_text.pack(fill=BOTH, expand=True)

        scrollbarh = ttk.Scrollbar(table_window, orient="horizontal", command=table_text.xview)
        scrollbarv = ttk.Scrollbar(table_window, orient="vertical", command=table_text.yview)
        scrollbarh.place(relx=0, rely=1, relwidth=1, anchor='sw')
        scrollbarv.place(relx=1, rely=0, relheight=1, anchor='ne')

    def show_report(self):
        if hasattr(self.sidebar, 'report') and self.sidebar.report is not None:
            tab1 = self.sidebar.report.round(6)
            table_window = tk.Toplevel(self)
            table_window.title("Regression Report Table")
            table_window.geometry('1920x400')

            table_text = ttk.Treeview(table_window, columns=tab1.columns, show='headings')

            table_text["columns"] = list(tab1.columns)
            table_text["show"] = "headings"

            for col in table_text["columns"]:
                table_text.heading(col, text=col)
                table_text.column(col, anchor="center")

            for index, row in tab1.iterrows():
                table_text.insert("", "end", values=list(row))

            table_text.pack(fill=BOTH, expand=True)
        else:
            toast = ToastNotification(
                title='Regression Report',
                message="The regression models wasn't built yet.",
                duration=5000,
                bootstyle='light'
            )
            toast.show_toast()

    def generate_html_report(self):
        if hasattr(self.sidebar, 'report') and self.sidebar.report is not None:
            try:
                report_df = self.sidebar.report
                model_name = self.sidebar.selected_model.get() if hasattr(self.sidebar, 'selected_model') else 'MADYS'
                filter_name = self.sidebar.selected_filter.get() if hasattr(self.sidebar, 'selected_filter') else 'G'
                age_myr = self.sidebar.scale_int.get() if hasattr(self.sidebar, 'scale_int') else 100
                mass_min = self.sidebar.low_int.get() if hasattr(self.sidebar, 'low_int') else 0.1
                mass_max = self.sidebar.hig_int.get() if hasattr(self.sidebar, 'hig_int') else 1.5
                dataset_df = DataManager.get_dataset()
                
                filepath = generate_spectra_html_report(
                    report_df, model_name, filter_name, age_myr, (mass_min, mass_max), dataset_df=dataset_df
                )
                ToastNotification(
                    title='HTML Report Generated',
                    message=f"Interactive HTML report generated and opened in browser:\n{filepath}",
                    duration=5000,
                    bootstyle='success'
                ).show_toast()
            except Exception as e:
                messagebox.showerror("HTML Report Error", f"Failed to generate HTML report:\n{e}")
        else:
            toast = ToastNotification(
                title='Regression Report',
                message="The regression models haven't been built yet. Please click 'Build Model' first.",
                duration=5000,
                bootstyle='light'
            )
            toast.show_toast()

    def choosing_target(self):
        plot_window = ttk.Toplevel(self)
        plot_window.title("Mathematical Modeling: Step 1")

        # Load the image and scale it to fit the window
        photo = Image.open(os.path.join(PLOTS_DIR, '_correlation_report.png')).resize((600, 800))
        image_tk = ImageTk.PhotoImage(photo)

        # Create a Label to display the image
        image_label = ttk.Label(plot_window, image=image_tk)
        image_label.pack(padx=20, pady=20)

        # Keep a reference to the image to prevent garbage collection
        image_label.image = image_tk

    def pca_analysis(self):
        plot_window = ttk.Toplevel(self)
        plot_window.title("Mathematical Modeling: Step 2")

        # Load the image and scale it to fit the window
        photo = Image.open(os.path.join(PLOTS_DIR, '_pca_report.png')).resize((800, 600))
        image_tk = ImageTk.PhotoImage(photo)

        # Create a Label to display the image
        image_label = ttk.Label(plot_window, image=image_tk)
        image_label.pack(padx=20, pady=20)

        # Keep a reference to the image to prevent garbage collection
        image_label.image = image_tk

class Sidebar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=5)
        # Initialize variables

        global table_data
        table_data = None
        self.filtered_data = None
        self.save_var = tk.IntVar()
        self.master = parent
        self.selected_features = []
        self.features = []
        self.method = tk.StringVar()
        self.comp_method = tk.StringVar()
        self.target = tk.StringVar()
        self.selected_model = tk.StringVar()
        self.iso_selected_model = tk.StringVar()
        self.selected_filter = tk.StringVar()
        self.cluster_dist = tk.DoubleVar()
        self.low_int = tk.DoubleVar()
        self.hig_int = tk.DoubleVar()
        self.teff = tk.DoubleVar()
        self.logl = tk.DoubleVar()
        self.check_var = ttk.IntVar()
        self.scale_int = tk.IntVar()
        self.current_theme = ttk.Style().theme_use()

        # Mass-Magnitude Regression attributes
        self.report = None
        self.model = None
        self.X = None
        self.y = None
        self.th_model_data = None

        self.create_widgets()
        self.pack(side=LEFT, fill=Y)

    def create_widgets(self):
        self.style = ttk.Style()
        current_theme = self.style.theme_use()
        self.style.configure('lefttab.TNotebook',
                             tabposition=tk.W + tk.N,
                             tabplacement=tk.N + tk.EW)
        self.style.theme_settings(current_theme,
                                  {"TNotebook.Tab": {"configure": {"padding": [12, 8]}}})

        self.notebook = ttk.Notebook(self, style='lefttab.TNotebook')
        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.page0 = ttk.Frame(self.notebook, width=580, height=700)
        self.page1 = ttk.Frame(self.notebook, width=580, height=700)
        self.page2 = ttk.Frame(self.notebook, width=580, height=700)
        self.page3 = ttk.Frame(self.notebook, width=580, height=700)
        self.page4 = ttk.Frame(self.notebook, width=580, height=700)
        self.page4 = ttk.Frame(self.notebook, width=580, height=700)

        self.notebook.add(self.page0, text='Home', sticky="nsew")
        self.notebook.add(self.page1, text='Isochrone Fitting', sticky="nsew")
        self.notebook.add(self.page2, text='Mass-Magnitude Modeling', sticky="nsew")
        self.notebook.add(self.page3, text='Primary Parameters', sticky="nsew")
        self.notebook.add(self.page4, text='Mathematical Modeling', sticky="nsew")

        self.apply_styles()

        self.setup_home_ui(self.page0)
        self.setup_isocfit_ui(self.page1)
        self.setup_rml_ui(self.page2)
        self.setup_primary_params_ui(self.page3)
        self.setup_modeling_ui(self.page4)

       #  self.setup_spectro_ui(self.page2)
       #  self.setup_statistical_ui(self.page4)

    def apply_styles(self):
        # Update the notebook style
        self.style = ttk.Style()
        current_theme = self.style.theme_use()
        self.style.configure('lefttab.TNotebook',
                             tabposition=tk.W + tk.N,
                             tabplacement=tk.N + tk.EW)
        self.style.theme_settings(current_theme,
                                  {"TNotebook.Tab": {"configure": {"padding": [12, 8]}}})

    def refresh_sidebar(self):
        # Clear existing widgets and recreate them
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()

    def setup_home_ui(self, frame):
        container = ttk.Frame(frame, padding=20)
        container.pack(expand=True, fill=BOTH)

        photo = Image.open(ICON_PATH).resize((320, 320))
        image_tk = ImageTk.PhotoImage(photo)

        image_label = ttk.Label(container, image=image_tk)
        image_label.pack(padx=20, pady=(10, 5))

        title_label = ttk.Label(container, text="S.P.E.C.T.R.A.", font=('Helvetica', 38, 'bold'), bootstyle="primary")
        title_label.pack(padx=20, pady=(0, 2))

        subtitle_label = ttk.Label(
            container,
            text="Stellar Parameter Estimation & Calculation Tools for Research & Analysis",
            font=('Helvetica', 11, 'italic'),
            bootstyle="secondary"
        )
        subtitle_label.pack(padx=20, pady=(0, 15))

        update_btn = ttk.Button(
            container,
            text="🔄  Atualizar Programa",
            bootstyle="primary-outline",
            command=self.master.update_program,
            padding=(15, 8)
        )
        update_btn.pack(side=BOTTOM, padx=20, pady=(10, 5))

        version_label = ttk.Label(container, text=f"Version {__version__} (build 280726)", font=('Helvetica', 9), bootstyle="secondary")
        version_label.pack(side=BOTTOM, padx=20, pady=2)

        image_label.image = image_tk

    def setup_modeling_ui(self, frame):
        container = ttk.Frame(frame, padding=20)
        container.pack(expand=True, fill=BOTH)

        # Module Header Card (Standardized Layout)
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=X, pady=(0, 15))
        lbl_title = ttk.Label(header_frame, text="🧮 Mathematical Modeling & Machine Learning Module", font=("Segoe UI", 14, "bold"), bootstyle="primary")
        lbl_title.pack(anchor="w")
        lbl_sub = ttk.Label(header_frame, text="Custom Multivariate Regression, PCA & Feature Selection for Custom Target Derivation", font=("Segoe UI", 9, "italic"), bootstyle="secondary")
        lbl_sub.pack(anchor="w")

        # Card 1: Feature Selection & Imputation
        card1 = ttk.Labelframe(container, text=" 1. Feature Selection & Data Imputation ", padding=15)
        card1.pack(fill=X, pady=(0, 15))

        f_step1 = ttk.Frame(card1)
        f_step1.pack(fill=X, pady=(0, 12))
        ttk.Button(f_step1, text="🔍  Analyze Features & Load Dataset", bootstyle="primary", command=self.correlation_analysis, padding=(12, 6)).pack(side=LEFT)

        f_params = ttk.Frame(card1)
        f_params.pack(fill=X)

        ttk.Label(f_params, text="Missing Imputation:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, padx=(0, 10), pady=6, sticky="w")
        data_completition_combobox = ttk.Combobox(f_params, textvariable=self.comp_method, values=['None', 'KNN', 'Iterative', 'MICE'], width=12, state="readonly")
        data_completition_combobox.current(0)
        data_completition_combobox.grid(row=0, column=1, padx=(0, 25), pady=6, sticky="w")

        ttk.Label(f_params, text="Select Target:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=2, padx=(0, 10), pady=6, sticky="w")
        self.target_combobox = ttk.Combobox(f_params, textvariable=self.target, width=15, state="readonly")
        self.target_combobox.grid(row=0, column=3, padx=0, pady=6, sticky="w")

        # Card 2: Model Training
        card2 = ttk.Labelframe(container, text=" 2. Model Training & Evaluation ", padding=15)
        card2.pack(fill=X, pady=(0, 15))

        f_build = ttk.Frame(card2)
        f_build.pack(fill=X)
        ttk.Button(f_build, text="🔨 Build Model", bootstyle="primary", command=self.modeling).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_build, text="📋 Model Report", bootstyle="info-outline", command=self.master.show_report).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_build, text="📉 Report Plot", bootstyle="success-outline", command=self.master.show_report_plot).pack(side=LEFT)

        # Card 3: Calculate & Results
        card3 = ttk.Labelframe(container, text=" 3. Calculation & Outputs ", padding=15)
        card3.pack(fill=X, pady=(0, 10))

        f_out = ttk.Frame(card3)
        f_out.pack(fill=X)
        ttk.Button(f_out, text="⚡ Calculate Target", bootstyle="primary", command=self.derive).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_out, text="📊 Show Table", bootstyle="info-outline", command=self.master.show_table).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_out, text="📈 Result Plot", bootstyle="success", command=self.master.show_result_plot).pack(side=LEFT)

    def get_info_columns(self):
        if table_data is None:
            open_table()
        columns_names = list(table_data.columns)
        self.target_combobox['values'] = columns_names
        self.target_combobox.current(0)

    def correlation_analysis(self):
        if table_data is None:
            open_table()
            
        def _task(cancel_event=None):
            MathModels.correlation_plot(table_data)
            self.master.choosing_target()
            self.get_info_columns()

        def _on_done(result, error):
            if error is not None:
                if isinstance(error, InterruptedError):
                    ToastNotification(
                        title='Correlation Analysis',
                        message="Analysis cancelled by user.",
                        duration=4000,
                        bootstyle='warning'
                    ).show_toast()
                return
        BusyWindow(
            self.master,
            "Analysing your dataset - please wait...",
            _task,
            _on_done,
        )

    def data_treat(self):
        """
        Performs data imputation using the specified method.

        Parameters:
            comp_method (str or object): The imputation method to use. Can be one of:
                - 'KNN': K-Nearest Neighbors imputation
                - 'Iterative': Iterative imputation
                - 'MICE': Multiple Imputation by Chained Equations (not implemented)
                - 'None': No imputation (returns the original data with missing values removed)

        Returns:
            pd.DataFrame: The imputed data

        Notes:
            This function performs the following steps:
            1. Filters the input data to exclude non-numeric columns.
            2. Drops columns with all missing values.
            3. Applies the specified imputation method to the filtered data.
            4. Returns the imputed data as a pandas DataFrame.

        Warning:
            The 'MICE' method is not currently implemented and will raise an error if selected.
        """
        if self.comp_method.get() in ['KNN', 'Iterative']:
            data_filtered = table_data.select_dtypes(exclude='object')
            data_filtered = data_filtered.dropna(axis=1, how='all')

            if self.comp_method.get() == 'KNN':
                imputer = KNNImputer(n_neighbors=5)
            elif self.comp_method.get() == 'Iterative':
                imputer = IterativeImputer(max_iter=10, random_state=0)

            self.filtered_data = pd.DataFrame(imputer.fit_transform(data_filtered),
                                              columns=data_filtered.columns,
                                              index=data_filtered.index)
        elif self.comp_method.get() == 'None':
            data_filtered = table_data.select_dtypes(exclude='object')
            data_filtered = data_filtered.dropna(axis=1, how='all')
            self.filtered_data = data_filtered

    def modeling(self):
        self.method = 'MOD'
        self.data_treat()
        target_name = self.target.get() if hasattr(self.target, 'get') else str(self.target)
        selected_features = MathModels.select_features(self.filtered_data, target_name)
        X = self.filtered_data[selected_features].values
        y = self.filtered_data[target_name].values

        def _task(cancel_event=None):
            self.model, self.report = create_regression_model(X, y)
            self.master.pca_analysis()
            self.selected_features = selected_features

        def _on_done(result, error):
            if error is not None:
                            if isinstance(error, InterruptedError):
                                ToastNotification(
                                    title='Mathematical Modeling',
                                    message="Modeling cancelled by user.",
                                    duration=4000,
                                    bootstyle='warning'
                                ).show_toast()
                            return
        BusyWindow(
            self.master,
            "Building your model - please wait...",
            _task,
            _on_done,
        )

    def derive(self):
        if table_data is None:
            open_table()
            if table_data is None:
                return

        if not hasattr(self, 'model') or self.model is None:
            messagebox.showwarning("Derivation Error", "No model built yet. Please run 'Build Model' first.")
            return

        if not hasattr(self, 'selected_features') or not isinstance(self.selected_features, list) or not self.selected_features:
            messagebox.showwarning("Derivation Error", "No features selected. Please run 'Build Model' first.")
            return

        target_name = self.target.get()
        if not target_name:
            messagebox.showwarning("Derivation Error", "No target selected.")
            return

        X = table_data[self.selected_features]
        yerr = np.zeros(len(X))
        y_out = np.zeros(len(X))

        k = ~np.isnan(X.values).any(axis=1) if hasattr(X, 'values') else ~np.isnan(X).any(axis=1)
        x = X.loc[k]

        if len(x) > 0:
            preds = self.model.predict(x.values)
            y_out[k] = preds

            # Incerteza do modelo baseada no RMSE do modelo treinado
            model_rmse = 0.05
            if hasattr(self, 'report') and isinstance(self.report, pd.DataFrame) and 'RMSE' in self.report.columns:
                model_rmse = float(self.report['RMSE'].min())
            yerr[k] = model_rmse

        table_data[target_name + '_calc'] = np.round(y_out, 4)
        table_data[target_name + '_e'] = np.round(yerr, 4)
        table_data.to_csv(os.path.join(TABLES_DIR, '_final_result_table.csv'), index=None)
        ToastNotification("Derivation by Mathematical Model",
                          f"{target_name} calculated successfully.",
                          duration=6000, bootstyle='dark').show_toast()



    def setup_spectro_ui(self, frame):
        pass

    def setup_statistical_ui(self, frame):
        pass  # Add statistical tools for analysis tab UI elements here

    def setup_isocfit_ui(self, frame):
        container = ttk.Frame(frame, padding=20)
        container.pack(expand=True, fill=BOTH)

        # Module Header Card (Standardized Layout)
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=X, pady=(0, 15))
        lbl_title = ttk.Label(header_frame, text="🌌 Isochrone Fitting & HRD Localization Module", font=("Segoe UI", 14, "bold"), bootstyle="primary")
        lbl_title.pack(anchor="w")
        lbl_sub = ttk.Label(header_frame, text="Stellar Age & Mass Estimation via Theoretical Isochrones (Siess 2000, BHAC15)", font=("Segoe UI", 9, "italic"), bootstyle="secondary")
        lbl_sub.pack(anchor="w")

        # Card 1: Configuration
        card1 = ttk.Labelframe(container, text=" 1. Model & Input Parameters ", padding=15)
        card1.pack(fill=X, pady=(0, 15))
        card1.grid_columnconfigure(1, weight=1)

        ttk.Label(card1, text="Isochrone Model:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        models = ('Siess 2000', 'BHAC15')
        iso_model_combobox = ttk.Combobox(card1, textvariable=self.iso_selected_model, values=models, width=15, state="readonly")
        iso_model_combobox.current(0)
        iso_model_combobox.grid(row=0, column=1, padx=10, pady=8, sticky="w")

        ttk.Label(card1, text="Effective Temp (Teff):", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, padx=10, pady=8, sticky="w")
        f_teff = ttk.Frame(card1)
        f_teff.grid(row=1, column=1, padx=10, pady=8, sticky="w")
        ttk.Entry(f_teff, textvariable=self.teff, width=12).pack(side=LEFT, padx=(0, 5))
        ttk.Label(f_teff, text="K", font=('Segoe UI', 9)).pack(side=LEFT)

        ttk.Label(card1, text="Luminosity (log L):", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, padx=10, pady=8, sticky="w")
        f_logl = ttk.Frame(card1)
        f_logl.grid(row=2, column=1, padx=10, pady=8, sticky="w")
        ttk.Entry(f_logl, textvariable=self.logl, width=12).pack(side=LEFT, padx=(0, 5))
        ttk.Label(f_logl, text="log L/L_sun", font=('Segoe UI', 9)).pack(side=LEFT)

        # Card 2: Processing & Action
        card2 = ttk.Labelframe(container, text=" 2. Processing & Star Localization ", padding=15)
        card2.pack(fill=X, pady=(0, 15))

        f_btns = ttk.Frame(card2)
        f_btns.pack(fill=X)

        ttk.Checkbutton(f_btns, text="🔍 Verbose Mode", variable=self.save_var, onvalue=1, offvalue=0, bootstyle="round-toggle").pack(side=LEFT, padx=(0, 15))
        ttk.Button(f_btns, text="⭐ Locate Stars", bootstyle="primary", command=self.locate_stars).pack(side=LEFT, padx=(0, 10))

        # Card 3: Results
        card3 = ttk.Labelframe(container, text=" 3. Results & Visualization ", padding=15)
        card3.pack(fill=X, pady=(0, 15))

        f_res = ttk.Frame(card3)
        f_res.pack(fill=X)

        ttk.Button(f_res, text="📊 Show Table", bootstyle="info-outline", command=self.master.show_table).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_res, text="📈 Mass Plot", bootstyle="success-outline", command=lambda: self.master.show_result_plot('Mass')).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_res, text="⏳ Age Plot", bootstyle="success-outline", command=lambda: self.master.show_result_plot('Age')).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_res, text="🌌 HRD Plot", bootstyle="success", command=self.master.show_hrd_plot).pack(side=LEFT)

        self.progress = ttk.Progressbar(container, mode='determinate', bootstyle='info')
        self.progress.pack(fill=X, side=BOTTOM, pady=(10, 0))

    def open_madys_manager(self):
        """
        Opens the MADYS Isochrone Models Repository Manager window.
        """
        MadysModelManagerWindow(self.master, on_update_callback=self.refresh_rml_models_combobox)

    def refresh_rml_models_combobox(self):
        """
        Refreshes the available models combobox list in the MMR tab.
        """
        if hasattr(self, 'rml_model_combobox'):
            models = get_available_madys_models()
            self.rml_model_combobox.configure(values=models)

    def on_rml_model_changed(self, event=None):
        """
        Dynamically updates Mass Range, Age Slider bounds, and Photometric Filters
        whenever the user selects a different Isochrone Model.
        """
        model_name = self.selected_model.get()
        if not model_name:
            return
            
        meta = get_madys_model_metadata(model_name)
        
        # 1. Update Mass Range (low_int, hig_int)
        self.low_int.set(round(meta['mass_range'][0], 3))
        self.hig_int.set(round(meta['mass_range'][1], 3))
        
        # 2. Update Age Scale range
        if hasattr(self, 'rml_age_scale'):
            self.rml_age_scale.configure(from_=meta['age_range'][0], to=meta['age_range'][1])
            # Keep current age if within bounds, otherwise reset to midpoint or min
            curr_age = self.scale_int.get()
            if curr_age < meta['age_range'][0] or curr_age > meta['age_range'][1]:
                self.scale_int.set(round(meta['age_range'][0], 1))

        # 3. Update Photometric Filter combobox
        if hasattr(self, 'filter_combobox'):
            filters = meta['filters']
            self.filter_combobox.configure(values=filters)
            if filters:
                if self.selected_filter.get() not in filters:
                    self.selected_filter.set('g')

    def setup_rml_ui(self, frame):
        container = ttk.Frame(frame, padding=20)
        container.pack(expand=True, fill=BOTH)

        # Module Header Card (Standardized Layout)
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=X, pady=(0, 15))
        lbl_title = ttk.Label(header_frame, text="⚖️ Mass-Magnitude Relationship (MMR) Module", font=("Segoe UI", 14, "bold"), bootstyle="primary")
        lbl_title.pack(anchor="w")
        lbl_sub = ttk.Label(header_frame, text="Empirical & Theoretical Photometric Mass Calibration with Distance Corrections", font=("Segoe UI", 9, "italic"), bootstyle="secondary")
        lbl_sub.pack(anchor="w")

        # Card 1: Model & Mass Range
        card1 = ttk.Labelframe(container, text=" 1. Model Configuration & Mass Range ", padding=15)
        card1.pack(fill=X, pady=(0, 15))

        ttk.Label(card1, text="Isochrone Model:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        models = get_available_madys_models()
        self.rml_model_combobox = ttk.Combobox(card1, textvariable=self.selected_model, values=models, width=16, state="readonly")
        if models:
            self.selected_model.set(models[0])
        self.rml_model_combobox.grid(row=0, column=1, padx=10, pady=8, sticky="w")
        self.rml_model_combobox.bind("<<ComboboxSelected>>", self.on_rml_model_changed)

        ttk.Button(card1, text="📦 Models Manager", bootstyle="info-outline", command=self.open_madys_manager).grid(row=0, column=2, padx=10, pady=8, sticky="w")

        ttk.Label(card1, text="Mass Range:", font=('Helvetica', 10, 'bold')).grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.low_int.set(0.1)
        self.hig_int.set(1.3)

        f_mass = ttk.Frame(card1)
        f_mass.grid(row=1, column=1, padx=10, pady=8, sticky="w")
        ttk.Label(f_mass, text="Min:").pack(side=LEFT, padx=(0, 4))
        ttk.Entry(f_mass, textvariable=self.low_int, width=6).pack(side=LEFT, padx=(0, 2))
        ttk.Label(f_mass, text="M_sun").pack(side=LEFT, padx=(0, 15))

        ttk.Label(f_mass, text="Max:").pack(side=LEFT, padx=(0, 4))
        ttk.Entry(f_mass, textvariable=self.hig_int, width=6).pack(side=LEFT, padx=(0, 2))
        ttk.Label(f_mass, text="M_sun").pack(side=LEFT)

        # Card 2: Age & Filter Selection
        card2 = ttk.Labelframe(container, text=" 2. Isochrone Age & Filter Selection ", padding=15)
        card2.pack(fill=X, pady=(0, 15))

        ttk.Label(card2, text="Isochrone Age:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.scale_int.set(112)
        f_age = ttk.Frame(card2)
        f_age.grid(row=0, column=1, padx=10, pady=8, sticky="w")
        self.rml_age_scale = ttk.Scale(f_age, from_=1, to=1000, length=150, orient='horizontal', variable=self.scale_int)
        self.rml_age_scale.pack(side=LEFT, padx=(0, 8))
        ttk.Entry(f_age, textvariable=self.scale_int, width=6).pack(side=LEFT, padx=(0, 4))
        ttk.Label(f_age, text="Myr").pack(side=LEFT)

        ttk.Label(card2, text="Photometric Filter:", font=('Helvetica', 10, 'bold')).grid(row=1, column=0, padx=10, pady=8, sticky="w")
        initial_meta = get_madys_model_metadata(self.selected_model.get() if self.selected_model.get() else 'bhac15')
        filters = initial_meta['filters']
        self.selected_filter.set(filters[0] if filters else 'G')
        self.filter_combobox = ttk.Combobox(card2, textvariable=self.selected_filter, values=filters, width=16, state="readonly")
        self.filter_combobox.grid(row=1, column=1, padx=10, pady=8, sticky="w")

        # Trigger dynamic metadata population for initial selected model
        self.on_rml_model_changed()

        f_mod_btns = ttk.Frame(card2)
        f_mod_btns.grid(row=2, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="w")
        ttk.Button(f_mod_btns, text="🔨 Build Model", bootstyle="primary", command=self.build_model).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_mod_btns, text="📋 Model Report", bootstyle="info-outline", command=self.master.show_report).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_mod_btns, text="🌐 HTML Report", bootstyle="warning-outline", command=self.master.generate_html_report).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_mod_btns, text="📉 Report Plot", bootstyle="success-outline", command=self.master.show_report_plot).pack(side=LEFT)

        # Card 3: Distance Correction & Calculation
        card3 = ttk.Labelframe(container, text=" 3. Distance Correction & Mass Calculation ", padding=15)
        card3.pack(fill=X, pady=(0, 10))

        self.check_var.set(1)
        self.cluster_dist.set(125)
        f_dist = ttk.Frame(card3)
        f_dist.pack(fill=X, pady=(0, 10))
        ttk.Checkbutton(f_dist, text="Distance Correction", variable=self.check_var, onvalue=1, offvalue=0).pack(side=LEFT, padx=(0, 15))
        ttk.Label(f_dist, text="Distance:").pack(side=LEFT, padx=(0, 4))
        ttk.Entry(f_dist, textvariable=self.cluster_dist, width=7).pack(side=LEFT, padx=(0, 4))
        ttk.Label(f_dist, text="pc").pack(side=LEFT)

        f_calc_btns = ttk.Frame(card3)
        f_calc_btns.pack(fill=X)
        ttk.Button(f_calc_btns, text="📁 Input Table", bootstyle="info-outline", command=open_table).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_calc_btns, text="⚡ Calculate Mass", bootstyle="primary", command=self.predict_mass).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_calc_btns, text="📊 Show Table", bootstyle="info-outline", command=self.master.show_table).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_calc_btns, text="📈 Result Plot", bootstyle="success", command=self.master.show_result_plot).pack(side=LEFT)

    # GridSearchCV in RegressionReport fits 9 models (including an SVR with
    # rbf/sigmoid kernels, which scale roughly O(n^2)-O(n^3)) across
    # multiple folds and hyperparameter combinations. The isochrone grid
    # used here defaults to n_steps=[1000, 1000] (up to ~1e6 points) —
    # feeding that whole grid into GridSearchCV can exhaust memory or run
    # for a very long time. Training is capped to a random subsample; the
    # full-resolution grid is still kept (self.X) for later mass
    # prediction/filtering, which isn't affected by this cap.
    MAX_TRAINING_SAMPLES = 5000

    def build_model(self):
        self.method = 'MMR'
        clust_age = self.scale_int.get()
        range_mass = [self.low_int.get(), self.hig_int.get()]
        mag_filter = self.selected_filter.get()

        if not self.selected_model:
            messagebox.showinfo("Regression model", "Failed to build the regression model for these parameters.")
            return

        selected_model_name = self.selected_model.get().strip()

        def _task(cancel_event=None):
            # 2. Silencia o prompt de terminal redirecionando o sys.stdin
            old_stdin = sys.stdin
            sys.stdin = io.StringIO("Y\nY\nY\nY\nY\n")
            
            try:
                th_model = madys.IsochroneGrid(
                    selected_model_name, 
                    mag_filter, 
                    mass_range=range_mass,
                    age_range=clust_age, 
                    n_steps=[1000, 1000]
                )
            finally:
                sys.stdin = old_stdin  # Restaura a entrada padrão
                    
            # Constroi a malha 2D de Massa (log10 Msun) compatível com th_model.data (n_masses, n_ages)
            if hasattr(th_model.masses, 'ndim') and th_model.masses.ndim == 1 and hasattr(th_model, 'ages') and hasattr(th_model.ages, 'ndim') and th_model.ages.ndim == 1:
                M_mesh, A_mesh = np.meshgrid(th_model.masses, th_model.ages, indexing='ij')
                y_raw = np.log10(np.maximum(1e-10, M_mesh.ravel()))
            else:
                y_raw = np.log10(np.maximum(1e-10, np.array(th_model.masses).ravel()))

            X_raw = th_model.data[:, :, 0].ravel()

            # Remove quaisquer valores NaN ou Inf da grade de dados do modelo (ex: MIST)
            valid_mask = ~np.isnan(X_raw) & ~np.isinf(X_raw) & ~np.isnan(y_raw) & ~np.isinf(y_raw)
            X_full = X_raw[valid_mask]
            y_full = y_raw[valid_mask]

            n = len(X_full)
            if n > self.MAX_TRAINING_SAMPLES:
                rng = np.random.default_rng(42)
                idx = rng.choice(n, size=self.MAX_TRAINING_SAMPLES, replace=False)
                X_train_input = X_full[idx].reshape(-1, 1)
                y_train_input = y_full[idx]
            else:
                X_train_input = X_full.reshape(-1, 1)
                y_train_input = y_full

            model_name, model, report = RegressionReport(X_train_input, y_train_input)
            if model_name is None:
                raise ValueError(
                    "Not enough samples in this grid to build a model "
                    "(try a wider mass/age range)."
                )

            th_model_data = pd.DataFrame({'X': X_full, 'y': y_full[:len(X_full)]})
            return model_name, model, report, X_full, y_full, th_model_data

        def _on_done(result, error):
            if error is not None:
                # BusyWindow already showed the error dialog; nothing more
                # to do here — the app stays usable either way.
                return
            model_name, model, report, X_full, y_full, th_model_data = result
            self.model = model
            self.report = report
            self.X = X_full
            self.y = y_full
            self.th_model_data = th_model_data
            ToastNotification(
                title='Regression model',
                message=f"{model_name} model built.",
                duration=5000,
                bootstyle='dark'
            ).show_toast()

        BusyWindow(
            self.master,
             f"Loading model {selected_model_name} (downloading if not found locally) "
              "and building the Mass-Magnitude regression model - this can take a while     "
              "depending on the selected mass/age range...",
            _task,
            _on_done,
        )

    def predict_mass(self):
        global table_data

        if table_data is None:
            open_table()

        mag_col = find_mag_column(table_data, self.selected_filter.get())
        if mag_col is None:
            ToastNotification("Collecting data:",
                              f"Magnitude for filter '{self.selected_filter.get()}' was not found in your table.",
                              duration=6000, bootstyle='light').show_toast()
        else:
            mag = np.array(table_data[mag_col].values, copy=True, dtype=float)
            yerr = np.zeros(len(mag))
            mass = np.zeros(len(mag))
            if hasattr(self.target, 'set'):
                self.target.set("Mass")
            else:
                self.target = tk.StringVar(value="Mass")
            if self.check_var.get() == 1:
                mag, k = FilterValues.filter_predict(mag, self.X, clust_dist=self.cluster_dist.get())
            else:
                mag, k = FilterValues.filter_predict_un(mag, self.X)
            mass[k] = self.model.predict(mag.reshape(-1, 1))

            # Incerteza do modelo baseada no RMSE do modelo treinado
            model_rmse = 0.05
            if hasattr(self, 'report') and isinstance(self.report, pd.DataFrame) and 'RMSE' in self.report.columns:
                model_rmse = float(self.report['RMSE'].min())

            key = np.where(np.array(mass) == 0.)[0]
            hold_mass = np.array(mass)
            hold_mass[key] = np.nan
            calc_mass = 10**hold_mass
            yerr[k] = calc_mass[k] * np.log(10) * model_rmse

            table_data['Mass_calc'] = np.round(calc_mass, 4)
            table_data['Mass_e'] = np.round(yerr, 4)
            table_data.to_csv(os.path.join(TABLES_DIR, '_final_result_table.csv'), index=None)

            ToastNotification("Mass Determination",
                              f"Mass calculated successfully for filter {self.selected_filter.get()}.",
                              duration=6000, bootstyle='dark').show_toast()
    def locate_stars(self):
        global table_data
        
        # 1. Leitura inicial dos campos da interface (rodado na thread principal da GUI)
        teff_input = self.teff.get()
        logl_input = self.logl.get()
        save_var = self.save_var.get()
        model_selected = self.iso_selected_model.get()
        self.method = 'ISO'
        if hasattr(self.target, 'set'):
            self.target.set("Mass")
        else:
            self.target = tk.StringVar(value="Mass")
        # Verifica se há dados nos campos manuais ou se deve usar/solicitar a tabela carregada
        has_manual_input = bool(teff_input) and (logl_input != 0.0)

        if not has_manual_input and table_data is None:
            open_table()

        # Determina a origem das variáveis de entrada
        if has_manual_input:
            Tinput = float(teff_input)
            Linput = float(logl_input)
            Nobjects = 1
            is_single_star = True
        elif isinstance(table_data, pd.DataFrame):
            teff_col = next((col for col in ['Teff', 'teff', 'T_eff', 'TEFF', 't_eff'] if col in table_data.columns), None)
            logl_col = next((col for col in ['logL', 'logl', 'log_L', 'LOGL', 'logL/L_sun'] if col in table_data.columns), None)
            if not teff_col or not logl_col:
                messagebox.showerror("Missing Columns", "Loaded dataset must contain 'Teff' and 'logL' columns.")
                return
            Tinput = table_data[teff_col].values
            Linput = table_data[logl_col].values
            Nobjects = len(Tinput)
            is_single_star = False
        else:
            # Caso o usuário cancele a abertura de arquivo e não tenha informado dados
            return

        def _task(cancel_event=None):
            var, Nlines, alldataiso = intpol(model_selected)
            primarydataset = []
            ff = []

            if Nobjects > 1:
                for i in range(Nobjects):
                    # 🛑 CHECAGEM DE CANCELAMENTO
                    if cancel_event.is_set():
                        raise InterruptedError("Process cancelled by the user.")

                    if np.isfinite(Linput[i]) and np.isfinite(Tinput[i]):
                        res = interp(Tinput[i], Linput[i], var, Nlines, alldataiso, save_var)
                        ff.append(i)
                        primarydataset.append(res)
                        
            elif Nobjects == 1:
                if cancel_event.is_set():
                    raise InterruptedError("Process cancelled by the user.")
                res = interp(Tinput, Linput, var, Nlines, alldataiso, save_var)
                primarydataset.append(res)

            # Conversão para DataFrame e renomeação de colunas
            df_primary = pd.DataFrame(primarydataset)
            df_primary = df_primary.rename(columns={0: 'Age', 1: 'Mass', 2: 'Teff', 3: 'logL'})

            # Estimativa Bayesiana de massa e idade (com incertezas 1-sigma reais)
            mass, age, yerr, aerr = interpolmass(df_primary, model_selected)

            # Atualização dos resultados calculados
            if is_single_star or table_data is None:
                res_table = df_primary.copy()
            else:
                res_table = table_data.copy()

            res_table['Age_calc (Myr)'] = np.round(age, 3)
            res_table['Age_e (Myr)'] = np.round(aerr, 3)
            res_table['Mass_calc'] = np.round(mass, 4)
            res_table['Mass_e'] = np.round(yerr, 4)

            # Exportação do resultado para disco na thread secundária
            res_table.to_csv(os.path.join(TABLES_DIR, '_final_result_table.csv'), index=None)

            return res_table

        def _on_done(result, error):
            global table_data
            if error is not None:
                if isinstance(error, InterruptedError):
                    ToastNotification(
                        title='Star Localization',
                        message="Calculation cancelled by user.",
                        duration=4000,
                        bootstyle='warning'
                    ).show_toast()
                else:
                    messagebox.showerror("Localization Error", f"An error occurred during star localization:\n{error}")
                return

            table_data = result
            DataManager.set_dataset(result)

            ToastNotification(
                title='Star Localization',
                message="Stars completely localized on HR-Diagram.",
                duration=5000,
                bootstyle='dark'
            ).show_toast()

        BusyWindow(
            self.master,
            "Locating stars on the HR-Diagram - please wait...",
            _task,
            _on_done,
        )

    def setup_primary_params_ui(self, parent_frame):
        container = ttk.Frame(parent_frame, padding=20)
        container.pack(fill=BOTH, expand=True)

        # Module Header Card (Standardized Layout)
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=X, pady=(0, 15))
        lbl_title = ttk.Label(header_frame, text="⭐ Primary Stellar Parameters Module", font=("Segoe UI", 14, "bold"), bootstyle="primary")
        lbl_title.pack(anchor="w")
        lbl_sub = ttk.Label(header_frame, text="Multi-band Photometric Derivation, Spectroscopic EW Classification & ML Goodness-of-Fit Modeling", font=("Segoe UI", 9, "italic"), bootstyle="secondary")
        lbl_sub.pack(anchor="w")

        # Card 1: Feature Analysis & Configuration
        card1 = ttk.Labelframe(container, text=" 1. Feature Analysis & Data Configuration ", padding=15)
        card1.pack(fill=X, pady=(0, 15))

        f_av = ttk.Frame(card1)
        f_av.pack(fill=X, pady=(0, 12))
        ttk.Label(f_av, text="Interstellar Extinction (Av mag):", font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=(0, 10))
        self.av_entry = ttk.Entry(f_av, width=10)
        self.av_entry.insert(0, "0.0")
        self.av_entry.pack(side=LEFT, padx=(0, 20))

        ttk.Label(f_av, text="Target Parameters:", font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=(0, 8))
        ttk.Label(f_av, text="Teff (K) | SpT | log g | T Tauri Class", font=("Segoe UI", 9, "italic"), bootstyle="secondary").pack(side=LEFT)

        f_c1_btns = ttk.Frame(card1)
        f_c1_btns.pack(fill=X)

        def _calc_phot():
            df = DataManager.get_dataset()
            if df is None:
                messagebox.showwarning("Primary Parameters", "Please load a dataset first!")
                return
            try:
                av = float(self.av_entry.get())
                res_df = estimate_photometric_dataset(df, extinction_av=av)
                DataManager.set_dataset(res_df)
                ToastNotification("Primary Parameters", "Photometric Teff, SpT & log g calculated successfully!", duration=4000, bootstyle="success").show_toast()
            except Exception as e:
                messagebox.showerror("Photometric Estimation Error", str(e))

        def _calc_spec():
            df = DataManager.get_dataset()
            if df is None:
                messagebox.showwarning("Primary Parameters", "Please load a dataset first!")
                return
            try:
                res_df = estimate_spectroscopic_dataset(df)
                DataManager.set_dataset(res_df)
                ToastNotification("Primary Parameters", "Spectroscopic EWs & T Tauri classification completed!", duration=4000, bootstyle="info").show_toast()
            except Exception as e:
                messagebox.showerror("Spectroscopic Estimation Error", str(e))

        ttk.Button(f_c1_btns, text="⚡ Calculate Photometric Parameters", bootstyle="primary", command=_calc_phot).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_c1_btns, text="🔬 Process EWs & Classify T Tauri Stars", bootstyle="info-outline", command=_calc_spec).pack(side=LEFT)

        # Card 2: Model Training & Evaluation
        card2 = ttk.Labelframe(container, text=" 2. Machine Learning Model Training & Evaluation ", padding=15)
        card2.pack(fill=X, pady=(0, 15))

        f_algo = ttk.Frame(card2)
        f_algo.pack(fill=X, pady=(0, 12))
        ttk.Label(f_algo, text="ML Regressor Algorithm:", font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=(0, 10))
        self.ml_algo_var = tk.StringVar(value="RandomForest")
        combo_algo = ttk.Combobox(f_algo, textvariable=self.ml_algo_var, values=["RandomForest", "GradientBoosting", "SVR", "KNN"], width=18, state="readonly")
        combo_algo.pack(side=LEFT)

        def _calc_ml():
            df = DataManager.get_dataset()
            if df is None:
                messagebox.showwarning("Primary Parameters", "Please load a dataset first!")
                return
            try:
                engine = PrimaryParameterMLEngine(algorithm=self.ml_algo_var.get())
                engine.train_on_calibrations()
                out_df = df.copy()
                teff_ml, spt_ml, logg_ml = [], [], []
                for _, r in df.iterrows():
                    colors = {}
                    if 'BPmag' in df.columns and 'RPmag' in df.columns:
                        colors['BP-RP'] = r['BPmag'] - r['RPmag']
                    elif 'BP' in df.columns and 'RP' in df.columns:
                        colors['BP-RP'] = r['BP'] - r['RP']
                    pred = engine.predict_star(colors)
                    teff_ml.append(pred['Teff_ml'])
                    spt_ml.append(pred['SpT_ml'])
                    logg_ml.append(pred['logg_ml'])
                out_df['Teff_ml'] = teff_ml
                out_df['SpT_ml'] = spt_ml
                out_df['logg_ml'] = logg_ml
                DataManager.set_dataset(out_df)
                ToastNotification("Primary Parameters", f"ML ({self.ml_algo_var.get()}) prediction completed!", duration=4000, bootstyle="secondary").show_toast()
            except Exception as e:
                messagebox.showerror("ML Prediction Error", str(e))

        f_c2_btns = ttk.Frame(card2)
        f_c2_btns.pack(fill=X)
        ttk.Button(f_c2_btns, text="🔨 Build ML Model", bootstyle="primary", command=_calc_ml).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_c2_btns, text="📋 Model Report", bootstyle="info-outline", command=self.master.show_report).pack(side=LEFT)

        # Card 3: Calculation & Outputs
        card3 = ttk.Labelframe(container, text=" 3. Calculation & Outputs ", padding=15)
        card3.pack(fill=X, pady=(0, 15))

        self.verbose_var = tk.BooleanVar(value=True)

        def _gen_analysis():
            df = DataManager.get_dataset()
            if df is None:
                messagebox.showwarning("Primary Parameters", "Please load a dataset first!")
                return
            try:
                res = generate_primary_params_analysis(df)
                ToastNotification("Analysis Generated", "Analysis plots & summary CSV generated in outputs/primary_parameters/!", duration=4000, bootstyle="info").show_toast()
            except Exception as e:
                messagebox.showerror("Analysis Error", str(e))

        def _gen_report():
            df = DataManager.get_dataset()
            if df is None:
                messagebox.showwarning("Primary Parameters", "Please load a dataset first!")
                return
            try:
                is_verbose = self.verbose_var.get()
                out_path = generate_primary_params_html_report(df, verbose=is_verbose)
                mode_str = "Verbose Detailed" if is_verbose else "Summary"
                ToastNotification("Primary Parameters Report", f"HTML ({mode_str}) Report generated: {os.path.basename(out_path)}", duration=4000, bootstyle="success").show_toast()
            except Exception as e:
                messagebox.showerror("Report Error", str(e))

        f_c3_btns = ttk.Frame(card3)
        f_c3_btns.pack(fill=X, pady=(0, 10))
        ttk.Button(f_c3_btns, text="⚡ Derive All Parameters", bootstyle="primary", command=_calc_ml).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_c3_btns, text="📊 Show Table", bootstyle="info-outline", command=self.master.show_table).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_c3_btns, text="📊 Generate Plots & Stats", bootstyle="info", command=_gen_analysis).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_c3_btns, text="🌐 HTML Report", bootstyle="warning", command=_gen_report).pack(side=LEFT, padx=(0, 10))

        ttk.Checkbutton(card3, text="🔍 Verbose Mode (Detailed Calculation Trace per Star)", variable=self.verbose_var, bootstyle="round-toggle").pack(anchor="w")


class TopMenu(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=5)
        self.help_menu = None
        self.file_menu = None
        self.toolbar_menu = None
        self.pack(side=TOP, fill=X)
        self.create_widgets()

    def change_style(self):
        # This method will call the style change function in the App class
        self.master.change_app_style()

    def create_widgets(self):
        # Create toolbar
        self.toolbar_menu = tk.Menu(self.master)

        # Create toolbar menus
        self.file_menu = tk.Menu(self.toolbar_menu, tearoff=False)
        self.file_menu.add_command(label='Open table', command=open_table)
        self.file_menu.add_command(label='Save session', command=SessionManager.save_session)
        self.toolbar_menu.add_cascade(label='File', menu=self.file_menu)

        self.help_menu = tk.Menu(self.toolbar_menu, tearoff=False)
        self.help_menu.add_command(label='Documentation', command=self.open_documentation)
        self.help_menu.add_command(label='Atualizar Programa', command=self.master.update_program)
        self.help_menu.add_command(label='About', command=self.open_about_window)
        self.help_menu.add_checkbutton(label='Dark Mode', 
                                variable=self.master.dark_mode_var, 
                                command=self.change_style
                                )
        self.toolbar_menu.add_cascade(label='Help', menu=self.help_menu)

        self.toolbar_menu.add_command(label='Exit', command=self.master.quit)

        self.master.configure(menu=self.toolbar_menu)

    def open_about_window(self):
        """
        Open the About window.
        """
        about_window = AboutWindow(self)
        about_window.grab_set()

    def open_documentation(self):
        """
        Open the Manual.
        """
        manual_url = "https://github.com/matosjp/spectra/blob/main/Manual.md"
        webbrowser.open_new_tab(manual_url)


def create_regression_model(X, y):
    model_name, model, report = RegressionReport(X, y)
    toast_sucess = ToastNotification(
        title='Regression model',
        message=f"{model_name} model built.",
        duration=5000,
        bootstyle='dark'
    )
    toast_sucess.show_toast()
    return model, report


def open_table():
    global table_data
    """
    Open a table file dialog and read its contents.
    """
    try:
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Text file", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            table_data = pd.read_csv(file_path)

            # Display message on successful file read
            messagebox.showinfo("Open Data Table", f"File read successfully: {file_path}")

            # Define possible column name variations
            teff_column_variations = ['Teff']
            logl_column_variations = ['logL',
                                      'lum',
                                      'logl',
                                      'L',
                                      'L/Ls',
                                      'Lsun',
                                      'logL*',
                                      'Lum',
                                      'Lbol']

            # Find the actual column names in the file
            teff_column = next((col for col in teff_column_variations if col in table_data.columns), None)
            logl_column = next((col for col in logl_column_variations if col in table_data.columns), None)

            # Create a mapping from actual column names to standard names
            column_mapping = {
                teff_column: 'Teff',
                logl_column: 'logL'
            }

            # Rename the columns
            table_data.rename(columns=column_mapping, inplace=True)

            # Se a coluna for Luminosidade linear L (ex: 'L', 'lum', 'L/Ls', 'Lsun'), converte para log10(L)
            linear_l_names = {'L', 'L/Ls', 'Lsun', 'lum', 'Lum', 'Lbol'}
            if logl_column in linear_l_names:
                table_data['logL'] = np.log10(np.maximum(1e-10, table_data['logL']))

            if not teff_column or not logl_column:
                missing_columns = []
                if not teff_column:
                    missing_columns.append('Teff')
                if not logl_column:
                    missing_columns.append('logL')

                messagebox.showerror("Open Data Table", f"Missing required columns for Isochrone Fitting:"
                                                        f" {', '.join(missing_columns)}")
            
            # Sync with DataManager
            DataManager.set_dataset(table_data)
        else:
            messagebox.showwarning("Open Data Table", "No file selected.")
    except FileNotFoundError:
        messagebox.showerror("Open Data Table", "File not found.")
    except pd.errors.EmptyDataError:
        messagebox.showerror("Open Data Table", "File is empty.")
    except pd.errors.ParserError:
        messagebox.showerror("Open Data Table", "Error parsing CSV file.")
    except Exception as e:
        messagebox.showerror("Open Data Table", f"Error: {str(e)}")