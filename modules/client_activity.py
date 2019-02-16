"""
Logs the activities of clients in online minutes in an hour
"""
from client import Client
from settings import Settings
import time

Settings.load_settings({"client_activity"})
settings = Settings.settings


def execute(ts, db):
    table = settings["client_activity"]["db_table_name"]
    cldbid_column = settings["client_activity"]["db_cldbid_column_name"]
    hour_column = settings["client_activity"]["db_hour_column_name"]
    points_column = settings["client_activity"]["db_points_column_name"]

    current_time = int(time.time())
    hour = int(current_time / 60 / 60)

    for client in Client.clients.values():
        if not client.online:
            continue
        cldbid = client.cldbid
        db.execute("INSERT INTO "+table+"("+cldbid_column+", "+hour_column+", "+points_column+") VALUES (" +
                   str(cldbid)+", "+str(hour)+", 1) ON DUPLICATE KEY UPDATE "+points_column+" = "+points_column+" + 1;")
