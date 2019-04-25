
  
# Twitter Saver    <img src="https://upload.wikimedia.org/wikipedia/en/9/9f/Twitter_bird_logo_2012.svg" width="42">
  
![Build Status](https://travis-ci.org/jmccartin/twitter_saver.svg?branch=master) 
[![codecov](https://codecov.io/gh/jmccartin/twitter_saver/branch/master/graph/badge.svg)](https://codecov.io/gh/jmccartin/twitter_saver)
       
Grabs tweets for a given user ID and collates threaded conversations into an offline LaTeX document (or a JSON file). This is particularly useful for when certain accounts decide to delete their tweet history, but also has value as an offline reference.
  
## Requirements  
**For saving conversations:** 
- Any Python 3.5+ distribution
 
**For publishing conversations:**  
- A working LaTeX distribution (with XeLaTeX)  
- Fontawesome 5 installed locally (OTF fonts)
  
## Usage
  
- Copy `configuration-defaults.yml` to your own version: `configuration.yml`, and specify the user whose tweets you wish to save. 
- To install the libraries, execute `pip install -r requirements.txt`  
- Execute `python src/python/main/saver.py --configuration conf/` to run the tweet saver.

The runtime bash scripts assume a Conda environment named 'TwitterSave'.
This assumption and requirement will be fixed in the future.
 - Execute `run.sh` from the command line to save tweets to the configured  
folder area.  
  
 - Execute `publish.sh` from the command line to publish a LaTeX file from   
the saved json database.
  
## Roadmap  
  
- More coverage of unit tests
- A tider and dynamic view of saved tweets  
  - Perhaps using HTML/AngularJS?