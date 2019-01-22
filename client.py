# Stores all information about clients
class Client:
    clients = dict()
    online_clients = set()

    # Called when creating a new instance. Builds all instance's variables
    def __init__(self, cldbid, ts):
        self.cldbid = cldbid
        # TODO: Expand set of available variables

    # Called initially. Builds the main structure
    @staticmethod
    def init(ts):
        clients_query = ts.clientlist()
        for client in clients_query:
            cldbid = int(client["client_database_id"])
            Client.clients[cldbid] = Client(cldbid, ts)
            Client.online_clients.add(cldbid)

    # Get a client by its cldbid
    @staticmethod
    def get_client(cldbid, ts):
        if cldbid not in Client.clients:
            None  # TODO: Create new client from cldbid
        return Client.clients[cldbid]
