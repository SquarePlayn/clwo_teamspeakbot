"""
For channels that have an associated steam owner, their steamid64 is put in the topic
"""
from channel import Channel
from settings import Settings

required_modules = {"channel_steamlink"}
required_settings = {"channel_steamlink_topic"}


def execute(ts, db):
    for channel in Channel.steam_channels.values():
        expected_topic = Settings.settings["channel_steamlink"]["topic"]\
            .replace("{steamid64}", str(channel.owner_steamid64))
        if channel.channel_topic != expected_topic:
            channel.edit_channel({"channel_topic": expected_topic}, ts, db)

