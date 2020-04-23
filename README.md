# 6CCS3PRJ
## Using Provenance for Online Tracking Data Analysis
__Student ID: 1747175
Supervisor: Luc Moreau__

## Installation
1. Navigate to the root directory of this project
2. Clone the OpenWPM repository: `git clone https://github.com/mozilla/OpenWPM`
2. Run install scripts
Run `install_pypackages.sh`
Run `conda activate prjprov`
__NOTE:__ Due to restrictions by OpenWPM, this software can only be run on Ubuntu and macOS (Homebrew required for macOS).
3. Navigate to the OpenWPM directory and run:
Ubuntu: `./install.sh` 
macOS: `./install-mac-dev.sh` 

## Running the program
1. Make sure the current conda environment is set to `prjprov`
2. Run `main_script.sh` with following parameters:
* `-s` followed by either a website URL or a filepath to a .txt file with the list of websites to visit separated by lines.
* `-d` followed by either 1 or 0. This indicates the DNT header value.   

__Example__: `./main_script.sh -s http://google.com -d 1`

3. OpenWPM will open a browser instance and visit the specified websites
4. `main.py` is executed which records provenance and outputs an analysis
5. Recorded files are located in the `Crawls/Results/` directory
