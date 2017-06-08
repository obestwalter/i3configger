# Getting started

## Simple

1. Cut your config file into chewable chunks with the extension `.conf` and put them in the directory `<i3 config folder>/config.d`.
2. Run `i3configger`.
3. `i3configger.json` and `.state.json` are created in `config.d`
4. A new config file is generated instead of your old config.
5. A backup of the last config is kept with suffix `.bak`

* `i3configger.json` can be used to do configuration of the status bars.
* `.state.json` remembers the state of your current settings

## Watch files in the background

If you are experimenting with the config and want it automatically updated on change:

run it in the foreground:

    $ i3configger --watch

run it as a daemon:

    $ i3configger --daemon

stop the daemon:

    $ i3configger --kill

