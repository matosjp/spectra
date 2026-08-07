# S.P.E.C.T.R.A. - Master Recalculation & Paper Results Re-Analysis Pipeline
# Copyright (C) 2026  João Paulo Matos Dias Gomes, Maria Jaqueline Vasconcelos, Adriano Hoth Cerqueira

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Ensure matplotlib runs headlessly
plt.switch_backend('Agg')
plt.style.use('seaborn-v0_8-paper' if 'seaborn-v0_8-paper' in plt.style.available else 'default')
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 12,
    'figure.dpi': 300
})

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from spectra.cli import run_isocfit_cli, run_rmm_cli, run_primary_cli
from spectra.StarLocalization import intpol, interp
from spectra.tools import interpolmass

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TCC_DATA_DIR = os.path.join(BASE_DIR, "articles", "tcc", "Resultados", "tabelas_dezembro_2024")
OUTPUT_DIR = os.path.join(BASE_DIR, "publishing", "analysis_outputs")
FIGURES_DIR = os.path.join(BASE_DIR, "publishing", "mnras_paper", "figures")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

print("================================================================================")
print("S.P.E.C.T.R.A. v1.2.0 - MASTER CLUSTER RE-CALCULATION & PAPER RE-ANALYSIS")
print("================================================================================")


# Helper class for CLI arguments
class CLIArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


# ------------------------------------------------------------------------------
# 1. DEFINE CLUSTER JOBS & METADATA
# ------------------------------------------------------------------------------
clusters = [
    {
        "name": "ONC",
        "label": "Orion Nebula Cluster (ONC)",
        "file": os.path.join(TCC_DATA_DIR, "onc", "onc_results_merged_table.csv"),
        "distance_pc": 414.0,
        "av_mag": 1.50,
        "nominal_age": 1.5,
        "rmm_model": "bhac15",
        "rmm_filter": "V",
        "mass_range": [0.05, 2.0],
        "lit_sources": [
            {"name": "Hillenbrand (1997)", "col": "H97_Mass"},
            {"name": "Davies et al. (2014)", "col": "D14_Mass"}
        ]
    },
    {
        "name": "UpperScorpius",
        "label": "Upper Scorpius",
        "file": os.path.join(TCC_DATA_DIR, "upperScorpius", "usco_results_merged_table.csv"),
        "distance_pc": 140.0,
        "av_mag": 0.70,
        "nominal_age": 10.0,
        "rmm_model": "bhac15",
        "rmm_filter": "G",
        "mass_range": [0.01, 1.5],
        "lit_sources": [
            {"name": "TESS V8.2", "col": "Tess_Mass"}
        ]
    },
    {
        "name": "hPersei",
        "label": "h Persei (NGC 869)",
        "file": os.path.join(TCC_DATA_DIR, "hPersei", "hper_results_merged_table.csv"),
        "distance_pc": 2300.0,
        "av_mag": 1.65,
        "nominal_age": 13.0,
        "rmm_model": "bhac15",
        "rmm_filter": "V",
        "mass_range": [0.20, 2.5],
        "lit_sources": [
            {"name": "Moraux et al. (2013)", "col": "M13_Mass"},
            {"name": "TESS V8.2", "col": "Tess_Mass"}
        ]
    },
    {
        "name": "Pleiades",
        "label": "Pleiades (M45)",
        "file": os.path.join(TCC_DATA_DIR, "pleiades", "pleiades_results_merged_table.csv"),
        "distance_pc": 136.2,
        "av_mag": 0.03,
        "nominal_age": 112.0,
        "rmm_model": "bhac15",
        "rmm_filter": "G",
        "mass_range": [0.05, 2.0],
        "lit_sources": [
            {"name": "Lodieu et al. (2019)", "col": "Lod19_Mass"},
            {"name": "Delfosse et al. (2000)", "col": "Del00_Mass"},
            {"name": "TESS V8.2", "col": "TESS_Mass"}
        ]
    },
    {
        "name": "NGC2516",
        "label": "NGC 2516",
        "file": os.path.join(TCC_DATA_DIR, "ngc2516", "ngc2516_final_result_table_merged_table.csv"),
        "distance_pc": 412.0,
        "av_mag": 0.33,
        "nominal_age": 150.0,
        "rmm_model": "bhac15",
        "rmm_filter": "V",
        "mass_range": [0.15, 1.8],
        "lit_sources": [
            {"name": "Jackson et al. (2012)", "col": "J12_Mass"},
            {"name": "TESS V8.2", "col": "Tess_Mass"}
        ]
    }
]


# ------------------------------------------------------------------------------
# 2. RE-CALCULATION & STATISTICAL ANALYSIS ENGINE
# ------------------------------------------------------------------------------
age_summaries = []
stat_comparison_rows = []

