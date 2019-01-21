import ts3, json

settings = dict()
with open('conf/passwords.json') as passwordsfile:
    settings.update(json.load(passwordsfile))

with ts3.query.TS3Connection(settings["teamspeak"]["host"]) as ts3conn:
    # Note, that the client will wait for the response and raise a
    # **TS3QueryError** if the error id of the response is not 0.
    try:
        ts3conn.login(
            client_login_name=settings["teamspeak"]["username"],
            client_login_password=settings["teamspeak"]["password"]
        )
    except ts3.query.TS3QueryError as err:
        print("Login failed:", err.resp.error["msg"])
        exit(1)

    ts3conn.use(sid=1)

    # Each query method will return a **TS3QueryResponse** instance,
    # with the response.
    resp = ts3conn.clientlist()
    print("Clients on the server:", resp.parsed)