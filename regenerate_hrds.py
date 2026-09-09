import os
import sys
import matplotlib.pyplot as plt

plt.switch_backend('Agg')

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from spectra.StarLocalization import plot_HRD
from spectra.cli import run_isocfit_cli

class CLIArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TCC_DATA_DIR = os.path.join(BASE_DIR, "articles", "tcc", "Resultados", "tabelas_dezembro_2024")
FIGURES_DIR = os.path.join(BASE_DIR, "publishing", "mnras_paper", "figures")

clusters = [
    {"name": "onc", "file": os.path.join(TCC_DATA_DIR, "onc", "onc_results_merged_table.csv")},
    {"name": "usco", "file": os.path.join(TCC_DATA_DIR, "upperScorpius", "usco_results_merged_table.csv")},
    {"name": "hper", "file": os.path.join(TCC_DATA_DIR, "hPersei", "hper_results_merged_table.csv")},
    {"name": "ple", "file": os.path.join(TCC_DATA_DIR, "pleiades", "pleiades_results_merged_table.csv")},
    {"name": "ngc2516", "file": os.path.join(TCC_DATA_DIR, "ngc2516", "ngc2516_final_result_table_merged_table.csv")}
]

for c in clusters:
    print(f"Regenerating HRD for {c['name']} with BHAC15...")
    args = CLIArgs(input=c["file"], model="BHAC15", output_dir=os.path.join(BASE_DIR, "outputs"), verbose=False, html=False)
    try:
        res = run_isocfit_cli(args)
        out_path = os.path.join(FIGURES_DIR, f"{c['name']}_hrd_complete.png")
        plot_HRD(res, "BHAC15", output_path=out_path)
        print(f"Saved {out_path}")
    except Exception as e:
        print(f"Failed for {c['name']}: {e}")
