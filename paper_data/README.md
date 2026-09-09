# SPECTRA Paper Data & Catalogs

This directory contains the supplementary data, input catalogs, and output results corresponding to the paper:
**Stellar Parameter Determination in Open Clusters: A Comparative Benchmark of 2D Bayesian Isochrone Fitting, Machine Learning Regressors, and Empirical Calibrations**.

To ensure these files are not confused with the underlying source code of the `SPECTRA` software, they have been explicitly organized here.

## Directory Structure

* **`derived_catalogs/`**: Contains the final output CSVs of the parameter determinations (masses, ages, etc.) for each of the five benchmark clusters ($h$ Persei, NGC 2516, Orion Nebula Cluster, Pleiades, and Upper Scorpius). It also includes the cross-source comparison statistical tables.
* **`observational_datasets/`**: Contains the sample inputs and test datasets used for validation and empirical control runs (including the eclipsing binary dataset).

## Theoretical Model Grids
The theoretical isochrone model grids (Baraffe/BHAC15, PARSEC, and SIESS) underlying the isochrone fitting methodologies are tightly coupled to the software's execution paths. Therefore, they remain located at the root directory in the `isochrone_models/` folder.
