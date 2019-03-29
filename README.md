
  
# Twitter Saver    <img src="https://upload.wikimedia.org/wikipedia/en/9/9f/Twitter_bird_logo_2012.svg" width="42">
  
![Build Status](https://travis-ci.org/jmccartin/twitter_saver.svg?branch=master) 
[![codecov](https://codecov.io/gh/jmccartin/twitter_saver/branch/master/graph/badge.svg)](https://codecov.io/gh/jmccartin/twitter_saver)
       
Grabs tweets for a given user ID and collates threaded conversations into an offline LaTeX document (or a JSON file). This is particularly useful for when certain accounts decide to delete their tweet history, but also has value as an offline reference.
  
## Requirements  
**For saving conversations:** 
Any Python 3.4+ distribution, with required libraries found in `requirements.txt`  
  
**For publishing conversations:**  
A working LaTeX distribution (with XeLaTeX)  
  
## Usage  
  
 - Copy `configuration-defaults.yml` to your own version: `configuration.yml`,  
and specify the user whose tweets you wish to save.  
  
 - Execute `run.sh` from the command line to save tweets to the configured  
folder area.  
  
 - Execute `publish.sh` from the command line to publish a LaTeX file from   
the saved json database.  
  
## Roadmap  
  
- Better handling of branching threads
- Unit tests  
- A tider and dynamic view of saved tweets  
  - Perhaps using HTML/AngularJS?