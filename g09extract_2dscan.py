#!/usr/bin/env python3
import argparse


def get_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", action='store', help='.log  file to extract E, H, G from')

    return parser.parse_args()


def extract_rs_Es(filename):

    log_file_lines = [line for line in open(filename, 'r')]

    input_geom_block = False
    coord_label1, coord_label2 = None, None
    coord1, coord2 = 0, 0

    for line in log_file_lines:

        if 'Initial Parameters':
            input_geom_block = True
        if 'Scan' in line and input_geom_block and coord_label1 is not None and coord_label2 is None:
            coord_label2 = line.split()[1]
            break
        if 'Scan' in line and input_geom_block and coord_label1 is None:
            coord_label1 = line.split()[1]

    opt_param_block, opt_done = False, False
    energy = 0

    for line in log_file_lines:

        if 'Optimized Parameters ' in line:
            opt_param_block = True

        if 'GradGradGradGradGradGradGradGradGradGradGradGradGradGradGradGradGradGrad' in line and opt_param_block:
            opt_param_block = False

        if coord_label1 in line and opt_param_block:
            coord1 = line.split()[3]
        if coord_label2 in line and opt_param_block:
            coord2 = line.split()[3]

        if 'SCF Done' in line:
            energy = line.split()[4]

        if 'Stationary point found' in line:
            opt_done = True

        if 'Input orientation' in line and opt_done:
            print(coord1, coord2, energy)
            opt_done = False

    return 0


if __name__ == '__main__':

    args = get_args()
    extract_rs_Es(args.filename)
