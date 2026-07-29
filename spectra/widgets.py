import ttkbootstrap as ttk
import tkinter as tk
import pickle
import threading
import os
import io
import contextlib
import subprocess
import shutil
from tkinter import filedialog, messagebox
import sys

from . import __version__
from .paths import PROJECT_ROOT

class SessionManager:
    @staticmethod
    def save_session():
        filename = filedialog.askopenfilename(filetypes=[("Text file", "*.text"), ("All files", "*.*")])
        if filename:
            with open(filename, 'wb') as f:
                pickle.dump(SessionManager.session_data, f)

    @staticmethod
    def load_session(filename):
        with open(filename, 'rb') as f:
            SessionManager.session_data = pickle.load(f)

    @staticmethod
    def set_session_data(key, value):
        SessionManager.session_data[key] = value

    @staticmethod
    def get_session_data(key):
        return SessionManager.session_data.get(key)


class AboutWindow(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About")
        self.geometry("800x450")
        self.create_widgets()

    def create_widgets(self):

        # License label
        license_label = tk.Label(self, 
        text=f"S.P.E.C.T.R.A. v{__version__} \n"
        "Copyright (C) 2026 João Paulo Almeida da Silva Matos, Maria Jaqueline Vasconcelos, Adriano Hoth Cerqueira \n"
        "This program comes with ABSOLUTELY NO WARRANTY. \n"
        "This is free software, and you are welcome to redistribute it under certain conditions under the  \n" 
        "terms of the GNU General Public License v3. For full license details, visit: https://www.gnu.org/licenses/")
        license_label.pack(padx=20, pady=20)

        # Description label
        description_label = tk.Label(self,
                                     text="Description: S.P.E.C.T.R.A. \n"
                                          "(Stellar Parameter Estimation and Calculation Tools for Research and Analysis) "
                                          "\nis a software tool designed for the comprehensive analysis of stellar "
                                          "data."
                                          "\nIt provides astronomers and astrophysicists with a suite of powerful "
                                          "algorithms"
                                          "\nfor determining various parameters related to stars, including stellar"
                                          ' type,'
                                          "\nluminosity, temperature, radius, mass, age, and distance. This program is "
                                          "\nintended for research and educational purposes, offering a user-friendly "
                                          "\ninterface and accurate analytical capabilities for studying the properties"
                                          "\nand behaviors of stars across the cosmos.")
        description_label.pack(padx=20, pady=10)

        # Label displaying program date
        date_label = tk.Label(self, text="Last update: 28/07/2026")
        date_label.pack(padx=20, pady=5)

        # Button to check for updates
        update_btn = ttk.Button(
            self,
            text="🔄 Atualizar Programa",
            bootstyle="primary",
            command=self._open_update_window
        )
        update_btn.pack(padx=20, pady=10)

    def _open_update_window(self):
        parent_app = self.master
        while hasattr(parent_app, 'master') and not hasattr(parent_app, 'update_program') and parent_app.master:
            parent_app = parent_app.master
        if hasattr(parent_app, 'update_program'):
            parent_app.update_program()
        else:
            UpdateWindow(self)


class UpdateWindow(ttk.Toplevel):
    """
    Window to check for and execute program updates via Git repository pull.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Atualizar Programa")
        self.geometry("450x180")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.status_var = tk.StringVar(value="Verificando atualizações no repositório...")
        tk.Label(self, textvariable=self.status_var, wraplength=410, justify="center", font=('Helvetica', 10)).pack(
            padx=20, pady=(20, 10), fill="x"
        )

        self.progress = ttk.Progressbar(self, mode='indeterminate')
        self.progress.pack(fill='x', padx=20, pady=10)
        self.progress.start(10)

        threading.Thread(target=self._run_update_check, daemon=True).start()

    def _run_update_check(self):
        git_path = shutil.which("git")
        if not git_path:
            self.after(0, lambda: self._finish_error("O Git não está instalado ou não foi encontrado no sistema (PATH)."))
            return

        git_dir = os.path.join(PROJECT_ROOT, ".git")
        if not os.path.exists(git_dir):
            self.after(0, lambda: self._finish_error("O diretório do programa não é um repositório Git válido."))
            return

        try:
            self.after(0, lambda: self.status_var.set("Conectando ao GitHub e baixando atualizações..."))
            
            result = subprocess.run(
                [git_path, "pull"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=30
            )

            stdout = result.stdout.strip() if result.stdout else ""
            stderr = result.stderr.strip() if result.stderr else ""

            if result.returncode == 0:
                if "Already up to date" in stdout or "Já está atualizado" in stdout or "Already up-to-date" in stdout:
                    self.after(0, lambda: self._finish_success("O S.P.E.C.T.R.A já está na versão mais recente!"))
                else:
                    msg = (
                        "Atualização realizada com sucesso!\n\n"
                        "Por favor, reinicie a aplicação para que todas as alterações entrem em vigor."
                    )
                    self.after(0, lambda: self._finish_success(msg, is_new_version=True))
            else:
                error_msg = stderr if stderr else stdout
                self.after(0, lambda err=error_msg: self._finish_error(f"Falha ao executar 'git pull':\n{err}"))
        except subprocess.TimeoutExpired:
            self.after(0, lambda: self._finish_error("Tempo limite esgotado ao tentar se conectar ao servidor de atualizações."))
        except Exception as e:
            self.after(0, lambda err=str(e): self._finish_error(f"Erro inesperado durante a atualização:\n{err}"))

    def _finish_success(self, message, is_new_version=False):
        self.progress.stop()
        self.grab_release()
        self.destroy()
        if is_new_version:
            messagebox.showinfo("Atualização Concluída", message)
        else:
            messagebox.showinfo("Atualização do Programa", message)

    def _finish_error(self, error_message):
        self.progress.stop()
        self.grab_release()
        self.destroy()
        messagebox.showwarning("Atualização do Programa", error_message)



class ModelDownloadWindow(ttk.Toplevel):
    """
    Shown on first launch, before the main window is displayed, to fetch the
    data the app depends on:
      1. MADYS isochrone models (BHAC15, PARSEC, MIST), via
         madys.ModelHandler.download_model.
      2. The Siess 2000 / BHAC15 evolutionary-track and isochrone data
         tables (the `isochrone_models/` folder), pulled from a shared
         Google Drive folder via `gdown`, since these aren't distributed
         with the app.
    Downloading happens on a background thread so the UI doesn't freeze;
    all widget updates are marshalled back onto the Tk main thread via
    `after(0, ...)`.
    """
    def __init__(self, parent, models, on_complete, isochrone_url=None, isochrone_dest=None):
        super().__init__(parent)
        self.title("Downloading Stellar Models")
        self.geometry("440x160")
        self.resizable(False, False)
        # Block the window-close button so the download can't be interrupted
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        self.models = models
        self.isochrone_url = isochrone_url
        self.isochrone_dest = isochrone_dest
        self.on_complete = on_complete

        total_steps = len(models) + (1 if isochrone_url else 0)

        self.status_var = tk.StringVar(value="Preparing to download stellar models...")
        tk.Label(self, textvariable=self.status_var, wraplength=400, justify="left").pack(
            padx=20, pady=(20, 10), fill="x"
        )

        self.progress = ttk.Progressbar(self, mode='determinate', maximum=max(total_steps, 1))
        self.progress.pack(fill='x', padx=20, pady=10)

        self.grab_set()
        self.after(100, self._start_download)

    def _start_download(self):
        threading.Thread(target=self._download_all, daemon=True).start()

    def _download_all(self):
        import madys
        failed = []
        step = 0
        available_hint = None  # fetched lazily, only if a download fails

        for model in self.models:
            self.after(0, lambda m=model: self.status_var.set(f"Downloading model: {m} ..."))
            try:
                old_stdin = sys.stdin
                sys.stdin = io.StringIO("Y\nY\nY\nY\nY\n")
                max_retries = 3

                for attempt in range(max_retries):
                    try:
                        madys.ModelHandler.download_model(model)
                        break  # Concluído com sucesso, sai do loop de retentativas
                    except Exception as download_err:
                        if attempt == max_retries - 1:
                            raise download_err  # Lança a exceção se falhar na última tentativa
                        self.after(0, lambda a=attempt+2: self.status_var.set(
                            f"Retrying download for {model} (Attempt {a}/{max_retries})..."
                        ))
                
            except Exception as e:
                if available_hint is None:
                    available_hint = self._get_available_models_hint()
                failed.append((model, f"{e}\n  Valid model_grid names reported by madys:\n  {available_hint}"))
            finally:
                sys.stdin = old_stdin

            step += 1
            self.after(0, lambda v=step: self.progress.configure(value=v))

        if self.isochrone_url:
            self.after(0, lambda: self.status_var.set(
                "Downloading isochrone/evolutionary-track data "
                "(Siess 2000, BHAC15) — this can take a while..."
            ))
            try:
                import gdown
                os.makedirs(self.isochrone_dest, exist_ok=True)
                gdown.download_folder(
                    url=self.isochrone_url,
                    output=self.isochrone_dest,
                    quiet=False,
                    use_cookies=False,
                )
            except Exception as e:
                failed.append(('isochrone_models', str(e)))
            step += 1
            self.after(0, lambda v=step: self.progress.configure(value=v))

        self.after(0, lambda: self._finish(failed))

    @staticmethod
    def _get_available_models_hint():
        """
        Best-effort lookup of the model_grid identifiers madys actually
        expects. madys.ModelHandler.available() may print its info rather
        than return it, so stdout is captured as a fallback.
        """
        try:
            import madys
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                result = madys.ModelHandler.available()
            if result:
                return str(result)
            printed = buf.getvalue().strip()
            return printed if printed else "(available() produced no output)"
        except Exception as e:
            return f"(could not call ModelHandler.available(): {e})"

    def _finish(self, failed):
        # Release this window's modal grab and stop blocking the close
        # button *before* popping any messagebox. Leaving the grab active
        # while a second modal dialog opens is what caused the window to
        # become unresponsive (clicks not registering on OK, the X button
        # doing nothing).
        self.grab_release()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        if failed:
            details = "\n".join(f"- {name}: {err}" for name, err in failed)
            messagebox.showwarning(
                "Model Download",
                "Some required data could not be downloaded and related "
                "features may not work until this is resolved:\n\n" + details,
                parent=self,
            )
        self.destroy()
        self.on_complete(failed)


class BusyWindow(ttk.Toplevel):
    """
    Generic "please wait" modal for any long-running background task (e.g.
    fitting the Mass-Magnitude regression models, which can involve
    GridSearchCV over several models and take a long time on large
    datasets). Runs `task` on a background thread so the Tk mainloop stays
    responsive instead of appearing to freeze, and so an exception in
    `task` (including something like a MemoryError from an oversized fit)
    is caught and reported cleanly instead of taking the whole app down.

    `task` must be a zero-argument callable that does NOT create or touch
    any Tk widgets (Tk is not thread-safe) — pure computation only. Its
    return value (or the exception it raised) is delivered to
    `on_complete(result, error)`, which runs back on the main thread, so
    that's the right place to create ToastNotifications, update widgets,
    etc.
    """
    def __init__(self, parent, message, task_func, on_done_func):
        super().__init__(parent)
        self.title("Please Wait")
        self.geometry("400x200")
        self.transient(parent)
        self.grab_set()

        self.cancel_event = threading.Event()

        lbl = ttk.Label(self, text=message, wraplength=350, justify="center")
        lbl.pack(pady=15)

        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x", padx=20, pady=5)
        self.progress.start(10)

        # 🔘 Botão de Cancelar
        self.btn_cancel = ttk.Button(
            self, 
            text="Cancel", 
            bootstyle="dark", 
            command=self._on_cancel
        )
        self.btn_cancel.pack(pady=10)

        def runner():
            try:
                # Passa o cancel_event para a tarefa de fundo
                try:
                    res = task_func(self.cancel_event)
                except TypeError:
                    res = task_func()
                err = None
            except Exception as e:
                res = None
                err = e
            
            self.after(0, lambda r=res, e=err: self._finish(r, e, on_done_func))

        threading.Thread(target=runner, daemon=True).start()

    def _on_cancel(self):
        # Dispara o sinal de cancelamento para o laço
        self.cancel_event.set()
        self.btn_cancel.config(text="Canceling...", state="disabled")

    def _finish(self, res, err, on_done_func):
        self.progress.stop()
        self.destroy()
        if on_done_func:
            on_done_func(res, err)


class SizeNotifier:
    def __init__(self, window, size_dict):
        self.window = window
        self.size_dict = {key: value for key, value in sorted(size_dict.items())}
        self.current_min_size = None
        self.window.bind('<Configure>', self.check_size)

        self.window.update()

        min_height = self.window.winfo_height()
        min_width = list(self.size_dict)[0]
        self.window.minsize(min_width, min_height)

    def check_size(self, event):
        if event.widget == self.window:
            window_width = event.width
            checked_size = None

            for min_size in self.size_dict:
                delta = window_width - min_size
                if delta >= 0:
                    checked_size = min_size

            if checked_size != self.current_min_size:
                self.current_min_size = checked_size
                self.size_dict[self.current_min_size]()


def get_madys_models_status():
    """
    Checks local installation status for all MADYS models.
    """
    try:
        import madys
        from madys.madys import stored_data
        
        models_dict = stored_data.get('models', {})
        if isinstance(models_dict, dict) and 'data' in models_dict:
            models_dict = models_dict['data']
            
        local_models = stored_data.get('local_model_list', {})
        local_names = set()
        if isinstance(local_models, (dict, list)):
            for k in local_models:
                clean_name = str(k).split('_')[0].lower()
                local_names.add(clean_name)
                
        isochrones_path = os.path.join(os.path.dirname(madys.__file__), 'isochrones')
        if os.path.exists(isochrones_path):
            for item in os.listdir(isochrones_path):
                clean_item = str(item).split('_')[0].lower()
                local_names.add(clean_item)

        results = []
        popular = ['bhac15', 'parsec', 'mist', 'baraffe15', 'baraffe98', 'siess2000']
        all_names = list(models_dict.keys())
        
        remaining = [m for m in all_names if m not in popular]
        ordered_names = [m for m in popular if m in all_names] + sorted(remaining)

        for m_name in ordered_names:
            info = models_dict.get(m_name, {})
            ref = info.get('ref', '')
            family = info.get('family', '')
            mass_r = info.get('mass_range', [0.1, 1.5])
            age_r = info.get('age_range', [1.0, 1000.0])
            
            is_installed = str(m_name).lower() in local_names
            results.append({
                'name': m_name,
                'family': family,
                'ref': ref,
                'mass_str': f"{mass_r[0]:.2f} - {mass_r[1]:.2f} M_sun",
                'age_str': f"{age_r[0]:.1f} - {age_r[1]:.0f} Myr",
                'installed': is_installed
            })
            
        return results
    except Exception:
        return [
            {'name': 'bhac15', 'family': 'PHOENIX', 'ref': 'Baraffe et al. (2015)', 'mass_str': '0.01 - 1.40 M_sun', 'age_str': '0.5 - 10000 Myr', 'installed': True},
            {'name': 'parsec', 'family': 'PARSEC', 'ref': 'Bressan et al. (2012)', 'mass_str': '0.09 - 14.00 M_sun', 'age_str': '0.1 - 10000 Myr', 'installed': False},
            {'name': 'mist', 'family': 'MIST', 'ref': 'Choi et al. (2016)', 'mass_str': '0.10 - 10.00 M_sun', 'age_str': '0.1 - 10000 Myr', 'installed': True},
        ]


class MadysModelManagerWindow(ttk.Toplevel):
    """
    Dedicated Manager Dialog allowing users to view, inspect, and download MADYS Isochrone Models.
    """
    def __init__(self, parent, on_update_callback=None):
        super().__init__(parent)
        self.title("📦 MADYS Isochrone Models Manager")
        self.geometry("900x580")
        self.resizable(True, True)
        self.transient(parent)
        self.on_update_callback = on_update_callback
        
        self._create_ui()
        self.refresh_list()
        
    def _create_ui(self):
        container = ttk.Frame(self, padding=20)
        container.pack(fill=BOTH, expand=True)
        
        # Header Card
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(header_frame, text="📦 MADYS Isochrone Models Repository", font=('Helvetica', 14, 'bold')).pack(anchor="w")
        ttk.Label(header_frame, text="Inspect installed evolutionary grids or download new model grids from Zenodo.", font=('Helvetica', 9)).pack(anchor="w", pady=(2, 0))
        
        self.status_summary_var = tk.StringVar(value="Loading models status...")
        ttk.Label(header_frame, textvariable=self.status_summary_var, font=('Helvetica', 10, 'bold'), bootstyle="info").pack(anchor="w", pady=(5, 0))
        
        # Table / Treeview Frame
        table_frame = ttk.Frame(container)
        table_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        columns = ("Model", "Status", "Mass Bounds", "Age Bounds", "Reference / Family")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=14)
        
        self.tree.heading("Model", text="Isochrone Model")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Mass Bounds", text="Mass Range")
        self.tree.heading("Age Bounds", text="Age Range")
        self.tree.heading("Reference / Family", text="Reference / Family")
        
        self.tree.column("Model", width=110, anchor="center")
        self.tree.column("Status", width=120, anchor="center")
        self.tree.column("Mass Bounds", width=130, anchor="center")
        self.tree.column("Age Bounds", width=140, anchor="center")
        self.tree.column("Reference / Family", width=340, anchor="w")
        
        sb_y = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb_y.set)
        
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        sb_y.pack(side=RIGHT, fill=Y)
        
        # Action Button Frame
        f_actions = ttk.Frame(container)
        f_actions.pack(fill=X)
        
        ttk.Button(f_actions, text="⬇️ Download Selected Model", bootstyle="primary", command=self.download_selected).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_actions, text="🔄 Refresh List", bootstyle="info-outline", command=self.refresh_list).pack(side=LEFT, padx=(0, 10))
        ttk.Button(f_actions, text="❌ Close", bootstyle="secondary-outline", command=self.destroy).pack(side=RIGHT)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.models_data = get_madys_models_status()
        installed_count = sum(1 for m in self.models_data if m['installed'])
        self.status_summary_var.set(f"Installed Models: {installed_count} / {len(self.models_data)} Available Grids")
        
        for m in self.models_data:
            status_text = "🟢 Installed" if m['installed'] else "⚪ Not Installed"
            ref_text = f"{m['ref']} ({m['family']})" if m['ref'] else m['family']
            self.tree.insert("", "end", values=(m['name'], status_text, m['mass_str'], m['age_str'], ref_text))
            
        if self.on_update_callback:
            try:
                self.on_update_callback()
            except Exception:
                pass

    def download_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Select Model", "Please select a model from the table list to download.", parent=self)
            return
            
        item_vals = self.tree.item(selected_item[0], "values")
        model_name = item_vals[0]
        status = item_vals[1]
        
        if "Installed" in status and "Not" not in status:
            messagebox.showinfo("Already Installed", f"Model '{model_name}' is already installed locally.", parent=self)
            return
            
        def _download_task(cancel_event=None):
            import madys
            old_stdin = sys.stdin
            sys.stdin = io.StringIO("Y\nY\nY\nY\nY\n")
            try:
                madys.ModelHandler.download_model(model_name)
            finally:
                sys.stdin = old_stdin

        def _on_done(res, err):
            if err:
                messagebox.showerror("Download Error", f"Failed to download model '{model_name}':\n{err}", parent=self)
            else:
                ToastNotification(
                    title="Model Downloaded",
                    message=f"MADYS Model '{model_name}' successfully downloaded and cached!",
                    duration=5000,
                    bootstyle="success"
                ).show_toast()
                self.refresh_list()

        BusyWindow(
            self,
            f"Downloading MADYS Model '{model_name}' from Zenodo repository — please wait...",
            _download_task,
            _on_done
        )