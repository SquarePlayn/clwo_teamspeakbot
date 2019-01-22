from channel import Channel
from client import Client
from settings import Settings

Settings.load_settings({"general"})
settings = Settings.settings


def execute():
    print("The example module is being executed")

    clients = Client.clients
    print("There are " + str(len(clients)) + " clients:")
    for client in clients.values():
        print("  " + str(client.cldbid))

    channels = Channel.channels
    print("There are " + str(len(channels)) + " channels:")
    for channel in channels.values():
        print("  " + str(channel.cid))
