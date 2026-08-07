import os
import sys
import numpy as np
import pandas as pd

# Define Paths
BASE_DIR = r"c:\Users\João & Jéssica\git\spectra"
TCC_DATA_DIR = os.path.join(BASE_DIR, "articles", "tcc", "Resultados", "tabelas_dezembro_2024")
OUTPUT_ANALYSIS_DIR = os.path.join(BASE_DIR, "publishing", "analysis_outputs")
FIGURES_DIR = os.path.join(BASE_DIR, "publishing", "mnras_paper", "figures")

os.makedirs(OUTPUT_ANALYSIS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

print("================================================================================")
print("S.P.E.C.T.R.A. - CLUSTER MASTER REFERENCE TABLE & COMPARATIVE ANALYSIS")
print("================================================================================")

# ------------------------------------------------------------------------------
# 1. CLUSTER MASTER REFERENCE TABLE DATAFRAME
# ------------------------------------------------------------------------------
master_cluster_data = [
    {
        "Cluster": "Orion Nebula Cluster (ONC)",
        "Alias": "NGC 1976 / M42",
        "RA_J2000": "05h 35m 16s",
        "Dec_J2000": "-05° 23′ 23″",
        "Distance_pc": 414,
        "Distance_err": 20,
        "DM_mag": 8.08,
        "Av_min_mag": 0.5,
        "Av_max_mag": 3.0,
        "Av_median_mag": 1.50,
        "Nominal_Age_Myr": "1 - 2",
        "Mass_Range_Msun": "0.05 - 2.0",
        "Primary_Catalogs": "Hillenbrand (1997), Davies et al. (2014)",
        "Secondary_Catalogs": "TESS V8.2 (Stassun et al. 2019)",
        "Best_Spectra_Model": "KNN BHAC15 (V-band)"
    },
    {
        "Cluster": "Upper Scorpius",
        "Alias": "USco OB Association",
        "RA_J2000": "16h 00m 00s",
        "Dec_J2000": "-24° 00′ 00″",
        "Distance_pc": 140,
        "Distance_err": 10,
        "DM_mag": 5.73,
        "Av_min_mag": 0.3,
        "Av_max_mag": 1.2,
        "Av_median_mag": 0.70,
        "Nominal_Age_Myr": "5 - 11",
        "Mass_Range_Msun": "0.01 - 1.5",
        "Primary_Catalogs": "Stauffer et al. (2019)",
        "Secondary_Catalogs": "TESS V8.2 (Stassun et al. 2019)",
        "Best_Spectra_Model": "KNN BHAC15 (Gaia G-band)"
    },
    {
        "Cluster": "h Persei",
        "Alias": "NGC 869",
        "RA_J2000": "02h 19m 05s",
        "Dec_J2000": "+57° 09′ 02″",
        "Distance_pc": 2300,
        "Distance_err": 100,
        "DM_mag": 11.81,
        "Av_min_mag": 1.50,
        "Av_max_mag": 1.80,
        "Av_median_mag": 1.65,
        "Nominal_Age_Myr": "13 ± 1",
        "Mass_Range_Msun": "0.20 - 2.5",
        "Primary_Catalogs": "Moraux et al. (2013)",
        "Secondary_Catalogs": "TESS V8.2 (Stassun et al. 2019)",
        "Best_Spectra_Model": "KNN BHAC15 (V-band)"
    },
    {
        "Cluster": "Pleiades",
        "Alias": "M45 / Seven Sisters",
        "RA_J2000": "03h 47m 24s",
        "Dec_J2000": "+24° 07′ 00″",
        "Distance_pc": 136.2,
        "Distance_err": 1.2,
        "DM_mag": 5.67,
        "Av_min_mag": 0.01,
        "Av_max_mag": 0.05,
        "Av_median_mag": 0.03,
        "Nominal_Age_Myr": "112 ± 5",
        "Mass_Range_Msun": "0.05 - 2.0",
        "Primary_Catalogs": "Lodieu et al. (2019), Delfosse et al. (2000)",
        "Secondary_Catalogs": "TESS V8.2 (Stassun et al. 2019)",
        "Best_Spectra_Model": "KNN BHAC15 (Gaia G-band)"
    },
    {
        "Cluster": "NGC 2516",
        "Alias": "Southern Pleiades / C0757-607",
        "RA_J2000": "07h 58m 04s",
        "Dec_J2000": "-60° 45′ 12″",
        "Distance_pc": 412,
        "Distance_err": 15,
        "DM_mag": 8.07,
        "Av_min_mag": 0.25,
        "Av_max_mag": 0.40,
        "Av_median_mag": 0.33,
        "Nominal_Age_Myr": "150 ± 10",
        "Mass_Range_Msun": "0.15 - 1.8",
        "Primary_Catalogs": "Jackson et al. (2012)",
        "Secondary_Catalogs": "TESS V8.2 (Stassun et al. 2019)",
        "Best_Spectra_Model": "KNN BHAC15 (V-band)"
    }
]

df_master = pd.DataFrame(master_cluster_data)

# Export Master Table
master_csv = os.path.join(OUTPUT_ANALYSIS_DIR, "cluster_master_reference_table.csv")
master_md = os.path.join(OUTPUT_ANALYSIS_DIR, "cluster_master_reference_table.md")
master_tex = os.path.join(OUTPUT_ANALYSIS_DIR, "cluster_master_reference_table.tex")

df_master.to_csv(master_csv, index=False)
with open(master_md, "w", encoding="utf-8") as f:
    f.write("# S.P.E.C.T.R.A. - Master Cluster Reference Table\n\n")
    f.write(df_master.to_markdown(index=False))

tex_lines = [
    "\\begin{table*}",
    "\\centering",
    "\\caption{Master physical parameters adopted for the five benchmark open clusters analyzed with \\textsc{SPECTRA}.}",
    "\\label{tab:master_cluster_parameters}",
    "\\begin{tabular}{lccccccr}",
    "\\hline",
    "Cluster & Distance (pc) & DM (mag) & $A_V$ (mag) & Nominal Age (Myr) & Mass Range ($M_\\odot$) & Best SPECTRA Model \\\\",
    "\\hline"
]
for _, row in df_master.iterrows():
    tex_lines.append(f"{row['Cluster']} & {row['Distance_pc']} $\\pm$ {row['Distance_err']} & {row['DM_mag']} & {row['Av_median_mag']} & {row['Nominal_Age_Myr']} & {row['Mass_Range_Msun']} & {row['Best_Spectra_Model']} \\\\")
tex_lines.extend(["\\hline", "\\end{tabular}", "\\end{table*}"])

with open(master_tex, "w", encoding="utf-8") as f:
    f.write("\n".join(tex_lines))

print(f"[OK] Saved Master Reference Table to CSV, MD, TEX in: {OUTPUT_ANALYSIS_DIR}")


# ------------------------------------------------------------------------------
# 2. CROSS-SOURCE STATISTICAL EVALUATION FUNCTION
# ------------------------------------------------------------------------------
def compute_stats(y_true, y_pred):
    valid_mask = np.isfinite(y_true) & np.isfinite(y_pred) & (y_true > 0) & (y_pred > 0)
    yt = np.array(y_true)[valid_mask]
    yp = np.array(y_pred)[valid_mask]
    N = len(yt)
    if N == 0:
        return {"N": 0, "R2": np.nan, "RMSE": np.nan, "MAE": np.nan, "Offset": np.nan, "Std_res": np.nan}

    residuals = yp - yt
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((yt - np.mean(yt))**2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 1.0
    rmse = np.sqrt(np.mean(residuals**2))
    mae = np.mean(np.abs(residuals))
    offset = np.mean(residuals)
    std_res = np.std(residuals)

    return {
        "N": N,
        "R2": round(r2, 4),
        "RMSE": round(rmse, 4),
        "MAE": round(mae, 4),
        "Offset": round(offset, 4),
        "Std_res": round(std_res, 4)
    }


# ------------------------------------------------------------------------------
# 3. ANALYSIS ACROSS CLUSTERS WITH MULTIPLE SOURCES
# ------------------------------------------------------------------------------
comparison_results = []

# --- A. Orion Nebula Cluster (ONC) ---
onc_file = os.path.join(TCC_DATA_DIR, "onc", "onc_results_merged_table.csv")
if os.path.exists(onc_file):
    df_onc = pd.read_csv(onc_file)
    if 'H97_Mass' in df_onc.columns and 'D14_Mass_calc' in df_onc.columns:
        s1 = compute_stats(df_onc['H97_Mass'], df_onc['D14_Mass_calc'])
        comparison_results.append({
            "Cluster": "ONC",
            "Comparison": "SPECTRA RMM (KNN BHAC15) vs Hillenbrand (1997)",
            **s1
        })
    if 'D14_Mass' in df_onc.columns and 'D14_Mass_calc' in df_onc.columns:
        s2 = compute_stats(df_onc['D14_Mass'], df_onc['D14_Mass_calc'])
        comparison_results.append({
            "Cluster": "ONC",
            "Comparison": "SPECTRA RMM (KNN BHAC15) vs Davies et al. (2014)",
            **s2
        })

# --- B. Upper Scorpius ---
usco_file = os.path.join(TCC_DATA_DIR, "upperScorpius", "usco_results_merged_table.csv")
if os.path.exists(usco_file):
    df_usco = pd.read_csv(usco_file)
    if 'Tess_Mass' in df_usco.columns and 'rml_Mass_calc' in df_usco.columns:
        s1 = compute_stats(df_usco['Tess_Mass'], df_usco['rml_Mass_calc'])
        comparison_results.append({
            "Cluster": "Upper Scorpius",
            "Comparison": "SPECTRA RMM (KNN BHAC15 G) vs TESS V8.2",
            **s1
        })
    if 'Tess_Mass' in df_usco.columns and 'iso_Mass_calc' in df_usco.columns:
        s2 = compute_stats(df_usco['Tess_Mass'], df_usco['iso_Mass_calc'])
        comparison_results.append({
            "Cluster": "Upper Scorpius",
            "Comparison": "SPECTRA IsocFit vs TESS V8.2",
            **s2
        })

usco_s18_file = os.path.join(TCC_DATA_DIR, "upperScorpius", "usco_results_merged_table_s18.csv")
if os.path.exists(usco_s18_file):
    df_usco_s18 = pd.read_csv(usco_s18_file)
    if 'S18_Mass' in df_usco_s18.columns and 'rml_Mass_calc' in df_usco_s18.columns:
        s3 = compute_stats(df_usco_s18['S18_Mass'], df_usco_s18['rml_Mass_calc'])
        comparison_results.append({
            "Cluster": "Upper Scorpius",
            "Comparison": "SPECTRA RMM (KNN BHAC15 G) vs Stauffer et al. (2019)",
            **s3
        })

# --- C. h Persei ---
hper_file = os.path.join(TCC_DATA_DIR, "hPersei", "hper_results_merged_table.csv")
if os.path.exists(hper_file):
    df_hper = pd.read_csv(hper_file)
    if 'M13_Mass' in df_hper.columns and 'M13_Mass_calc' in df_hper.columns:
        s1 = compute_stats(df_hper['M13_Mass'], df_hper['M13_Mass_calc'])
        comparison_results.append({
            "Cluster": "h Persei",
            "Comparison": "SPECTRA RMM (KNN BHAC15 V) vs Moraux et al. (2013)",
            **s1
        })
    if 'Tess_Mass' in df_hper.columns and 'Tess_Mass_calc' in df_hper.columns:
        s2 = compute_stats(df_hper['Tess_Mass'], df_hper['Tess_Mass_calc'])
        comparison_results.append({
            "Cluster": "h Persei",
            "Comparison": "SPECTRA IsocFit vs TESS V8.2",
            **s2
        })

# --- D. Pleiades ---
ple_file = os.path.join(TCC_DATA_DIR, "pleiades", "pleiades_results_merged_table.csv")
if os.path.exists(ple_file):
    df_ple = pd.read_csv(ple_file)
    if 'Lod19_Mass' in df_ple.columns and 'Lod19_Mass_calc' in df_ple.columns:
        s1 = compute_stats(df_ple['Lod19_Mass'], df_ple['Lod19_Mass_calc'])
        comparison_results.append({
            "Cluster": "Pleiades",
            "Comparison": "SPECTRA RMM (KNN BHAC15 G) vs Lodieu et al. (2019)",
            **s1
        })
    if 'Del00_Mass' in df_ple.columns and 'Lod19_Mass_calc' in df_ple.columns:
        s2 = compute_stats(df_ple['Del00_Mass'], df_ple['Lod19_Mass_calc'])
        comparison_results.append({
            "Cluster": "Pleiades",
            "Comparison": "SPECTRA RMM (KNN BHAC15 G) vs Delfosse et al. (2000)",
            **s2
        })
    if 'TESS_Mass' in df_ple.columns and 'TESS_Mass_calc' in df_ple.columns:
        s3 = compute_stats(df_ple['TESS_Mass'], df_ple['TESS_Mass_calc'])
        comparison_results.append({
            "Cluster": "Pleiades",
            "Comparison": "SPECTRA IsocFit vs TESS V8.2",
            **s3
        })

# --- E. NGC 2516 ---
ngc_file = os.path.join(TCC_DATA_DIR, "ngc2516", "ngc2516_final_result_table_merged_table.csv")
if os.path.exists(ngc_file):
    df_ngc = pd.read_csv(ngc_file)
    if 'J12_Mass' in df_ngc.columns and 'J12_Mass_calc' in df_ngc.columns:
        s1 = compute_stats(df_ngc['J12_Mass'], df_ngc['J12_Mass_calc'])
        comparison_results.append({
            "Cluster": "NGC 2516",
            "Comparison": "SPECTRA RMM (KNN BHAC15 V) vs Jackson et al. (2012)",
            **s1
        })
    if 'Tess_Mass' in df_ngc.columns and 'Gaia_Mass_calc' in df_ngc.columns:
        s2 = compute_stats(df_ngc['Tess_Mass'], df_ngc['Gaia_Mass_calc'])
        comparison_results.append({
            "Cluster": "NGC 2516",
            "Comparison": "SPECTRA IsocFit vs TESS V8.2",
            **s2
        })

df_comp = pd.DataFrame(comparison_results)
comp_csv = os.path.join(OUTPUT_ANALYSIS_DIR, "cluster_cross_source_comparison_stats.csv")
comp_md = os.path.join(OUTPUT_ANALYSIS_DIR, "cluster_cross_source_comparison_stats.md")
comp_tex = os.path.join(OUTPUT_ANALYSIS_DIR, "cluster_cross_source_comparison_stats.tex")

df_comp.to_csv(comp_csv, index=False)
with open(comp_md, "w", encoding="utf-8") as f:
    f.write("# S.P.E.C.T.R.A. - Cross-Source Comparative Mass Statistics\n\n")
    f.write(df_comp.to_markdown(index=False))

comp_tex_lines = [
    "\\begin{table*}",
    "\\centering",
    "\\caption{Cross-source mass recovery statistics across open clusters benchmarked with \\textsc{SPECTRA}.}",
    "\\label{tab:cross_source_comparison}",
    "\\begin{tabular}{llcccccr}",
    "\\hline",
    "Cluster & Comparison & $N$ & $R^2$ & RMSE ($M_\\odot$) & MAE ($M_\\odot$) & Offset ($M_\\odot$) & $\\sigma_{\\text{res}}$ ($M_\\odot$) \\\\",
    "\\hline"
]
for _, row in df_comp.iterrows():
    comp_tex_lines.append(f"{row['Cluster']} & {row['Comparison']} & {row['N']} & {row['R2']} & {row['RMSE']} & {row['MAE']} & {row['Offset']} & {row['Std_res']} \\\\")
comp_tex_lines.extend(["\\hline", "\\end{tabular}", "\\end{table*}"])

with open(comp_tex, "w", encoding="utf-8") as f:
    f.write("\n".join(comp_tex_lines))

print("[OK] Cross-Source Comparative Analysis Completed!")
print(df_comp.to_string(index=False))
