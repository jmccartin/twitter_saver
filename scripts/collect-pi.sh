#!/usr/bin/env bash

# For some reason, the working dir isn't added
# to Python's path on a raspberry pi.
export PYTHONPATH=$(pwd)
cat twitter_saver/resources/banner.txt
python3 twitter_saver/saver.py --configuration conf/
