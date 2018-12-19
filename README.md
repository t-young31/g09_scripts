# Scripts for parsing Gaussian09 output

## scan_to_ts.py

Script to parse a scan output file and generate a ts guess .xyz file

Using the script:

Run with `python scan_to_ts.py file.log`, where `file.log` is a
gaussian output file.

## log2SI.py

Script to parse .log files and extract E, H, G along with the coordinates

Using the script:

Run with `python log2SI.py file.log`, where `file.log` is a
gaussian output file. To run with multiple files `python log2SI.py *.log`
which will generate an output.txt (name modified with the -o flag).