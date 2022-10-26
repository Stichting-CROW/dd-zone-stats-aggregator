import requests
import os

# To start without DB.
chats = [
   {
      "chat_id": -687323795,
      "all": True
   },
   {
      "chat_id": -724867662,
      "all": False,
      "municipalities": ["GM0518"]
   }
]

def send_telegram_msg(text, chat_id):
   token = os.getenv("TELEGRAM_TOKEN")
   print(chat_id)
   print(text)
   # Info on parse_mode:
   # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#message-formatting-bold-italic-code-
   # https://stackoverflow.com/a/66640534
   # https://docs.python-telegram-bot.org/en/stable/telegram.parsemode.html
   url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + str(chat_id) + "&parse_mode=MarkdownV2&text=" + text
   results = requests.get(url_req)
   print(results.json())

def send_msg(text, municipality):
   for chat in chats:
      if chat["all"] or municipality in chat["municipalities"]:
         send_telegram_msg(text, chat["chat_id"])
