"""
/*********************************************************************************/
*                              S.T.E.L.A.R. Program                               *
*                     Stellar Type Examination and Analysis Resource              *
*                                                                                 *
*  Author: [João Paulo Matos Dias Gomes]                                          *
*  Version: 1.0                                                                   *
*  Date: [05/06/2024]                                                             *
*                                                                                 *
*  Description:                                                                   *
*  S.T.E.L.A.R. (Stellar Type Examination and Analysis Resource) is a software    *
*  tool designed for the comprehensive analysis of stellar data. It provides      *
*  astronomers and astrophysicists with a suite of powerful algorithms for        *
*  determining various parameters related to stars, including stellar type,       *
*  luminosity, temperature, radius, mass, age, and distance.                      *
*                                                                                 *
*  This program is intended for research and educational purposes, offering a     *
*  user-friendly interface and accurate analytical capabilities for studying the  *
*  properties and behaviors of stars across the cosmos.                           *
*********************************************************************************/
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
import madys

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import KNNImputer, IterativeImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import missingno as msno
import os
import pandas as pd
import numpy as np

from StarLocalization import intpol, interp, readiso, plot_HRD
from tools import RegressionReport, MathModels, ResultDisplay, FilterValues, interpolmass
from widgets import SessionManager, AboutWindow

setup_path = os.getcwd()
default_pth = os.getcwd()
table_output = default_pth + '/outputs/tables/'
themes_path = setup_path + '/external/themes.json'
os.chdir(default_pth)

class App(ttk.Window):
    def __init__(self):
        super().__init__()
        self.target = tk.StringVar
        self.title("S.T.E.L.A.R")
        self.geometry("820x560")
        self.current_theme = 'light_theme'  # Default theme
        self.load_custom_theme(self.current_theme)
        self.create_widgets()
        os.chdir(os.getcwd())
        default_pth = os.getcwd()

    def load_custom_theme(self, theme_name):
        style = ttk.Style()
        style.load_user_themes(themes_path)
        style.theme_use(theme_name)

    def change_app_style(self):
        # Toggle between themes or apply a new one
        new_theme = 'light_theme' if self.current_theme == 'dark_theme' else 'dark_theme'
        self.current_theme = new_theme
        self.load_custom_theme(new_theme)
        self.sidebar.refresh_sidebar()

    def create_widgets(self):
        self.sidebar = Sidebar(self)
        self.sidebar.pack(side=LEFT, fill=Y)
        self.top_menu = TopMenu(self)
        self.top_menu.pack(side=TOP, fill=X)

    def create_widgets(self):
        self.sidebar = Sidebar(self)
        self.sidebar.pack(side=LEFT, fill=Y)
        self.top_menu = TopMenu(self)
        self.top_menu.pack(side=TOP, fill=X)

    def show_result_plot(self):
        tab1 = table_data
        method = self.sidebar.method
        y = tab1['Mass_calc'].values
        if method == 'MMR':
            x = tab1[f'{self.sidebar.selected_filter.get()}mag'].values
        else:
            x = tab1['Teff'].values
        yerr = tab1['Mass_e'].values
        fra = ResultDisplay(x, y, yerr, method)
        if fra:
            # Create and save the image plot
            fra.res_plot(save_file=True)

            # Create a new Toplevel window
            plot_window = ttk.Toplevel(self)
            plot_window.title("Mass Results Plot")

            # Load the image and scale it to fit the window
            photo = Image.open('_mass_results_display.png').resize((800, 600))
            image_tk = ImageTk.PhotoImage(photo)

            # Create a Label to display the image
            image_label = ttk.Label(plot_window, image=image_tk)
            image_label.pack(padx=20, pady=20)

            # Keep a reference to the image to prevent garbage collection
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
            photo = Image.open('_hrd_complete.png').resize((800, 600))
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
            photo = Image.open('_visual_report.png').resize((800, 600))
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

        if self.sidebar.report is not None:
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

    def choosing_target(self):
        plot_window = ttk.Toplevel(self)
        plot_window.title("Mathematical Modeling: Step 1")

        # Load the image and scale it to fit the window
        photo = Image.open('_correlation_report.png').resize((600, 800))
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
        photo = Image.open('_pca_report.png').resize((800, 600))
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
        self.master = parent
        self.selected_features = pd.DataFrame
        self.features = []
        self.method = tk.StringVar()
        self.comp_method = tk.StringVar()
        self.target = tk.StringVar()
        self.selected_model = tk.StringVar()
        self.iso_selected_model = tk.StringVar()
        self.selected_filter = tk.StringVar()
        self.clsuter_dist = tk.DoubleVar()
        self.low_int = tk.DoubleVar()
        self.hig_int = tk.DoubleVar()
        self.check_var = ttk.IntVar()
        self.scale_int = tk.IntVar()
        self.current_theme = ttk.Style().theme_use()

        self.create_widgets()
        self.pack(side=LEFT, fill=Y)

    def create_widgets(self):
        self.style = ttk.Style()
        current_theme = self.style.theme_use()
        self.style.configure('lefttab.TNotebook',
                             tabposition=tk.W + tk.N,
                             tabplacement=tk.N + tk.EW)
        self.style.theme_settings(current_theme,
                                  {"TNotebook.Tab": {"configure": {'background': 'lightblue', "padding": [10, 8]}}})

        self.notebook = ttk.Notebook(self, style='lefttab.TNotebook')
        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.page0 = ttk.Frame(self.notebook, width=580, height=700)
        self.page1 = ttk.Frame(self.notebook, width=580, height=700)
        self.page2 = ttk.Frame(self.notebook, width=580, height=700)
        self.page3 = ttk.Frame(self.notebook, width=580, height=700)
        self.page4 = ttk.Frame(self.notebook, width=580, height=700)

        self.notebook.add(self.page0, text='Home', sticky="nsew")
        self.notebook.add(self.page1, text='Mass Determination', sticky="nsew")
        # self.notebook.add(self.page2, text='Spectroscopic Parameters', sticky="nsew")
        self.notebook.add(self.page3, text='Mathematical Modeling', sticky="nsew")
        #self.notebook.add(self.page4, text='Probability & Statistics', sticky="nsew")

        self.apply_styles()

        self.setup_home_ui(self.page0)
        self.setup_mass_determination_ui(self.page1)
        self.setup_modeling_ui(self.page3)

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
                                  {"TNotebook.Tab": {"configure": {'background': 'lightblue', "padding": [10, 8]}}})

    def refresh_sidebar(self):
        # Clear existing widgets and recreate them
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()

    def setup_home_ui(self, frame):
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        photo = Image.open(setup_path + '/icon.png').resize((400, 400))
        image_tk = ImageTk.PhotoImage(photo)

        # Create a Label to display the image
        image_label = ttk.Label(frame, image=image_tk)
        image_label.pack(padx=20, pady=10)

        version_label = tk.Label(frame, text="S.T.E.L.A.R", font=('Helvetica', 46, 'bold'))
        version_label.pack(padx=20, pady=0)

        # Label displaying program version
        version_label = tk.Label(frame, text="Version: V1.00.000_build_201224")
        version_label.pack(side=BOTTOM, padx=20, pady=0)

        # Keep a reference to the image to prevent garbage collection
        image_label.image = image_tk

    def setup_modeling_ui(self, frame):
        frame.grid_columnconfigure(3, weight=1)
        frame.grid_rowconfigure(12, weight=1)


        title_label_1 = tk.Label(frame, text="1. Feature Selection",
                              font=('Helvetica', 14, 'bold'))
        title_label_1.grid(row=0, column=0, columnspan=3, pady=(10, 5), padx=10, sticky="w")

        data_split_button = tk.Button(frame,
                                      text="Analyze",
                                      command=self.correlation_analysis)
        data_split_button.grid(row=2, column=0, pady=(10, 5), padx=10, sticky="w")

        data_label = tk.Label(frame, text="Missing Imputation:",
                              font=('Helvetica', 10))
        data_label.grid(row=1, column=1, pady=(10, 5), padx=10, sticky="w")

        data_completition_combobox = ttk.Combobox(frame,
                                                  textvariable=self.comp_method,
                                                  width=12)
        data_completition_combobox['values']=['None',
                                              'KNN',
                                              'Iterative',
                                              'MICE']
        data_completition_combobox.current(0)
        data_completition_combobox.grid(row=2, column=1, pady=(10,5), padx=10, stick='w')

        target_label = tk.Label(frame, text="Select Target:",
                              font=('Helvetica', 10))
        target_label.grid(row=1, column=2, pady=(10, 5), padx=10, sticky="w")

        self.target_combobox = ttk.Combobox(frame,
                                            textvariable=self.target,
                                            width=12)
        self.target_combobox.grid(row=2, column=2,  pady=(10, 5), padx=10, sticky="w")


        separator = ttk.Separator(frame, orient='horizontal')
        separator.grid(row=3, column=0, columnspan=4, pady=10, sticky="ew")


        title_label_2 = tk.Label(frame,
                               text="2. Modeling",
                               font=('Helvetica', 14, 'bold'))
        title_label_2.grid(row=4, column=0, columnspan=3, pady=(10, 5), padx=10, sticky="w")

        data_pca_button = tk.Button(frame,
                                    text="Build Model",
                                    command=self.modeling)
        data_pca_button.grid(row=5, column=0, pady=(10, 5), padx=10, sticky="w")

        report_button = tk.Button(frame,
                                  text="Model Report",
                                  command=self.master.show_report)
        report_button.grid(row=5, column=1, pady=(10, 5), padx=10, sticky="w")

        report_plot_button = tk.Button(frame,
                                       text="Model Report Plot",
                                       command=self.master.show_report_plot)
        report_plot_button.grid(row=5, column=2, pady=(10, 5), padx=10, sticky="w")

        separator = ttk.Separator(frame, orient='horizontal')
        separator.grid(row=6, column=0, columnspan=4, pady=10, sticky="ew")

        title_label_1 = tk.Label(frame, text="3. Calculate",
                                 font=('Helvetica', 14, 'bold'))
        title_label_1.grid(row=7, column=0, columnspan=3, pady=(10, 5), padx=10, sticky="w")

        derive_button = tk.Button(frame,
                                       text="Calculate",
                                       command=self.derive)
        derive_button.grid(row=8, column=0, pady=(10, 5), padx=10, sticky="w")

        results_button = tk.Button(frame, text="Result Plot", command=self.master.show_result_plot)
        results_button.grid(row=8, column=1, pady=(10, 5), padx=10, sticky="w")

        table_button = tk.Button(frame, text="Show Table", command=self.master.show_table)
        table_button.grid(row=8, column=2, pady=(10, 5), padx=10, sticky="w")

    def get_info_columns(self):
        if table_data is None:
            open_table()
        columns_names = list(table_data.columns)
        self.target_combobox['values'] = columns_names
        self.target_combobox.current(0)

    def correlation_analysis(self):
        if table_data is None:
            open_table()
        MathModels.correlation_plot(table_data)
        self.master.choosing_target()
        self.get_info_columns()

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
        selected_features = MathModels.select_features(self.filtered_data, self.target.get())
        X = self.filtered_data[selected_features].values
        y = self.filtered_data[self.target.get()].values
        self.model, self.report = create_regression_model(X, y)
        self.master.pca_analysis()
        self.selected_features = selected_features

    def derive(self):
        X = table_data[self.selected_features]
        yerr = np.zeros(len(X))
        y_out = np.zeros(len(X))

        k = ~np.isnan(X).any(axis=1)
        x = X.loc[k]
        y_out[k] = self.model.predict((x.values.reshape(-1, 1)))
        yerr[k] = self.mass_uncertainty(y_out[k]) * 0.15

        table_data[self.target.get() + '_calc'] = y_out
        table_data[self.target.get() + '_e'] = yerr
        table_data.to_csv('_final_result_table.csv', index=None)

        ToastNotification("Derivation by Mathematical Model",
                          f"{self.target.get()} calculated successfully.",
                          duration=6000, bootstyle='dark').show_toast()



    def setup_spectro_ui(self, frame):
        pass

    def setup_statistical_ui(self, frame):
        pass  # Add statistical tools for analysis tab UI elements here

    def setup_mass_determination_ui(self, frame):
        frame.grid_columnconfigure(3, weight=1)
        frame.grid_rowconfigure(12, weight=1)

        isoc_label = tk.Label(frame, text="Isochrones Fitting", font=('Helvetica', 12, 'bold'))
        isoc_label.grid(row=0, column=0, columnspan=3, pady=(10, 5), padx=10, sticky="w")

        # Define widgets and layout for Isochrones Fitting
        model_label = tk.Label(frame, text="Select Isochrone Model:")
        model_label.grid(row=1, column=0, pady=(10, 5), padx=10, sticky="w")

        models = ('Siess 2000', 'BHAC15', 'PARSEC')

        iso_model_combobox = ttk.Combobox(frame, textvariable=self.iso_selected_model, width=10)
        iso_model_combobox['values'] = models
        iso_model_combobox.current(0)
        iso_model_combobox.grid(row=1, column=1, pady=(10, 5), padx=(0, 10), sticky="w")

        locate_stars_button = tk.Button(frame, text="Locate Stars", command=self.locate_stars)
        locate_stars_button.grid(row=1, column=2, pady=(10, 5), padx=0, sticky="w")

        self.progress = ttk.Progressbar(frame, length=200, mode='determinate', style='info')
        self.progress.grid(row=2, column=0, columnspan=4, pady=(10, 5), ipadx=0, sticky='ew')

        isoc_label = tk.Label(frame, text="Mass-Magnitude Modeling", font=('Helvetica', 12, 'bold'))
        isoc_label.grid(row=3, column=0, columnspan=3, pady=(10, 5), padx=10, sticky="w")

        model_label = tk.Label(frame, text="Isochrone Model:")
        model_label.grid(row=4, column=0, pady=(10, 5), padx=10, sticky="w")

        models = ('bhac15', 'parsec', 'mist')

        model_combobox = ttk.Combobox(frame, textvariable=self.selected_model, width=10)
        model_combobox['values'] = models
        model_combobox.current(0)
        model_combobox.grid(row=4, column=1, pady=(10, 5), padx=(0, 10), sticky="w")

        self.low_int.set(0.1)
        self.hig_int.set(1.3)
        spin_low = ttk.Spinbox(frame, from_=0.01, to=0.6, increment=0.1, textvariable=self.low_int, width=5)
        spin_low.grid(row=5, column=1, pady=(10, 5), padx=0, sticky="w")
        spin_high = ttk.Spinbox(frame, from_=0.6, to=1.39, increment=0.1, textvariable=self.hig_int, width=5)
        spin_high.grid(row=5, column=2, pady=(10, 5), padx=0, sticky="w")
        spin_label = ttk.Label(frame, text='Mass range:')
        spin_label.grid(row=5, column=0, pady=(10, 5), padx=10, sticky="w")

        label = tk.Label(frame, text='Isochrone Age:')
        label.grid(row=7, column=0, pady=(10, 5), padx=10, sticky="w")

        self.scale_int.set(112)
        scale = ttk.Scale(frame, from_=1, to=1000, length=165, orient='horizontal', variable=self.scale_int)
        scale.grid(row=7, column=1, pady=(10, 5), padx=(0, 10), sticky="w")

        entry = tk.Entry(frame, textvariable=self.scale_int, width=5)
        entry.grid(row=7, column=2, pady=(10, 5), padx=(0, 10), sticky="w")
        label = ttk.Label(frame, text='Myr')
        label.grid(row=7, column=2, pady=(10, 5), padx=65, sticky="w")

        filter_label = tk.Label(frame, text="Select Magnitude Filter:")
        filter_label.grid(row=8, column=0, pady=(10, 5), padx=10, sticky="w")

        filters = ('G', 'G_BP', 'G_RP', 'U', 'B', 'V', 'I', 'J', 'H', 'K')
        self.selected_filter.set(filters[0])

        filter_combobox = ttk.Combobox(frame, textvariable=self.selected_filter, width=10)
        filter_combobox['values'] = filters
        filter_combobox.grid(row=8, column=1, pady=(10, 5), padx=(0, 10), sticky="w")

        # Create button to calculate mass
        build_button = tk.Button(frame, text="Build Model", command=self.build_model)
        build_button.grid(row=8, column=2, pady=(10, 5), padx=0, sticky="w")
        self.check_var.set(1)
        menu_toggle = ttk.Checkbutton(frame,
                                      text='Distance Correction',
                                      variable=self.check_var,
                                      onvalue=1,
                                      offvalue=0)
        menu_toggle.grid(row=10, column=0, pady=(10, 5), padx=10, sticky="w")

        self.clsuter_dist.set(125)

        entry2 = tk.Entry(frame, textvariable=self.clsuter_dist, width=5)
        entry2.grid(row=10, column=1, pady=(10, 5), padx=0, sticky="w")
        label = ttk.Label(frame, text='pc')
        label.grid(row=10, column=1, pady=(10, 5), padx=65, sticky="w")

        report_button = tk.Button(frame, text="Model Report", command=self.master.show_report)
        report_button.grid(row=9, column=0, pady=(10, 5), padx=10, sticky="w")
        report_plot_button = tk.Button(frame, text="Model Report Plot", command=self.master.show_report_plot)
        report_plot_button.grid(row=9, column=1, pady=(10, 5), padx=0, sticky="w")

        calculate_mass_button = tk.Button(frame, text="Calculate Mass", command=self.predict_mass)
        calculate_mass_button.grid(row=10, column=2, pady=(10, 5), padx=0, sticky="w")

        separator = ttk.Separator(frame, orient='horizontal')
        separator.grid(row=11, column=0, columnspan=4, pady=10, sticky="ew")

        table_button = tk.Button(frame, text="Show Table", command=self.master.show_table)
        table_button.grid(row=12, column=0, pady=0, padx=10, sticky="w")

        results_button = tk.Button(frame, text="Result Plot", command=self.master.show_result_plot)
        results_button.grid(row=12, column=1, pady=0, padx=(0, 10), sticky="w")

    def build_model(self):
        self.method = 'MMR'
        clust_age = self.scale_int.get()
        range_mass = [self.low_int.get(), self.hig_int.get()]
        mag_filter = self.selected_filter.get()

        if self.selected_model:
            th_model = madys.IsochroneGrid(self.selected_model.get(), mag_filter, mass_range=range_mass,
                                           age_range=clust_age, n_steps=[1000, 1000])
            y = np.log10(th_model.masses)
            X = th_model.data[:, :, 0].ravel().reshape(-1, 1)
            self.model, self.report = create_regression_model(X, y)
            self.X = th_model.data[:, :, 0].ravel()
            self.y = y
            self.th_model_data = pd.DataFrame({'X': th_model.data[:, :, 0].ravel(), 'y': y})
        else:
            messagebox.showinfo("Regression model", f"Failed to build the regression model for these parameters.")

    @staticmethod
    def mass_uncertainty(y):
        mu = np.mean(np.nan_to_num(y))
        sigma = np.var(np.nan_to_num(y))
        uncertainty = np.sqrt(mu ** 2 + sigma ** 2)
        return uncertainty

    def predict_mass(self):
        global table_data

        if table_data is None:
            open_table()

        if f'{self.selected_filter.get()}mag' in table_data.items():
            ToastNotification("Collecting data:",
                              f"Magnitude in filter {self.selected_filter.get()} isn't found on your table.",
                              duration=6000, bootstyle='light').show_toast()
        else:
            mag = table_data[f'{self.selected_filter.get()}mag'].values
            yerr = np.zeros(len(mag))
            mass = np.zeros(len(mag))

            if self.check_var.get() == 1:
                mag, k = FilterValues.filter_predict(mag, self.X, clust_dist=self.clsuter_dist.get())
            else:
                mag, k = FilterValues.filter_predict_un(mag, self.X)

            mass[k] = self.model.predict(mag.reshape(-1, 1))
            yerr[k] = self.mass_uncertainty(mass[k]) * 0.15
            key = np.where(np.array(mass) == 0.)[0]
            hold_mass = np.array(mass)
            hold_mass[key] = np.nan
            table_data['Mass_calc'] = 10**hold_mass
            table_data['Mass_e'] = yerr
            table_data.to_csv('_final_result_table.csv', index=None)

            ToastNotification("Mass Determination",
                              f"Mass calculated successfully for filter {self.selected_filter.get()}.",
                              duration=6000, bootstyle='dark').show_toast()

    def locate_stars(self):
        global table_data
        if table_data is None:
            open_table()
        model = self.iso_selected_model.get()
        self.method = 'ISO'
        var, Nlines, alldataiso = intpol(model)
        teff = table_data['Teff'].values
        Tinput = teff
        Linput = table_data['logL'].values
        Nobjects = len(Tinput)

        primarydataset = []
        ff = []

        for i in range(Nobjects):
            if np.isfinite(Linput) is not None:
                res = interp(Tinput[i], Linput[i], var, Nlines, alldataiso)
                ff.append(i)
                primarydataset.append(res)

                self.progress['value'] = (i + 1) / Nobjects * 100
                self.update_idletasks()

        # Convert primarydataset to DataFrame
        primarydataset = pd.DataFrame(primarydataset)
        primarydataset = primarydataset.rename(columns={0: 'Age', 1: 'Mass', 2: 'Teff', 3: 'logL'})
        mass = interpolmass(primarydataset, self.iso_selected_model.get())
        yerr = np.zeros(len(teff))

        row = pd.DataFrame({'mass': mass})
        hold = np.zeros(len(mass))
        hold[ff] = row.loc[ff, 'mass'].values
        yerr[ff] = self.mass_uncertainty(hold[ff]) * 0.1

        mass = hold

        table_data['Mass_calc'] = mass
        table_data['Mass_e'] = yerr

        table_data.to_csv('_final_result_table.csv', index=None)
        self.master.show_hrd_plot()
        toast = ToastNotification(
            title='Star Localization',
            message="Stars completely localized on HR-Diagram.",
            duration=5000,
            bootstyle='dark'
            )
        toast.show_toast()


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
        self.help_menu.add_command(label='Documentation', command=lambda: print('Test button'))
        self.help_menu.add_command(label='About', command=self.open_about_window)
        self.help_menu.add_command(label='Dark Mode', command=self.change_style)
        self.toolbar_menu.add_cascade(label='Help', menu=self.help_menu)

        self.toolbar_menu.add_command(label='Exit', command=self.master.quit)

        self.master.configure(menu=self.toolbar_menu)

    def open_about_window(self):
        """
        Open the About window.
        """
        about_window = AboutWindow(self)
        about_window.grab_set()


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

            if not teff_column or not logl_column:
                missing_columns = []
                if not teff_column:
                    missing_columns.append('Teff')
                if not logl_column:
                    missing_columns.append('logL')

                messagebox.showerror("Open Data Table", f"Missing required columns for Isochrone Fitting:"
                                                        f" {', '.join(missing_columns)}")
            else:
                pass
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
