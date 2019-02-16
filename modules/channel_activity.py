"""
Logs the activities of channels per hour
"""
from client import Client
from settings import Settings
import time

Settings.load_settings({"channel_activity"})
settings = Settings.settings


def execute(ts, db):
    table = settings["channel_activity"]["db_table_name"]
    cid_column = settings["channel_activity"]["db_cid_column_name"]
    hour_column = settings["channel_activity"]["db_hour_column_name"]
    points_column = settings["channel_activity"]["db_points_column_name"]

    current_time = int(time.time())
    hour = int(current_time / 60 / 60)

    for client in Client.clients.values():
        if not client.online:
            continue
        cid = client.cid
        db.execute("INSERT INTO "+table+"("+cid_column+", "+hour_column+", "+points_column+") VALUES (" +
                   str(cid)+", "+str(hour)+", 1) ON DUPLICATE KEY UPDATE "+points_column+" = "+points_column+" + 1;")
