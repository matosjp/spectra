import os
import shutil
from setuptools import setup
from distutils.core import Extension
import sys
import subprocess
import glob
import platform

WIN32 = platform.system() == 'Windows'

long_description = ('It provides astronomers and astrophysicists with a suite of powerful algorithms for determining '
                    'various parameters related to stars, including stellar type, luminosity, temperature, radius, '
                    'mass, age, and distance. This program is intended for research and educational purposes, '
                    'offering a user-friendly interface and accurate analytical capabilities for studying the '
                    'properties and behaviors of stars across the cosmos.')

install_requires = [
    'statsmodels',
    'mfouesneau/tap',
    'scipy',
    'scikit-learn',
    'matplotlib',
    'ttkbootstrap',
    'numpy',
    'pandas',
    'madys',
    'pillow',
    'tabulate']

setup(name='stelar',
      version='1.0.dev0',
      description="S.T.E.L.A.R. (Stellar Type Examination and Analysis Resource) "
                  "\nis a software tool designed for the comprehensive analysis of stellar "
                  "data.",
      author='João Paulo Matos Dias Gomes',
      author_email='jpmdgomes.bf@gmail.com',
      license='',
      long_description=long_description,
      url='https://github.com/Gomes-JP/stelar',
      package_dir={'stelar/': ''},
      packages=['stelar',
                'stelar/external'],
      package_data={'mwdust/util': ['extCurves/extinction.tbl',
                                    'extCurves/apj398709t6_ascii.txt']},
      install_requires=install_requires,
      classifiers=[
          "Development Status :: 1 - Initial",
          "Intended Audience :: Science/Research",
          "License :: ",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3",
          "Topic :: Scientific :: Astrophysics",
          "Topic :: Scientific :: Statistics"]
      )
