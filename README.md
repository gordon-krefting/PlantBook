# PlantBook
***Warning! This only works on a Mac and it probably only works for me. It's probably not a good example of how to
write Lightroom plugs or Python applications. If want to look at it anyway, have fun!***
Generates fancy plant guides based on tagged photos in an Adobe Lightroom catalog. There are two main parts of the app:
* A Lightroom plugin that provides a metadata structure for the tagging, does incremental exporting of the photos, and creates a control file that's used by:
* A Python app that generates a website showing off all the plants. Someday it will also produce a nice pdf
