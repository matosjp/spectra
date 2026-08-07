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


def main_entry():
    """
    Main entry point for executable command 'spectra'.
    Behavior:
    - Calling `spectra` (or `spectra -g`) opens the Graphical User Interface (GUI).
    - Calling `spectra -e` (or `spectra --cli`) launches the interactive CLI shell.
    - Calling `spectra isocfit ...` runs direct headless CLI subcommands.
    """
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ["-g", "--gui"]):
        # Launch Graphical User Interface (GUI) Mode
        from spectra.interface import App
        app = App()
        app.mainloop()
    elif len(sys.argv) == 2 and sys.argv[1] in ["-e", "--cli"]:
        # Launch Interactive Command Shell (REPL Mode)
        from spectra.cli import interactive_cli_shell
        interactive_cli_shell()
    else:
        # Strip leading -e / --cli if user typed e.g. spectra -e isocfit ...
        if sys.argv[1] in ["-e", "--cli"]:
            sys.argv.pop(1)
        from spectra.cli import main_cli
        main_cli()


if __name__ == "__main__":
    main_entry()