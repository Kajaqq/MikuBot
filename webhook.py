import aiohttp
import discord


async def send_message(item, webhook):
    async with aiohttp.ClientSession() as session:
        discord_webhook = discord.Webhook.from_url(webhook, session=session)
        await discord_webhook.send(
            content="New item found on Mercari!",
            embeds=[create_embed(item)],
        )


def create_embed(item):
    listing_id = item["ID"]
    name = item["Name"]
    price = str(item["Price"]) + "¥"
    url = f"https://jp.mercari.com/item/{listing_id}"
    image_url = f"https://static.mercdn.net/item/detail/orig/photos/{listing_id}_1.jpg"
    embed = discord.Embed(
        title=name,
        color=0x03B2F8,
        url=url,
        timestamp=discord.utils.utcnow(),
    )
    embed.add_field(name="Price", value=price, inline=False)
    embed.set_image(url=image_url)
    return embed
