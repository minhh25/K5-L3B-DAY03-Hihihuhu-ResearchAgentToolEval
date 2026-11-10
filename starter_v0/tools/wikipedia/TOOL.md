---
name: wikipedia
track: bonus
kind: live_api
provider: Wikipedia REST (no key)
requires_env: []
inputs: [title, lang]
outputs: [items]
side_effect: false
---
# wikipedia

Gets the lead summary of one Wikipedia article (background/definition of a
person, company, concept). Not for fresh news. Returns an error dict on empty
title, unsupported `lang`, or HTTP failure (e.g. 404 page not found).
