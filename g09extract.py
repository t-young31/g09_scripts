#!/usr/bin/env python3
import argparse


def get_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", action='store', help='.log  file to extract E, H, G from')

    return parser.parse_args()


def print_ehg_lumo_homo(filename):

    e, h, g = 0, 0, 0

    last_scf = None
    last_occ_eigenvalue = None
    first_virt_eigenvalue = None

    log_file_lines = [line for line in open(filename, 'r')]

    for line in log_file_lines:
        if 'SCF Done' in line:
            last_scf = line.split()[4]
        if 'Sum of electronic and thermal Enthalpies' in line:
            h = line.split()[-1]
        if 'Sum of electronic and thermal Free Energies' in line:
            g = line.split()[-1]

    e = last_scf

    for line in reversed(log_file_lines):

        if 'Alpha  occ. eigenvalues' in line and last_occ_eigenvalue is None:
            last_occ_eigenvalue = line.split()[-1]
        if 'Alpha virt. eigenvalues' in line and last_occ_eigenvalue is None:
            first_virt_eigenvalue = line.split()[4]

    e_homo = last_occ_eigenvalue
    e_lumo = first_virt_eigenvalue

    return print('E =', e, '\tH =', h, '\tG =', g, '\tE_HOMO =', e_homo, '\tE_LUMO =', e_lumo, sep='  ')


if __name__ == '__main__':

    args = get_args()
    print_ehg_lumo_homo(args.filename)
