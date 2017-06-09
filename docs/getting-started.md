# Getting started

**WARNING** going ahead will overwrite your existing config file, so make sure your config is under source control and/or you have a backup. i3configger will create a backup of your old config but only one, so running i3configger twice will leave no trace of your original configuration file.

Having that out of the way: simply running i3configger once you have it installed should get you set up nicely.

    $ i3configger -vv

yields something like:

```text
2017-06-08 19:25:49,131 i3configger.main:main:28 INFO: set i3 refresh method to <bound method I3.reload_i3 of <class 'i3configger.ipc.I3'>>
2017-06-08 19:25:49,131 i3configger.base:set_notify_command:54 DEBUG: do not send notifications
2017-06-08 19:25:49,131 i3configger.config:fetch:159 INFO: read config from /home/oliver/.i3/config.d/i3configger.json
2017-06-08 19:25:49,132 i3configger.config:fetch:161 DEBUG: use:
{'bars': {'defaults': {'key': 'i3status',
                       'target': '..',
                       'template': 'tpl',
                       'value': 'default'},
          'targets': {}},
 'main': {'target': '../config'}}
2017-06-08 19:25:49,132 i3configger.config:fetch:159 INFO: read config from /home/oliver/.i3/config.d/.messages.json
2017-06-08 19:25:49,132 i3configger.config:fetch:161 DEBUG: use:
{'select': {}, 'set': {}}
2017-06-08 19:25:49,133 i3configger.config:__init__:43 DEBUG: initialized config  I3configgerConfig:
{'barTargets': {},
 'configPath': PosixPath('/home/oliver/.i3/config.d/i3configger.json'),
 'mainTargetPath': PosixPath('/home/oliver/.i3/config'),
 'message': None,
 'partialsPath': PosixPath('/home/oliver/.i3/config.d'),
 'payload': {'bars': {'defaults': {'key': 'i3status',
                                   'target': '..',
                                   'template': 'tpl',
                                   'value': 'default'},
                      'targets': {}},
             'main': {'target': '../config'}},
 'state': {'select': {}, 'set': {}},
 'statePath': PosixPath('/home/oliver/.i3/config.d/.messages.json')}
2017-06-08 19:25:49,134 i3configger.partials:select:92 DEBUG: selected:
[Partial(config.conf)]
```

## What happened?

* a structure like this has been created in your `i3` folder:

```text
<your i3 folder>
 ├── config
 ├── config.bak
 └── config.d
     ├── .messages.json
     ├── config.conf
     └── i3configger.json
```

* your config has been copied verbatim to `config.d/config.conf` so that you can now turn it into a malleable, chunky i3configger config as you see fit.

* a new config file has been generated instead of your old config (which should still be basically the same as your old one).

* a backup of the last config was created with `.bak`

* `i3configger.json` can be used to do configuration of the status bars.
* `.messages.json` remembers all the messages you have already sent to the configuration

## What now?

Have a look at the [examples](https://github.com/obestwalter/i3configger/tree/master/examples) to get an idea about how you can move towards a more dynamic configuration.

For a real world example look at [my own i3 config](https://github.com/obestwalter/i3config). Here are the config partials and settings: [.i3/config.d](https://github.com/obestwalter/i3config/tree/master/config.d), from which [config](https://github.com/obestwalter/i3config/tree/master/config) and all `i3status.*conf` files are built.

## Dev mode - watch config folder

If you are experimenting with the config and want it automatically updated on change:

run it in the foreground:

    $ i3configger --watch

run it as a daemon:

    $ i3configger --daemon

stop the daemon:

    $ i3configger --kill
