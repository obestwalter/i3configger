# i3 configger

Generate i3 config files from a set of *.i3config files in a config.d folder.

Either as script or a deamon watching the folder and triggering a build on changes of one of the .i3config files.

* build config as one shot script
* watch a folder for changes and build automatically
* runs as deamon or in foreground

# Ideas

## replace variables

Everything that is set with `set $<whatever> <value>` can be replaced using string template substitutions

It is then possible to switch sets of seetings by simply replacing the source of variables.

## Dynamic settings

Have settings.py instead of (or addtionally to) settings.i3conf that can then automatically adjust to environment changes.

Environment changes that are interesting need to be polled then (e.g. number of connected monitors, processes being spawned, whatever)

... or turn this into a py3status module after all ...