for item in clusters:
    c_name = item["name"]
    c_label = item["label"]
    fpath = item["file"]

    print(f"\n--------------------------------------------------------------------------------")
    print(f"[PROCESSING] Cluster: {c_label}")
    print(f"   Input file: {fpath}")

    if not os.path.exists(fpath):
        print(f"⚠️ Warning: File not found: {fpath}, skipping.")
        continue

    # A. 2D Isochrone Fitting - Siess 2000
    args_siess = CLIArgs(input=fpath, model="Siess 2000", output_dir=OUTPUT_DIR, verbose=False, html=False)
    res_siess = run_isocfit_cli(args_siess)

    valid_ages_s = res_siess['Age_calc (Myr)'].dropna()
    valid_ages_s = valid_ages_s[np.isfinite(valid_ages_s)]
    mean_age_s = np.mean(valid_ages_s) if len(valid_ages_s) > 0 else np.nan
    std_age_s = np.std(valid_ages_s) if len(valid_ages_s) > 0 else np.nan
    sem_age_s = std_age_s / np.sqrt(len(valid_ages_s)) if len(valid_ages_s) > 1 else 0.0
    med_age_s = np.median(valid_ages_s) if len(valid_ages_s) > 0 else np.nan

    # B. 2D Isochrone Fitting - BHAC15
    args_bhac = CLIArgs(input=fpath, model="BHAC15", output_dir=OUTPUT_DIR, verbose=False, html=False)
    res_bhac = run_isocfit_cli(args_bhac)

    valid_ages_b = res_bhac['Age_calc (Myr)'].dropna()
    valid_ages_b = valid_ages_b[np.isfinite(valid_ages_b)]
    mean_age_b = np.mean(valid_ages_b) if len(valid_ages_b) > 0 else np.nan
    std_age_b = np.std(valid_ages_b) if len(valid_ages_b) > 0 else np.nan
    sem_age_b = std_age_b / np.sqrt(len(valid_ages_b)) if len(valid_ages_b) > 1 else 0.0
    med_age_b = np.median(valid_ages_b) if len(valid_ages_b) > 0 else np.nan

    age_summaries.append({
        "Cluster": c_name,
        "Nominal_Age": item["nominal_age"],
        "N_stars": len(valid_ages_s),
        "Siess_Mean_Age": round(mean_age_s, 2),
        "Siess_SEM_Age": round(sem_age_s, 2),
        "Siess_Std_Age": round(std_age_s, 2),
        "Siess_Med_Age": round(med_age_s, 2),
        "BHAC15_Mean_Age": round(mean_age_b, 2),
        "BHAC15_SEM_Age": round(sem_age_b, 2),
        "BHAC15_Std_Age": round(std_age_b, 2),
        "BHAC15_Med_Age": round(med_age_b, 2)
    })

    # C. Cross-Source Mass Evaluation against Literature
    for lit in item["lit_sources"]:
        lit_name = lit["name"]
        lit_col = lit["col"]

        if lit_col in res_siess.columns:
            yt = res_siess[lit_col]
            yp = res_siess['Mass_calc']

            valid = np.isfinite(yt) & np.isfinite(yp) & (yt > 0) & (yp > 0)
            y_true = np.array(yt)[valid]
            y_pred = np.array(yp)[valid]

            N = len(y_true)
            if N > 0:
                residuals = y_pred - y_true
                ss_res = np.sum(residuals**2)
                ss_tot = np.sum((y_true - np.mean(y_true))**2)
                r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 1.0
                rmse = np.sqrt(np.mean(residuals**2))
                mae = np.mean(np.abs(residuals))
                offset = np.mean(residuals)
                std_res = np.std(residuals)

                stat_comparison_rows.append({
                    "Cluster": c_name,
                    "Comparison": f"SPECTRA IsocFit vs {lit_name}",
                    "N": N,
                    "R2": round(r2, 4),
                    "RMSE": round(rmse, 4),
                    "MAE": round(mae, 4),
                    "Offset": round(offset, 4),
                    "Std_res": round(std_res, 4)
                })

                # Plot Mass Recovery Comparison for paper
                fig, ax = plt.subplots(1, 2, figsize=(8, 3.5))

                ax[0].scatter(y_true, y_pred, alpha=0.6, color='#1f77b4', edgecolors='none', s=20)
                m_max = max(np.max(y_true), np.max(y_pred)) * 1.05
                ax[0].plot([0, m_max], [0, m_max], 'k--', lw=1.2, label='1:1 Line')
                ax[0].set_xlabel(f'Literature Mass ({lit_name}) [$M_\\odot$]')
                ax[0].set_ylabel('SPECTRA Calculated Mass [$M_\\odot$]')
                ax[0].set_title(f'{c_name}: Mass Recovery ($R^2 = {r2:.3f}$)')
                ax[0].legend(loc='upper left')
                ax[0].grid(True, linestyle=':', alpha=0.6)

                ax[1].hist(residuals, bins=25, color='#2ca02c', alpha=0.7, edgecolor='k')
                ax[1].axvline(0, color='k', linestyle='--', lw=1.2)
                ax[1].axvline(offset, color='red', linestyle='-', lw=1.2, label=f'Mean Offset: {offset:.3f}')
                ax[1].set_xlabel('Mass Residuals $\\Delta M$ [$M_\\odot$]')
                ax[1].set_ylabel('Count')
                ax[1].set_title(f'Residual Distribution ($\\sigma = {std_res:.3f}$)')
                ax[1].legend(loc='upper right')
                ax[1].grid(True, linestyle=':', alpha=0.6)

                plt.tight_layout()
                plot_file = os.path.join(FIGURES_DIR, f"fig_mass_recovery_{c_name}_{lit_col}.png")
                plt.savefig(plot_file, dpi=300)
                plt.close()


