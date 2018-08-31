# Scripts for parsing Gaussian09 output

scan_to_ts.py

Script to parse a scan output file and generate a ts guess .xyz file

Using the script:

Run with `python scan_to_ts.py file.log`, where `file.log` is the
gaussian output file.


## Making the script an executable

`mkdir $HOME/scripts`  
`cd $HOME/scripts`
`vi scan_to_ts`  
Paste the python code into the file and save (`:wq` in vim)

Get the full path to Python with `which python` (and make sure
  `python --version` is >3)

Add the line `#! /path/to/python` to the top of the fist line of scan_to_ts

`echo "PATH=$HOME/scripts:$PATH" >> ~/.bash_profile`  
`source ~/.bash_profile`
