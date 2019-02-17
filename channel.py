import inspect

from settings import Settings
from utility import set_type

Settings.load_settings({"channel_variables"})


# Stores all information about channels
class Channel:
    channels = dict()
    subscriptions = dict()

    # Called when creating a new instance. Builds all instance's variables
    def __init__(self, cid, ts):
        self.cid = cid
        self.clients = set()  # Will be filled when creating the clients
        self.load_info(ts)

    # Executes a corresponding function on all subscribed modules
    def action_executed(self, action, ts, db):
        if action in Channel.subscriptions:
            for module in Channel.subscriptions[action]:
                function = getattr(module, "on_channel_"+action)
                function(self, ts, db)

    # Query and save all default channel variables
    def load_info(self, ts):
        tsinfo = ts.channelinfo(cid=self.cid)[0]
        channel_variables = Settings.settings["channel_variables"]
        for var_name in channel_variables:
            var_type = channel_variables[var_name]
            setattr(self, var_name, set_type(tsinfo[var_name], var_type))

    # Called initially. Builds the main structure
    @staticmethod
    def init(ts):
        channels_query = ts.channellist()
        for channel in channels_query:
            cid = int(channel["cid"])
            Channel.channels[cid] = Channel(cid, ts)

    # Get a channel by its cid
    @staticmethod
    def get_channel(cid, ts):
        return Channel.channels[cid]

    # Allows a module to subscribe to a certain action being executed
    @staticmethod
    def subscribe(action):
        module = inspect.getmodule(inspect.stack()[1][0])
        if action not in Channel.subscriptions:
            Channel.subscriptions[action] = list()
        Channel.subscriptions[action].append(module)
