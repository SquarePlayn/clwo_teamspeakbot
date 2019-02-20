"""
This module sets clients' first part of their descriptions to their steamid64
Also actively removes descriptions from non-verified clients
Relies on the steam_verification module
"""
from client import Client

required_modules = {"steam_verification"}


def execute(ts, db):
    for client in Client.clients.values():
        if not client.online:
            continue

        description = client.client_description

        # If verified and steamid64 not first part of description
        if client.is_verified and description[:len(str(client.steamid64))] != str(client.steamid64):
            # Set description to steamid64
            if client.confirm_online(ts):
                new_description = str(client.steamid64)
                ts.clientedit(clid=client.clid, client_description=new_description)
                client.client_description = new_description
                client.action_executed("description_edited", ts, db)

        # If not verified but does have a description
        if not client.is_verified and description != "":
            # Remove description
            if client.confirm_online(ts):
                ts.clientedit(clid=client.clid, client_description="")
                client.client_description = ""
                client.action_executed("description_edited", ts, db)
