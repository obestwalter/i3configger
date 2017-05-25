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

## Examples

### Changing display configurations

I have workspaces assigned to concrete displays. If my display configuration changes I want that assignment to adapt also. (e.g. laptop only vs. docked)

    # Displays
    set $DISP0 DP-0
    set $DISP1 DP-3
    set $DISP2 DP-0

    bindcode Mod4+40 focus output $DISP0
    bindcode Mod4+Shift+40 move container to output $DISP0
    workspace $ws1 output $DISP0
    ...

Switching from docked to laptop only would need this readjustment:

        # Displays
        set $DISP0 DP-3
        set $DISP1 DP-3
        set $DISP2 DP-3
        
        ... rest stays the same as vars are used

I also might want application windows to go somewhere else by default (e.g. my IDE windows on multi monitor setups should be in different workspaces on differetn monitors and on laptop they should all be on the same workspace).

### Display specific bars on specific displays

Those bars should only be integrated if the display is present

### Changing appearance

To change the appearance you want to ue variables for all colors and switch them e.g. by switching out a theme file.

### different needs on different hosts

When on a different hosts, certain settings should be used that could also live in different files named by host.

## Solution

All these problems can be solved by introducing a simple mechanism that loads config files only when certain criteria are met. These criteria can be specified either manually (e.g. themes) or automatically (e.g. different hosts). A changing monitor configuration might be handled either manually or automatically depending on the personal taste of the user.

## Replace variables

Everything that is set with `set $<whatever> <value>` can be replaced using string template substitutions

It is then possible to switch sets of settings by simply replacing the source of variables.

This overcomes the restriction of the i3config that I can't assig variables to other variables (e.g. you can't say `set $someVar $someOtherVar`).

## Build on startup

It i3configger is started/run once before i3 is started the config can be build depending on settings and environments. e.g in xinitrc before i3wm is started.

e.g. which displays are connected and how should the workspaces and bars be configured according to that.

## Backup of last config

Don't clobber by default to protect users who don't have their config under SCM.

## Dynamic settings

Have settings.py instead of (or addtionally to) settings.i3conf that can then automatically adjust to environment changes.

Environment changes that are interesting need to be polled then (e.g. number of connected monitors, processes being spawned, whatever)

... or turn this into a py3status module after all ...
