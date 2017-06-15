# Ideas

# generate unused keys

https://www.reddit.com/r/i3wm/comments/6f8znm/does_i3_support_transient_states/digobgi/

It's tedious, but worthwhile, to define unused keys as "nop" inside a mode. This avoids typos "falling through" into the file you're editing for example.

* Convention for mode: mode-<whatever>.conf
* add unused keys

## integrat wal

https://github.com/dylanaraps/wal

# Some inspiration from i3 project

> * Never break configuration files or existing workflows. Breaking changes require a major version bump (v4 → v5).
* Keep mental complexity low: once you know i3’s key features, other features should be easy to understand.
* Only add features which benefit many people, instead of going to great lengths to support rarely used workflows.
* Only documented behavior is supported. Clear documentation is a requirement for contributions.

# Display specific bars on specific displays

Those bars should only be integrated if the display is present

Use http://python-xlib.sourceforge.net/doc/html/python-xlib_16.html to read display infos?

# Build on startup

It i3configger is started/run once before i3 is started the config can be build depending on settings and environments. e.g in xinitrc before i3wm is started.

    tox -e i3configger

    tox -e i3configger -- --daemon

e.g. which displays are connected and how should the workspaces and bars be configured according to that.


# AUR package

**TODO**
