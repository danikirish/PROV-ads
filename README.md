# 6CCS3PRJ
## Using Provenance for Online Tracking Data Analysis
__Student ID: 1747175
Supervisor: Luc Moreau__

## Installation
1. Clone this repository
2. Run install scripts
Run `install_pypackages.sh`
Run `conda activate prjprov`
__NOTE:__ Due to restrictions by OpenWPM, this software can only be run on Ubuntu and MacOS.
Navigate the OpenWPM directory
Ubuntu: run `./install.sh` 
MacOS: run `./install-mac-dev.sh`

## Running the program
1. Make sure the current conda environment is set to `prjprov`
1. Run `main_script.sh` with following parameters:
..* `-s` followed by either a website URL or a filepath to a .txt file with the list of websites to visit separated by lines.
..* `-d` foolowed by either 1 or 0. This indicates the DNT header value.
__Example__: `./main_script.sh -s http://google.com -d`
2. OpenWPM will open a browser instance and visit the specified websites
3. `main.py` is executed which records provenance and outputs an analysis
4. Recorded files are located in the `Crawls/Results/` directory
