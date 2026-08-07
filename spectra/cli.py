# S.P.E.C.T.R.A. - Command Line Interface (CLI / Text Mode)
# Copyright (C) 2026  João Paulo Matos Dias Gomes, Maria Jaqueline Vasconcelos, Adriano Hoth Cerqueira
#
# Licensed under GNU General Public License v3.0

import os
import sys
import argparse
import json
import pandas as pd
import numpy as np

from .StarLocalization import intpol, interp
from .tools import (
    interpolmass, RegressionReport, get_available_madys_models,
    get_madys_model_metadata, find_mag_column, generate_spectra_html_report,
    generate_primary_params_html_report, generate_interactive_html_table
)
from .primary_parameters import estimate_photometric_dataset, estimate_spectroscopic_dataset, PrimaryParameterMLEngine
from .paths import OUTPUTS_DIR, ISOCFIT_DIR, RML_DIR, TABLES_DIR, PLOTS_DIR, STATS_DIR


def print_flush(*args, **kwargs):
    """Prints with immediate stdout buffer flushing for real-time terminal output."""
    kwargs.setdefault('flush', True)
    print(*args, **kwargs)


def run_isocfit_cli(args):
    """
    Executes the IsocFit module from the command line.
    """
    input_path = args.input
    model = args.model
    output_dir = args.output_dir if args.output_dir else ISOCFIT_DIR

    print_flush(f"\n[SPECTRA CLI] Executing 2D Isochrone Fitting (IsocFit)")
    print_flush(f"   Input Dataset: {input_path}")
    print_flush(f"   Isochrone Model: {model}")

    if not os.path.exists(input_path):
        print_flush(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)

    df = pd.read_csv(input_path) if input_path.endswith('.csv') else pd.read_excel(input_path)
    teff_col = next((col for col in ['Teff', 'teff', 'T_eff', 'TEFF', 't_eff'] if col in df.columns), None)
    logl_col = next((col for col in ['logL', 'logl', 'log_L', 'LOGL', 'logL/L_sun'] if col in df.columns), None)

    if not teff_col or not logl_col:
        print_flush("[ERROR] Dataset must contain 'Teff' and 'logL' columns.")
        sys.exit(1)

    Tinput = df[teff_col].values
    Linput = df[logl_col].values
    Nobjects = len(Tinput)

    var, Nlines, alldataiso = intpol(model)
    primarydataset = []
    verbose_flag = 1 if getattr(args, 'verbose', False) else 0

    for i in range(Nobjects):
        if np.isfinite(Linput[i]) and np.isfinite(Tinput[i]):
            res = interp(Tinput[i], Linput[i], var, Nlines, alldataiso, verbose_flag)
            primarydataset.append(res)

    df_primary = pd.DataFrame(primarydataset).rename(columns={0: 'Age', 1: 'Mass', 2: 'Teff', 3: 'logL'})
    mass, age, yerr, aerr = interpolmass(df_primary, model)

    res_table = df.copy()
    res_table['Age_calc (Myr)'] = np.round(age, 3)
    res_table['Age_e (Myr)'] = np.round(aerr, 3)
    res_table['Mass_calc'] = np.round(mass, 4)
    res_table['Mass_e'] = np.round(yerr, 4)

    valid_ages = res_table['Age_calc (Myr)'].dropna()
    valid_ages = valid_ages[np.isfinite(valid_ages)]
    mean_age = np.mean(valid_ages) if len(valid_ages) > 0 else np.nan
    std_age = np.std(valid_ages) if len(valid_ages) > 0 else np.nan
    sem_age = std_age / np.sqrt(len(valid_ages)) if len(valid_ages) > 1 else 0.0

    print_flush(f"[RESULTS] Estimated Cluster Mean Age: {mean_age:.2f} +/- {sem_age:.2f} Myr (std = {std_age:.2f} Myr, N = {len(valid_ages)})")

    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    out_csv = os.path.join(output_dir, f"{base_name}_isocfit_results.csv")
    res_table.to_csv(out_csv, index=False)
    print_flush(f"[OK] Results CSV saved: {out_csv}")

    if getattr(args, 'html', False):
        html_file = generate_interactive_html_table(res_table, title=f"IsocFit Results ({model}) - {base_name}", output_dir=output_dir)
        print_flush(f"[OK] Interactive HTML table generated: {html_file}")

    return res_table


