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

import sys
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module=".*madys.*")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command-Line Text Mode (Headless / Batch Pipeline)
        from spectra.cli import main_cli
        main_cli()
    else:
        # Graphical User Interface (GUI) Mode
        from spectra.interface import App
        app = App()
        app.mainloop()