import asyncio
import logging
import os

from mercapi import Mercapi
from mercapi.requests import SearchRequestData

from webhook import send_message

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
keywords = ['初音ミク　どでか', '初音ミク メガジャンボ寝そべりぬいぐるみ',
            '初音ミク 特大寝そべりぬいぐるみ']  # Search keywords
names = ['ミク　どでか', 'ミク寝そべり', '初音ミク', 'ミクプライズ']  # Any of the words MUST be in the title
txt_cache_path = "log/cache.txt"


def load_txt_cache(file):
    isExist = os.path.exists(file)
    if isExist:
        with open(file, newline='') as f:
            read_items = set([line.rstrip() for line in f])
        return read_items
    else:
        return []


def save_txt_cache(file, ids, cache):
    # print(f"cache: {cache}, ids: {ids}")
    with open(file, "a") as fp:
        for line in ids:
            if line not in cache:
                fp.write(line)
                fp.write('\n')


async def main():
    m = Mercapi()
    results = []
    async with asyncio.TaskGroup() as tg:
        for keyword in keywords:
            results.append(await tg.create_task(m.search(keyword, status=[SearchRequestData.Status.STATUS_ON_SALE])))
    await parse_results(results)


async def parse_results(results):
    for idx, result in enumerate(results):
        cache = load_txt_cache(txt_cache_path)
        new_ids = set()
        print(f'Got {result.meta.num_found} items for keyword {keywords[idx]}')
        for item in result.items:
            if item.id_ not in cache and item.status != "ITEM_STATUS_SOLD_OUT":
                new_ids.add(item.id_)
                await parse_item(item)
                # print(f'adding {item.id_} to {new_ids}')
            else:
                print(f'ID {item.id_} already exists, skipping')
        print(f'Got {len(new_ids)} new results for keyword {keywords[idx]}')
        save_txt_cache(txt_cache_path, new_ids, cache)


async def parse_item(item):
    title_check = [name for name in names if (name in item.name)]
    if title_check:
        data = {
            'ID': item.id_,
            'Name': item.name,
            'Price': item.price,
        }
        send_message(data)


if __name__ == '__main__':
    asyncio.run(main())
