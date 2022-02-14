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

logging.basicConfig(level=logging.DEBUG, format='%(message)s', filename='lists/logs/collect.log')


SESSION_OPENED_LAST_24Hrs = 'lists/session_opened_last_24hrs.txt'

GROUP_LINK = input("write down the group without @")
OUTPUT_FILE = 'reports/'+format(GROUP_LINK)+'-all-members.csv'
counter = 0
OVERALL_COUNTER = 0
DEAD_SESSIONS = 'lists/dead_sessions.txt'
TOTAL_LIVE_COUNTER = 0
TOTAL_DEAD_COUNTER = 0
 
TARGET_GROUP_LINK_SELECTOR = 0

APP_ID_CODE = []
APP_ID = []

GROUP_LINK_path = [GROUP_LINK]

def file_open(file_name):
    with open(file_name, 'r') as file:
        data = file.read()
        lst_of_data = data.split('\n')
        for i_data in lst_of_data:
            app_id, app_code = i_data.split(' ')
            APP_ID_CODE.append(app_code)
            APP_ID.append(app_id)


file_open("lists/app_id.txt")


all_sessions = [x for x in os.listdir('.') if 'session' in x] 
 
for session in all_sessions: 
    
    TELEGRAM_SELECTOR = random.randrange(0, len(APP_ID))
    print(format(APP_ID[TELEGRAM_SELECTOR])+' '+format(session))
    logging.info('TOTAL: ')
    logging.info(OVERALL_COUNTER)

    if session in open(DEAD_SESSIONS).read():
        logging.info("found dead")
        TOTAL_DEAD_COUNTER += 1
        # logging.info(TOTAL_DEAD_COUNTER)
        continue
    else:
        logging.info("found alive")
        TOTAL_LIVE_COUNTER += 1
        # logging.info(TOTAL_LIVE_COUNTER)

    client = TelegramClient(session, APP_ID_CODE[TELEGRAM_SELECTOR], APP_ID[TELEGRAM_SELECTOR])
    
    try:
        client.connect()
        # print(client.__dict__)
    except Exception as ex:
        print('cant connect with session')
        continue

    if not client.get_me():

        if session not in open(DEAD_SESSIONS).read():
            f = open(DEAD_SESSIONS, "a")
            f.write(session)
            f.write('\n')
            f.close()

        else:
            with open(SESSION_OPENED_LAST_24Hrs, "rw") as f:
                data = f.read().split('\n')
                if session in data:
                    continue
                else:
                    f.write(session)

        logging.info('{} is dead'.format(session))
        print ('{} is dead'.format(session))
        client.disconnect()

        # file = open("numbers_count/"+session, "w") 
        # file.write('DEAD :(') 
        # file.close() 

        time.sleep(1.1)
        # logging.info(datetime.datetime.now().time())
        continue

    if OVERALL_COUNTER == 1:
        print('Successfully finished collecting...')
        exit()
 
    logging.info(GROUP_LINK_path[OVERALL_COUNTER])
    logging.info(OVERALL_COUNTER)
    print(format(OVERALL_COUNTER)+' '+format(GROUP_LINK_path[OVERALL_COUNTER]))
    try:
        group = client.get_entity('t.me/'+GROUP_LINK_path[OVERALL_COUNTER])
    except Exception as ex:
        print('cant get group details')
        # logging.info(ex)
        # OVERALL_COUNTER += 1
        continue
        # logging.info(group)
        # print(group)
    try:
        client(JoinChannelRequest(group))
    except Exception as ex:
        print('cant join group')
        logging.info(ex)
        # OVERALL_COUNTER += 1
        continue
        # participants = client.get_participants(group)
    try:    
        participants = client.get_participants(group, aggressive=True)
        print(participants)
    except Exception as ex:
        print('cant get group participants')
        logging.info(ex)
        await client(LeaveChannelRequest(group))
        print("[+] left from "+format(group))
        # client(LeaveChannelRequest(group))
        # print("[+] left from "+format(group))
        # OVERALL_COUNTER += 1
        continue
        # logging.info(participants)
        o = []
        
    with open(OUTPUT_FILE, 'a') as output:
        for p in participants:
            # if p.phone or p.access_hash or p.username or p.first_name or p.last_name:
                # if type(p.status) is UserStatusOffline:
                # if type(p.status) is UserStatusOnline:
                    # if (datetime.datetime.utcnow() - p.status.was_online.replace(tzinfo=None)).days < LAST_ACTIVE_DAYS:
            logging.info(counter)
            logging.info(p.phone)
            print(format(counter)+' '+format(p.phone)+' '+format(p.access_hash)+' '+format(p.username)+' '+format(p.first_name)+' '+format(p.last_name)+' '+format(p.restriction_reason)+' '+format(p.status)+' '+format(p.deleted)+' '+format(p.bot)+' '+format(p.restricted)+' '+format(p.lang_code)+' '+format(p.id))
            output.write(format('t.me/'+GROUP_LINK[OVERALL_COUNTER]))
            output.write(format(p.phone)+', ')
            output.write(format(p.access_hash)+', ')
            output.write(format(p.username)+', ')
            output.write(format(p.first_name)+', ')
            output.write(format(p.last_name)+', ')
            output.write(format(p.deleted)+', ')
            output.write(format(p.bot)+', ')
            output.write(format(p.restricted)+', ')
            output.write(format(p.lang_code)+', ')
            output.write(format(p.id)+', ')
            output.write(format(p.restriction_reason)+', ')
            output.write(format('t.me/'+GROUP_LINK[OVERALL_COUNTER]))
            output.write(format(p.status))

            
            output.write('\n')
            counter += 1


        OVERALL_COUNTER += 1
        await client(LeaveChannelRequest(group))
        print("[+] left from "+format(group))

    # client(LeaveChannelRequest(group))
    # print("[+] left from "+format(group))
    continue

    # except Exception as ex:
    #     print()
    #     logging.info(ex)
    #     # OVERALL_COUNTER += 1
    #     continue

logging.info('Success.')
