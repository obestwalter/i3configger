# i3configger

**Disclaimer:** this is a tool aimed at users who already know how the configuration of [i3](https://i3wm.org) works (as described in the [excellent docs](https://i3wm.org/docs/userguide.html)). i3configger is an independent add-on, not directly affiliated with the project and in no way necessary to use i3 productively. It is strictly command line oriented and file based using a very slight enhancement of the existing i3 configuration format with some json sprinkled on top. If you are looking for a graphical tool to help you create a configuration, check out the [resources](resources.md).

**NOTE** using i3configger will replace your existing config files (configs and optional status bar configs), but it will move them to `<original-name>.bak` if no backup exists yet, so that you can easily revert the damage if you want to go back to your old files.

## Why?

I3 already has a very nice and simple configuration system. i3configger makes it a bit more malleable by making it possible to send "messages" to your configuration to change variables or to switch between alternative sub configurations (e.g. different color schemes). This is done by adding a build step that can be triggered by calling i3configger directly or by running it as a watcher process that automatically rebuilds and reloads when source files change or sending a message.

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
* if `i3 -C -c <path to new config>` fails with the newly rendered config, the old config will be kept, no harm done
