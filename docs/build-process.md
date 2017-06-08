# Build process

1. merge all files that fit the conditions and configuration
2. read in all lines that fit the pattern ``set $.*``
3. parse them into a map key -> value
4. Resolve all indirect assignments (e.g. ``set $bla $blub``)
5. Replace all variables in configs with their values (bar configs get
   local context merged before substitution)
6. Write results
7. Check if config is valid - if not switch back to saved backup