def run_rmm_cli(args):
    """
    Executes the Mass-Magnitude Relationship (RMM) module from the command line.
    """
    input_path = args.input
    model = args.model
    filter_name = args.filter
    age_myr = args.age
    mass_min = args.mass_min
    mass_max = args.mass_max
    distance_pc = args.distance
    output_dir = args.output_dir if args.output_dir else RML_DIR

    print_flush(f"\n[SPECTRA CLI] Executing Mass-Magnitude Relationship (RMM)")
    print_flush(f"   Input Dataset: {input_path}")
    print_flush(f"   Model: {model} | Filter: {filter_name} | Age: {age_myr} Myr")
    print_flush(f"   Mass Range: [{mass_min}, {mass_max}] M_sun | Distance: {distance_pc} pc")

    if not os.path.exists(input_path):
        print_flush(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)

    df = pd.read_csv(input_path) if input_path.endswith('.csv') else pd.read_excel(input_path)
    mag_col = find_mag_column(df, filter_name)

    if not mag_col:
        print_flush(f"[ERROR] Could not find magnitude column matching filter '{filter_name}' in dataset.")
        sys.exit(1)

    import madys
    old_stdin = sys.stdin
    devnull_f = open(os.devnull, 'r')
    try:
        sys.stdin = devnull_f
        th_model = madys.IsochroneGrid(
            model, 
            filter_name, 
            mass_range=[mass_min, mass_max],
            age_range=[age_myr, age_myr], 
            n_steps=[250, 250]
        )
    finally:
        sys.stdin = old_stdin
        devnull_f.close()

    if hasattr(th_model.masses, 'ndim') and th_model.masses.ndim == 1 and hasattr(th_model, 'ages') and hasattr(th_model.ages, 'ndim') and th_model.ages.ndim == 1:
        M_mesh, A_mesh = np.meshgrid(th_model.masses, th_model.ages, indexing='ij')
        y_raw = np.log10(np.maximum(1e-10, M_mesh.ravel()))
    else:
        y_raw = np.log10(np.maximum(1e-10, np.array(th_model.masses).ravel()))

    X_raw = th_model.data[:, :, 0].ravel()
    valid_mask = ~np.isnan(X_raw) & ~np.isinf(X_raw) & ~np.isnan(y_raw) & ~np.isinf(y_raw)
    X_full = X_raw[valid_mask]
    y_full = y_raw[valid_mask]

    n = len(X_full)
    max_samples = 2000
    if n > max_samples:
        rng = np.random.default_rng(42)
        idx = rng.choice(n, size=max_samples, replace=False)
        X_train_input = X_full[idx].reshape(-1, 1)
        y_train_input = y_full[idx]
    else:
        X_train_input = X_full.reshape(-1, 1)
        y_train_input = y_full

    model_name, best_model, report_df = RegressionReport(X_train_input, y_train_input)

    DM = 5 * np.log10(distance_pc) - 5
    mabs = df[mag_col].values - DM
    valid_mabs = np.isfinite(mabs)

    log_m_pred = np.full(len(mabs), np.nan)
    if np.any(valid_mabs):
        log_m_pred[valid_mabs] = best_model.predict(mabs[valid_mabs].reshape(-1, 1))

    m_pred = 10**log_m_pred
    res_table = df.copy()
    res_table['Mass_calc'] = np.round(m_pred, 4)

    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    out_csv = os.path.join(output_dir, f"{base_name}_rmm_results.csv")
    res_table.to_csv(out_csv, index=False)
    print_flush(f"[OK] Results CSV saved: {out_csv}")

    if getattr(args, 'html', False):
        html_file = generate_spectra_html_report(
            report_df, model, filter_name, age_myr, (mass_min, mass_max), dataset_df=res_table
        )
        print_flush(f"[OK] Interactive HTML report generated: {html_file}")

    return res_table


