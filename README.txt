This is a personal project for getting the best plushies at the best price 
Can be changed to basically everything else for mercari though, see the app.py for details.
Now with partial async support and easy configurability!

How to use:

With Docker:
1. Fill in the .env file with your Discord Webhook URL for sending new Mikus, you can set your wanted search keywords here too
2. Build and then run the image with docker-compose.yaml
3. 9
Remember to mount a persistent volume while using Docker for saving of already sent Mikus between runs.

Without Docker:
1. pip install -r requirements.txt
2.  Fill in the .env file with your Discord Webhook URL for sending new Mikus, you can set your wanted search keywords here too
3. python app.py 

By default it searches for:
- Dodeka Miku 
- Jumbo Nesoberi Miku
- Tera Jumbo Nesoberi Miku