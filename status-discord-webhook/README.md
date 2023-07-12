UIUCTF chal status bot

to deploy:
1. create discord webhook, make it send a message (use `init_message.py`
  to make this easy), copy:
  1. webhook url -> WEBHOOK in `bot.secret.yaml`
  2. sent message ID -> MESSAGE_ID in `bot.yaml`
2. `./chal start`
