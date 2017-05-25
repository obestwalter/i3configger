# i3configger

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/latest/wip.svg)](http://www.repostatus.org/#wip)

Generate i3 config files from a set of partial config files in a config folder. Do some nifty conditional integration and variable resolution (aslo for i3status configs). This makes switching of themes (optical or key bindings or whatever) possible and things like having per host settings.

## Example

I use this generate my own config. See [my i3 config](https://github.com/obestwalter/i3config): [.i3/config.d](https://github.com/obestwalter/i3config/tree/master/config.d)

The call:

    $ i3configger --select-host=$(hostname) --select-theme=solarized-dark

Creates [config](https://github.com/obestwalter/i3config/tree/master/config) and [i3status.main.conf](https://github.com/obestwalter/i3config/tree/master/i3status.main.conf) from the sources.

##  Features

* build main config and one or several i3status configs from the same sources
* render variables slightly more intelligently than i3 does it
* also render variables in i3status configs (set anywhere in the sources)
* reload or restart i3 when a change has been done (using `i3-msg`)
* notify when new config has been created and activated (using `notify-send`)
* conditional building of config depending on settings
* simple way to communicate settings to renderer
* build config as one shot script
* watch sources for changes and build automatically
* run as daemon or in foreground

Some things are still in the air - see [notes](notes.md).

# Installation

    $ pip install "git+https://github.com/obestwalter/i3configger.git#egg=i3configger"

Pypi release will be done, once the project reached beta state.

# Usage

**Default uses `.i3config` files in `~/.i3/config.d` and writes to `~/.i3/config`.**

one shot:

    $ i3configger

as daemon:

    $ i3configger --daemon

more info:

    $ i3configger --help
