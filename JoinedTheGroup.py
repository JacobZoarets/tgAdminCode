import datetime
from telethon import TelegramClient, sync
from telethon.tl.types import ChannelParticipantCreator, UserStatusOffline
from telethon.tl.types import UserStatusOnline
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import LeaveChannelRequest
import os
import random
import time
import logging
from telethon.errors.rpcerrorlist import PhoneNumberOccupiedError, SessionPasswordNeededError, PhoneNumberBannedError
import socks
# logging.basicConfig(level=logging.DEBUG, format='%(message)s', filename='lists/logs/collect.log')

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

SESSION_OPENED_LAST_24Hrs = 'lists/session_opened_last_24hrs.txt'

# GROUP_LINK = input("write down the group without @")
# OUTPUT_FILE = 'reports/'+format(GROUP_LINK)+'-all-members.csv'

OUTPUT_FILE = input("write down the list name:")

OUTPUT_DAYS = input("write how many days?:")
OUTPUT_FILE = 'lists/'+ OUTPUT_FILE + '_' + str(OUTPUT_DAYS) + '_days.txt'

OUTPUT_FILE_groups = 'lists/good_groups.txt'
counter = 70
OVERALL_COUNTER = 70
DEAD_SESSIONS = 'lists/dead_sessions.txt'
TOTAL_LIVE_COUNTER = 0
TOTAL_DEAD_COUNTER = 0
 
TARGET_GROUP_LINK_SELECTOR = 0

APP_ID_CODE = []
APP_ID = []

#all

with open("lists/groups_list.txt") as fp:
    GROUP_LINK = fp.read().strip().split("\n")
    # print(GROUP_LINK)
    # time.sleep(20)
    
def file_open(file_name):
    with open(file_name, 'r') as file:
        data = file.read()
        lst_of_data = data.split('\n')
        for i_data in lst_of_data:
            app_id, app_code = i_data.split(' ')
            APP_ID_CODE.append(app_code)
            APP_ID.append(app_id)


file_open("lists/app_id.txt")


all_sessions = [x for x in os.listdir('.') if '.session' in x and not '-journal' in x and not '.py' in x ]
 
