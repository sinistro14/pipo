#!usr/bin/env python3
import os
import urllib

from .bot import bot, groovy


def main():
    channel = os.environ["CHANNEL"]
    token = os.environ["TOKEN"]

    while True:  # wait for internet connection
        try:
            urllib.request.urlopen("https://www.google.pt/", timeout=5)
            break
        except:
            pass
    groovy.channel_id = channel
    bot.run(token)


if __name__ == "__main__":
    main()
