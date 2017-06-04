[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/latest/active.svg)](http://www.repostatus.org/#active)
 [![Build Status](https://travis-ci.org/obestwalter/i3configger.svg?branch=master)](https://travis-ci.org/obestwalter/i3configger) [![PyPI version](https://badge.fury.io/py/i3configger.svg)](https://badge.fury.io/py/i3configger)

# i3configger

## Overview

* generate an [i3](https://i3wm.org) config from a set of `.conf` files in `<i3 config folder>/config.d`.

* automatically restart or reload i3 when changes were made (optional - on by default). This makes it possible to dynamically change settings that need changes in the configuration files (e.g. switch bar mode between hide and docked or cycle through different color schemes).

* keep it DRY (optional):

    * assign variables to variables
    * use variables in i3status configuration files
    * generate `bar {...}` settings from a simple template with some extra config.

##  Detailed Features

* build main config and one or several i3status configs from the same sources
* variables are handled slightly more intelligently than i3 does it (variables assigned to other variables are resolved)
* end of line comments are possible (removed at build time)
* variables in i3status configs are also resolved (set anywhere in the sources)
* reload or restart i3 when a change has been done (using `i3-msg`)
* notify when new config has been created and activated (using `notify-send`)
* simple way to render partials based on key value pairs in file name
* simple way to change the configuration by sending messages
* build config as one shot script or watch for changes
* send messages to watching i3configger process
* if `i3 -C fails` with the newly rendered config, the old config will be kept, no harm done

## Installation

**Note** the code is Python 3.6 only. I want to play with the new toys :)

`i3configger` is released on [the Python Package Index](https://pypi.org/project/i3configger/). The standard installation method is:

    $ pip install i3configger

**==> [i3configger release announcements and discussion](https://www.reddit.com/r/i3wm/comments/6exzgs/meet_i3configger/) <==**

## Getting started

### Simple

1. Cut your config file into chewable chunks with the extension `.conf` and put them in the directory `<i3 config folder>/config.d`.
2. Run `i3configger`.
3. `i3configger.json` and `.state.json` are created in `config.d`
4. A new config file is generated instead of your old config.
5. A backup of the last config is kept with suffix `.bak`

* `i3configger.json` can be used to do configuration of the status bars.
* `.state.json` remembers the state of your current settings

### Watch files in the background

If you are experimenting with the config and want it automatically updated on change:

run it in the foreground:

    $ i3configger --watch

run it as a daemon:

    $ i3configger --daemon

stop the daemon:

    $ i3configger --kill

## Diving a bit deeper

I use this to generate [my own i3 config](https://github.com/obestwalter/i3config). Here are the config partials and settings: [.i3/config.d](https://github.com/obestwalter/i3config/tree/master/config.d), from which [config](https://github.com/obestwalter/i3config/tree/master/config) and all `i3status.*conf` files are built.

With my config, the call:

    $ i3configger select scheme solarized-dark

will integrate `scheme.solarized-dark.conf` in the build and exclude all other `scheme.*.conf` files.

    $ i3configger select-next scheme

will switch to the next scheme (and wrap around to the first scheme)

This is persisted in `.state.json`

If I want to get my dock out of the way:

    $ i3configger set mode hide

**`select`** integrates different partial files. Config partials that follow the naming scheme `<key>.<value>.conf` are only rendered into the config if explicitly set via configuration or a message from the command line.

**`set`** assigns values to arbitrary variables that are set anywhere in the configuration.

All changes done this way are persisted in `.state.json`.

## Build process

1. merge all files that fit the conditions and configuration
2. read in all lines that fit the pattern `set $.*`
3. parse them into a map key -> value
4. Resolve all indirect assignments (e.g. `set $bla $blub`)
5. Replace all variables in configs with their values (bar configs get local context merged before substitution)
6. Write results
7. Check if config is valid - if not switch back to saved backup

## Resources

### I3 official

* [i3wm](https://i3wm.org/)
* [i3wm reddit group (FAQs)](https://www.reddit.com/r/i3wm/)
* [Archlinux Wiki](https://wiki.archlinux.org/index.php/I3)

### Other Tools

... from the i3wm ecosystem

* [online color configurator](https://thomashunter.name/i3-configurator/)
* [j4-make-config (i3-theme)](https://github.com/okraits/j4-make-config)
* [i3-style](https://github.com/acrisci/i3-style)
* [i3ColourChanger](https://github.com/PMunch/i3ColourChanger)
* [i3-manager](https://github.com/erayaydin/i3-manager)