for session in all_sessions: 
    
    TELEGRAM_SELECTOR = random.randrange(0, len(APP_ID))
    print(format(APP_ID[TELEGRAM_SELECTOR])+' '+format(session))
    # logging.info('TOTAL: ')
    # logging.info(OVERALL_COUNTER)

    if session in open(DEAD_SESSIONS).read():
        logging.info("found dead")
        TOTAL_DEAD_COUNTER += 1
        # logging.info(TOTAL_DEAD_COUNTER)
        continue
    else:
        logging.info("found alive")
        TOTAL_LIVE_COUNTER += 1
        # logging.info(TOTAL_LIVE_COUNTER)

    use_proxy = get_random_proxy()
    print(f"Using Proxy {use_proxy}")
    try:
        client = TelegramClient(session, APP_ID_CODE[TELEGRAM_SELECTOR], APP_ID[TELEGRAM_SELECTOR]) #, proxy = use_proxy
    except ConnectionError:
        pass
    except:
    	continue

    try:
        client.connect()
        # print(client.__dict__)
    except Exception as ex:
        print('cant connect with session')
        continue
    # print('1111')
    if not client.is_user_authorized():

        # if session not in open(DEAD_SESSIONS).read():
        #     f = open(DEAD_SESSIONS, "a")
        #     f.write(session)
        #     f.write('\n')
        #     f.close()

        # else:
        #     with open(SESSION_OPENED_LAST_24Hrs, "rw") as f:
        #         data = f.read().split('\n')
        #         if session in data:
        #             continue
        #         else:
        #             f.write(session)
        # print('22222')
        # logging.info('{} is dead'.format(session))
        print ('{} is dead'.format(session))
        client.disconnect()

        # file = open("numbers_count/"+session, "w") 
        # file.write('DEAD :(') 
        # file.close() 

        time.sleep(1.4)
        # logging.info(datetime.datetime.now().time())
        continue

    if OVERALL_COUNTER == 700:
        print('Successfully finished collecting...')
        exit()
 
    # logging.info(GROUP_LINK[OVERALL_COUNTER])
    # logging.info(OVERALL_COUNTER)
    print(format(OVERALL_COUNTER)+' '+format(GROUP_LINK[OVERALL_COUNTER]))
    try:
        group = client.get_entity('t.me/'+GROUP_LINK[OVERALL_COUNTER])
    except Exception as ex:
        print('cant get group details')
        # logging.info(ex)
        OVERALL_COUNTER += 1
        continue
        # logging.info(group)
        # print(group)
    try:
        client(JoinChannelRequest(group))
    except Exception as ex:
        print('cant join group')
        # logging.info(ex)
        # OVERALL_COUNTER += 1
        continue
        # participants = client.get_participants(group)
    try:    
        # print(group)
        # time.sleep(20)
        participants = client.get_participants(group, aggressive=True)
        with open(OUTPUT_FILE_groups, 'a') as output2:
            output2.write(format(GROUP_LINK[OVERALL_COUNTER]))
            output2.write('\n')
        # print(participants)
    except Exception as ex:
        print(ex) 
        print('cant get group participants')
        client(LeaveChannelRequest(group))
        print("[+] left from "+format(group))
        # logging.info(ex)
        # client(LeaveChannelRequest(group))
        # print("[+] left from "+format(group))
        OVERALL_COUNTER += 1
        continue
        # logging.info(participants)
        o = []
        
    with open(OUTPUT_FILE, 'a') as output:
        for p in participants:
            try: 
                # if p.phone or p.access_hash or p.username or p.first_name or p.last_name:
                if p.username:
                    # if type(p.status) is UserStatusOffline:
                    # if type(p.status) is UserStatusOnline:
                    #    if (datetime.datetime.utcnow() - p.status.was_online.replace(tzinfo=None)).days < 5:
                    if (datetime.datetime.utcnow() - p.participant.date.replace(tzinfo=None)).days < int(OUTPUT_DAYS):

                # logging.info(counter)
                # logging.info(p.phone)
                
                            print(format(p.username))
                            output.write(format(p.username))
                            output.write('\n')
                # print(format(counter)+' '+format(p.phone)+' '+format(p.access_hash)+' '+format(p.username)+' '+format(p.first_name)+' '+format(p.last_name)+' '+format(p.restriction_reason)+' '+format(p.status)+' '+format(p.deleted)+' '+format(p.bot)+' '+format(p.restricted)+' '+format(p.lang_code)+' '+format(p.id))
                # output.write(format('t.me/'+GROUP_LINK[OVERALL_COUNTER]))
                # output.write(format(p.phone)+', ')
                # output.write(format(p.access_hash)+', ')
                # output.write(format(p.username)+', ')
                # output.write(format(p.first_name)+', ')
                # output.write(format(p.last_name)+', ')
                # output.write(format(p.deleted)+', ')
                # output.write(format(p.bot)+', ')
                # output.write(format(p.restricted)+', ')
                # output.write(format(p.lang_code)+', ')
                # output.write(format(p.id)+', ')
                # output.write(format(p.restriction_reason)+', ')
                # output.write(format('t.me/'+GROUP_LINK[OVERALL_COUNTER]))
                # output.write(format(p.status))
            except Exception as ex:
                print(format(p.username))
                    
            counter += 1


        OVERALL_COUNTER += 1
        client(LeaveChannelRequest(group))
        print("[+] left from "+format(group))

    # client(LeaveChannelRequest(group))
    # print("[+] left from "+format(group))
    continue

    # except Exception as ex:
    #     print()
    #     logging.info(ex)
    #     # OVERALL_COUNTER += 1
    #     continue

# logging.info('Success.')

