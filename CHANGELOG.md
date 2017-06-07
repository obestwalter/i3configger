# CHANGELOG

## [Unreleased]

### Removed

- end of line comments are not allowed anymore (too much bug potential - would need some form of parsing already to make it work -> not worth the fuzz)

### Changes

- Notification is off by default: cli arg changed from `--no-notify-` to `--notify`

### Fixed

- checking the config with `i3 -C` did not work because `-c` (small c) was not passed and the passed path to the new config was silently ignored and the active config was checked instead

## 0.4.4

### Fixed

- #2 - fails if not using i3status. Fixed by making the refresh call ignore any errors - not nice, just a quick fix.

# 0.0 - 0.4.3

**Basic implementation**

* build main config and one or several i3status configs from the same sources
* variables are handled slightly more intelligently than i3 does it (variables assigned to other variables are resolved)
* end of line comments are possible (removed at build time)
* variables in i3status configs are also resolved (set anywhere in the sources)
* reload or restart i3 when a change has been done (using `i3-msg`)
* notify when new config has been created and activated (using `notify-send`)
* simple way to render partials based on key value pairs in file name
* simple way to change the configuration by sending messages
* build config as one shot script or watch for changes
* send messages to watching i3configger process
* if `i3 -C fails` with the newly rendered config, the old config will be kept, no harm done

---

**Note:** The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).
