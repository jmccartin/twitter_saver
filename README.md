<img src="https://upload.wikimedia.org/wikipedia/en/9/9f/Twitter_bird_logo_2012.svg" width="64">
Twitter Saver

===================================

Grabs all tweets for a given user ID and collates threaded 
conversations into an offline LaTeX document (or a JSON file).

## Requirements
**For saving conversations:** 
Python 3, with all libraries found in `requirements.txt`

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

- Better thread handling
- Unit tests
- A tider and dynamic view of saved tweets
  - Perhaps using HTML/AngularJS?

