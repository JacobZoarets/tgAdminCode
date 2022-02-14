import os
import random
import sys
from pathlib import Path
import re
import httpx
import trio
from telethon.sync import TelegramClient
from uuid import uuid4
from json.decoder import JSONDecodeError


async def checknum(num, ses):
    api_id = '888487'
    api_hash = '16346e5d78b44564dc51065ed21ac667'
    tgclient = TelegramClient(str(ses), api_id, api_hash)
    tgclient.connect()
    if not tgclient.is_user_authorized():
        print(F"Unable to connect to --> {num}")
        tgclient.disconnect()
        return False
    else:
        return tgclient


async def creator(sessions, proxies):
    limit = trio.CapacityLimiter(1)

    async with trio.open_nursery() as nurse:
        async def worker(ses, task_status=trio.TASK_STATUS_IGNORED):
            task_status.started()
            async with limit:
                num = f"+{os.path.basename(ses).split('.')[0]}"
                tgclient = await checknum(num, ses)
                if tgclient:
                    while True:
                        try:
                            proxy = {
                                'http': "http://{}:{}".format(*random.choice(proxies))
                            }
                            async with httpx.AsyncClient(proxies=proxy, timeout=None) as client:
                                data = {
                                    "phone": num
                                }
                                r = await client.post('https://my.telegram.org/auth/send_password', data=data)
                                rh = r.json()['random_hash']
                                print(num, rh)
                                break
                                match = re.search('code:.*?(\w.*?)$', str(tgclient.get_messages(None)[
                                                  0].message), re.MULTILINE | re.DOTALL).group(1)
                                data = {
                                    "phone": num,
                                    "random_hash": rh,
                                    "password": match
                                }
                                r = await client.post('https://my.telegram.org/auth/login', data=data)
                                print(r, r.text)
                                break

                        except JSONDecodeError:
                            print(f"Number: {num} Is Busy Currently.")
                            tgclient.disconnect()
                            break

        for session in sessions:
            await nurse.start(worker, session)


async def amain():
    if (len(sys.argv) != 3) or (not os.path.isdir(sys.argv[1])) or (not os.path.isfile(sys.argv[2])):
        return "Usage:\n     python script.py SessionDirectory ProxyFile"

    sessions = list(Path(sys.argv[1]).glob("*.session"))
    print(sessions)
    proxies = list(map(lambda x: x.split(','), Path(
        sys.argv[2]).read_text().splitlines()))

    if len(sessions) >= 1 and len(proxies) >= 1:
        await creator(sessions, proxies)
    else:
        return "Sessions or Proxies is empty!"


def main():
    return trio.run(amain)


if __name__ == "__main__":
    sys.exit(main())
