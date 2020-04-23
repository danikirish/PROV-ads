#!/bin/bash

while getopts d:s: option
do
case "${option}"
in
d) dnt=${OPTARG};;
s) sites=${OPTARG};;
esac
done

echo "STARTING CRAWL"
echo $sites
echo $dnt
source OpenWPM/venv/bin/activate
python crawl.py --dnt $dnt --sites $sites
deactivate
python main.py
