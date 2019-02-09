import traceback
import ts3
import MySQLdb

from channel import Channel
from client import Client
from settings import Settings

# Load the main settings and all the modules
from utility import debug

Settings.load_settings({"passwords", "modules", "general"})
settings = Settings.settings
Settings.load_modules(settings["active_modules"])
loaded_modules = Settings.loaded_modules
modules_ordered = list()

# These sets keep track of for which modules a certain action has already been performed
initialized_modules = set()
executed_modules = set()


# Main execution: Core of the program. What's called at the start
def main():
    with ts3.query.TS3Connection(settings["teamspeak"]["host"]) as ts:
        try:
            teamspeak_login(ts)
        except Exception as e:
            debug("TeamSpeak login failed:", repr(e), urgency=20, fatal=True, error=e)

        try:
            db = database_login()
        except Exception as e:
            debug("Database login failed:", repr(e), urgency=20, fatal=True, error=e)

        try:
            Client.init(ts)
        except Exception as e:
            debug("Client initialization failed:", repr(e), urgency=20, fatal=True, error=e)

        try:
            Channel.init(ts)
        except Exception as e:
            debug("Channel initialization failed:", repr(e), urgency=20, fatal=True, error=e)

        # Find an appropriate topological module order
        order_modules(loaded_modules)

        execute_modules_function("init", ts, db)
        execute_modules_function("execute", ts, db)
        execute_modules_function("finalize", ts, db)


# Log into the teamspeak query
def teamspeak_login(ts):
    try:
        ts.login(
            client_login_name=settings["teamspeak"]["username"],
            client_login_password=settings["teamspeak"]["password"]
        )
    except ts3.query.TS3QueryError as err:
        debug("TeamSpeak login failed:", repr(err.resp.error["msg"]), urgency=20, fatal=True, error=e)
        exit(1)
    ts.use(sid=settings["teamspeak"]["sid"])
    ts.clientupdate(client_nickname=settings["general"]["bot_name"])


# Log into the database
def database_login():
    dbconn = MySQLdb.connect(
        host=settings["db"]["host"],
        user=settings["db"]["username"],
        passwd=settings["db"]["password"],
        db=settings["db"]["database"]
    )
    dbconn.autocommit(True)
    db = dbconn.cursor(MySQLdb.cursors.DictCursor)
    return db


# Adds the given modules to the modules_ordered list such that for each module, its required modules are before it
def order_modules(module_names):
    for module_name in module_names:
        if module_name not in modules_ordered:
            module = loaded_modules[module_name]
            if hasattr(module, "required_modules"):
                order_modules(module.required_modules)
            modules_ordered.append(module_name)


# Executes one function on all loaded modules in specified order (if it has that function)
def execute_modules_function(function_name, ts, db, reverse=False):
    order = modules_ordered
    if reverse:
        order = reversed(order)
    for module_name in order:
        module = loaded_modules[module_name]
        if hasattr(module, function_name):
            function = getattr(module, function_name)
            try:
                function(ts, db)
            except Exception as e:
                debug("An exception occurred during execution of `" + function_name + "` on module `" + module_name + "`:", traceback.format_exc(), urgency=20, fatal=True, error=e)


# Function called at the end of all executions
def finalize(ts, db):
    db.close()


main()
