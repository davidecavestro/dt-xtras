---
trigger: glob
globs: **/*(.vue|.js|.py)
---
# Given this example taxonomies.yaml file where the user dynamically defines taxonomies
```
taxonomies:
- hierarchical: false
  color: '#ff0000'
  id: brand
  name: Brand
  priority: 1
  regex_pattern: ^brand:(?P<value>.+)$
  relations: []
- hierarchical: false
  color: '#b942f0'
  id: region
  name: Region
  priority: 1
  regex_pattern: ^region:(?<id>\w+)$
  relations: []
- hierarchical: false
  color: '#42bcf0'
  id: bundle_version
  name: Bundle version
  priority: 1
  regex_pattern: ^(?!(?:brand|region|bundle|cust|env|deploy):)(?<bundle_name>[\w-]+):(?<version>[\d\w\.-]+)$
  relations: []
- associative: true
  color: '#42f057'
  id: site
  name: Site
  priority: 1
  regex_pattern: ^site:(?<brand>\w+):(?<region>\w+):(?<bundle_version>[\w-]+:[\d\.]+)$
  relations:
  - group: brand
    targets: brand
  - group: region
    targets: region
  - group: bundle_version
    targets: bundle_version

```
# And given the following example tags matching Site taxonomy
```
site:qualcoz:eu:bee:2026.05
site:qualcoz:eu:myapp:1.0.0
site:y:emea:bee:2025.12
site:y:eu:myapp:2.0.0
```
# brand:qualcoz has two bundles bee:2026.05 and myapp:1.0.0 on region:eu
# brand:y has a bundle bee:2026.05 on region:emea and myapp:2.0.0 on region:eu
# On the Navigation Tree/Hierarchical mode in the Frontend of the application, the region:eu under site:qualcoz doesn't share any data with the region:eu under site:y
# The Hierarchical data is computed on the backend as a tree defined by the tags matching taxonomies having attribute "hierarchical" set to True. The taxonomy relations determine the tree paths. Every relation target tag is a tree node, the first is the root, the second is its child, and so on.
