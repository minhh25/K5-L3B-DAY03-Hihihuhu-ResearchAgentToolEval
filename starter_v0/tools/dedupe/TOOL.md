---
name: dedupe
track: bonus
kind: local_formatter
requires_env: []
inputs: [items]
outputs: [items, removed]
side_effect: false
---
# dedupe

Removes duplicate items (same url, else same title ignoring case/accents) from
already-collected results before formatting. Items with neither url nor title
are dropped. Returns an error dict if `items` is not a list.
