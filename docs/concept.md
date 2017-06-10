# Concept

The configuration is built from so called `partials` in `<i3 config folder>/config.d`. For very simple usages (just changing some variable for example) it is not even necessary to spread the configuration over several files though. Have a look at the [examples](https://github.com/obestwalter/i3configger/tree/master/examples) to get an idea about how it can be used.

Changes that are made to the configuration via i3configger messages are not written back to the `partials` but are persisted in a `.messages.json` in the source folder. This file is used to override variables and choose alternative files during build. Deleting that file puts everything back to normal.

## Terms

* **`partials`**: the i3 configuration (including status bars and theirs configuration files - if configured) is built from files in `config.d` that make up the parts of the configuration to be built. They contain exactly what a normal configuration for i3 would contain only spread over several files (including status bar config files) - with somme added functionality mainly variable resolution, alternatives and bar configurations from templates.

* **`message`**: when invoking i3configger with positional arguments they constitute a simple message to the configuration, effectively triggering a build with the changes requested in the message.

## Message "mini language"

A message consists of a command, a  key and - depending on the command - a value.

Make sure you keep your filenames simple and avoid special characters. To be on the safe side always **single quote** values with special characters like color values or variable markers (`$`) - e.g. `i3configger set bar_bg_color '$orange'`.

### Commands

* **`set <key> <value>`** assigns a new value to any variable that is set anywhere in the configuration (note: `<key>` is the variable name **without** leading `$` sign). You can also assign variables to variables with set, just like in the configuration - e.g. `i3configger set someVar '$someOtherVar'` (note the **single quotes** to make sure the shell does not try to resolve the variable before passsing it to i3configger).

* **`select <key> <value>`** chooses a `partial` from a group of alternatives following the naming scheme `<key>.<value>.conf`.

* **`select-next <key>`**, **`select-previous <key>`** chooses the next/previous `partial` from a group of alternatives (in lexical order).

* **`shadow <key> <value>`** shadows any entry in `i3configger.json` - to address nested dictionaries chain the keys with `:` as separator - e.g. `i3configger shadow bars:targets:laptop:mode dock` will translate into:
    ```python
    {"bars": {"targets": {"laptop": {"mode": "dock"}}}}
    ```

* **`merge <path>`** merges the data from a given path into `.messages.json` to make larger changes in one step. If a relative path is given it is relative to `config.d`. An absolute path is used unchanged.

* **`prune <path>`** the opposite of merge: remove all keys in given file from `.messages.json`. If a relative path is given it is relative to `config.d`. An absolute path is used unchanged.

### Special values

* `del` if passed as value to `set` or `shadow` the key is deleted. E.g. `i3configger set someVar del`, will remove the key `someVar` in `.messages.json->set`

## Example: change variables values with `set`

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

... and the bar is docked after the first command and jumps to the bottom after the second message has been sent.

This is completely generic. All variables you set anywhere in the configuration can be changed by this.

### Warning about variables

The implementation of this is very simple (it just parses all variables and an optional message into a single dictionary and uses [Python Template String](https://docs.python.org/2/library/string.html#template-strings) to do the substitutions. To i3configger all `$varName` are the same and will be replaced with their value wherever they are.

This could bite you if you are not aware of that and use regular expressions containing `$` e.g. in [for_window](https://i3wm.org/docs/userguide.html#for_window). So make sure that you do not use an expression where a part containing `$whatever` also matches an existing variable that was assigned with `set $whatever`.

## Example: switch between alternatives with `select`

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

## Special conventions

#### Automatic selection for hostname

At the moment there is one special name that I deem useful to be populated differently, which is `hostname`. If you have `partials` in your `config.d` that follow the scheme `hostname.<value>.conf` the one will automatically be chosen that matches your current hostname the value (or none if none matches).

#### deactivate partials in `config.d`

If you want to deactivate a partial, you can do that by prepending a `.` to the file name, e.g. `.whatever.conf` or `.whatever.else.conf` are not included in the build even if they reside in your `config.d`.

## Bonus track: keep it DRY

Using i3configger you can also:

* assign variables to variables (`set $someVar $someOtherVar`)
* Use variables set anywhere in config `partials` in i3status configuration files
* generate `bar {...}` settings from templates with some extra config.
