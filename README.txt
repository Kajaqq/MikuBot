This is a personal project for getting the best plushies at the best price 
Can be changed to basically everything else for mercari though, see the app.py for details.
Now with partial async support!

How to use:

With Docker:
1. Fill in the MIKU_WEBHOOK env variable with your webhook URL in the Dockerfile or your docker-compose.yaml
2. Run the image
3. 9
Remember to mount a persistent volume while using Docker for saving of already sent Mikus between runs.

Without Docker:
1. pip install -r requirements.txt
2. Fill in the discord webhook URL for sending new Mikus in .env
3. python app.py 

By default it searches for:
- Dodeka Miku 
- Jumbo Nesoberi Miku
- Tera Jumbo Nesoberi Miku