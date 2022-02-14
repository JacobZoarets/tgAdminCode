import datetime
from telethon import TelegramClient, sync
from telethon.tl.types import UserStatusOffline
from telethon.tl.types import UserStatusOnline
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import LeaveChannelRequest
import os
import random
import time
import logging
from telethon.errors.rpcerrorlist import PhoneNumberOccupiedError, SessionPasswordNeededError, PhoneNumberBannedError
import socks

proxy_list = []
try:
    with open("lists/proxy_list.txt") as fp:
        proxy_data = fp.read().strip().split("\n")

    for proxy_text in proxy_data:
        addr, port = proxy_text.split(",")
        proxy_list.append(
                {
                    'proxy_type': socks.HTTP, # (mandatory) protocol to use (see above)
                    'addr': addr.strip(), # (mandatory) proxy IP address
                    'port': int(port), # (mandatory) proxy port number
                    #'username': 'foo', # (optional) username if the proxy requires auth
                    #'password': 'bar', # (optional) password if the proxy requires auth
                    #'rdns': True # (optional) whether to use remote or local resolve, default remote
                }
            )
except Exception as e:
    print(f"Exception : {e}") 
    print(f"Error while getting proxy. So proxy will not be added to telegram script.")
#print(proxy_list)
def get_random_proxy():
    return random.choice(proxy_list)

OVERALL_COUNTER = 0
TOTAL_LIVE_COUNTER = 0
TOTAL_DEAD_COUNTER = 0
 
TARGET_GROUP_LINK_SELECTOR = 0

APP_ID_CODE = []
APP_ID = []

def file_open(file_name):
    with open(file_name, 'r') as file:
        data = file.read()
        lst_of_data = data.split('\n')
        for i_data in lst_of_data:
            app_id, app_code = i_data.split(' ')
            APP_ID_CODE.append(app_code)
            APP_ID.append(app_id)


file_open("lists/app_id.txt")


all_sessions = [x for x in os.listdir('.') if '.session' in x and 'py' not in x]
print('**************************************')
print('Total Sessions to examine: '+format(len(all_sessions)))
print('**************************************')
print('\n')

for session in all_sessions: 
    time.sleep(0.2)
    OVERALL_COUNTER += 1
    
    TELEGRAM_SELECTOR = random.randrange(0, len(APP_ID))
    # print(format(APP_ID[TELEGRAM_SELECTOR])+' '+format(session))

    use_proxy = get_random_proxy()
    # print(f"Using Proxy {use_proxy}")
    try:
        client = TelegramClient(session, APP_ID_CODE[TELEGRAM_SELECTOR], APP_ID[TELEGRAM_SELECTOR])#, proxy = use_proxy
    except ConnectionError:
        print(format(OVERALL_COUNTER)+'. connection error')
        pass

    try:
        client.connect()
        # print(client.__dict__)
    except Exception as ex:
        print(format(OVERALL_COUNTER)+'. cant connect with session')
        continue
    
    if not client.is_user_authorized():
        # print(client.__dict__)
        TOTAL_DEAD_COUNTER += 1
        print (format(OVERALL_COUNTER)+'. '+format(session)+' is dead. Removing session...')
        client.disconnect()

        #delete session file
        #os.remove(session)
        try:
            os.remove(session)
            # print(format(session)+' removed')
        except OSError as e:
            print ("Error: %s - %s." % (e.filename, e.strerror))
        continue

    else:
        TOTAL_LIVE_COUNTER += 1
        print (format(OVERALL_COUNTER)+'. '+format(session)+' is alive')
        # print(client.__dict__)
        # print(client.__dict__[_flood_waited_requests])
        client.disconnect()


print('Successfully finished collecting...')
print('\n')
print('**************************************')
print('# TOTAL: '+format(OVERALL_COUNTER))
print('# LIVE: '+format(TOTAL_LIVE_COUNTER))
print('# DEAD: '+format(TOTAL_DEAD_COUNTER))
print('**************************************')
print('\n')
exit()