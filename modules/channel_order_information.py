"""
This module provides channel instances with information about the following (when applicable, otherwise None):
* Channel above them (In same section)
* Channel below them (In same section)
* Parent section (1 section up)
* Main section (1st subsection of root)
* Children (All channels that are direct subsection of them)
* Successors (All channels that are recursively subsection of them)

Note that all these variables hold (for the last 2 sets of) instances of channels, not their cid
"""
from channel import Channel

# NB: This channel does not exist but is used by TS as the root for the channel tree
ROOT_CHANNEL_ID = 0


def init(ts, db):
    Channel.subscribe("edited_var_pid")
    Channel.subscribe("edited_var_channel_order")
    calculate_order_information()


# Recalculate when a channel's section gets edited
def on_channel_edited_var_pid(channel, ts, db):
    calculate_order_information()


# Recalculate when the order of a channel gets edited
def on_channel_edited_var_channel_order(channel, ts, db):
    calculate_order_information()


# (Re-)Calculate all the order information of all channels
def calculate_order_information():
    channels = Channel.channels

    # Initialize
    for channel in channels.values():
        channel.above = None
        channel.below = None
        channel.parent = None
        channel.main_section = None
        channel.children = list()
        channel.successors = set()
        channel.pos_in_section = -1

    # Fill directly findable values: above, below, parent
    for channel in Channel.channels.values():
        if channel.channel_order != ROOT_CHANNEL_ID:
            channel.above = channels[channel.channel_order]
            channel.above.below = channel
        if channel.pid != ROOT_CHANNEL_ID:
            channel.parent = channels[channel.pid]

    # Fill recursive values: main section, successors
    for channel in Channel.channels.values():
        recurse_channel = channel.parent
        while recurse_channel is not None:
            recurse_channel.successors.add(channel)
            if recurse_channel.parent is None:
                channel.main_section = recurse_channel
            recurse_channel = recurse_channel.parent

    # Fill positions in section and children
    for channel in Channel.channels.values():
        if channel.above is None:
            pos = 0
            walk_channel = channel
            while walk_channel is not None:
                walk_channel.pos_in_section = pos
                if walk_channel.parent is not None:
                    walk_channel.parent.children.append(walk_channel)
                pos += 1
                walk_channel = walk_channel.below

