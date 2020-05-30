"""
This module detects whether people are blacklisted and gives them the rank accordingly
"""
import requests

from client import Client
from settings import Settings

required_settings = {"gameserver_staff"}
required_modules = {"steam_verification"}


# Check and store for all clients what gameserver staff ranks they have
# If they are, store their staff info for all servers they are staff on
def init(ts, db):
    gameserver_settings = Settings.settings["gameserver_staff"]

    # Get the staff API data
    gameserver_staff_api_data = requests.get(gameserver_settings["api"])
    if gameserver_staff_api_data.status_code < 200 or 299 < gameserver_staff_api_data.status_code:
        raise Exception("Gameserver staff API not available")
    gameserver_staff_data = gameserver_staff_api_data.json()

    if "results" not in gameserver_staff_data.keys():
        raise Exception(
            "GameServer Staff API response has no key for 'data'. Total data: " + str(gameserver_staff_data))
    if gameserver_staff_data["pagination"]["total_results"] > gameserver_staff_data["pagination"]["MaxPerPage"]:
        raise Exception("MaxPerPage of GameServer Staff API request not high enough to fetch all data.")

    for client in Client.clients.values():
        client.gameserver_staff_ranks = dict()
        if client.is_verified:
            # Loop over all verified clients

            for gameserver_staff_entry in gameserver_staff_data["data"]:
                if gameserver_staff_entry["AccountID"] == client.accountID:
                    client.gameserver_staff_ranks[gameserver_staff_entry["ServerID"]] = gameserver_staff_entry


# Give or remove the gameserver staff ranks accordingly
def execute(ts, db):
    gameserver_staff_group_ids = Settings.settings["gameserver_staff"]["group_ids"]
    for client in Client.clients.values():
        client.has_ts_ingame_staff_rank = False
        # Update their staff ranks
        for gameserver_staff_server_id in gameserver_staff_group_ids.keys():
            teamspeak_group_id = gameserver_staff_group_ids[gameserver_staff_server_id]
            if int(gameserver_staff_server_id) in client.gameserver_staff_ranks.keys():
                # This person is staff on this server, ensure he has the TeamSpeak rank
                client.has_ts_ingame_staff_rank = True
                if teamspeak_group_id not in client.servergroups:
                    ts.servergroupaddclient(sgid=teamspeak_group_id, cldbid=client.cldbid)
                    client.servergroups.add(teamspeak_group_id)
                    client.action_executed("staff_rank_changed", ts, db)
                    client.action_executed("staff_rank_added", ts, db)
            else:
                # This person is not staff on this server, ensure he does not have the TeamSpeak rank
                if teamspeak_group_id in client.servergroups:
                    ts.servergroupdelclient(sgid=teamspeak_group_id, cldbid=client.cldbid)
                    client.servergroups.remove(teamspeak_group_id)
                    client.action_executed("staff_rank_changed", ts, db)
                    client.action_executed("staff_rank_removed", ts, db)

        # If they have a TS staff rank, ensure they do not have ranks that staff can't have anymore
        if client.has_ts_ingame_staff_rank:
            for teamspeak_group_id in Settings.settings["gameserver_staff"]["ranks_staff_cant_have"]:
                if teamspeak_group_id in client.servergroups:
                    ts.servergroupdelclient(sgid=teamspeak_group_id, cldbid=client.cldbid)
                    client.servergroups.remove(teamspeak_group_id)
