# i3configger

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/latest/active.svg)](http://www.repostatus.org/#active)

Generate i3 config files from a set of partial config files in a config folder.

See [my i3 config](https://github.com/obestwalter/i3config) for an example: [.i3/config.d](https://github.com/obestwalter/i3config/tree/master/config.d) is turned into [config](https://github.com/obestwalter/i3config/tree/master/config)

##  Features

* build config as one shot script
* watch a folder for changes and build automatically
* run as deamon or in foreground

##  Planned

* substitution of variables
* dynamic stuff yet to be determined

# Installation

    $ pip install "git+https://github.com/obestwalter/i3configger.git#egg=i3configger"

# Usage

**Default uses `.i3config` files in `~/.i3/config.d` and writes to `~/.i3/config` and `~/.i3/status-bar.conf` see [i3configger.ini](i3configger/i3configger.ini).**

one shot:

    $ i3configger

as daemon:

    $ i3configger --daemon


more info:

    $ i3configger --help

# Ideas

## Build on startup

It i3configger is started/run once before i3 is started the config can be build depending on settings and environments. e.g in xinitrc before i3wm is started.

## Pick different sources depending on host/env/cmdline

A certain sub group of configuration is dependent on the environment. e.g. different sub folders qith hostnames are only used if the host fits

## Backup of last config

Don't clobber by default to protect users who don't have their config under SCM.

## Replace variables

Everything that is set with `set $<whatever> <value>` can be replaced using string template substitutions

It is then possible to switch sets of settings by simply replacing the source of variables.

This overcomes the restriction of the i3config that I can't assig variables to other variables (e.g. you can't say `set $someVar $someOtherVar`).

## Dynamic settings

Have settings.py instead of (or addtionally to) settings.i3conf that can then automatically adjust to environment changes.

Environment changes that are interesting need to be polled then (e.g. number of connected monitors, processes being spawned, whatever)

... or turn this into a py3status module after all ...
