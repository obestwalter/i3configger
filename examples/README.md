# Examples

This folder contains some `config.d` folders and what is generated from them (in the folder above, just like it would be in the i3 config directory).

## [default](0-default)

The i3configger version of the i3 default configuration

Taken from `/etc/i3/config`

Simplest possible way of using it and a bit pointless, but you have to start somewhere.

## [chunked](1-chunks)

Different kinds of settings have their own files now and the bar is also build from `config.d`. The name fo the status bar config file is set dynamically with variables populated from `i3configger.json->bars->targets` section for every bar. There is only one bar here though, so this doesn't really show yet.

## [bars](2-bars)

Let's generate more bars now. If you have an external monitor where you want to have a different bar, you can add another section to i3configger.json->bars->targets, add another status bar configuration file. Two bar settings will be generated in the config and the two configuration files are rendered and referenced from the variables in the bar template.

## Variables

**TODO**

## Schemes

**TODO**
