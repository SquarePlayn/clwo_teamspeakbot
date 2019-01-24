from channel import Channel
from client import Client
from settings import Settings

# In this set you can specify which json settings files should be loaded for this module
required_settings = {"general"}
settings = Settings.settings

# In this set you can specify which modules are required to be loaded for this module
# They are guaranteed to be ran before this module is ran (be it executed, initialized or other action)
required_modules = {}


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
