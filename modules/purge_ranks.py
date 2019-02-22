"""
This module adds functionality to purge server and channels ranks from people
It uses the do_purge_ranks client subscription to fire
"""
from client import Client
from settings import Settings
from utility import debug

required_settings = {"purge_ranks"}


# Subscribe to the do_purge_ranks action and check to make sure not both whitelist and blacklist are on
def init(ts, db):
    whitelist_enabled = Settings.settings["purge_ranks"]["whitelist_enabled"]
    blacklist_enabled = Settings.settings["purge_ranks"]["blacklist_enabled"]
    if whitelist_enabled and blacklist_enabled:
        # Both whitelist and blacklist enabled. Makes no sense
        debug("Both whitelist and blacklist are enabled for purging ranks. Removing as many ranks as I can.", urgency=10)
    if whitelist_enabled or blacklist_enabled:
        Client.subscribe("do_purge_ranks")


# Remove the client from channel- and server-groups according to the whitelist & blacklist settings
def on_client_do_purge_ranks(client, ts, db):
    default_channel_rank = Settings.settings["purge_ranks"]["default_channel_rank"]
    whitelist_enabled = Settings.settings["purge_ranks"]["whitelist_enabled"]
    blacklist_enabled = Settings.settings["purge_ranks"]["blacklist_enabled"]
    servergroups_whitelist = Settings.settings["purge_ranks"]["servergroups_whitelist"]
    servergroups_blacklist = Settings.settings["purge_ranks"]["servergroups_blacklist"]
    channelgroups_whitelist = Settings.settings["purge_ranks"]["channelgroups_whitelist"]
    channelgroups_blacklist = Settings.settings["purge_ranks"]["channelgroups_blacklist"]

    for servergroup in client.servergroups.copy():
        if (whitelist_enabled and servergroup not in servergroups_whitelist) \
                or (blacklist_enabled and servergroup in servergroups_blacklist):
            # Remove server groups
            ts.servergroupdelclient(sgid=servergroup, cldbid=client.cldbid)
            client.servergroups.remove(servergroup)
            client.action_executed("ranks_changed", ts, db)
            client.action_executed("rank_removed", ts, db)

    cgid = client.client_channel_group_id
    if (whitelist_enabled and cgid not in channelgroups_whitelist) \
            or (blacklist_enabled and cgid in channelgroups_blacklist):
        # Remove channel group
        ts.setclientchannelgroup(cgid=default_channel_rank, cldbid=client.cldbid, cid=client.cid)
        client.client_channel_group_id = default_channel_rank
        client.action_executed("channel_rank_changed", ts, db)
