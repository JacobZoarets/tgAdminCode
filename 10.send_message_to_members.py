from telethon.sync import TelegramClient, events
from random import randint
from time import sleep
import json

# Clients data
api_id = 990322
api_hash = "a05dda98010122bcac37968c4cc2f512"
session_name = "31644002673.session"
bot_token = "1639006646:AAGOG8U7R6myCme-Zk5VQvP7ZGWIwKiTW9I"

# text file containing message you like to send
message_text_path = "message_content.txt"

# default is None, else if you like to send image or document
# then you can specify its path
message_file_path = 'mp4.JPG'

with open(message_text_path) as message:
    message_data = message.read().strip()

print("[+] Bot started")
# logining to bot session
bot = TelegramClient(session_name, api_id, api_hash).start(bot_token=bot_token)
if not bot.is_user_authorized():
    print("\n[-] Error occured while signing in, delete session file and try again.")
    exit()

@bot.on(events.ChatAction)
async def new_user(handler):
    try:
        if handler.user_joined or handler.user_left:
            await bot.send_message(handler.user, message_data, file=message_file_path)
            print(f"[+] Message sent to {handler.user.first_name}")
    except Exception as e:
        print("[-]",e)


bot.run_until_disconnected()