# ------------------------------------------------------------------------------
# 3. EXPORT SUMMARY TABLES TO DISK (CSV, MD, TEX)
# ------------------------------------------------------------------------------
df_ages = pd.DataFrame(age_summaries)
df_stats = pd.DataFrame(stat_comparison_rows)

print("\n================================================================================")
print("S.P.E.C.T.R.A. - RE-CALCULATED CLUSTER AGES SUMMARY")
print("================================================================================")
print(df_ages.to_string(index=False))

print("\n================================================================================")
print("S.P.E.C.T.R.A. - RE-CALCULATED CROSS-SOURCE MASS COMPARISONS")
print("================================================================================")
print(df_stats.to_string(index=False))

# Export CSVs
df_ages.to_csv(os.path.join(OUTPUT_DIR, "recalculated_cluster_ages_summary.csv"), index=False)
df_stats.to_csv(os.path.join(OUTPUT_DIR, "recalculated_cross_source_stats.csv"), index=False)

# Export LaTeX Tables for MNRAS Paper
tex_ages = [
    "\\begin{table*}",
    "\\centering",
    "\\caption{Recalculated cluster mean ages and standard errors derived with \\textsc{SPECTRA} v1.2.0 across five benchmark open clusters.}",
    "\\label{tab:recalculated_cluster_ages}",
    "\\begin{tabular}{lccccr}",
    "\\hline",
    "Cluster & Nominal Age (Myr) & $N_{\\text{stars}}$ & Siess (2000) Mean Age (Myr) & BHAC15 Mean Age (Myr) & Siess Median Age (Myr) \\\\",
    "\\hline"
]
for _, r in df_ages.iterrows():
    tex_ages.append(f"{r['Cluster']} & {r['Nominal_Age']} & {r['N_stars']} & {r['Siess_Mean_Age']} $\\pm$ {r['Siess_SEM_Age']} & {r['BHAC15_Mean_Age']} $\\pm$ {r['BHAC15_SEM_Age']} & {r['Siess_Med_Age']} \\\\")
tex_ages.extend(["\\hline", "\\end{tabular}", "\\end{table*}"])

with open(os.path.join(OUTPUT_DIR, "recalculated_cluster_ages_summary.tex"), "w", encoding="utf-8") as f:
    f.write("\n".join(tex_ages))

tex_stats = [
    "\\begin{table*}",
    "\\centering",
    "\\caption{Recalculated cross-source mass recovery statistics evaluated with \\textsc{SPECTRA} v1.2.0.}",
    "\\label{tab:recalculated_cross_source_stats}",
    "\\begin{tabular}{llcccccr}",
    "\\hline",
    "Cluster & Comparison & $N$ & $R^2$ & RMSE ($M_\\odot$) & MAE ($M_\\odot$) & Offset ($M_\\odot$) & $\\sigma_{\\text{res}}$ ($M_\\odot$) \\\\",
    "\\hline"
]
for _, r in df_stats.iterrows():
    tex_stats.append(f"{r['Cluster']} & {r['Comparison']} & {r['N']} & {r['R2']} & {r['RMSE']} & {r['MAE']} & {r['Offset']} & {r['Std_res']} \\\\")
tex_stats.extend(["\\hline", "\\end{tabular}", "\\end{table*}"])

with open(os.path.join(OUTPUT_DIR, "recalculated_cross_source_stats.tex"), "w", encoding="utf-8") as f:
    f.write("\n".join(tex_stats))

print(f"\n[OK] Master Recalculation & Re-Analysis Pipeline Completed!")
print(f"     Tables saved in: {OUTPUT_DIR}")
print(f"     Figures saved in: {FIGURES_DIR}")
