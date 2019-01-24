import ts3
import MySQLdb

from channel import Channel
from client import Client
from settings import Settings

# Load the main settings and all the modules
Settings.load_settings({"passwords", "modules", "general"})
settings = Settings.settings
Settings.load_modules(settings["active_modules"])
loaded_modules = Settings.loaded_modules

# These sets keep track of for which modules a certain action has already been performed
initialized_modules = set()
executed_modules = set()


# Main execution: Core of the program. What's called at the start
def main():
    with ts3.query.TS3Connection(settings["teamspeak"]["host"]) as ts:
        teamspeak_login(ts)
        db = database_login()
        Client.init(ts)
        Channel.init(ts)

        # Initialize all the loaded modules
        for module_name in loaded_modules:
            initialize_module(module_name, ts, db)

        # Execute all the loaded modules
        for module_name in loaded_modules:
            execute_module(module_name, ts, db)


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
    ts.use(sid=settings["teamspeak"]["sid"])
    ts.clientupdate(client_nickname=settings["general"]["bot_name"])


# Log into the database
def database_login():
    try:
        dbconn = MySQLdb.connect(
            host=settings["db"]["host"],
            user=settings["db"]["username"],
            passwd=settings["db"]["password"],
            db=settings["db"]["database"]
        )
    except:
        print("Error connecting to MySQL Database")
        exit(1)
        return
    dbconn.autocommit(True)
    db = dbconn.cursor()
    return db


# Initializes a module. If the module has other required modules, those are initialized first
def initialize_module(module_name, ts, db):
    if module_name not in initialized_modules:
        module = loaded_modules[module_name]
        if hasattr(module, "required_modules"):
            for required_module_name in module.required_modules:
                if required_module_name not in initialized_modules:
                    initialize_module(required_module_name, db, ts)
        if hasattr(module, "init"):
            module.init(ts, db)
        initialized_modules.add(module_name)


# Executes a module. If the module has other required modules, those are executed first
def execute_module(module_name, ts, db):
    if module_name not in executed_modules:
        module = loaded_modules[module_name]
        if hasattr(module, "required_modules"):
            for required_module_name in module.required_modules:
                if required_module_name not in executed_modules:
                    execute_module(required_module_name, db, ts)
        if hasattr(module, "execute"):
            module.execute(ts, db)
        executed_modules.add(module_name)


# Function called at the end of all executions
def finalize(ts, db):
    db.close()


main()
