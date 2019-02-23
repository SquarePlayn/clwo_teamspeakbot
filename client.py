import inspect
import ts3
import ts3.definitions

from channel import Channel
from settings import Settings
from utility import set_type, debug

Settings.load_settings({"client_variables"})

TS_INVALID_CLID_ERROR_ID = 512


# Stores all information about clients
class Client:
    clients = dict()
    online_clients = set()
    subscriptions = dict()

    # Called when creating a new instance. Builds all instance's variables
    def __init__(self, ts, cldbid, online, clid=0):
        self.servergroups = set()
        self.cldbid = cldbid
        self.online = online
        if online:
            self.clid = clid
            self.load_info(ts)

    # Executes a corresponding function on all subscribed modules
    def action_executed(self, action, ts, db):
        if action in Client.subscriptions:
            for module in Client.subscriptions[action]:
                function = getattr(module, "on_client_"+action)
                function(self, ts, db)

    # Query and save all default channel variables
    def load_info(self, ts):
        # General client info
        if self.confirm_online(ts):
            tsinfo = ts.clientinfo(clid=self.clid)[0]
            client_variables = Settings.settings["client_variables"]
            for var_name in client_variables:
                var_type = client_variables[var_name]
                setattr(self, var_name, set_type(tsinfo[var_name], var_type))
            Channel.channels[self.cid].clients.add(self.cldbid)  # Add itself to clients in channel it is in

        # Group data (only the group ids are stored)
        servergroups_data = ts.servergroupsbyclientid(cldbid=self.cldbid)
        for servergroup in servergroups_data:
            self.servergroups.add(int(servergroup["sgid"]))

    # Confirm / re-check whether this client is still online
    def confirm_online(self, ts):
        if self.online:
            try:
                ts.clientgetuidfromclid(clid=self.clid)
            except ts3.query.TS3QueryError as e:
                if e.resp.error["id"] != str(TS_INVALID_CLID_ERROR_ID):
                    raise e
                else:
                    debug("Checked client with clid "+str(self.clid)+" which is not online.", urgency=1)
                    self.online = False
                    clients_copy = Client.clients.copy()
                    clients_copy.pop(self.cldbid, None)
                    Client.clients = clients_copy
        return self.online

    # Send the client a message
    def message(self, msg, ts):
        if not self.confirm_online(ts):
            return
        ts.sendtextmessage(
            targetmode=ts3.definitions.TextMessageTargetMode.CLIENT,
            target=self.clid,
            msg=msg
        )

    # Move the client to a channel
    def move(self, cid, ts, db):
        if not self.confirm_online(ts):
            return
        if self.cid == cid:
            debug("Tried moving client "+str(self.cldbid)+" to channel "+str(cid)+" but already in that channel")
            return
        ts.clientmove(cid=cid, clid=self.clid)
        Channel.channels[self.cid].clients.remove(self.cldbid)
        Channel.channels[self.cid].action_executed("clients_changed", ts, db)
        self.load_info(ts)
        Channel.channels[cid].clients.add(self.cldbid)
        Channel.channels[cid].action_executed("clients_changed", ts, db)

    # Called initially. Builds the main structure
    @staticmethod
    def init(ts):
        clients_query = ts.clientlist()
        for client in clients_query:
            cldbid = int(client["client_database_id"])
            clid = int(client["clid"])
            Client.clients[cldbid] = Client(ts, cldbid, online=True, clid=clid)
            Client.online_clients.add(cldbid)

    # Get a client by its cldbid
    @staticmethod
    def get_client(cldbid, ts):
        if cldbid not in Client.clients:
            pass  # TODO: Create new client from cldbid
        return Client.clients[cldbid]

    # Allows a module to subscribe to a certain action being executed
    @staticmethod
    def subscribe(action):
        module = inspect.getmodule(inspect.stack()[1][0])
        if action not in Client.subscriptions:
            Client.subscriptions[action] = list()
        Client.subscriptions[action].append(module)
