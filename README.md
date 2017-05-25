# i3configger

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/latest/active.svg)](http://www.repostatus.org/#active)

Generate i3 config files from a set of partials in a config folder. Do some nifty conditional integration and variable resolution (also for i3status configs). This makes switching of themes (optical or via key binding or whatever) possible.

## Why?

* To be able to switch parts of the config dynamically depending on selectors
* To be able to assign variables to variables and use variables in the status bar configurations
* To be able to split my long and messy config file in many short, aptly named, messy config partials

## How?

This can best be understood by how I use this to generate [my own i3 config](https://github.com/obestwalter/i3config) - here are the config partials: [.i3/config.d](https://github.com/obestwalter/i3config/tree/master/config.d)

The call

    $ i3configger --select-host=$(hostname) --select-theme=solarized-dark

creates [config](https://github.com/obestwalter/i3config/tree/master/config) and [i3status.main.conf](https://github.com/obestwalter/i3config/tree/master/i3status.main.conf) from the sources.

The idea is simple:

Config partials that follow the naming scheme \<selector\>.\<name\>.conf are only rendered into the config if explicitly requested.

* The partial `host.ob1.conf` will be rendered if the option `--select-host-ob1` is passed to `i3configger`.
* The partial `theme.solaris-dark.conf` will only be rendered if `--select-theme-solaris-dark` is passed.

`host` and `theme` are selector names I chose for my use case, but they can be freely chosen as long as the naming scheme is adhered to.

##  Features

* build main config and one or several i3status configs from the same sources
* render variables slightly more intelligently than i3 does it
* also render variables in i3status configs (set anywhere in the sources)
* reload or restart i3 when a change has been done (using `i3-msg`)
* notify when new config has been created and activated (using `notify-send`)
* simple way to render partials based on selectors (see example above)
* simple way to communicate settings to renderer (`$i3configger_key value`)
* build config as one shot script or watch for changes (foreground and daemon)

Some things are still in the air - see [notes](notes.md).

## Installation

You should install this into a Python 3.6 interpreter.

`i3configger` is released on [the Python Package Index](https://pypi.org/project/i3configger/). The standard installation method is:

    $ pip install i3configger

## Usage

**Default uses `.i3config` files in `~/.i3/config.d` and writes to `~/.i3/config`.**

one shot:

    $ i3configger

as daemon:

    $ i3configger --daemon

more info:

    $ i3configger --help
