from threading import Thread

from flask import Flask

app = Flask(__name__)
'''
This scripts creates an online server (thanks, Repl.it!) which is only made to keep the bot running at all times.
Additionally, to actually keep it running for more than 30 minutes (that's when repl.it shutdowns idle servers)
we use Uptime Robot which pings the server every 25 minutes.
'''
@app.route('/')
def home():
    return "Pomelo Bot: ONLINE"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    thread = Thread(target=run)
    thread.start()
