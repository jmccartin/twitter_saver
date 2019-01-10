#!/usr/bin/env bash

source activate TwitterSave
cat conf/banner.txt
python src/python/main/saver.py --configuration conf/