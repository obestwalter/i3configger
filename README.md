# i3 configger

Generate i3 config files from a set of *.i3config files in a config.d folder.

Either as script or a deamon watching the folder and triggering a build on changes of one of the .i3config files.

# TODO

* [X] watch a folder for changes
* [X] only react on changes to .i3config files
* [X] concatenate .i3conf files and write to config
* [X] add command line handling
* [X] add watch and daemonize
* [ ] replace variables depending on certain criteria (e.g. hostname, number of connected monitors, etc.)
* [ ] think about integrating it into py3status

# Ideas

## Dynamic settings

Have settings.py instead of (or addtionally to) settings.i3conf that can then automatically adjust to environment changes.

Environment changes that are interesting need to be polled then (e.g. number of connected monitors, processes being spawned, whatever)

... or turn this into a py3status module after all ...
