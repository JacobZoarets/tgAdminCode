import random
import time
import requests
from telethon import TelegramClient
from telethon.sync import TelegramClient, connection
from telethon.errors.rpcerrorlist import PhoneNumberOccupiedError, SessionPasswordNeededError, PhoneNumberBannedError
import datetime
import logging
from telethon import functions, types
import socks
# proxy = ("proxy.digitalresistance.dog", 443, "d41d8cd98f00b204e9800998ecf8427e")

COUNTER = 0

logging.basicConfig(level=logging.DEBUG, format='%(message)s', filename='lists/logs/auto_registration.log')

datetime.datetime.now()

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

def get_random_proxy():
    return random.choice(proxy_list)

HOW_MANY_SESSIONS_TO_CREATE = int(input("Please enter the number of sessions ? : "))

APP_ID_CODE = []
APP_ID = []
count_working_array=[]
count_not_working_array=[]

def file_open(file_name):
    with open(file_name, 'r') as file:
        data = file.read()
        lst_of_data = data.split('\n')
        for i_data in lst_of_data:
            app_id, app_code = i_data.split(' ')
            APP_ID_CODE.append(app_code)
            APP_ID.append(app_id)


file_open("lists/app_id.txt")


def get_data_from_txt(file_name):
    with open(file_name, 'r') as file:
        data = file.read()
        lst_of_data = data.split('\n')
        return lst_of_data


SMSPVA_API_KEY = get_data_from_txt("lists/smspva_key.txt")

OVERALL_COUNTER = 0
# COUNTRY_CODE = get_data_from_txt("lists/countries_all.txt")  
# COUNTRY_ABBR = get_data_from_txt("lists/countries_abr_all.txt")

COUNTRY_CODE = get_data_from_txt("lists/countries.txt")  
COUNTRY_ABBR = get_data_from_txt("lists/countries_abr.txt")
for x_tmp in COUNTRY_CODE:
    count_working_array.append(0)
    count_not_working_array.append(0)
not_working_numbers=[]
working_numbers=[]
COUNTRY_SELECTOR = 0


TELEGRAM_SELECTOR = 0


def get_number():
    url = 'http://smspva.com/priemnik.php?metod=get_number&country={}&service=opt29&apikey={}'.format(
        COUNTRY_ABBR[COUNTRY_SELECTOR], SMSPVA_API_KEY)
    # print(requests.get(url).text)
    resp = requests.get(url).json()
    # print(resp)
    return resp.get('number'), resp.get('id')


def get_sms(n):
    url = 'http://smspva.com/priemnik.php?metod=get_sms&country={}&service=opt29&apikey={}&id={}'.format(
        COUNTRY_ABBR[COUNTRY_SELECTOR], SMSPVA_API_KEY, n)
    # print(requests.get(url).text)
    resp = requests.get(url).json()
    # print(resp)
    return resp.get('sms') if resp.get('response') == "1" else None


