# i3configger

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/latest/active.svg)](http://www.repostatus.org/#active)

Generates an [i3](https://i3wm.org) config from a set of `.conf` files in `~/.i3/config.d`. Does some nifty conditional integration of files on demand and variable resolution (also for i3status configs).

## Why?

* To be able to split my long and messy config file in many short, aptly named, messy files
* To be able to assign variables to variables (`set $var $otherVar`)
* To bea able to use variables in `i3status.conf`
* To be able to change the config dynamically without having to manually make changes to the config file

## Usage

### Simple

1. Cut your config file into chewable chunks with the extension `.conf` and put them in the directory `~/.i3/config.d`.
2. Run `i3configger`.
3. A new config file - `~/.i3/config` - is generated.

Nothing exiting. Quite nice though, if you don't like long files.

**This is already working with the current release (plus variable resolution, and i3status variable resolution).**

### RFC

Description of different workflows I would like to use myself. Comments very welcome in the issues.

### Slightly less simple use case

**NOTE** Since 4.13 color variables can be set system wide via Xresources: http://i3wm.org/docs/userguide.html#xresources

Say you have a dark color scheme for your window decorations. Now you want to add a light scheme for when you hack at the beach in the glaring sun. You want to be able to switch that easily with a keyboard shortcut or a simple command line call.

1. Put all relevant settings regarding color in an extra configuration file
3. Name that file `scheme.dark.conf`
4. Copy that file to `scheme.light.conf`
5. Change the color values or variables in the new file to your liking

To switch to the next scheme, call:

    $ `i3configger --next-scheme`

`scheme` is an arbitrary name here and can be used with anything depending how you call the config partials. If you called your files `colors.dark.conf` and colors `colors.light.conf` `i3configger --next-colors` would do the job.

If you want to choose a specific partial configuration using the example from above, you can do:


    (i3) 03:13:11 oliver@ob1 [0] < ~ >  7842 %
    i3configger theme="#very dark" i3status=main "host=$(hostname)" 
    ['theme=#very dark', 'i3status=main', 'host=ob1']



    $ `i3configger --select-scheme=dark`

or :

    $ `i3configger --select-scheme=light`


### Getting even more specific

If you want to alter a specific setting:

    $ `i3configger --config-hide_edge_borders=smart`

If you want to set the value of a specific variable, you can do:

    $ `i3configger --set-<variable name>=<variable value>`

e.g. if you configuration containes `set $lock_screen_color #00000` you can change by calling:

#FIXME try out the limitations of the command line here ... spaces? other special chars?

    $ `i3configger --set-lock_screen_color=#00000`


All these changes don't touch your source files but are still persistent unless you either wipe them:


    $ `i3configger --wipe

... or make them permanent by writing the changes back to your source files

    $ `i3configger --freeze


### Switching status bar scheme

... now the i3status settings don't allow use of variables in the default use of i3. With i3configger you can also use variable names there

### Different settings depending on which monitors are connected

**TODO**

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

### Other Tools

... from the i3wm ecosystem

I did not try them all, but stumbled over them while checking if somebody else solved my problem already.

* [i3ColourChanger](https://github.com/PMunch/i3ColourChanger)
* [i3-manager](https://github.com/erayaydin/i3-manager)
