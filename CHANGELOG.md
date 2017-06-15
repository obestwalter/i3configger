# CHANGELOG

## 0.7.7 (It's just getting better and better) - 2017-06-16
### Added

- resolve variables with as many levels of indirections as you want
- if resolving fails proper feedback about the failing path is given
- better error handling/notification, when config is broken
- tests for resolving contexts

### Fixed

- watch process does not crash anymore but gives proper feedback
- don't crash if switching without a default in .messages.json

## 0.7.6 (The devil is in the detail) - 2017-06-11
### Changed

- do not add partial into config if it purely contains set statements
- strip empty lines from beginning and end of partials

## 0.7.5 (Time to make an -git AUR?) - 2017-06-11
### Changed

- make checks more forgiving if no i3 is installed - for testing a complete run after a PKGBUILD

## 0.7.4 (Packaging is fun and good for testing) - 2017-06-11
### Changed

- improve ipc handling - fix setting methods too late

## 0.7.3 (Do the right thing) - 2017-06-11
### Fixed

- use actual partials path for initialization instead of assuming that parent of config path == partials path

## 0.7.2 (Need for speed) - 2017-06-11
### Changed

- shave off a few hundred precious milliseconds startup time, by moving the very expensive version fetching into a function that is only called, when the version is really needed.
- help the user, when they use a non existing command
- remove unwanted side effects from message
- when config.d already exists, but no i3configger.json exists yet, it is automatically created now
- better examples/tests

## 0.7.1 (The great packaging adventure begins) - 2017-06-10
### Changed

- (internal) vendor in a different inotify library that  makes it easier to package for Archlinux

## 0.7.0 (Better safe than sorry) - 2017-06-10
### Changed

- always create a backup of the users files if it does not exist already. Do **not** clobber it on subsequent builds to make sure you can always go back to your old files if needed, even if they are no external backups or SCM in place.

## 0.6.0 (Command & Conquer) - 2017-06-10
### Fixed

- wrong ordering of context merges (set was not working in all cases)

### Added

- new command: shadow - shadow arbitrary entries in `i3configger.json`

- new command: merge - merge a `.json` file into `.messages.json`

- new command: prune - opposite of merge: remove all keys from a given `.json` file in `.messages.json`

### Changed

- renamed file containing frozen messages from `.state.json` to `.messages.json`

## 0.5.3 (KISS) - 2017-06-09
### Changed

- de-rocket-science release process
- change description of tool

## 0.5.2 (Releasing correctly is hard) - 2017-06-09
### Fixed

- wrong CHANGELOG :)

## 0.5.1 (Maybe I should test more) - 2017-06-09
### Fixed

- #4 repair watch and daemon mode

## 0.5.0 (Half way there) - 2017-06-08
### Added

- proper documentation at http://oliver.bestwalter.de/i3configger/
- copy user or default config into `config.d` on initialization

### Removed

- end of line comments are not supported anymore (too much bug potential - would need some form of parsing already to make it work -> not worth the fuzz)

### Changed

- comments are not stripped from the build anymore
- notification is off by default: cli arg changed from `--no-notify-` to `--notify`

### Fixed

- checking the config with `i3 -C` did not work because `-c` (small c) was not passed and the passed path to the new config was silently ignored and the active config was checked instead

## 0.4.4 (I am not alone) - 2017-06-05
### Fixed

- #2 - fails if not using i3status. Fixed by making the refresh call ignore any errors - not nice, just a quick fix.

## 0.4.3 - (The Curious Incident of the Dog in the Night-Time) - 2017-06-04
### Added

* examples that are used as test cases

### Fixed

* some small fixes regarding selection

## 0.4.2 (The answer) - 2017-06-03
### Basic implementation

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

**Note:** format based on: [Keep a Changelog](http://keepachangelog.com/) project adheres to [Semantic Versioning](http://semver.org/).
