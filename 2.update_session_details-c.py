import trio
import sys
import os
from pathlib import Path
from telethon.sync import TelegramClient
from telethon.tl.functions.account import UpdateProfileRequest


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


async def checker(sessions):
    OVERALL_COUNTER = 0
    limit = trio.CapacityLimiter(9)

    async with trio.open_nursery() as nurse:

        async def check(ses, task_status=trio.TASK_STATUS_IGNORED):
            async with limit:
                task_status.started()
                num = f"+{os.path.basename(ses).split('.')[0]}"
                tgcl = await checknum(num, ses)
                if tgcl:
                    result = tgcl(UpdateProfileRequest(
                        first_name=name[0],
                        last_name=name[1]
                    ))

                    print('#################################')
                    print(format(OVERALL_COUNTER)+". NUMBER: {}, ".format(num))
                    print('NAME: '+format(result.first_name)+' '+format(result.last_name))
                    print('DELETED?: '+format(result.deleted))
                    print('ID: '+format(result.id))
                    print('PHONE: '+format(result.phone))
                    print('HASH: '+format(result.access_hash))
                    print('USERNAME: '+format(result.username))
                    print('#################################')
                    print('\n')

        for ses in sessions:
            OVERALL_COUNTER += 1
            await nurse.start(check, ses)


async def amain():
    if (len(sys.argv) != 2) or (not os.path.isdir(sys.argv[1])):
        return "Please Provide an Input Of Session Directory"
    global name
    name = input(
        "Please Insert First & Last Name Sepearted By Space: \n").split()
    sessions = list(Path(sys.argv[1]).glob("*.session"))
    await checker(sessions)


def main():
    return trio.run(amain)


if __name__ == "__main__":
    sys.exit(main())
