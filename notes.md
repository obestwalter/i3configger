## Some inspiration from i3 project

> * Never break configuration files or existing workflows. Breaking changes require a major version bump (v4 → v5).
* Keep mental complexity low: once you know i3’s key features, other features should be easy to understand.
* Only add features which benefit many people, instead of going to great lengths to support rarely used workflows.
* Only documented behavior is supported. Clear documentation is a requirement for contributions.


**TODO** try the defaults again for a change: http://i3wm.org/docs/refcard.html


## TODO/TO CHECK

* should just work with a simple bar config without any special settings or variable assignments
* Show different ways of organizing (topics, bindings|settings|modes)
* DEMO Turn default config into config.d (maybe with test)

## Use cases

### Slightly less simple use case

Say you have a dark color scheme for your window decorations. Now you want to add a light scheme for when you hack at the beach in the glaring sun. You want to be able to switch that easily with a keyboard shortcut or a simple command line call.

1. Put all relevant settings regarding color in an extra configuration file
3. Name that file `scheme.dark.conf`
4. Copy that file to `scheme.light.conf`
5. Change the color values or variables in the new file to your liking

To switch to the next scheme, call:

    $ `i3configger next scheme`

`scheme` is an arbitrary name here and can be used with anything depending how you call the config partials. If you called your files `colors.dark.conf` and colors `colors.light.conf` `i3configger --next-colors` would do the job.

    $ `i3configger select scheme dark`

or :

    $ `i3configger select scheme light`

### Defaults

Can be saved in `.state.json`

# Build process

1. merge all files that fit the conditions and configuration
2. read in all lines that fit the pattern `set $.*`
3. parse them into a map key -> value
4. Resolve all indirect assignments (e.g. `set $bla $blub`)
5. Replace all variables in configs with their values

# Problem

some things in the i3 config are  static but it would be convenient to be able to change them dynamically depending on environment or on request.

**Elements to consider:**

* workspaces
* outputs
* keybindings
* bars

### Display specific bars on specific displays

Those bars should only be integrated if the display is present

Use http://python-xlib.sourceforge.net/doc/html/python-xlib_16.html to read display infos?

### different needs on different hosts

When on a different hosts, certain settings should be used that could also live in different files named by host.

## Solution

All these problems can be solved by introducing a simple mechanism that loads config files only when certain criteria are met. These criteria can be specified either manually (e.g. themes) or automatically (e.g. different hosts). A changing monitor configuration might be handled either manually or automatically depending on the personal taste of the user.

## Replace variables

Everything that is set with `set $<whatever> <value>` can be replaced using string template substitutions

It is then possible to switch sets of settings by simply replacing the source of variables.

This overcomes the restriction of the i3config that I can't assign variables to other variables (e.g. you can't say `set $someVar $someOtherVar`).

## Build on startup

It i3configger is started/run once before i3 is started the config can be build depending on settings and environments. e.g in xinitrc before i3wm is started.

e.g. which displays are connected and how should the workspaces and bars be configured according to that.


## TODO: collect and check resources


### Other Tools

... from the i3wm ecosystem

I did not try them all, but stumbled over them while checking if somebody else solved my problem already.

* [j4-make-config (i3-theme)](https://github.com/okraits/j4-make-config)
* [i3ColourChanger](https://github.com/PMunch/i3ColourChanger)
* [i3-manager](https://github.com/erayaydin/i3-manager)
