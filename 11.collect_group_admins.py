from telethon.sync import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins
import time

with open("lists/groups_list.txt") as fp:
    GROUP_LINK = fp.read().strip().split("\n")

OUTPUT_FILE = 'lists/groups_admins.txt'

print("[+] Script started")
# logining to phone
client = TelegramClient('37255919654.session', '876811', '6c4317d4ac954471af5dfb54b7930560').start(phone='37255919654.session')
if not client.is_user_authorized():
    print("\n[-] Error occured while signing in, delete session file and try again.")
    exit()

async def main():
    COUNTER = 0
    for group_name in GROUP_LINK:
        COUNTER += 1
        print(format(COUNTER)+'.')
        print(f"\n[+] Group : {group_name}\n[+] Admins :")
        try:
            async for user in client.iter_participants(group_name, filter=ChannelParticipantsAdmins):
                if not user.bot:
                    print(f"    - {user.first_name}({user.username})")
                    with open(OUTPUT_FILE, 'a') as output:
                        output.write(format(user.username))
                        output.write('\n')

        except Exception as e:
            print(f"[-] Error Occurred while getting admins in {group_name}")
            print(f"[-] Error : {e}\n")


client.loop.run_until_complete(main())
