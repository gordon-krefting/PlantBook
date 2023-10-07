# PlantBook
***Warning! This only works on a Mac and it probably only works for me. It's probably not a good example of how to write Lightroom plugins or Python applications. If you want to look at it anyway, have fun!***

Generates fancy plant guides based on tagged photos in an Adobe Lightroom catalog. There are two main parts of the app:
* A Lightroom plugin that provides a metadata structure for the tagging, does incremental exporting of the photos, and creates a control file that's used by:
* A Python app that generates a website showing off all the plants. Someday it will also produce a nice pdf

Prerequisites:
* Lightroom Classic (tested on 12.5)
* Poetry (tested on 1.6.1, installed by Homebrew)
* Python (tested on 3.11.5, installed by Homebrew)
* ssh keys set up for remote host

How set it up:
* Add the plugin using Lightroom's Plugin Manager
* Create a new Plant Book Publish Service with a local staging directory and remote host info
* Create a single Collection in the Publish Service
* Create <thisdir>/bookformatter/main.sh based on template.main.sh - this is to avoid trying to get Poetry into Lightroom's path
* Add photos (or smart collection parameters) to the collection
* Click publish
*
Stuff to know:
* Lightroom plugin logs to ~/Documents/LrClassicLogs/PlantBookPlugin.log
* main.py logs to <thisdir>/logs/o.log & <thisdir>/logs/rsync.log
* logtail.sh tails all logs at once
