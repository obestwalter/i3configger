# Examples

This folder contains some `config.d` folders and what is generated from them (in the folder above, just like it would be in the i3 config directory).

## [default](0-default)

The i3configger version of the i3 default configuration

Taken from `/etc/i3/config`

Simplest possible way of using it and a bit pointless, but you have to start somewhere.

## [partials](1-partials)

Different kinds of settings have their own files now and the bar is also build from `config.d`. The name fo the status bar config file is set dynamically with variables populated from `i3configger.json->bars->targets` section for every bar. There is only one bar here though, so this doesn't really show yet.

## [bars](2-bars)

Let's generate more bars now. If you have an external monitor where you want to have a different bar, you can add another section to i3configger.json->bars->targets, add another status bar configuration file. Two bar settings will be generated in the config and the two configuration files are rendered and referenced from the variables in the bar template.

## [variables](3-variables)

Variables can be set and used anywhere (independent of order. Variables can also be assigned the value of other variables.

## [schemes](4-schemes)

Files following `<key>.<value>.conf` signal that only one of them should be integrated and you can switch between them. One of them will always be included (alphabetically first one on initialization).

In this example there is also a `.message.json` which usually should not be committed as it contains volatile state. This is to demonstrate how messages play into the build behaviour.
