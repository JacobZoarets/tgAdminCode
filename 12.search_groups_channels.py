from telethon.sync import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins
from telethon import functions
from time import sleep
from random import randint
import pathlib
from telethon.tl.types import ChannelParticipantsAdmins

# Clients data
api_id = 1454150
api_hash = "6bb467eaad074e28b7bfec3ad1a75d83"

# enter phone number as a session name
session_name = "37255937683.session"

search_keyword_file = 'lists/search_keywords.txt'

# True = for only groups
# False = for groups and channels
search_only_groups = True

output_file_name = 'lists/search_results_output.csv'

print("[+] Script started")

try:
    keyword_list = []
    with open(search_keyword_file) as fp:
        temp_list = fp.read().strip().split("\n")
        for i in temp_list:
            if not i.strip() == '':
                keyword_list.append(i.strip())
    print(f"[+] Sucessfully got keywords from '{search_keyword_file}'")
except Exception as e:
    print(f"[-] Error Occured while reading '{search_keyword_file}'")
    print(f"[-] Error : {e}")
    exit()

def add_data_to_output_file(keyword, data):
    if not pathlib.Path(output_file_name).exists():
        with open(output_file_name, 'w') as fw:
            fw.write("Keyword,Type,Title,Username,Participants,Admins")
    new_data = ''
    for i in data:
        new_data += f'\n{keyword},{i}'
    with open(output_file_name, 'a') as fw:
        fw.write(new_data)

# add_data_to_output_file(keyword_list)
# exit()

# logining to phone
client = TelegramClient(session_name, api_id, api_hash).start(phone=session_name)
if not client.is_user_authorized():
    print("\n[-] Error occured while signing in, delete session file and try again.")
    exit()

print("[+] Sucessfully logged in\n")
print(f"[+] Total keywords found in file : {len(keyword_list)}\n")



async def main():
    for index, keyword in enumerate(keyword_list):
        print(f"[{index+1}] {keyword}")
        result = await client(functions.contacts.SearchRequest(
            q=keyword,
            limit=100
        ))
        # print(result.stringify())
        data = []
        for i in result.chats:
            if i.megagroup:
                chat_type = "group"
                chat_admins = ""
                try:
                    async for user in client.iter_participants(i.username, filter=ChannelParticipantsAdmins):
                        if not user.bot:
                            if chat_admins:
                                chat_admins += f"|{user.first_name}({user.username})"
                            else:
                                chat_admins = f"{user.first_name}({user.username})"
                except:
                    chat_admins = "None"
                data.append(f"{chat_type},{i.title},{i.username},{i.participants_count},{chat_admins}")
            else:
                chat_type = "channel"
                chat_admins = "None"
                if not search_only_groups:
                    data.append(f"{chat_type},{i.title},{i.username},{i.participants_count},{chat_admins}")
        add_data_to_output_file(keyword, data)
        sleep(randint(1,3))
    print("\n[+] All keyword done, terminating script")

client.loop.run_until_complete(main())