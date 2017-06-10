# Build process

1. merge all files that fit the conditions and configuration
2. read in all lines that fit the pattern ``set $.*``
3. parse them into a map key -> value
4. Resolve all indirect assignments (e.g. ``set $bla $blub``)
5. merge additional context from `i3configger.json` and `.message.json`
5. Replace all variables in configs with their values
6. Write results
7. If config is valid: replace and reload. If not: leave the old configuration in place
