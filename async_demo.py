import asyncio
from sys import argv
from datetime import datetime
from time import time

import aiohttp


async def get_html(session, num):
    print(f"{datetime.utcnow().isoformat()}: > request #{num} sent")
    async with session.get("https://httpbin.org/delay/3") as response:
        await response.text()
        print(f"{datetime.utcnow().isoformat()}: < response #{num} received")


async def sync_calls(session):
    for i in range(3):
        await get_html(session, i)


async def async_calls(session):
    tasks = []
    for i in range(3):
        tasks.append(get_html(session, i))

    await asyncio.gather(*tasks)


async def main():
    start = time()
    print(f"{datetime.utcnow().isoformat()}: START\n")

    async with aiohttp.ClientSession() as session:
        if len(argv) > 1 and argv[1] == "sync":
            await sync_calls(session)
        else:
            await async_calls(session)

    print(f"\nExecution time: {time() - start}")


if __name__ == "__main__":
    asyncio.run(main())
