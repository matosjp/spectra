import os
import sys

# Ensure parent directory is in sys.path if launched directly from inside spectra/
pkg_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(pkg_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from .interface import App
except (ImportError, ValueError):
    try:
        from spectra.interface import App
    except (ImportError, ModuleNotFoundError):
        from interface import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
