import random
from telethon.errors.rpcerrorlist import PhoneNumberOccupiedError, SessionPasswordNeededError, PhoneNumberBannedError
from telethon import TelegramClient


PHONE_NUMBER = input('Enter phone: ')+'972'

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

            return APP_ID, APP_ID_CODE


APP_ID, APP_ID_CODE = file_open("lists/app_id.txt")

TELEGRAM_SELECTOR = random.randrange(0, len(APP_ID))

client = TelegramClient(PHONE_NUMBER, APP_ID_CODE[TELEGRAM_SELECTOR], APP_ID[TELEGRAM_SELECTOR])
client.connect()
client.send_code_request('+' + PHONE_NUMBER)

code = input("Please Enter Code : ")
f_name = '.'
l_name = '.'

try:
    client.sign_up(code, f_name, l_name, phone='+' + PHONE_NUMBER)
    print('Signed up!!')
except Exception as e:
    print("Error!")
    print(e)


