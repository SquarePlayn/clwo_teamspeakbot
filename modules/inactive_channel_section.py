"""
Moves channels from between two sections depending on whether they are recently active or not
If the sort_channels module is active, it takes into account sorting when swapping to different section
"""
import time

from channel import Channel
from settings import Settings

required_modules = {"channel_activity", "channel_order_information"}
Settings.load_settings({"channel_archived_section", "channel_freeze"})
settings = Settings.settings


def init(ts, db):

    # Return whether a channel is deemed active or not (= achievable)
    def is_active(self, db):
        current_hour = int(time.time() / 60 / 60)
        min_hour = current_hour - settings["channel_archived_section"]["hours_to_consider"]

        activity = self.get_activity(min_hour, db)
        if settings["channel_archived_section"]["include_subchannel_activity"]:
            for subchannel in self.successors:
                activity += subchannel.get_activity(min_hour, db)

        if activity >= settings["channel_archived_section"]["min_activity_for_active"]:
            return True
        elif settings["channel_archived_section"]["active_if_people_in_channel"] and len(self.clients) > 0:
            return True
        else:
            return False

    # Enable the above function on all channels
    setattr(Channel, "is_active", is_active)


def execute(ts, db):
    channels = Channel.channels

    active_section = channels[settings["channel_archived_section"]["active_section"]]
    archived_section = channels[settings["channel_archived_section"]["archived_section"]]

    # Move inactive channels in active section to archived section
    for channel in active_section.children:
        if not channel.is_active(db):
            insert_channel_in_section(channel, archived_section, ts, db)

    # Move active channels in archived section to active section
    for channel in archived_section.children:
        if channel.is_active(db):
            insert_channel_in_section(channel, active_section, ts, db)


# Insert a channel into a section. Defaults to top, unless sorting is enabled
def insert_channel_in_section(channel, section, ts, db):
    frozen_channels = settings["channel_freeze"]

    # Do not move frozen channels
    if channel.cid in frozen_channels:
        return

    # Insert in section (move to other section)
    underneath_channel_cid = 0
    if "sort_channels" in Settings.loaded_modules:
        for subchannel in section.children:
            if subchannel.cid in frozen_channels \
                    or subchannel.get_sorting_activity(db) >= channel.get_sorting_activity(db):
                underneath_channel_cid = subchannel.cid
            else:
                break
    channel.move_channel(section.cid, underneath_channel_cid, ts, db)




