"""
Detects which clients are bots and which are normal people
"""
from client import Client
from settings import Settings

Settings.load_settings({"bot_detection"})


def init(ts, db):
    for client in Client.clients.values():
        if client.cldbid in Settings.settings["bot_detection"]["marked_bots"]:
            client.is_bot = True
            continue

        # TODO Better detect whether a client is a bot
        client.is_bot = False
