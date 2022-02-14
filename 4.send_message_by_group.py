from telethon.sync import TelegramClient
from random import randint
from time import sleep
from telethon.tl.types import UserStatusOffline
from telethon.tl.types import UserStatusOnline
from telethon.tl.types import UserStatusRecently
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import LeaveChannelRequest
import json
import os
import time
import random, traceback
from datetime import datetime, timedelta
from telethon.errors.rpcerrorlist import PeerFloodError, FloodWaitError, InputUserDeactivatedError
from telethon.errors.rpcerrorlist import UserDeactivatedBanError
from telethon.errors.common import MultiError
import socks
from telegram import ParseMode


with open('message_content.txt') as message:
    message_data = message.read().strip()

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
#print(f"Random Proxy = {get_random_proxy()}")
#exit()

OVERALL_COUNTER = 0
TELEGRAM_SELECTOR = 0
COUNTER_SKIPPED = 0
COUNTER_DEAD = 0
COUNTER_BANNED = 0
COUNTER_GOOD = 0
people_counter = 0
people_counter_not_added = 0
send_admin = 0

is_joined_to_group = dict()
APP_ID_CODE = []
APP_ID = []

is_all_user_sent = False
random_sleep_range_btw_message = (1,2)
message_file_path = 'photo.jpg'
message_file_path_gif = 'mp4.mp4'
DEAD_SESSIONS = 'lists/dead_sessions.txt'
USER_ADMIN = input("username for admin for testing?")
telegram_link = 'http://t.me/'
group_name_only = input("name of group to take from?")
group = format(telegram_link)+format(group_name_only)

days_chosen = int(input("how many days last seen? (i.e: 5 = 5 days ago. 2 = 2 days ago)"))

SENT_MEMBERS_LIST = 'reports/'+format(group_name_only)+'-already_sent_members.csv'
NOT_SENT_MEMBERS_LIST = 'reports/'+format(group_name_only)+'-cant_be_sent_members.csv'
ALREADY_ADDED_PATH = 'reports/'+format(group_name_only)+'-sent_ids.json'

bot_token="1639006646:AAGOG8U7R6myCme-Zk5VQvP7ZGWIwKiTW9I"

try:
    with open(ALREADY_ADDED_PATH) as fp:
        sent_ids = json.load(fp)
