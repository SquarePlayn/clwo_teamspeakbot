# Stores all information about clients
class Channel:
    channels = dict()

    # Called when creating a new instance. Builds all instance's variables
    def __init__(self, cid, ts):
        self.cid = cid
        # TODO: Expand set of available variables

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
