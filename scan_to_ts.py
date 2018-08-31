import sys
import numpy as np

"""
Written by T.Young 08/18. It should be called with the filename to scan 
as the first argument i.e. 'python scan_to_ts.py scan_filename.log'
"""

atom_labels = {1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne',
               11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 35: 'Br', 53: 'I'}


def open_log_file(filename):
    """
    :param filename: Name of the .log file to open. It should exist!
    :return: The python file object
    """

    try:
        return open(filename, 'r')

    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
        exit(1)


def get_converged_structures_and_energies(file):
    """
    From a python file object trawl through the reversed file and find the energy and xyz lines
    :param file: The .log file as a python file object
    :return: xyzs in the format [point1, point2, ...] where point1 = [xyzline1, xyzline2, ...] and energies as a list
    """

    rev_lines = reversed(list(file))            # Gaussian output files are terrible. Easier to parse the reversed

    xyz_list, energy_list = [], []
    opt_converged = False
    xyz_section = False
    scan_step = -1

    for line in rev_lines:

        if 'Input orientation:' in line:
            opt_converged = False

        if ' Number     Number       Type             X           Y           Z' in line:
            xyz_section = False

        if opt_converged:
            if xyz_section and '-----------------------' not in line:
                xyz_list[scan_step].append(line.split())
            if ' SCF Done:' in line:
                energy_list.append(line.split()[4])

        if ' Rotational constants (GHZ)' in line:
            xyz_section = True

        if 'Stationary point found' in line:
            scan_step +=1
            xyz_list.append([])
            opt_converged = True

    return xyz_list, energy_list


def get_peak_in_energy_list(energy_list):
    """
    From a list of energies determine if there are any peaks. Script will exit if there are none and pick the
    highest in realtive energy if there is more than one
    :param energy_list: List of energies
    :return: Index corresponding to the peak. If [strucutre1, strucutre2, strucure3, ...] and strucutre2 is the peak
    then 1 is returned. (where the indices of the list are 0, 1, 2, ...)
    """

    energy_array = np.array([float(energy) for energy in energy_list])
    n_points = len(energy_list)
    rel_energies = [(energy - min(energy_array)) for energy in energy_array]

    peak_list = [False for i in range(n_points)]

    for i in range(n_points):

        if i != 0 and i != n_points - 1:
            if rel_energies[i-1] < rel_energies[i] and rel_energies[i+1] < rel_energies[i]:
                peak_list[i] = True

    if sum(peak_list) == 0:
        print('No viable TS (peak in the scan). Unlucky punk')
        exit(1)

    if sum(peak_list) > 1:
        print('There is more than one peak in the scan. Will use the tallest')

        max_rel_energy = 0.0
        index_max_rel_energy = None

        for i in range(n_points):
            if rel_energies[i] > max_rel_energy:
                max_rel_energy = rel_energies[i]
                index_max_rel_energy = i

        if index_max_rel_energy is not None:
            return index_max_rel_energy

    if sum(peak_list) == 1:
        for i in range(n_points):
            if peak_list[i] is True:
                return i


def print_xyz_file_at_peak(xyz_list, peak_idx, filename):
    """
    From the list of xyz lines from the g09 .log file, and the index of the peak output a filename.xyz
    :param xyz_list: List of xyzs
    :param peak_idx: Index of the peak strucure
    :param filename: Filename
    :return: Nothing. The file is written in the function
    """

    peak_xyzs = xyz_list[peak_idx]

    n_atoms = len(peak_xyzs)
    xyz_file = open(filename, 'w')

    print(n_atoms, '\n', file=xyz_file)

    for line in peak_xyzs:
        print(atom_labels[int(line[1])], '\t', line[3], '\t', line[4], '\t', line[5], file=xyz_file)


if __name__ == "__main__":

    log_file_str = sys.argv[1]
    # log_file_str = 'test.log'

    log_file = open_log_file(filename=log_file_str)

    xyzs, energies = get_converged_structures_and_energies(file=log_file)
    peak_index = get_peak_in_energy_list(energies)
    print_xyz_file_at_peak(xyzs, peak_index, filename=log_file_str.replace('.log', '_ts.xyz'))
