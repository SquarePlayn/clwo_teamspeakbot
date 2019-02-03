import inspect


# Stores all information about clients
from settings import Settings
from utility import set_type

Settings.load_settings({"client_variables"})


class Client:
    clients = dict()
    online_clients = set()
    subscriptions = dict()

    # Called when creating a new instance. Builds all instance's variables
    def __init__(self, ts, cldbid, online, clid=0):
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
        tsinfo = ts.clientinfo(clid=self.clid)[0]
        client_variables = Settings.settings["client_variables"]
        for var_name in client_variables:
            var_type = client_variables[var_name]
            setattr(self, var_name, set_type(tsinfo[var_name], var_type))

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
            None  # TODO: Create new client from cldbid
        return Client.clients[cldbid]

    # Allows a module to subscribe to a certain action being executed
    @staticmethod
    def subscribe(action):
        module = inspect.getmodule(inspect.stack()[1][0])
        if action not in Client.subscriptions:
            Client.subscriptions[action] = list()
        Client.subscriptions[action].append(module)
