"""
Purges ranks of non-verified players
"""
from client import Client

required_modules = {"steam_verification", "purge_ranks"}


# Purge ranks of non-verified players
def execute(ts, db):
    for client in Client.clients.values():
        if not client.is_verified:
            client.action_executed("do_purge_ranks", ts, db)
