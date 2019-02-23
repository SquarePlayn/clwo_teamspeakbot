"""
Associate user's channels with their steamid64's and let people create and find their own channel by steamid64
Only one channel is allowed per steamid64
"""
import time

from channel import Channel
from client import Client
from settings import Settings

required_modules = {"steam_verification", "channel_order_information"}
Settings.load_settings({"channel_steamlink", "channel_ranks"})
steamlink_settings = Settings.settings["channel_steamlink"]

table = steamlink_settings["db_table"]
cid_column = steamlink_settings["db_cid_column_name"]
steamid_column = steamlink_settings["db_steam64_column_name"]
request_date_column = steamlink_settings["db_request_date_column_name"]


def init(ts, db):
    Channel.steam_channels = dict()
    channels = Channel.channels
    steam_channels = Channel.steam_channels
    steam_clients = Client.steam_clients

    # On each steam-claimed channel that still exists,
    # set the appropriate channel and client(s) values
    db.execute("SELECT * FROM "+table+";")
    for channel_row in db.fetchall():
        cid = channel_row[cid_column]
        steamid64 = channel_row[steamid_column]
        request_date = channel_row[request_date_column]
        if cid in channels:
            channel = channels[cid]
            steam_channels[steamid64] = channel
            channel.owner_steamid64 = steamid64
            channel.request_date = request_date
            if steamid64 in steam_clients:
                for steam_client in steam_clients[steamid64]:
                    steam_client.user_channel = channel


def execute(ts, db):
    claim_channel_handling(ts, db)
    give_channel_admins(ts, db)


# Handles all the people that are in the claim-your-channel channel
def claim_channel_handling(ts, db):
    room_request_cid = steamlink_settings["room_request_cid"]
    if room_request_cid not in Channel.channels:
        return
    claim_channel = Channel.channels[room_request_cid]

    for client_id in claim_channel.clients.copy():
        client = Client.clients[client_id]
        if not client.confirm_online(ts):
            continue
        if not hasattr(client, "user_channel"):
            # Does not have a channel  on the server yet: Make one if verified and didn't have one earlier
            if not client.is_verified:
                client.message(steamlink_settings["nonverified_message"], ts)
            else:
                # Check DB whether there is a channel in the DB already (e.g. got their channel removed)
                query = "SELECT * FROM "+table+" WHERE "+steamid_column+" = '"+str(client.steamid64)+"';"
                db.execute(query)
                if db.rowcount > 0:
                    client.message(steamlink_settings["channel_previously_removed_message"], ts)
                    continue

                # Get information needed to make channel
                section = Channel.channels[steamlink_settings["put_new_rooms_in_section"]]
                if len(section.children) == 0:
                    bottom_channel_id = 0
                else:
                    bottom_channel_id = section.children[len(section.children)-1].cid
                base_name = client.client_nickname+"'s Room"
                name = base_name

                # Make sure the name is not yet taken: Append random letters if it is
                append_number = 2
                used_names = {channel.channel_name for channel in section.children}
                while name in used_names:
                    name = base_name + " " + str(append_number)
                    append_number += 1

                # Create a channel for them and put it in section below bottom_channel
                parameters = steamlink_settings["channel_settings"]
                channel = Channel.create_channel(name, ts, db, options=parameters)
                channel.move_channel(section.cid, bottom_channel_id, ts, db)

                # Insert it into the database
                current_time = int(time.time())
                query = "INSERT INTO "+table+"("+cid_column+", "+steamid_column+", "+request_date_column+") " \
                        "VALUES ("+str(channel.cid)+", "+str(client.steamid64)+", "+str(current_time)+");"
                db.execute(query)

                # Assign user their channel in internal model and vice versa
                client.user_channel = channel
                Channel.steam_channels[client.steamid64] = channel
                channel.owner_steamid64 = client.steamid64

        # If they have a channel, put them in it
        if hasattr(client, "user_channel"):
            # Move client to their channel
            channel = client.user_channel
            client.move(channel.cid, ts, db)


# Gives channel admin to the people that are in their own channel (by steamid64)
def give_channel_admins(ts, db):
    channel_admin_rank_id = Settings.settings["channel_ranks"]["channel_admin_rank_id"]
    for client in Client.clients.values():
        if hasattr(client, "user_channel"):     # Has a channel of their own
            if client.user_channel.cid == client.cid:   # In their own channel
                if channel_admin_rank_id != client.client_channel_group_id:     # Not channel admin
                    if client.confirm_online(ts):
                        ts.setclientchannelgroup(cgid=channel_admin_rank_id, cldbid=client.cldbid, cid=client.user_channel.cid)


