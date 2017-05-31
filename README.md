# i3configger [![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/latest/active.svg)](http://www.repostatus.org/#active)

Generates an [i3](https://i3wm.org) config from a set of `.conf` files in `~/.i3/config.d`. Does some nifty conditional integration of files on demand and variable resolution (also for i3status configs).

## Why?

* To be able to split my long and messy config file in many short, aptly named, messy config files
* To be able to assign variables to variables (`set $var $otherVar`)
* To be able to also use variables in i3status configurations
* To be able to change the config dynamically without having to manually make changes to the config file

## Getting started


    $ i3configger --init [/path/to/your/i3/config/dir]

If you use the standard location for saving your config (`~/.i3`)
* Creates a backup copy of your config (config.bak)

### Simple

1. Cut your config file into chewable chunks with the extension `.conf` and put them in the directory `~/.i3/config.d`.
2. Run `i3configger`.
3. A new config file - `~/.i3/config` - is generated.

Nothing exiting. Quite nice though, if you don't like long files.

**This is already working with the current release (plus variable resolution, and i3status variable resolution).**

### Watch files in the background

If you are experimenting with the config and want it automatically updated on change:

run it as a daemon:

    $ i3configger --daemon

stop the daemon:

    $ i3configger --kill

Run it in the foreground:

    $ i3configger --watch

## How?

This can best be understood by how I use this to generate [my own i3 config](https://github.com/obestwalter/i3config) - here are the config partials: [.i3/config.d](https://github.com/obestwalter/i3config/tree/master/config.d)

The call

    $ i3configger --select-host=$(hostname) --select-theme=solarized-dark

creates [config](https://github.com/obestwalter/i3config/tree/master/config) and [i3status.main.conf](https://github.com/obestwalter/i3config/tree/master/i3status.main.conf) from the sources.

The idea is simple:

Config partials that follow the naming scheme \<selector\>.\<name\>.conf are only rendered into the config if explicitly requested.

* The partial `host.ob1.conf` will be rendered if the option `--select-host=ob1` is passed to `i3configger`.
* The partial `theme.solaris-dark.conf` will only be rendered if `--select-theme=solaris-dark` is passed.

`host` and `theme` are selector names I chose for my use case, but they can be freely chosen as long as the naming scheme is adhered to.

##  Features

* build main config and one or several i3status configs from the same sources
* variables are handled slightly more intelligently than i3 does it (variables assignmed to other variabels are resolved)
* end of line comments are possible (removed at build time)
* variables in i3status configs are also resolved (set anywhere in the sources)
* reload or restart i3 when a change has been done (using `i3-msg`)
* notify when new config has been created and activated (using `notify-send`)
* simple way to render partials based on selectors (see example above)
* simple way to communicate settings to renderer (`$i3configger_key value`)
* build config as one shot script or watch for changes (foreground and daemon)

Some things are still in the air - see [notes](https://github.com/obestwalter/i3configger/blob/master/notes.md).

## Installation

You should install this into a Python 3.6 interpreter.

`i3configger` is released on [the Python Package Index](https://pypi.org/project/i3configger/). The standard installation method is:

    $ pip install i3configger

## Resources

### I3 official

* [i3wm](https://i3wm.org/)
* [reddit group](https://www.reddit.com/r/i3wm/)
* [Archlinux Wiki](https://wiki.archlinux.org/index.php/I3)

### Other Tools

... from the i3wm ecosystem

I did not try them all, but stumbled over them while checking if somebody else solved my problem already.

* [i3ColourChanger](https://github.com/PMunch/i3ColourChanger)
* [i3-manager](https://github.com/erayaydin/i3-manager)
