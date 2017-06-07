[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/latest/active.svg)](http://www.repostatus.org/#active)
 [![Build Status](https://travis-ci.org/obestwalter/i3configger.svg?branch=master)](https://travis-ci.org/obestwalter/i3configger) [![PyPI version](https://badge.fury.io/py/i3configger.svg)](https://badge.fury.io/py/i3configger)

# i3configger

**Note In case you have no idea what this is about:** This is a tool mainly aimed at users who already have some experience with [i3](https://i3wm.org). i3 is a great tiling window manager - try it out if you have some time, but be careful: you might never be able to switch back to traditional desktop environments.

**What does it do?** In short: i3configger makes i3 a bit more malleable by adding a way to simply change variable values and switch between different parts of the configuration.

## Main concepts

**`set`** assigns values to arbitrary variables that are set anywhere in the configuration.

**`select`** switches between `partials` marked as alternatives by following the naming scheme `<key>.<value>.conf`.

### Overriding variables with `set`

A lot in the i3 configuration can be changed the value of variables. i3configger adds an interface to change them with a (very, very) simple command language.

One example would be to switch aspects of the status bar(s) - for example mode and position:

A configuration containing:

```text
set $bar_mode hidden
set $bar_position top
...
bar {
    ...
    mode $bar_mode
    position $bar_position
}
```

can be manipulated by invoking:

```text
$ i3configger set bar_mode dock
$ i3configger set bar_position bottom
```

... and the dock appears and the bar is at the bottom now.

### Switching between alternatives with `select`

Bigger changes can be done by switching between `partials`. To realize this there is a simple naming convention for `partials` to mark them as alternatives of which only ever one is integrated into the final configuration.

The following `partials` form a group of alternatives:

    ~/.i3/config.d/scheme.blue.conf
    ~/.i3/config.d/scheme.red.conf
    ~/.i3/config.d/scheme.black.conf

The first part of the file (`scheme`) serves as the key of that group of alternatives and the second part (`blue`, `red`, `black`) is the value that can be chosen.

To choose a concrete alternative:

```text
$ i3configger select scheme red
```

To cycle through these different alternatives:

```text
$ i3configger select-next scheme
$ i3configger select-previous scheme
```

How you call your groups and their values is completely up to you, as long as you stick with the naming convention.

### Bonus track: keep it DRY

Using i3configger you can also:

* assign variables to variables (`set $someVar $someOtherVar`)
* Use variables set anywhere in config `partials` in i3status configuration files
* generate `bar {...}` settings from templates with some extra config.

## Installation

**Note** the code is Python 3.6 only. I want to play with the new toys :)

`i3configger` is released on [the Python Package Index](https://pypi.org/project/i3configger/). The standard installation method is:

    $ pip install i3configger

[i3configger release announcements and discussion](https://www.reddit.com/r/i3wm/comments/6exzgs/meet_i3configger/)

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

## How does it work?

The configuration is built from so called `partials` in `<i3 config folder>/config.d`. For very simple usages (just changing some variable for examples) it is not even necessary to spread the configuration over several files though. Have a look at the [examples](examples/README.md) to get an idea about how it can be used.

I use this to generate [my own i3 config](https://github.com/obestwalter/i3config). Here are the config partials and settings: [.i3/config.d](https://github.com/obestwalter/i3config/tree/master/config.d), from which [config](https://github.com/obestwalter/i3config/tree/master/config) and all `i3status.*conf` files are built.

Changes that are made to the configuration via i3configger messages are not written back to the `partials` but are persisted in a `.state.json` in the source folder. This file is used to override variables and choose alternative files during build. Deleting that file puts everything back to normal.

### Build process

1. merge all files that fit the conditions of the current configuration
2. read in all lines that fit the pattern `set $.*`
3. convert them into a map key -> value
4. Resolve all indirect assignments (e.g. `set $bla $blub`)
5. Replace all variables in configs with their values (bar configs get local context merged before substitution)
6. Write results to temporary location
7. Check if config is valid
8. backup current configuration
9. move configuration to the final target

##  Detailed Features

* build main config and one or several i3status configs from the same sources
* variables are handled slightly more intelligently than i3 does it (variables assigned to other variables are resolved)
* variables in i3status configs are also resolved (set anywhere in the sources)
* reload or restart i3 when a change has been done (using `i3-msg`)
* notify when new config has been created and activated (using `notify-send`)
* simple way to render partials based on key value pairs in file name
* simple way to change the configuration by sending messages
* build config as one shot script or watch for changes
* send messages to watching i3configger process
* if `i3 -C` fails with the newly rendered config, the old config will be kept, no harm done

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
