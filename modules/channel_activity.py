"""
Logs the activities of channels per hour
Also adds a function to the channel class that lets you get the activity of a channel
"""
import decimal
import time
from channel import Channel
from client import Client
from settings import Settings

Settings.load_settings({"channel_activity"})
settings = Settings.settings

table = settings["channel_activity"]["db_table_name"]
cid_column = settings["channel_activity"]["db_cid_column_name"]
hour_column = settings["channel_activity"]["db_hour_column_name"]
points_column = settings["channel_activity"]["db_points_column_name"]


def init(ts, db):

    # Returns the activity logged in a channel from min_hour (incl) and stores it in a dict activity (key = min_hour)
    def get_activity(self, min_hour, db):
        if not hasattr(self, "activity"):
            self.activity = dict()
        if min_hour not in self.activity:
            cid = self.cid
            query = "SELECT SUM("+points_column+") AS activity FROM "+table+" WHERE "+cid_column+" = "+str(cid) + \
                          " AND "+hour_column+" >= "+str(min_hour)+";"
            db.execute(query)

            # Returns 1 row containing the activity score (as a decimal.Decimal), or None if no score found
            db_activity = db.fetchone()["activity"]
            if isinstance(db_activity, (int, decimal.Decimal)):
                self.activity[min_hour] = int(db_activity)
            else:
                self.activity[min_hour] = 0

        return self.activity[min_hour]

    # Add the above method to the Client class
    setattr(Channel, "get_activity", get_activity)


def execute(ts, db):
    current_time = int(time.time())
    hour = int(current_time / 60 / 60)

    for client in Client.clients.values():
        if not client.online:
            continue
        cid = client.cid
        db.execute("INSERT INTO "+table+"("+cid_column+", "+hour_column+", "+points_column+") VALUES (" +
                   str(cid)+", "+str(hour)+", 1) ON DUPLICATE KEY UPDATE "+points_column+" = "+points_column+" + 1;")
