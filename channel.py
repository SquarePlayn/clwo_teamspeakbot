import inspect

from settings import Settings
from utility import set_type, debug

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

    # Edit some channel variable(s)
    def edit_channel(self, changes, ts, db):
        try:
            ts.channeledit(cid=self.cid, **changes)
        except Exception as e:
            debug("Error editing channel " + str(self.cid) + " to " + str(changes), urgency=10)
            raise e

        for key in changes:
            setattr(self, key, changes[key])
            self.action_executed("edited_var_"+key, ts, db)

    # Move a channel to be in a section underneath a given channel (0 for top channel/level)
    def move_channel(self, section_id, underneath_id, ts, db):
        if self.pid == section_id:
            debug("Attempting to move channel "+str(self.cid)+" to section "+str(section_id) +
                  " under "+str(underneath_id)+" while already in that section.", urgency=10)
            return

        # Check if the name is available
        name = self.channel_name
        used_names_dest = {channel.channel_name for channel in Channel.channels.values() if channel.pid == section_id}
        if name in used_names_dest:
            used_names = {channel.channel_name for channel in Channel.channels.values()
                          if channel.pid in {section_id, self.pid}}
            append_number = 2
            base_name = name
            while name in used_names:
                name = base_name + " " + str(append_number)
                append_number += 1
            self.edit_channel({"channel_name": name}, ts, db)

        # Execute the move
        ts.channelmove(cid=self.cid, cpid=section_id, order=underneath_id)
        self.pid = section_id
        self.channel_order = underneath_id
        self.action_executed("edited_var_pid", ts, db)
        self.action_executed("edited_var_channel_order", ts, db)
        for client in self.clients:
            Client.clients[client].load_info(ts)

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

    # Create a new channel
    @staticmethod
    def create_channel(name, ts, db, options=None):
        if options is None:
            options = dict()
        cid = int(ts.channelcreate(channel_name=name, **options)[0]["cid"])
        channel = Channel(cid, ts)
        Channel.channels[cid] = channel
        channel.action_executed("edited_var_pid", ts, db)
        channel.action_executed("edited_var_channel_order", ts, db)
        return channel

# Need import afterwards to avoid cycle
from client import Client