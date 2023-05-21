#!usr/bin/env python3
import os
import time
import logging
import urllib.request

from pipo.bot import bot, pipo


def main():
    logging.basicConfig(encoding="utf-8", level=logging.INFO)
    channel = int(os.environ["CHANNEL"])
    voice_channel = int(os.environ["VOICE_CHANNEL"])
    token = os.environ["TOKEN"]

    while True:  # wait for internet connection
        try:  # TODO remove this check later
            urllib.request.urlopen("https://www.google.com/", timeout=5)
            break
        except:
            print("No internet connection.")
            time.sleep(5)
    pipo.channel_id = channel
    pipo.voice_channel_id = voice_channel
    bot.run(token)


if __name__ == "__main__":
    main()
