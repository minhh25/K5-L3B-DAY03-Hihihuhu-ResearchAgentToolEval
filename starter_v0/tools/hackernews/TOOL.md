---
name: hackernews
track: bonus
kind: live_api
provider: HN Algolia (no key)
requires_env: []
inputs: [query, sort_by, max_results]
outputs: [items]
side_effect: false
---
# hackernews

Searches Hacker News stories (developer/tech community discussion). Not for
tweets or general news. Returns an error dict on empty query, bad `sort_by`, or HTTP failure.
