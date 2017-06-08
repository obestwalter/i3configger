[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/latest/active.svg)](http://www.repostatus.org/#active)
 [![Build Status](https://travis-ci.org/obestwalter/i3configger.svg?branch=master)](https://travis-ci.org/obestwalter/i3configger) [![PyPI version](https://badge.fury.io/py/i3configger.svg)](https://badge.fury.io/py/i3configger)

# i3configger

**Disclaimer:** this is a tool aimed at users who already know how the configuration of [i3](https://i3wm.org) works (as described in the [excellent docs](https://i3wm.org/docs/userguide.html)). i3configger is an independent add-on, not directly affiliated with the project and in no way necessary to use i3 productively. It is strictly command line oriented and file based using a very slight enhancement of the existing i3 configuration format with some json sprinkled on top. If you are looking for a graphical tool to help you create a configuration, check out the [resources in the docs](http://oliver.bestwalter.de/i3configger/resources).


**WARNING** using i3configger will overwrite your existing config file, so make sure your config is under source control and/or you have a backup before you try this. i3configger will create a backup of your old config but only one, so running i3configger twice will leave no trace of your original configuration file.

## Why?

I3 already has a very nice and simple configuration system. i3configger makes it a bit more malleable by making it possible to send "messages" to your configuration.

## How?

You can change any variable you have defined in the configuration by invoking `i3configger set <variable name> <new value>`.

You can switch between alternative sub configurations (e.g. different color schemes) that conform with a simple naming convention (`config.d/<key>.<value1>.conf`, `config.d/<key>.<value2>.conf`, etc.) by invoking e.g. `i3configger select-next <key>` or `i3configger select <value2>`.

This is realized by adding a build step that can be triggered by calling i3configger directly or by running it as a watcher process that automatically rebuilds and reloads when source files change or messages are sent.

To get an idea how this works, have a look at the [examples](https://github.com/obestwalter/i3configger/tree/master/examples) and [read the docs](http://oliver.bestwalter.de/i3configger).

## Installation

    $ pip install i3configger

See [docs](http://oliver.bestwalter.de/i3configger/installation) For more details and different ways of installation.

## Documentation

Read it here: http://oliver.bestwalter.de/i3configger

[Release announcements and discussion.](https://www.reddit.com/r/i3wm/comments/6exzgs/meet_i3configger/)
