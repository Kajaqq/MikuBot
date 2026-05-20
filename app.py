import ast
import asyncio
import logging
import os
import sys
from pathlib import Path

import uvloop
from dotenv import load_dotenv
from mercapi import Mercapi
from mercapi.requests import SearchRequestData

from webhook import send_message

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
load_dotenv(override=True)

keywords = ast.literal_eval(os.getenv("MIKU_KEYWORDS", "[]"))  # Search keywords
names = ast.literal_eval(os.getenv("MIKU_NAMES", "[]"))
negative_names = ast.literal_eval(os.getenv("TETO_NAMES", "[]"))
min_price = ast.literal_eval(os.getenv("MIKU_MIN_PRICE", "[]"))
max_price = ast.literal_eval(os.getenv("MIKU_MAX_PRICE", "[]"))

txt_cache_path = Path("log/cache.txt")
WEBHOOK_SCHEMA = "https://discord.com/api/webhooks/"

# Webhook reading procedure
try:
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
    log_file.parent.mkdir(exist_ok=True, parents=True)
    if not log_file.is_file():
        return set()

    with log_file.open(encoding="utf-8", newline="") as f:
        return {line.rstrip() for line in f if line.rstrip()}


def append_txt_cache(file, item_id):
    log_file = Path(file)
    log_file.parent.mkdir(exist_ok=True, parents=True)
    with log_file.open("a", encoding="utf-8") as fp:
        fp.write(item_id)
        fp.write("\n")


async def main():
    m = Mercapi()
    tasks = []
    async with asyncio.TaskGroup() as tg:
        for keyword in keywords:
            tasks.append(
                tg.create_task(
                    m.search(
                        keyword,
                        price_min=min_price,
                        price_max=max_price,
                        status=[SearchRequestData.Status.STATUS_ON_SALE],
                    )
                )
            )
    results = [task.result() for task in tasks]
    await parse_results(results)


async def parse_results(results):
    cache = load_txt_cache(txt_cache_path)
    for idx, result in enumerate(results):
        new_ids = set()
        print(f"Got {result.meta.num_found} items for keyword {keywords[idx]}")
        for item in result.items:
            item_id = str(item.id_)
            if item_id not in cache:
                sent = await parse_item(item)
                if sent:
                    append_txt_cache(txt_cache_path, item_id)
                    cache.add(item_id)
                    new_ids.add(item_id)
                    # print(f'adding {item_id} to {new_ids}')
            # elif item.id_ in cache:
            #         print(f'ID {item.id_} already exists, skipping')
        print(f"Got {len(new_ids)} new results for keyword {keywords[idx]}")


def should_send_item(item):
    if not names:
        return True

    if any(name in item.name for name in negative_names):
        return False

    return any(name in item.name for name in names)


async def parse_item(item):
    if not should_send_item(item):
        return False

    data = {
        "ID": item.id_,
        "Name": item.name,
        "Price": item.price,
    }
    await send_message(data, webhook)
    return True


if __name__ == "__main__":
    uvloop.run(main())
    os.unsetenv("MIKU_WEBHOOK")
