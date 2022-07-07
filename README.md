# pathfinder
Simple script to extract unique directories/structures from a list of URLs, mainly used for attempting to find leaks in deep subdirectories or checking for routes that could be pointing to another host/secondary context.


## Example usage
Get a list of unique and known directories/structures for a given target, gathering URLs using [gau]().
```
gau example.com | python3 pathfinder.py
```

This will break down any directories into all possible directory structures, for example, let's say we have the following input from some tool.
```
http://example.com/some/path/getting/really/deep/
http://example.com/some/unique/path/
http://example.com/blah/test/
```
It will return the following output.
```
http://example.com/some/path/getting/really/deep/
http://example.com/some/path/
http://example.com/some/
http://example.com/
http://example.com/some/path/getting/
http://example.com/some/path/getting/really/
http://example.com/some/unique/
http://example.com/some/unique/path/
http://example.com/blah/
http://example.com/blah/test/
```

This can then be utilised with tools such as nuclei to check for vulnerabilities or leaks in subfolders several steps deep instead of simply the base directory. 

E.g.
```
gau -subs target.com | python3 pathfinder.py | nuclei -t exposures/configs/git-config.yaml
```

Issues and PRs are welcome :) 
