# Pomelo Discord Bot

Discord bot for fun. Ripe, fresh and juicy.

# How to run Pomelo locally

1. Clone the repository.
2. Set the working directory as the root directory of the repository (`/pomelo-discord-bot` by default).
3. Get the necessary API tokens and set them up as environmental variables:
   - Discord bot token
   - Google Maps API token
   - MongoDB's connection token (full identifier)
4. Execute `poetry install`.
5. Run the script by executing `poetry run pyton src/main.py`.

## FAQ

- When executing a command that connects to MongoDB, I get "certificate verify failed: certificate has expired" error. What do I do?  
The Root CA the Mongo Atlas uses has expired. Install ISRG Root X1, ISRG Root X2 and Let's Encrypt R3 certificates from [here](https://letsencrypt.org/certificates/).  
- How could I run Pomelo from AWS?  
Ahh, those were the days. Use [crontab](https://man7.org/linux/man-pages/man5/crontab.5.html) together with [nohup](https://en.wikipedia.org/wiki/Nohup). You should find a relevant, thorough guide somewhere.  

## History of Pomelo the Traveler

List of hosting services Pomelo used, in chronological order:
1. Localhost (sic!)
2. replit.com (I'm not even joking)
3. AWS (my wallet still hurts)
4. Heroku (it was wonderful)
5. ???
