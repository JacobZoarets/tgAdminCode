import datetime
import logging
import os
import random
import time
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import PhoneNumberOccupiedError, SessionPasswordNeededError, PhoneNumberBannedError
from telethon import functions, types
from telethon.sync import TelegramClient
from telethon import TelegramClient, events, sync
from datetime import datetime, timedelta

datetime.now()
OVERALL_COUNTER = 0
DEAD_SESSIONS = 'lists/dead_sessions.txt'
ADMIN_USER = input("write down the username you want to recieve the messages")
TARGET_GROUP_LINK_SELECTOR = 0

APP_ID_CODE = []
APP_ID = []
SESSION_LIST = []
DATE_LIST = []

logging.basicConfig(level=logging.DEBUG, format='%(message)s', filename='lists/logs/update_sessions.log')


def file_open(file_name):
    with open(file_name, 'r') as file:
        data = file.read()
        lst_of_data = data.split('\n')
        for i_data in lst_of_data:
            app_id, app_code = i_data.split(' ')
            APP_ID_CODE.append(app_code)
            APP_ID.append(app_id)
        logging.info(APP_ID)
        logging.info(APP_ID_CODE)


file_open("lists/app_id.txt")

TELEGRAM_SELECTOR = 0

all_sessions = [x for x in os.listdir('.') if 'session' in x]

for session in all_sessions:
    print(format(OVERALL_COUNTER)+'. '+session)
    OVERALL_COUNTER += 1
    if session in open(DEAD_SESSIONS).read():
        print("already found dead")
        continue

    TELEGRAM_SELECTOR = random.randrange(0, len(APP_ID))
    logging.info(datetime.now().time())
    logging.info(session)
    # print(session)
    logging.info(APP_ID[TELEGRAM_SELECTOR])
    client = TelegramClient(session, APP_ID_CODE[TELEGRAM_SELECTOR], APP_ID[TELEGRAM_SELECTOR])

    try:
        client.connect()
        # file = open("sessions_count/"+session, "w") 
        # file.write('1') 
        # file.close()
    except Exception as e:
        print(e)

        continue

    if not client.is_user_authorized():
        print('{} is dead'.format(session))
    # if not client.get_me():
    #     f = open(DEAD_SESSIONS, "a")
    #     f.write(session)
    #     f.write('\n')
    #     f.close()
    #     print('{} is dead'.format(session))
    #     client.disconnect()

        # time.sleep(1.1)
        logging.info(datetime.now().time())
        continue

    try:
        
        #offset_date = datetime.now() + timedelta(days=-1)  # Here, I am adding a negative timedelta
    	for dialog in client.get_dialogs(offset_date=datetime.now() + timedelta(days=-1)):
            if dialog.unread_count:
                print(format(dialog.name+', '))
                print(format(dialog.entity.username)+', ')
                print(format(dialog.entity.phone)+', ')
                print(format(dialog.date))
                print(format(dialog.message.message)+', ')
                print('\n')
                try:
                    client.send_message(ADMIN_USER,'שם: '+format(dialog.name)+'\nיוזר: '+format(dialog.entity.username)+'\nטלפון: '+format(dialog.entity.phone)+'\nתאריך/שעה: '+format(dialog.date)+'\nהודעה: '+format(dialog.message.message))
                    client.send_read_acknowledge(dialog.entity.id, dialog.message)
                except Exception as e:
                    print(e)
                    continue
    except Exception as e:
        print(e)
        continue

    time.sleep(0.3)
    client.disconnect()
