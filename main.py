import traceback
import ts3
import ts3.definitions
import MySQLdb

from channel import Channel
from client import Client
from settings import Settings
from utility import debug

USERNAME_TAKEN_ERROR_ID = 513


# Load the main settings and all the modules
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
            debug("TeamSpeak login failed:", traceback.format_exc(), urgency=20, fatal=True, error=e)

        try:
            db = database_login()
        except Exception as e:
            debug("Database login failed:", traceback.format_exc(), urgency=20, fatal=True, error=e)

        try:
            Channel.init(ts)
        except Exception as e:
            debug("Channel initialization failed:", traceback.format_exc(), urgency=20, fatal=True, error=e)

        try:
            Client.init(ts)
        except Exception as e:
            debug("Client initialization failed:", traceback.format_exc(), urgency=20, fatal=True, error=e)

        try:
            teamspeak_set_name(ts)
        except Exception as e:
            debug("Bot name setting failed:", traceback.format_exc(), urgency=10, fatal=False, error=e)

        # Find an appropriate topological module order
        order_modules(loaded_modules)

        execute_modules_function("init", ts, db)
        execute_modules_function("execute", ts, db)
        execute_modules_function("finalize", ts, db)

        finalize_main(ts, db)


# Log into the teamspeak query
def teamspeak_login(ts):
    try:
        ts.login(
            client_login_name=settings["teamspeak"]["username"],
            client_login_password=settings["teamspeak"]["password"]
        )
    except ts3.query.TS3QueryError as err:
        debug("TeamSpeak login failed:", repr(err.resp.error["msg"]), urgency=20, fatal=True, error=err)
        exit(1)
    ts.use(sid=settings["teamspeak"]["sid"])


# Set the desired TeamSpeak name for the Bot
# If the name is taken, that person is kicked
def teamspeak_set_name(ts):
    name = settings["general"]["bot_name"]
    try:
        ts.clientupdate(client_nickname=name)
    except ts3.query.TS3QueryError as error:
        if error.resp.error["id"] == str(USERNAME_TAKEN_ERROR_ID):
            debug("Could not claim name `" + name + "` because someone else took it", urgency=10, fatal=False)
            for client in Client.clients.values():
                if client.client_nickname == name:
                    debug("Clid "+str(client.clid)+", steamid64 "+client.client_description+" was the culprit, kicked!", urgency=10, fatal=False)
                    msg = "Please change your name"
                    ts.clientkick(clid=client.clid, reasonid=ts3.definitions.ReasonIdentifier.KICK_SERVER, reasonmsg=msg)
                    ts.clientupdate(client_nickname=name)
                    return
        else:
            raise error


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
        if module_name not in loaded_modules:
            continue
        module = loaded_modules[module_name]
        if hasattr(module, function_name):
            function = getattr(module, function_name)
            try:
                function(ts, db)
            except Exception as e:
                unload_module(module_name)
                debug("An exception occurred during execution of `" + function_name + "` on module `" + module_name + "`:", traceback.format_exc(), urgency=10, fatal=False, error=e)


# Recursively unload a module and the modules that depend on it to prevent them from running
def unload_module(module_name):
    # Unload the module
    loaded_modules.pop(module_name)
    modules_ordered.remove(module_name)

    # Find which modules depend on the module to be removed
    depending_modules = set()
    for check_module_name in loaded_modules:
        check_module = loaded_modules[check_module_name]
        if hasattr(check_module, "required_modules"):
            if module_name in check_module.required_modules:
                depending_modules.add(check_module_name)

    # Unload the depending modules and recurse
    for depending_module in depending_modules:
        unload_module(depending_module)


# Function called at the end of all executions
def finalize_main(ts, db):
    db.close()


main()