except:
    print(format(ALREADY_ADDED_PATH)+" not found. creating it.")
    sent_ids = []
    with open(ALREADY_ADDED_PATH, "w") as fp:
        json.dump(sent_ids, fp)

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
    if is_all_user_sent:
        print("[+] Message sent to all user in group. Closing script.")
        exit()
    OVERALL_COUNTER += 1
    TELEGRAM_SELECTOR = random.randrange(0, len(APP_ID_CODE))
    # print(session)

    if session in open(DEAD_SESSIONS).read():
        COUNTER_DEAD += 1
        continue

    session_count_path = "sessions_count/"+session
    if ( os.path.isfile(session_count_path)):

        # session_count_counter +=1
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
            print(format(OVERALL_COUNTER)+". number worked in less in 24 hours. left: "+format(time_difference))
            COUNTER_SKIPPED +=1
            continue

    session_count_path = "sessions_count_banned/"+session
    if ( os.path.isfile(session_count_path)):
        session_count_counter +=1
        # print(session_count_counter)
        file = session
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(file)
        last_modified = time.ctime(mtime)
        last_modified = datetime.strptime(last_modified, "%a %b %d %H:%M:%S %Y")

        #add 24 hours
        last_modified_plus24 = last_modified + timedelta(hours=48)
        # print(last_modified_plus24)

        now_UTC = datetime.utcnow()
        # now_UTC = datetime.strptime(now_UTC, "%a %b %d %H:%M:%S %Y")
        # print(now_UTC)
        if(now_UTC < last_modified_plus24):
            time_difference = (last_modified_plus24-now_UTC)
            print(format(OVERALL_COUNTER)+". number banned. waiting 48 hours. left: "+format(time_difference))
            COUNTER_SKIPPED +=1
            continue
            
    while True:
        try:
            use_proxy = get_random_proxy()
            print(f"Using Proxy {use_proxy}")
            client = TelegramClient(session, APP_ID_CODE[TELEGRAM_SELECTOR], APP_ID[TELEGRAM_SELECTOR], proxy = use_proxy).start(bot_token=bot_token)
            client.connect()
            # break
        except ConnectionError:
            pass

    file_session = open("sessions_count/"+session, "w") 
    file_session.write('1') 
    file_session.close()
    if not client.is_user_authorized():
        if session not in open(DEAD_SESSIONS).read():
            f = open(DEAD_SESSIONS, "a")
            f.write(session)
            f.write('\n')
            f.close()
        COUNTER_DEAD += 1
        print (format(OVERALL_COUNTER)+'. '+format(datetime.now().time())+' {} is dead'.format(session))
        # print("\n[-] Session dead.")
        # exit()
        continue
    if not is_joined_to_group.get(session):
        try:
            client(JoinChannelRequest(group))
            print("[+] Joined to ",group)
        except:
            print("[-] Failed to join group :", group)
            # exit()
            continue
        # sleep(randint(*random_sleep_range_btw_message))
        is_joined_to_group[session] = True
    print(send_admin)
    if send_admin == 0:
        client.send_message(USER_ADMIN, message_data,parse_mode=ParseMode.HTML, file=message_file_path_gif)
        print('sent message to admin')
        send_admin = 1

    async def main():


        error_ids = []
        limit_counter = 1
        global sent_ids, people_counter, people_counter_not_added,COUNTER_GOOD, COUNTER_BANNED, COUNTER_DEAD, COUNTER_SKIPPED, is_all_user_sent, ALREADY_ADDED_PATH
        is_new_user = False
        t = time.time()
        async for user in client.iter_participants(group):
            # print('this user id: '+format(user.id)+' '+format(user.username)) 
            # print(user.status)

            if str(user.id) in sent_ids or user.is_self or user.bot :
                #print('already sent to:'+format(user.first_name))
                if not is_new_user: 
                    is_all_user_sent = True
                continue
            
            #sleep(0.5)
            if str(user.deleted) != 'False':
                print('user '+format(user.id)+' '+format(user.first_name)+' is deleted')
                continue

            if ('UserStatusOnline' in format(user.status)):
                print ('user '+format(user.first_name)+' online now!')
                # print(user.status.expires)
            if ('UserStatusRecently' in format(user.status)):
                print('user '+format(user.first_name)+' last seen recently at: '+format(user.status))

            if ('UserStatusOffline' in format(user.status) and (datetime.utcnow() - user.status.was_online.replace(tzinfo=None)).days <= days_chosen):
                print('user '+format(user.first_name)+' was online '+format(days_chosen)+' days ago or less: '+format(user.status.was_online))
            else:
                print('user '+format(user.first_name)+' was online more then '+format(days_chosen)+' days ago, skipping...')
                continue
                    
            is_new_user = True
            is_all_user_sent = False
            if limit_counter == 5:
                COUNTER_GOOD += 1
                await client(LeaveChannelRequest(group))
                print("[+] left from "+format(group))
                # await client(LeaveChannelRequest(group_to))
                # print("[+] left from "+format(group_to))
                break
            print(f"\n## Time Taken : {time.time() - t} seconds.")
            try:
                # print('trying sending message to '+format(user.id)+'...')
                await client.send_message(user, message_data, file=message_file_path_gif)
                sent_ids.append(str(user.id)) 
                with open(ALREADY_ADDED_PATH, "w") as fwrite:
                    json.dump(sent_ids, fwrite)
                
                # print("added to json")
                print(f"[+] Message sent to {user.id}, {user.first_name}, {user.last_name}")

                with open(SENT_MEMBERS_LIST, 'a') as sent_members:
                    sent_members.write(format(group)+', ')
                    sent_members.write(format(user.phone)+', ')
                    sent_members.write(format(user.access_hash)+', ')
                    sent_members.write(format(user.username)+', ')
                    sent_members.write(format(user.first_name)+', ')
                    sent_members.write(format(user.last_name)+', ')
                    sent_members.write(format(user.deleted)+', ')
                    sent_members.write(format(user.bot)+', ')
                    sent_members.write(format(user.restricted)+', ')
                    sent_members.write(format(user.lang_code)+', ')
                    sent_members.write(format(user.id)+', ')
                    sent_members.write(format(user.restriction_reason)+', ')
                    # sent_members.write(format(message_data)+', ')
                    sent_members.write(format(user.status))

                    sent_members.write('\n')

                people_counter += 1
                limit_counter += 1
                
                # time.sleep(randint(1,3))
            except FloodWaitError as ex:
                # print(ex)
                print (format(OVERALL_COUNTER)+'. '+format(datetime.now().time())+' {} is flood wait'.format(session))
                limit_counter = 0
                COUNTER_BANNED += 1
                await client(LeaveChannelRequest(group))
                print("[+] left from "+format(group))
                # people_counter_not_added +=1 
                continue
            except PeerFloodError as ex:
                print(ex)
                print (format(OVERALL_COUNTER)+'. '+format(datetime.now().time())+' {} is flood error'.format(session))
                limit_counter = 0
                COUNTER_BANNED += 1
                # await client(LeaveChannelRequest(group))
                print("[+] left from "+format(group))
                # people_counter_not_added +=1
                continue
            except MultiError as ex:
                print(ex)
                print (format(OVERALL_COUNTER)+'. '+format(datetime.now().time())+' {} is multi error'.format(session))
                limit_counter = 0
                COUNTER_BANNED += 1
                await client(LeaveChannelRequest(group))
                print("[+] left from "+format(group))
                # people_counter_not_added +=1
                continue
            except InputUserDeactivatedError as ex:
                sent_ids.append(str(user.id))
                with open(ALREADY_ADDED_PATH, "w") as fwrite:
                    json.dump(sent_ids, fwrite)
                limit_counter += 1


                with open(NOT_SENT_MEMBERS_LIST, 'a') as not_sent_members:
                    not_sent_members.write(format(group)+', ')
                    not_sent_members.write(format(user.phone)+', ')
                    not_sent_members.write(format(user.access_hash)+', ')
                    not_sent_members.write(format(user.username)+', ')
                    not_sent_members.write(format(user.first_name)+', ')
                    not_sent_members.write(format(user.last_name)+', ')
                    not_sent_members.write(format(user.deleted)+', ')
                    not_sent_members.write(format(user.bot)+', ')
                    not_sent_members.write(format(user.restricted)+', ')
                    not_sent_members.write(format(user.lang_code)+', ')
                    not_sent_members.write(format(user.id)+', ')
                    not_sent_members.write(format(user.restriction_reason)+', ')
                    # not_sent_members.write(format(message_data)+', ')
                    not_sent_members.write(format(user.status))

                    not_sent_members.write('\n')
                people_counter_not_added +=1
                print (format(OVERALL_COUNTER)+'. '+format(datetime.now().time())+' {} session is deleted'.format(session))
            except UserDeactivatedBanError as ex:
                sent_ids.append(str(user.id))
                continue
                with open(ALREADY_ADDED_PATH, "w") as fwrite:
                    json.dump(sent_ids, fwrite)
                limit_counter += 1 

                with open(NOT_SENT_MEMBERS_LIST, 'a') as not_sent_members:
                    not_sent_members.write(format(group)+', ')
                    not_sent_members.write(format(user.phone)+', ')
                    not_sent_members.write(format(user.access_hash)+', ')
                    not_sent_members.write(format(user.username)+', ')
                    not_sent_members.write(format(user.first_name)+', ')
                    not_sent_members.write(format(user.last_name)+', ')
                    not_sent_members.write(format(user.deleted)+', ')
                    not_sent_members.write(format(user.bot)+', ')
                    not_sent_members.write(format(user.restricted)+', ')
                    not_sent_members.write(format(user.lang_code)+', ')
                    not_sent_members.write(format(user.id)+', ')
                    not_sent_members.write(format(user.restriction_reason)+', ')
                    not_sent_members.write(format(user.status))
                people_counter_not_added +=1
                print (format(OVERALL_COUNTER)+'. '+format(datetime.now().time())+' {} user is deleted'.format(session))
            except Exception as ex:
                await client(LeaveChannelRequest(group))
                print("[+] left from "+format(group))
                # time.sleep(3.7)
                # print(ex)
                #traceback.print_exc()
                sent_ids.append(str(user.id))
                with open(ALREADY_ADDED_PATH, "w") as fwrite:
                    json.dump(sent_ids, fwrite)
                if 'Too many' in str(ex) or 'USER_DEACTIVATED_BAN' in str(ex) or 'deleted/deactivated' in str(
                        ex) or 'banned from sending' in str(
                        ex) or 'seconds is required' in str(ex):
                    # limit_counter += 1
                    limit_counter = 0
                    COUNTER_BANNED += 1
                    # people_counter_not_added +=1
                    print (format(OVERALL_COUNTER)+'. '+format(datetime.now().time())+' {} is banned'.format(session))
                    continue
                # if 'The user has been deleted' in str(ex):
                #     with open(NOT_ADDEDABLE_MEMBERS_LIST_FILE, 'a') as already:
                #         already.write(str(user.id))
                #         already.write('\n')
                #         limit_counter += 1
                #         people_counter_not_added +=1
                #         print (format(OVERALL_COUNTER)+'. '+format(datetime.now().time())+' {} cant be added'.format(session))
                #     continue

                if 'privacy settings' in str(ex) or 'already in too many channels' in str(ex):
                    print (format(OVERALL_COUNTER)+'. '+format(datetime.now().time())+' {} is privacy settings'.format(session))
                    people_counter_not_added +=1
                    limit_counter += 1
                    continue

                else:
                    print('else')
                    print (format(OVERALL_COUNTER)+'. '+format(datetime.now().time())+' {} is other error'.format(session))
                    print(ex)
                    with open(ALREADY_ADDED_PATH, "w") as fwrite:
                        json.dump(sent_ids, fwrite)

                    with open(NOT_SENT_MEMBERS_LIST, 'a') as not_sent_members:
                        not_sent_members.write(format(group)+', ')
                        not_sent_members.write(format(user.phone)+', ')
                        not_sent_members.write(format(user.access_hash)+', ')
                        not_sent_members.write(format(user.username)+', ')
                        not_sent_members.write(format(user.first_name)+', ')
                        not_sent_members.write(format(user.last_name)+', ')
                        not_sent_members.write(format(user.deleted)+', ')
                        not_sent_members.write(format(user.bot)+', ')
                        not_sent_members.write(format(user.restricted)+', ')
                        not_sent_members.write(format(user.lang_code)+', ')
                        not_sent_members.write(format(user.id)+', ')
                        not_sent_members.write(format(user.restriction_reason)+', ')
                        not_sent_members.write(format(user.status))
                    # limit_counter += 1
                    people_counter_not_added +=1
                    continue
                    # people_counter += 1
            #sent_ids.append(user.id)
            
            # limit_counter += 1 
        print('\n')
        print('**************************************')
        print('# '+format(datetime.now().time())+' TOTAL: '+format(OVERALL_COUNTER))
        print('# '+format(datetime.now().time())+' GOOD: '+format(COUNTER_GOOD))
        print('# '+format(datetime.now().time())+' MEMBERS SENT: '+format(people_counter))
        print('# '+format(datetime.now().time())+' MEMBERS NOT AVAILABLE: '+format(people_counter_not_added))
        print('# '+format(datetime.now().time())+' SKIPPED: '+format(COUNTER_SKIPPED))
        print('# '+format(datetime.now().time())+' BANNED: '+format(COUNTER_BANNED))
        print('# '+format(datetime.now().time())+' DEAD: '+format(COUNTER_DEAD))
        print('**************************************')
        print('\n')


    client.loop.run_until_complete(main())
