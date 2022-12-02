#!usr/bin/env python3
import os
import time
import urllib.request

from .bot import bot, groovy


def main():
    channel = os.environ["CHANNEL"]
    voiceChannel = os.environ["VOICE_CHANNEL"]
    token = os.environ["TOKEN"]

    while True:  # wait for internet connection
        try:
            urllib.request.urlopen("https://www.google.com/", timeout=5)
            break
        except:
            print("No internet connection")
            time.sleep(5)
            pass
    groovy.channel_id = channel
    groovy.voiceChannel_id = voiceChannel
    bot.run(token)


if __name__ == "__main__":
    main()
