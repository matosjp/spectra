# S.P.E.C.T.R.A. - Stellar Parameter Estimation and Calculation Tools for Research and Analysis
# Copyright (C) 2026  João Paulo Matos Dias Gomes, Maria Jaqueline Vasconcelos, Adriano Hoth Cerqueira
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact:
#   João Paulo Matos Dias Gomes — jpmdgomes.bf@gmail.com
#   Maria Jaqueline Vasconcelos — mjvasc@uesc.br
#   Adriano Hoth Cerqueira — hoth@uesc.br
#   Universidade Estadual de Santa Cruz (UESC), Ilhéus - BA, Brasil

from setuptools import setup

with open('README.md', 'r') as fp:
    long_description = fp.read()

setup(
    name='S.P.E.C.T.R.A.',
    version='1.0',
    description='Tools for derive stellar parameters, focused on stellar mass.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    keywords=['stellar parameters: mass', 'isochrone fitting', 'machine learning', 'robust statistics'],
    author='João Paulo Matos Dias Gomes',
    author_email='jpmdgomes.bf@gmail.com',
    packages=['spectra'],
    install_requires=[
        'ttkbootstrap',
        'Pillow',
        'numpy',
        'pandas',
        'scipy',
        'scikit-learn',
        'statsmodels',
        'matplotlib',
        'seaborn',
        'missingno',
        'madys',
        'gdown',
    ],
    classifiers=[
        'Development Status :: 1 - Beta',
        'Topic :: Astronomy/Astrophysics',
        'License :: [WHEN I GOT]',
        'Programming Language :: Python :: 3'
    ]
)