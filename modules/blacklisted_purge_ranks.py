"""
Purges ranks of blacklisted players
"""
from client import Client

required_modules = {"blacklist", "purge_ranks"}


# Give or remove the blacklist server rank accordingly
def init(ts, db):
    for client in Client.clients.values():
        if client.is_verified:
            if client.blacklisted:
                client.action_executed("do_purge_ranks", ts, db)
