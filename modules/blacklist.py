"""
This module detects whether people are blacklisted and gives them the rank accordingly
"""
import requests

from client import Client
from settings import Settings

required_settings = {"blacklist"}
required_modules = {"steam_verification"}


# Check and store for all clients whether they are blacklisted.
# If they are, store their blacklist_info as well
def init(ts, db):
    bl_settings = Settings.settings["blacklist"]
    for client in Client.clients.values():
        if client.is_verified:
            # Loop over all verified clients
            blacklist_data = requests.get(bl_settings["api"].replace("{steamid64}", str(client.steamid64))).json()
            client.blacklisted = False
            if blacklist_data["results"] > 0:
                for blacklist_id in blacklist_data["data"]:
                    # API sometimes returns dictionary, sometimes list :/
                    if isinstance(blacklist_id, str):
                        blacklist = blacklist_data["data"][blacklist_id]
                    else:
                        blacklist = blacklist_id
                    if int(blacklist["Enabled"]) == 1:
                        if int(blacklist["Perm"]) == 1 or int(blacklist["ExpiresInMinutes"]) > 0:
                            client.blacklisted = True
                            client.blacklist_info = blacklist
                            break


# Give or remove the blacklist server rank accordingly
def execute(ts, db):
    bl_group_id = Settings.settings["blacklist"]["blacklisted_group_id"]
    for client in Client.clients.values():
        if client.blacklisted and bl_group_id not in client.servergroups:
            # Blacklisted person without blacklist server rank. Give them the server rank
            ts.servergroupaddclient(sgid=bl_group_id, cldbid=client.cldbid)
            client.action_executed("blacklisted_rank_changed", ts, db)
            client.action_executed("blacklisted_rank_added", ts, db)

        if not client.blacklisted and bl_group_id in client.servergroups:
            # Not blacklisted but does have blacklist server rank. Take the rank away
            ts.servergroupdelclient(sgid=bl_group_id, cldbid=client.cldbid)
            client.action_executed("blacklisted_rank_changed", ts, db)
            client.action_executed("blacklisted_rank_removed", ts, db)
