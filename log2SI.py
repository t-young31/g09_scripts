#!/usr/bin/env python3
import numpy as np
import argparse


def get_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", action='store', help='.log file(s) extract xyzs and E, H, G from', nargs='+')
    parser.add_argument("-o", action='store', default='output.txt', help='Name of the output file')

    return parser.parse_args()


def print_output(output_filename, mol_obj):

    with open(output_filename, 'a') as output_file:
        print(mol_obj.filename, file=output_file)
        print('E = ', np.round(mol_obj.e, 6), file=output_file)
        if mol_obj.freq:
            print('H = ', np.round(mol_obj.h, 6), file=output_file)
            print('G = ', np.round(mol_obj.g, 6), '\n', file=output_file)
        for xyz_line in mol_obj.xyzs:
            print('{:<5s}{:10.5f}{:10.5f}{:10.5f}'.format(*xyz_line),file=output_file)
        print('\n', file=output_file)

    return 0


class Molecule(object):

    def __init__(self, filename):

        self.filename = filename
        self.calc_type = None
        self.freq = False
        self.opt_done = False
        self.atom_labels = []
        self.xyzs = []
        self.e, self.h, self.g = 0, 0, 0

        first_xyzs, check_geom, opt_xyzs = False, False, False
        n_atom = 0

        with open(self.filename, 'r') as log_file:
            for line in log_file:

                if line.startswith(' #') and self.calc_type is None:
                    if 'opt' in line or 'Opt' in line:
                        self.calc_type = 'opt'
                    else:
                        self.calc_type = 'sp'
                    if 'freq' in line or 'Freq' in line:
                        self.freq = True

                if 'Charge' in line and 'Multiplicity' in line and len(self.atom_labels) == 0:
                    first_xyzs = True

                if 'Redundant internal coordinates found in file' in line and len(self.atom_labels) == 0:
                    check_geom = True

                if len(line.split()) == 0 or len(line.split(',')) == 0:
                    first_xyzs = False

                if first_xyzs:

                    if len(line.split()) == 4:
                        self.atom_labels.append(line.split()[0])

                    if self.calc_type == 'sp' and len(line.split()) == 4:
                        xyz_line = line.split()
                        self.atom_labels.append(xyz_line[0])
                        self.xyzs.append([xyz_line[0], float(xyz_line[1]), float(xyz_line[2]), float(xyz_line[3])])

                    if check_geom and len(line.split(',')) == 5:
                        xyz_line = line.split(',')
                        self.atom_labels.append(xyz_line[0])
                        self.xyzs.append([xyz_line[0], float(xyz_line[2]), float(xyz_line[3]), float(xyz_line[4])])

                if 'Stationary point found' in line:
                    self.opt_done = True

                if 'Standard orientation' in line and self.opt_done:
                    opt_xyzs = True

                if 'Distance matrix' in line:
                    opt_xyzs = False

                if len(line.split()) > 0:
                    if opt_xyzs and line.split()[0].isdigit():
                        if n_atom < len(self.atom_labels):
                            n_atom += 1
                            coord_line = line.split()[3:]
                            self.xyzs.append([self.atom_labels[n_atom-1],
                                              float(coord_line[0]),
                                              float(coord_line[1]),
                                              float(coord_line[2])]
                                             )

                if 'SCF Done:' in line:
                    self.e = float(line.split()[4])

                if 'Sum of electronic and thermal Enthalpies=' in line:
                    self.h = float(line.split()[-1])

                if 'Sum of electronic and thermal Free Energies=' in line:
                    self.g = float(line.split()[-1])


if __name__ == '__main__':

    args = get_args()

    for log_filename in args.filenames:
        mol = Molecule(log_filename)
        print_output(args.o, mol_obj=mol)
