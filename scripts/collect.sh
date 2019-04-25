#!/usr/bin/env bash

source activate TwitterSave
cat twitter_saver/resources/banner.txt
python twitter_saver/saver.py --configuration conf/
