import ts3

from channel import Channel
from client import Client
from settings import Settings

Settings.load_settings({"passwords", "modules", "general"})
settings = Settings.settings


# Main execution: Core of the program. What's called at the start
def main():
    with ts3.query.TS3Connection(settings["teamspeak"]["host"]) as ts:
        teamspeak_login(ts)
        Client.init(ts)
        Channel.init(ts)

        # Execute all the activated modules
        for module_name in settings["active_modules"]:
            module = __import__("modules." + module_name, fromlist=["modules"])
            module.execute()


# Log into the teamspeak query
def teamspeak_login(ts):
    try:
        ts.login(
            client_login_name=settings["teamspeak"]["username"],
            client_login_password=settings["teamspeak"]["password"]
        )
    except ts3.query.TS3QueryError as err:
        print("Login failed:", err.resp.error["msg"])
        exit(1)
    ts.use(sid=1)


main()
