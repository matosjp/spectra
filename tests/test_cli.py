import os
import sys
import unittest
import shutil
import pandas as pd
import numpy as np

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from spectra.cli import run_isocfit_cli, run_rmm_cli, run_primary_cli, run_batch_cli
from spectra.paths import OUTPUTS_DIR, ISOCFIT_DIR, RML_DIR


class TestSpectraCLIArchitecture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "scratch_cli_test"))
        os.makedirs(cls.test_dir, exist_ok=True)
        cls.dataset_csv = os.path.join(cls.test_dir, "test_cluster_stars.csv")

        # Generate test dataset
        df = pd.DataFrame({
            "Star": [f"Star_{i}" for i in range(1, 10)],
            "Teff": [4200, 3900, 3500, 4500, 4100, 3800, 4400, 3600, 4000],
            "logL": [-0.2, -0.6, -1.1, 0.1, -0.4, -0.8, 0.0, -1.0, -0.5],
            "Gmag": [11.8, 13.1, 14.5, 10.9, 12.4, 13.7, 11.2, 14.1, 12.8],
            "Vmag": [12.2, 13.6, 15.0, 11.3, 12.9, 14.2, 11.6, 14.6, 13.3],
            "Jmag": [10.5, 11.8, 13.0, 9.8, 11.1, 12.4, 10.1, 12.7, 11.4]
        })
        df.to_csv(cls.dataset_csv, index=False)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir, ignore_errors=True)

    def test_01_isocfit_cli_siess(self):
        class Args:
            input = self.dataset_csv
            model = "Siess 2000"
            output_dir = self.test_dir
            verbose = False
            html = True

        res = run_isocfit_cli(Args())
        self.assertIn("Age_calc (Myr)", res.columns)
        self.assertIn("Mass_calc", res.columns)
        self.assertTrue((res["Mass_calc"] > 0).any())

        out_csv = os.path.join(self.test_dir, "test_cluster_stars_isocfit_results.csv")
        self.assertTrue(os.path.exists(out_csv))

    def test_02_isocfit_cli_bhac15(self):
        class Args:
            input = self.dataset_csv
            model = "BHAC15"
            output_dir = self.test_dir
            verbose = False
            html = True

        res = run_isocfit_cli(Args())
        self.assertIn("Age_calc (Myr)", res.columns)
        self.assertIn("Mass_calc", res.columns)

    def test_03_rmm_cli_bhac15_gband(self):
        class Args:
            input = self.dataset_csv
            model = "bhac15"
            filter = "G"
            age = 100.0
            mass_min = 0.1
            mass_max = 1.5
            distance = 136.2
            output_dir = self.test_dir
            html = True

        res = run_rmm_cli(Args())
        self.assertIn("Mass_calc", res.columns)
        self.assertTrue((res["Mass_calc"] > 0).any())

    def test_04_primary_cli(self):
        class Args:
            input = self.dataset_csv
            av = 0.3
            distance = 140.0
            output_dir = self.test_dir
            html = True

        res = run_primary_cli(Args())
        self.assertIn("Teff", res.columns)

    def test_05_batch_cli_directory_mode(self):
        class Args:
            config = None
            dir = self.test_dir
            module = "isocfit"
            model = "Siess 2000"

        # Run batch pipeline across test_dir
        run_batch_cli(Args())


if __name__ == "__main__":
    unittest.main()
