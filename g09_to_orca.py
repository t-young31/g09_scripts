"""
From a Gaussian09 output file create a set of ORCA input files.
ORCA keywords specified at the top of this script

------------------------------ Usage ----------------------------

python g09_to_orca.py filename.log

Output: generates filename_sp.inp
_________________________________________________________________

python g09_to_orca.py *.log

Output: generates filename1_sp.inp, filename2_sp.inp, filename3_sp.inp, ..
_________________________________________________________________

python g09_to_orca.py filename.log -e single_point

Output: generates filename_single_point.inp
_________________________________________________________________
"""
import argparse

orca_keywords = ['!', 'DLPNO-CCSD(T)', 'def2-TZVPP', 'def2-TZVPP/C',
                 'RIJCOSX', 'def2/J', 'TIGHTSCF', 'PAL8']


def get_args():
    """Get the command line arguments with argparse"""
    parser = argparse.ArgumentParser()

    parser.add_argument("filenames", action='store', nargs='+',
                        help='G09 .log file(s) convert to ORCA.inp')

    parser.add_argument('-e', '--extension', action='store', default='_sp',
                        help='Additional extension to the')

    return parser.parse_args()


class GaussianOutput:

    def _populate_symbols(self, possible_lines):
        """Get the atomic symbols from the start of a G09 log file"""

        if len(self.symbols) > 0:
            # No need to re-populate atomic symbols
            return

        for line in possible_lines:

            if len(line.split()) == 0:
                # Break on a blank line
                return

            # expecting e,g, "C   -0.0   0.0  0.0"
            if not len(line.split()) == 4:
                continue

            symbol, _, _, _ = line.split()

            # Ensure that the symbol contains no number and at most two letters
            assert all(char.isalpha() for char in symbol) and len(symbol) < 3
            self.symbols.append(symbol)

        if len(self.symbols) == 0:
            raise Exception('Failed to extract atomic symbols')

        return

    def _populate(self, file_name):

        log_lines = open(file_name, 'r').readlines()

        for i, line in enumerate(log_lines):

            if 'Charge' in line and 'Multiplicity' in line:

                # e.g.  "Charge =  0 Multiplicity = 1"
                _, _, self.charge, _, _, self.multiplicity = line.split()

                # Atomic symbols should be on the next line
                self._populate_symbols(possible_lines=log_lines[i+1:])

            if ('Standard orientation' in line
                    or 'Input orientation' in line):

                # In a coordinates block..
                n_atoms = len(self.symbols)

                # Blank the coordinates
                self.coords = []

                xyz_lines = log_lines[i + 5:i + 5 + n_atoms]

                # Set the coordinates
                for xyz_line in xyz_lines:
                    x, y, z = xyz_line.split()[3:]
                    self.coords.append([float(x), float(y), float(z)])

        # Number of coordinates needs to be the same at the number of atomic
        # symbols
        if len(self.coords) != len(self.symbols):
            raise Exception('Coordinates not extracted correctly')

        return

    def __init__(self, file_name):
        """Gaussian 09 ouput"""

        self.charge = None          # int
        self.multiplicity = None    # int
        self.symbols = []           # list(str) e.g. ['H', 'H']
        self.coords = []            # list(list(float))  e.g. [[0.0, 0.0, 0.0]]

        self._populate(file_name)


class ORCAInput:

    def print(self, file_name):
        """Print a ORCA .inp file"""

        xyzs = ''
        for i, symbol in enumerate(self.g09.symbols):
            x, y, z = self.g09.coords[i]
            xyzs += f'{symbol} {x:^10.5f} {y:^10.5f} {z:^10.5f}\n'

        with open(file_name, 'w') as input_file:

            print(f'{" ".join(orca_keywords)}\n'
                  f'*xyz {self.g09.charge} {self.g09.multiplicity}\n'
                  f'{xyzs}'
                  f'*', file=input_file)

        return None

    def __init__(self, g09_output):
        """ORCA Input (v. 4.0 >)"""

        self.g09 = g09_output


if __name__ == '__main__':

    args = get_args()

    for filename in args.filenames:
        # Must be a .log file
        assert filename.endswith('.log')

        orca_input = ORCAInput(g09_output=GaussianOutput(filename))

        input_filename = filename.replace('.log', f'{args.extension}.inp')
        orca_input.print(file_name=input_filename)
