"""
A module that ensures verification of TeamSpeak users via Steam.
It requires a simple steam login website and accompanying database
It will send a login link every minute.
Verified users get a verified rank, non-verified users do not (actively removes the rank)
"""

import random
import string
import ts3.definitions

from client import Client
from settings import Settings
from utility import escape_string

required_settings = {"steam_verification"}
settings = Settings.settings


def init(ts, db):
    sv_settings = settings["steam_verification"]
    Client.steam_clients = dict()
    clients = Client.clients
    steam_clients = Client.steam_clients

    for client in clients.values():
        query = "SELECT * FROM " + sv_settings["table_name"] + " WHERE cldbid = " + escape_string(
            str(client.cldbid)) + ";"
        db.execute(query)
        if db.rowcount <= 0:
            # There is no verification data about this user
            # Generate a new code and insert an entry into the table
            client.is_verified = False
            client.verification_code = generate_code()
            query = "INSERT INTO " + sv_settings["table_name"] + " (" + sv_settings["cldbid_db_field_name"] + ", " + \
                    sv_settings["verification_code_db_field_name"] + ") VALUES ('" + escape_string(
                str(client.cldbid)) + "', '" + escape_string(client.verification_code) + "');"
            db.execute(query)
        else:
            # There is already verificatoin data about this user
            # Get it and save it in the client's variables
            db_verification_info = db.fetchone()
            client.is_verified = db_verification_info[sv_settings["steamid64_db_field_name"]] is not None
            if client.is_verified:
                client.steamid64 = db_verification_info[sv_settings["steamid64_db_field_name"]]
                steam_clients[client.steamid64] = client
            client.verification_code = db_verification_info[sv_settings["verification_code_db_field_name"]]


def execute(ts, db):
    sv_settings = settings["steam_verification"]
    verification_group_id = sv_settings["verified_group_id"]
    clients = Client.clients
    for client in clients.values():
        has_verified_rank = verification_group_id in client.servergroups

        # If verified and not verified rank:
        if client.is_verified and not has_verified_rank:
            # Give verified rank
            ts.servergroupaddclient(
                sgid=verification_group_id,
                cldbid=client.cldbid
            )
            client.action_executed("verification_rank_changed", ts, db)
            client.action_executed("verification_rank_added", ts, db)
            has_verified_rank = True

        # If not verified but does have rank:
        if not client.is_verified and has_verified_rank:
            # Remove verify rank
            ts.servergroupdelclient(
                sgid=verification_group_id,
                cldbid=client.cldbid
            )
            client.action_executed("verification_rank_changed", ts, db)
            client.action_executed("verification_rank_removed", ts, db)
            has_verified_rank = False

        # If not verified:
        if not client.is_verified and client.confirm_online(ts):
            # Send verification message
            link = sv_settings["base_link"] + "?" + sv_settings["cldbid_web_field_name"] + "=" + str(client.cldbid) \
                   + "&" + sv_settings["verification_code_web_field_name"] + "=" + client.verification_code
            message = sv_settings["message"].replace("{link}", link)
            ts.sendtextmessage(
                targetmode=ts3.definitions.TextMessageTargetMode.CLIENT,
                target=client.clid,
                msg=message
            )


# Generates a random string of specified length consisting of {a-z,A-Z,0-9}
def generate_code():
    code = ""
    for i in range(settings["steam_verification"]["code_length"]):
        code += random.choice(string.ascii_letters)
    return code
