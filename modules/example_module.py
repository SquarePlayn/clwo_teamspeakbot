from channel import Channel
from client import Client
from settings import Settings

# In this set you can specify which json settings files should be loaded for this module
required_settings = {"general"}
settings = Settings.settings

# In this set you can specify which modules are required to be loaded for this module
# They are guaranteed to be ran before this module is ran (be it executed, initialized or other action)
required_modules = {}


# A module may have an init function, which will be called before any of the other functions
def init(ts, db):
    print("- Initialization of the example module is being run now:")
    # For example here you can open your database connection
    # Or, for example, you can subscribe to an action of the clients or channels
    Client.subscribe("exampleaction")
    Channel.subscribe("exampleaction")


# A module may have an execute funcion, which will be called once
def execute(ts, db):
    print("- The example module is being executed:")

    clients = Client.clients
    print("There are " + str(len(clients)) + " clients online:")
    for client in clients.values():
        print("  " + str(client.cldbid))

    channels = Channel.channels
    print("There are " + str(len(channels)) + " channels:")
    for channel in channels.values():
        print("  " + str(channel.cid))

    someclient = next(iter(clients.values()))   # Getting an arbitrary client to run our example action on
    print("We are going to run the example action on the client with cldbid " + str(someclient.cldbid))
    someclient.action_executed("exampleaction", ts, db)

    somechannel = next(iter(channels.values()))  # Getting an arbitrary client to run our example action on
    print("We are going to run the example action on the channel with cid " + str(somechannel.cid))
    somechannel.action_executed("exampleaction", ts, db)


# Our example action of the client. Called when the action is executed on a client instance
def on_client_exampleaction(client, ts, db):
    print("Our example action was executed on the CLIENT with cldbid " + str(client.cldbid) + ".")


# Our example action of the channel. Called when the action is executed on a client instance
def on_channel_exampleaction(channel, ts, db):
    print("Our example action was executed on the CHANNEL with cid " + str(channel.cid) + ".")


# A module may have a finalize function, which will be called at the end.
# It is called before finalize is called on the other required modules
def finalize(ts, db):
    print("- The example module is being finalized:")
    # For example here you can close any database connection you opened
