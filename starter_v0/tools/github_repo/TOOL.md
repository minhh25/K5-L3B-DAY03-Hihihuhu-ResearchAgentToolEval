---
name: github_repo
track: bonus
kind: live_api
provider: GitHub REST (no key)
requires_env: []
inputs: [repo]
outputs: [items]
side_effect: false
---
# github_repo

Gets stats of one public GitHub repo (description, stars, language, last push).
Accepts `owner/name` or a full github.com URL. Returns an error dict on a
malformed repo string or HTTP failure.