def run_primary_cli(args):
    """
    Executes the Primary Stellar Parameters module from the command line.
    """
    input_path = args.input
    av = args.av
    distance_pc = args.distance
    output_dir = args.output_dir if args.output_dir else OUTPUTS_DIR

    print_flush(f"\n[SPECTRA CLI] Executing Primary Stellar Parameters Derivation")
    print_flush(f"   Input Dataset: {input_path}")
    print_flush(f"   Extinction Av: {av} mag | Distance: {distance_pc} pc")

    if not os.path.exists(input_path):
        print_flush(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)

    df = pd.read_csv(input_path) if input_path.endswith('.csv') else pd.read_excel(input_path)

    # Run Photometric derivation
    res_table = estimate_photometric_dataset(df, av=av, distance_pc=distance_pc)

    # Run Spectroscopic derivation if EW columns exist
    res_table = estimate_spectroscopic_dataset(res_table)

    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    out_csv = os.path.join(output_dir, f"{base_name}_primary_params_results.csv")
    res_table.to_csv(out_csv, index=False)
    print_flush(f"[OK] Results CSV saved: {out_csv}")

    if getattr(args, 'html', False):
        html_file = generate_primary_params_html_report(res_table, av_mag=av)
        print_flush(f"[OK] Interactive HTML report generated: {html_file}")

    return res_table


