# import datetime
from datetime import datetime, timedelta
from telethon import TelegramClient, sync
from telethon.tl.types import UserStatusOffline
from telethon.tl.types import UserStatusOnline
from telethon.tl.functions.channels import JoinChannelRequest
import os
import random
import time
import logging
from telethon.errors.rpcerrorlist import PhoneNumberOccupiedError, SessionPasswordNeededError, PhoneNumberBannedError


from telethon.tl.functions.messages import AddChatUserRequest

from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

datetime.now()
OVERALL_COUNTER = 0
DEAD_SESSIONS = 'lists/dead_sessions.txt'
TARGET_GROUP_LINK = input("write down the group or channel username without @")

COUNTER_SKIPPED = 0
COUNTER_DEAD = 0
COUNTER_BANNED = 0
COUNTER_GOOD = 0

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

TELEGRAM_SELECTOR = 0
session_count_counter = 0

all_sessions = [x for x in os.listdir('.') if 'session' in x]

for session in all_sessions:
    OVERALL_COUNTER += 1
    TELEGRAM_SELECTOR = random.randrange(0, len(APP_ID_CODE))
    # print(session)
    # print(APP_ID[TELEGRAM_SELECTOR])

    if session in open(DEAD_SESSIONS).read():
        #print("already found dead")
        continue

    session_count_path = "sessions_count/"+session
    if ( os.path.isfile(session_count_path)):
        session_count_counter +=1
        # print(session_count_counter)
        file = session
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(file)
        last_modified = time.ctime(mtime)
        last_modified = datetime.strptime(last_modified, "%a %b %d %H:%M:%S %Y")

        #add 24 hours
        last_modified_plus24 = last_modified + timedelta(hours=24)
        # print(last_modified_plus24)

        now_UTC = datetime.utcnow()
        # now_UTC = datetime.strptime(now_UTC, "%a %b %d %H:%M:%S %Y")
        # print(now_UTC)
        if(now_UTC < last_modified_plus24):
            time_difference = (last_modified_plus24-now_UTC)
            print("number worked in less in 24 hours. left: "+format(time_difference))
            COUNTER_SKIPPED +=1
            continue

    client = TelegramClient(session, APP_ID_CODE[TELEGRAM_SELECTOR], APP_ID[TELEGRAM_SELECTOR])
    # print(session)
    # print(session.__dict__)
    try:
        client.connect() 
        file = open("sessions_count/"+session, "w") 
        file.write('1') 
        file.close()
    except Exception as ex:
        print('cant connect with session')
        COUNTER_DEAD += 1
        continue

    if not client.get_me():

        if session not in open(DEAD_SESSIONS).read():
            f = open(DEAD_SESSIONS, "a")
            f.write(session)
            f.write('\n')
            f.close()
 
        # else:
        #     with open(SESSION_OPENED_LAST_24Hrs, "rw") as f:
        #         data = f.read().split('\n')
        #         if session in data:
        #             continue
        #         else:
        #             f.write(session)

        logging.info('{} is dead'.format(session))
        print (format(datetime.now().time())+' {} is dead'.format(session))
        client.disconnect()

        time.sleep(0.6)
        COUNTER_DEAD += 1
        continue

    # else:
    #     with open(SESSION_OPENED_LAST_24Hrs, "rw") as f:
    #         data = f.read().split('\n')
    #         if session in data:
    #             continue
    #         else:
    #             f.write(session)

    try:
        # group = client.get_entity(TARGET_GROUP_LINK)
        group = client.get_entity('t.me/'+TARGET_GROUP_LINK)
        # print(group)
    except Exception as ex:
        print(ex) 
        print('cant get group details')
        continue

    try:
        client(JoinChannelRequest(group))
        # print(joining)
    except Exception as ex:
        print (ex)
        print('cant join group')
        continue

    # time.sleep(20)
    # people = []
    # limit_counter = 1
    # to_be_added = []
    # with open(NOT_ADDEDABLE_MEMBERS_LIST_FILE, 'r') as b:
    #     cant_be_added = b.read().split('\n')
    # with open(ALREADY_ADDED_MEMBERS_LIST_FILE, 'r') as a:
    #     already_added = a.read().split('\n')
    # with open(MEMBERS_LIST_FILE, 'r') as te:
    #     everyone = te.read().split('\n')
    #     random.shuffle(everyone)
    #     for p in everyone:
    #         if p not in already_added and p not in cant_be_added:
    #             to_be_added.append(p)
    #     print('total {}'.format(len(to_be_added)))
    #     for t in to_be_added:
    #         if limit_counter == 5:
    #             COUNTER_GOOD += 1

    #             with open(GOOD_SESSIONS_AFTER_INSPECT, 'a') as inspected:
    #                 # inspected.append(session)
    #                 inspected.write(session)
    #                 inspected.write('\n')
    #             break
    #         try:
    #             client(InviteToChannelRequest(
    #                 group,
    #                 [t],
    #                 # fwd_limit=10
    #             ))

    #             print(format(datetime.now().time())+' '+format(limit_counter)+' added {}'.format(t))
    #             # print(limit_counter);
    #             limit_counter += 1
    #             time.sleep(0.1)
    #             # time.sleep(1.5)
    #             with open(ALREADY_ADDED_MEMBERS_LIST_FILE, 'a') as already:
    #                 already_added.append(t)
    #                 already.write(t)
    #                 already.write('\n')

    #         except Exception as ex:
    #             time.sleep(0.7)
    #             print(ex)
    #             if 'Too many' in str(ex) or 'USER_DEACTIVATED_BAN' in str(ex) or 'deleted/deactivated' in str(
    #                     ex) or 'banned from sending' in str(
    #                     ex) or 'seconds is required' in str(ex):
    #                 limit_counter = 0
    #                 COUNTER_BANNED += 1
    #                 break 
    #             if 'already in too many channels' in str(ex) or 'privacy settings' in str(ex) or 'No user has' in str(ex) or 'not a mutual contact' in str(ex) or 'Chat admin privileges are required' in str(ex) or 'Nobody is using this username' in str(ex):
    #                 with open(NOT_ADDEDABLE_MEMBERS_LIST_FILE, 'a') as already:
    #                     # already_added.append(t)
    #                     already.write(t)
    #                     already.write('\n')
    #                     limit_counter += 1
    #                 continue
    #             else:
    #                 print('else')
    #                 print(ex)
    #                 limit_counter += 1
        # print('Done')
        print(format(datetime.now().time())+' TOTAL: '+format(OVERALL_COUNTER))
        print(format(datetime.now().time())+' GOOD: '+format(COUNTER_GOOD))
        print(format(datetime.now().time())+' SKIPPED: '+format(COUNTER_SKIPPED))
        print(format(datetime.now().time())+' BANNED: '+format(COUNTER_BANNED))
        print(format(datetime.now().time())+' DEAD: '+format(COUNTER_DEAD))
        # print(OVERALL_COUNTER)
        client.disconnect()
        time.sleep(0.7)
