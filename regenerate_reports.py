import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from spectra.tools import ResultDisplay

clusters = [
    {"name": "onc", "file": "articles/tcc/Resultados/tabelas_dezembro_2024/onc/onc_results_merged_table.csv"},
    {"name": "usco", "file": "articles/tcc/Resultados/tabelas_dezembro_2024/upperScorpius/usco_results_merged_table.csv"},
    {"name": "hper", "file": "articles/tcc/Resultados/tabelas_dezembro_2024/hPersei/hper_results_merged_table.csv"},
    {"name": "ple", "file": "articles/tcc/Resultados/tabelas_dezembro_2024/pleiades/pleiades_results_merged_table.csv"},
    {"name": "ngc2516", "file": "articles/tcc/Resultados/tabelas_dezembro_2024/ngc2516/ngc2516_final_result_table_merged_table.csv"}
]

for c in clusters:
    print(f"Generating for {c['name']}...")
    try:
        df = pd.read_csv(c['file'])
        
        teff_col = next((col for col in ['Teff', 'teff', 'T_eff', 'TEFF', 't_eff', 'Teff_x'] if col in df.columns), None)
        if not teff_col:
            print(f"Skipping {c['name']}: No Teff column")
            continue
            
        x = df[teff_col]
        
        y_col = [col for col in df.columns if 'Mass_calc' in col]
        err_col = [col for col in df.columns if 'Mass_e' in col]
        
        if y_col:
            y = df[y_col[0]]
            yerr = df[err_col[0]] if err_col else np.zeros_like(y)
            
            fra = ResultDisplay(x.values, y.values, yerr.values, 'ISO', target_name='Estimated')
            fra.res_plot(save_file=True)
            
            src = os.path.join('outputs', 'plots', '_results_display.png')
            dst = os.path.join('publishing', 'mnras_paper', 'figures', f'{c["name"]}_results_report.png')
            
            if os.path.exists(dst):
                os.remove(dst)
            os.rename(src, dst)
            print(f"Saved {dst}")
        else:
            print(f"Skipping {c['name']}: No Mass_calc column")
    except Exception as e:
        print(f"Failed for {c['name']}: {e}")
