from discord_webhook import DiscordWebhook, DiscordEmbed
import re
WEBHOOK_URL= "WEBHOOK_URL_HERE"
REGEX_PATTERN = r'm\d{11,}'

def send_message(item):
  webhook = DiscordWebhook(url=WEBHOOK_URL, username="MikuBot")
  embed = create_embed(item)
  webhook.content = "New item found on Mercari!"
  webhook.add_embed(embed)
  response = webhook.execute()

def create_embed(item):
  name = item['Name']
  price = item['Price']+'¥'
  url = item['URL']
  listing_id=re.search(REGEX_PATTERN, url).group()
  if url.startswith('https://jp.mercari.com/'):
    image_url = f'https://static.mercdn.net/item/detail/orig/photos/{listing_id}_1.jpg'
  else:
     image_url = 'https://1001freedownloads.s3.amazonaws.com/vector/thumb/63319/Placeholder.png'
  print(image_url)  
  embed = DiscordEmbed(title=name, color="03b2f8", url=url)
  embed.set_timestamp()
  embed.add_embed_field(name="Price", value=price,inline=False)
  embed.set_image(url=image_url)
  return embed
