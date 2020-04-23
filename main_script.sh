#!/bin/bash

while getopts d:s: option
do
case "${option}"
in
d) dnt=${OPTARG};;
s) sites=${OPTARG};;
esac
done

./testcript -d $dnt -s $sites
./provtest