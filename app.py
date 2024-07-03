import asyncio
import logging
import os
import sys
import ast 

from pathlib import Path
from dotenv import load_dotenv

from mercapi import Mercapi
from mercapi.requests import SearchRequestData

from webhook import send_message

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
load_dotenv(override=True)
keywords = ast.literal_eval(os.getenv("MIKU_KEYWORDS",'[]')) # Search keywords
names =  ast.literal_eval(os.getenv("MIKU_NAMES",'[]'))
negative_names =  ast.literal_eval(os.getenv("LUKA_NAMES",'[]'))
min_price = ast.literal_eval(os.getenv("MIKU_MIN_PRICE",'[]'))
max_price = ast.literal_eval(os.getenv("MIKU_MAX_PRICE",'[]'))

txt_cache_path = "log/cache.txt"
WEBHOOK_SCHEMA = 'https://discord.com/api/webhooks/'


try:              # Webhook reading procedure
                  # Try loading webhook from .env file if exists, 
                  # not used for Docker as it's should be provided via compose file.
    webhook = os.environ["MIKU_WEBHOOK"]
    if webhook.startswith(WEBHOOK_SCHEMA):
        pass
    elif not webhook:
        raise KeyError
    else:
        raise ValueError
except KeyError: 
    sys.exit("No Webhook URL found in .env or MIKU_WEBHOOK variable")
except ValueError:
    sys.exit("The URL provided is not a valid discord webhook")


def load_txt_cache(file):
    log_file = Path(file)
    isExist = log_file.is_file()
    if isExist:
        with open(file, newline='') as f:
            read_items = set([line.rstrip() for line in f])
        return read_items
    else:
        log_file.parent.mkdir(exist_ok=True, parents=True)
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
            results.append(await tg.create_task(m.search(keyword, price_min=min_price, price_max=max_price, status=[SearchRequestData.Status.STATUS_ON_SALE])))
    await parse_results(results)


async def parse_results(results):
    for idx, result in enumerate(results):
        cache = load_txt_cache(txt_cache_path)
        new_ids = set()
        print(f'Got {result.meta.num_found} items for keyword {keywords[idx]}')
        for item in result.items:
            if item.id_ not in cache:
                new_ids.add(item.id_)
                await parse_item(item)
                #print(f'adding {item.id_} to {new_ids}')
            # elif item.id_ in cache:
            #         print(f'ID {item.id_} already exists, skipping')
        print(f'Got {len(new_ids)} new results for keyword {keywords[idx]}')
        save_txt_cache(txt_cache_path, new_ids, cache)


async def parse_item(item):
    if names:
        negative_title_check = [name for name in negative_names if (name in item.name)]
        if not negative_title_check:
            title_check = [name for name in names if (name in item.name)]
        else:
            title_check = False
    elif not names:
        title_check=True
    if title_check:
        data = {
            'ID': item.id_,
            'Name': item.name,
            'Price': item.price,
        }
        send_message(data, webhook)


if __name__ == '__main__':
    asyncio.run(main())
    os.unsetenv("MIKU_WEBHOOK")