if __name__ == '__main__':
    while COUNTER < HOW_MANY_SESSIONS_TO_CREATE:
        logging.info(COUNTER)
        print(COUNTER)
        COUNTER += 1
        number = None
        uid = None
        code = None
        is_connected = False
        code_sent = False
        limit_counter = 0
        code_counter = 0
        phone_counter = 0
        while not number:
            COUNTRY_SELECTOR = random.randrange(0, len(COUNTRY_ABBR))
            number, uid = get_number()
            time.sleep(0.4)
            # logging.info(COUNTRY_ABBR[COUNTRY_SELECTOR])
            print('No phone yet in country! '+format(COUNTRY_ABBR[COUNTRY_SELECTOR])+' '+format(COUNTRY_CODE[COUNTRY_SELECTOR]))
            # logging.info('No phone yet!')
            # print()
            time.sleep(0.3)
            phone_counter += 1
            if phone_counter > 2:
                break
        if not number:
            COUNTER -= 1
            continue

        logging.info(format(datetime.datetime.now().time())+' Number is taken: {}'.format(number))
        print('Number is taken: {}'.format(COUNTRY_ABBR[COUNTRY_SELECTOR])+''+format(number))

        TELEGRAM_SELECTOR = random.randrange(0, len(APP_ID))

        logging.info(APP_ID[TELEGRAM_SELECTOR])
        print(APP_ID[TELEGRAM_SELECTOR])
        # client = TelegramClient(format(COUNTRY_CODE[COUNTRY_SELECTOR].replace('+',''),number), APP_ID_CODE[TELEGRAM_SELECTOR], APP_ID[TELEGRAM_SELECTOR])
        try:
            use_proxy = get_random_proxy()
            print(f"Using Proxy {use_proxy}")
            client = TelegramClient(#"{}{}"
                    "{}{}".format(COUNTRY_CODE[COUNTRY_SELECTOR].replace('+',''),number),
                    APP_ID_CODE[TELEGRAM_SELECTOR],
                    APP_ID[TELEGRAM_SELECTOR]
                    # connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
                    # proxy=proxy
                )
            # print(client)
        except Exception as e:
            print(e)
            COUNTER -= 1
            break


        if not is_connected:
            try:
                time.sleep(0.6)
                client.connect()
                # print(client)
                is_connected = True
            except ConnectionResetError:
                # print('444')
                time.sleep(0.4)
                logging.info('connection to Telegram failed')
                print('connection to Telegram failed')
                count_not_working_array[COUNTRY_SELECTOR] = count_not_working_array[COUNTRY_SELECTOR] + 1
                not_working_numbers.append(number)

                tfile = open('lists/not_working.txt','a')
                # print('Not Working Numbers')
                for index in range(0,len(count_not_working_array)):
                    if count_not_working_array[index]!=0:
                        tfile.write('\n'+COUNTRY_CODE[index]+'('+str(count_not_working_array[index])+'),')
                        # print(COUNTRY_CODE[index]+'('+str(count_not_working_array[index])+'),')
                # for number_name in not_working_numbers:
                    # tfile.write('\n'+number_name)
                    # print('\n'+number_name)
                tfile.close()
                continue
            except Exception as e:
                # print('555')
                print(e)
                continue
        # if not is_connected:
        #     COUNTER -= 1
        #     continue
        while not code_sent:
            try:
                client.send_code_request(COUNTRY_CODE[COUNTRY_SELECTOR] + number, force_sms=True)
                code_sent = True
            # except (PhoneNumberBannedError, ConnectionError):
            #     logging.info('Remove {}'.format(number))
            #     print('Remove {}'.format(number))

            #     count_not_working_array[COUNTRY_SELECTOR] = count_not_working_array[COUNTRY_SELECTOR] + 1
            #     not_working_numbers.append(number)
            #     break
            # except ConnectionResetError:
            #     count_not_working_array[COUNTRY_SELECTOR] = count_not_working_array[COUNTRY_SELECTOR] + 1
            #     not_working_numbers.append(number)
            #     continue
            except Exception as e:
                print(e)
                COUNTER -= 1
                count_not_working_array[COUNTRY_SELECTOR] = count_not_working_array[COUNTRY_SELECTOR] + 1
                not_working_numbers.append(number)

                tfile = open('lists/not_working.txt','a')
                # print('Not Working Numbers')
                for index in range(0,len(count_not_working_array)):
                    if count_not_working_array[index]!=0:
                        tfile.write('\n'+COUNTRY_CODE[index]+'('+str(count_not_working_array[index])+'),')
                        # print(COUNTRY_CODE[index]+'('+str(count_not_working_array[index])+'),')
                # for number_name in not_working_numbers:
                    # tfile.write('\n'+number_name)
                    # print('\n'+number_name)
                tfile.close()
                break
        if not code_sent:
            # COUNTER -= 1
            continue
        while not code:
            code = get_sms(uid)
            time.sleep(1)
            print(format(datetime.datetime.now().time())+' No code yet!')
            code_counter += 1
            if code_counter > 60:
                count_not_working_array[COUNTRY_SELECTOR] = count_not_working_array[COUNTRY_SELECTOR] + 1
                not_working_numbers.append(number)

                tfile = open('lists/not_working.txt','a')
                # print('Not Working Numbers')
                for index in range(0,len(count_not_working_array)):
                    if count_not_working_array[index]!=0:
                        tfile.write('\n'+COUNTRY_CODE[index]+'('+str(count_not_working_array[index])+'),')
                        # print(COUNTRY_CODE[index]+'('+str(count_not_working_array[index])+'),')
                # for number_name in not_working_numbers:
                    # tfile.write('\n'+number_name)
                    # print('\n'+number_name)
                tfile.close()
                break
        if not code:
            COUNTER -= 1
            continue
        logging.info('Code is taken: {}'.format(code))
        print(format(datetime.datetime.now().time())+' Code is taken: {}'.format(code))
        logging.info(datetime.datetime.now().time())
    
        try:
            client.sign_in(COUNTRY_CODE[COUNTRY_SELECTOR] + number, code)
            print('Signed in!!')

            count_working_array[COUNTRY_SELECTOR] = count_working_array[COUNTRY_SELECTOR] + 1
            working_numbers.append(number)

            logging.info('Signed in!!')

            tfile = open('lists/working.txt','a')
            # print('Working Numbers')
            for index in range(0,len(count_working_array)):
                if count_working_array[index]!=0:
                    tfile.write('\n'+COUNTRY_CODE[index]+'('+str(count_working_array[index])+'),')
                    # print(COUNTRY_CODE[index]+'('+str(count_working_array[index])+'),')
            # for number_name in working_numbers:
                # tfile.write('\n'+number_name)
                # print('\n'+number_name)
            tfile.close()

        except Exception as e:
            print(e)
            try:
                client.sign_up(phone="{}{}".format(COUNTRY_CODE[COUNTRY_SELECTOR].replace('+',''),number), code=code, first_name='.', last_name='.')
                count_working_array[COUNTRY_SELECTOR] = count_working_array[COUNTRY_SELECTOR] + 1
                working_numbers.append(number)

                tfile = open('lists/working.txt','a')
                # print('Working Numbers')
                for index in range(0,len(count_working_array)):
                    if count_working_array[index]!=0:
                        tfile.write('\n'+COUNTRY_CODE[index]+'('+str(count_working_array[index])+'),')
                        # print(COUNTRY_CODE[index]+'('+str(count_working_array[index])+'),')
                # for number_name in working_numbers:
                    # tfile.write('\n'+number_name)
                    # print('\n'+number_name)
                tfile.close()

            except Exception as e:
                print(e)
                COUNTER -= 1
                count_not_working_array[COUNTRY_SELECTOR] = count_not_working_array[COUNTRY_SELECTOR] + 1
                not_working_numbers.append(number)

                tfile = open('lists/not_working.txt','a')
                # print('Not Working Numbers')
                for index in range(0,len(count_not_working_array)):
                    if count_not_working_array[index]!=0:
                        tfile.write('\n'+COUNTRY_CODE[index]+'('+str(count_not_working_array[index])+'),')
                        # print(COUNTRY_CODE[index]+'('+str(count_not_working_array[index])+'),')
                # for number_name in not_working_numbers:
                    # tfile.write('\n'+number_name)
                    # print('\n'+number_name)
                tfile.close()

                continue
            

            logging.info('Signed up!!')
            print('Signed up!!')

        logging.info('Waiting 1 seconds for account to mature')
        print(format(datetime.datetime.now().time())+' Waiting 7 seconds for account to mature')
        logging.info(datetime.datetime.now().time())
        # print(datetime.datetime.now().time())
        time.sleep(1)
        client.disconnect()
    
