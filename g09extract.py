#!/usr/bin/env python3
import argparse


def get_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", action='store', help='.log  file to extract E, H, G & charges from')

    return parser.parse_args()


def print_ehg_lumo_homo(filename):

    basename = filename.replace('.log', '')

    e, h, g = 0, 0, 0

    last_scf = None
    last_occ_eigenvalue = None
    first_virt_eigenvalue = None

    mul_charges = []
    mul_charges_section = False

    nbo_charges = []
    nbo_charges_section = False

    log_file_lines = [line for line in open(filename, 'r')]

    for n, line in enumerate(log_file_lines):
        if 'SCF Done' in line:
            last_scf = line.split()[4]
        if 'Sum of electronic and thermal Enthalpies' in line:
            h = line.split()[-1]
        if 'Sum of electronic and thermal Free Energies' in line:
            g = line.split()[-1]

        if 'Sum of Mulliken charges' in line and mul_charges_section:
            mul_charges_section = False

        if mul_charges_section and len(line.split()) >= 3:
            mul_charges.append(float(line.split()[2]))

        if 'Mulliken charges and spin densities:' in line or 'Mulliken charges:' in line:
            mul_charges_section = True

        if 'Natural Population' in line and 'Charge' in log_file_lines[n+2] and len(nbo_charges) == 0:
            nbo_charges_section = True

        if nbo_charges_section and ' * Total *' in line:
            nbo_charges_section = False

        if nbo_charges_section and len(line.split()) == 7 and line.split()[-1][-1].isdigit():
            nbo_charges.append(float(line.split()[2]))

    e = last_scf

    for line in reversed(log_file_lines):

        if 'Alpha  occ. eigenvalues' in line and last_occ_eigenvalue is None:
            last_occ_eigenvalue = line.split()[-1]
        if 'Alpha virt. eigenvalues' in line and last_occ_eigenvalue is None:
            first_virt_eigenvalue = line.split()[4]

    e_homo = last_occ_eigenvalue
    e_lumo = first_virt_eigenvalue

    if len(mul_charges) == len(nbo_charges) and len(nbo_charges) > 0:
        print('Printing Mulliken and NBO charges to filename_charges.csv...\n')
        with open(basename + '_charges.csv', 'w') as charges_file:
            print('Mulliken', 'NBO', sep=',', file=charges_file)
            for n_charge in range(len(mul_charges)):
                print(mul_charges[n_charge], nbo_charges[n_charge], sep=',', file=charges_file)

    return print('E =', e, '\tH =', h, '\tG =', g, '\tE_HOMO =', e_homo, '\tE_LUMO =', e_lumo, sep='  ')


if __name__ == '__main__':

    args = get_args()
    print_ehg_lumo_homo(args.filename)
