from discord_webhook import DiscordWebhook, DiscordEmbed

def send_message(item, webhook):
    webhook = DiscordWebhook(url=webhook, rate_limit_retry=True)
    embed = create_embed(item)
    webhook.content = "New item found on Mercari!"
    webhook.add_embed(embed)
    response = webhook.execute()


def create_embed(item):
    listing_id = item['ID']
    name = item['Name']
    price = str(item['Price']) + '¥'
    url = f'https://jp.mercari.com/item/{listing_id}'
    image_url = f'https://static.mercdn.net/item/detail/orig/photos/{listing_id}_1.jpg'
    embed = DiscordEmbed(title=name, color="03b2f8", url=url)
    embed.set_timestamp()
    embed.add_embed_field(name="Price", value=price, inline=False)
    embed.set_image(url=image_url)
    return embed
