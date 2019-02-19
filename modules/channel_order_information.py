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
    channels = Channel.channels

    # Initialize
    for channel in channels.values():
        setattr(channel, "above", None)
        setattr(channel, "below", None)
        setattr(channel, "parent", None)
        setattr(channel, "main_section", None)
        setattr(channel, "children", set())
        setattr(channel, "successors", set())

    # Fill directly findable values
    for channel in Channel.channels.values():
        if channel.channel_order != ROOT_CHANNEL_ID:
            channel.above = channels[channel.channel_order]
            channel.above.below = channel
        if channel.pid != ROOT_CHANNEL_ID:
            channel.parent = channels[channel.pid]
            channel.parent.children.add(channel)

    # Fill recursive values
    for channel in Channel.channels.values():
        recurse_channel = channel.parent
        while recurse_channel is not None:
            recurse_channel.successors.add(channel)
            if recurse_channel.parent is None:
                channel.main_section = recurse_channel
            recurse_channel = recurse_channel.parent