def run_batch_cli(args):
    """
    Executes a batch processing pipeline across multiple cluster datasets.
    """
    print_flush(f"\n[SPECTRA CLI] Executing Batch Multi-Cluster Pipeline")

    jobs = []
    if getattr(args, 'config', None):
        if not os.path.exists(args.config):
            print_flush(f"[ERROR] Config file not found: {args.config}")
            sys.exit(1)
        with open(args.config, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
    elif getattr(args, 'dir', None):
        if not os.path.isdir(args.dir):
            print_flush(f"[ERROR] Directory not found: {args.dir}")
            sys.exit(1)
        for fname in os.listdir(args.dir):
            if fname.endswith(('.csv', '.xlsx')):
                jobs.append({
                    "module": getattr(args, 'module', None) or "isocfit",
                    "input": os.path.join(args.dir, fname),
                    "model": getattr(args, 'model', None) or "Siess 2000"
                })

    if not jobs:
        print_flush("[ERROR] No jobs found to process in batch mode.")
        sys.exit(1)

    print_flush(f"[INFO] Found {len(jobs)} jobs to process.\n")
    for idx, job in enumerate(jobs, 1):
        print_flush(f"--------------------------------------------------------------------------------")
        print_flush(f"[JOB {idx}/{len(jobs)}] Processing: {job.get('input', 'Unknown')}")
        mod = job.get("module", "isocfit").lower()

        # Build dummy args object
        class DummyArgs:
            pass

        d_args = DummyArgs()
        d_args.input = job.get("input")
        d_args.model = job.get("model", "Siess 2000" if mod == "isocfit" else "bhac15")
        d_args.output_dir = job.get("output_dir", None)
        d_args.verbose = job.get("verbose", False)
        d_args.html = job.get("html", True)
        d_args.filter = job.get("filter", "G")
        d_args.age = float(job.get("age", 100.0))
        d_args.mass_min = float(job.get("mass_min", 0.1))
        d_args.mass_max = float(job.get("mass_max", 1.5))
        d_args.distance = float(job.get("distance", 100.0))
        d_args.av = float(job.get("av", 0.0))

        try:
            if mod == "isocfit":
                run_isocfit_cli(d_args)
            elif mod in ["rmm", "mass-modeling"]:
                run_rmm_cli(d_args)
            elif mod in ["primary", "primary-params"]:
                run_primary_cli(d_args)
            print_flush(f"[OK] Job {idx}/{len(jobs)} completed successfully!")
        except Exception as e:
            print_flush(f"[ERROR] Job {idx} failed: {e}")

    print_flush("\n[COMPLETE] Batch processing pipeline finished!")


def main_cli():
    parser = argparse.ArgumentParser(
        description="S.P.E.C.T.R.A. - Stellar Parameter Estimation and Calculation Tools for Research and Analysis (CLI Text Mode)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Processing Module / Mode")

    # 1. IsocFit Subcommand
    p_iso = subparsers.add_parser("isocfit", help="2D Isochrone Fitting & Stellar Age/Mass Recovery")
    p_iso.add_argument("--input", "-i", required=True, help="Path to input dataset (CSV/Excel) with Teff and logL")
    p_iso.add_argument("--model", "-m", default="Siess 2000", help="Isochrone model: 'Siess 2000' or 'BHAC15'")
    p_iso.add_argument("--output-dir", "-o", help="Output directory")
    p_iso.add_argument("--verbose", "-v", action="store_true", help="Enable verbose interpolation trace")
    p_iso.add_argument("--html", action="store_true", help="Generate interactive HTML report")

    # 2. RMM Subcommand
    p_rmm = subparsers.add_parser("rmm", help="Machine Learning Mass-Magnitude Relationship (RMM)")
    p_rmm.add_argument("--input", "-i", required=True, help="Path to input dataset (CSV/Excel)")
    p_rmm.add_argument("--model", "-m", default="bhac15", help="MADYS Isochrone model grid (e.g. bhac15, parsec, mist)")
    p_rmm.add_argument("--filter", "-f", default="G", help="Photometric filter band (e.g. G, V, J, K)")
    p_rmm.add_argument("--age", "-a", type=float, default=100.0, help="Cluster age in Myr")
    p_rmm.add_argument("--mass-min", type=float, default=0.1, help="Min mass bound (M_sun)")
    p_rmm.add_argument("--mass-max", type=float, default=1.5, help="Max mass bound (M_sun)")
    p_rmm.add_argument("--distance", "-d", type=float, default=125.0, help="Cluster distance in pc")
    p_rmm.add_argument("--output-dir", "-o", help="Output directory")
    p_rmm.add_argument("--html", action="store_true", help="Generate interactive HTML report")

    # 3. Primary Parameters Subcommand
    p_prim = subparsers.add_parser("primary", help="Primary Stellar Parameters Derivation & Accretion Classification")
    p_prim.add_argument("--input", "-i", required=True, help="Path to input dataset (CSV/Excel)")
    p_prim.add_argument("--av", type=float, default=0.0, help="Interstellar extinction Av in mag")
    p_prim.add_argument("--distance", "-d", type=float, default=100.0, help="Distance in pc")
    p_prim.add_argument("--output-dir", "-o", help="Output directory")
    p_prim.add_argument("--html", action="store_true", help="Generate interactive HTML report")

    # 4. Batch Pipeline Subcommand
    p_batch = subparsers.add_parser("batch", help="Automated Batch Multi-Cluster Pipeline")
    p_batch.add_argument("--config", "-c", help="Path to JSON/YAML batch job config file")
    p_batch.add_argument("--dir", help="Directory containing multiple CSV files to process")
    p_batch.add_argument("--module", help="Module for directory batch mode (isocfit, rmm, primary)")
    p_batch.add_argument("--model", help="Model for directory batch mode")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.subcommand == "isocfit":
        run_isocfit_cli(args)
    elif args.subcommand == "rmm":
        run_rmm_cli(args)
    elif args.subcommand == "primary":
        run_primary_cli(args)
    elif args.subcommand == "batch":
        run_batch_cli(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main_cli()
