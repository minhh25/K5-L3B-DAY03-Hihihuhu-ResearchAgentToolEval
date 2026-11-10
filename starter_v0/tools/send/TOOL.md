---
name: send
track: bonus
kind: action
provider: Telegram Bot API
requires_env: [TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]
inputs: [text, confirmed]
outputs: [status]
side_effect: true
requires_confirmation: true
---
# send

Posts text to the configured private Telegram channel. Only literal boolean
`confirmed=True` authorizes this low-level tool. The chat runtime additionally
requires an approval token tied to the exact message preview. Eval blocks writes.
An empty text, API rejection or timeout returns an error; token URLs are redacted.
