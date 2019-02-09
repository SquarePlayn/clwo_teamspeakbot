# Includes functions that can be used by all modules for any purpose
import json
import requests

from settings import Settings

Settings.load_settings({"general", "slack"})


# Prints a debug message when it is urgent or when debugging is on
def debug(message, message_2="", urgency=0, fatal=False, error=None):
    if urgency > 0 or Settings.settings["general"]["debug"]:
        print(message)
    slack_urgency = Settings.settings["general"]["slack_error_reporting_min_urgency"]
    if 0 <= slack_urgency <= urgency:
        send_to_slack(message, message_2, inform_dev=True)

    if fatal:
        raise error


# Send a message to Slack
def send_to_slack(message, message_2="", inform_dev=False):
    url = Settings.settings["slack"]["hook"]
    channel = Settings.settings["slack"]["channel"]
    bot_name = Settings.settings["slack"]["bot_name"]
    icon_emoji = Settings.settings["slack"]["icon_emoji"]

    if inform_dev:
        dev_id = Settings.settings["slack"]["dev_member_id"]
        message = "<@" + str(dev_id) + "> " + message

    if message_2 != "":
        message = message + "\n>>>" + message_2
    else:
        message = ">" + message

    data = {
        'text': message,
        'channel': channel,
        'username': bot_name,
        'icon_emoji': icon_emoji,
        'link_names': 1
    }
    response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )


# Casts a variable to a given type.
# If var_type is a set/list, type_2 is the type of its entries
def set_type(var, var_type, type_2="str"):
    if var_type == "int":
        return int(var)
    elif var_type == "bool":
        return bool(var)
    elif var_type == "str":
        return str(var)
    elif var_type == "intlist":
        return set_type(var, "list", "int")
    elif var_type == "strlist":
        return set_type(var, "list", "str")
    elif var_type == "intdict":
        return set_type(var, "dict", "int")
    elif var_type == "strdict":
        return set_type(var, "dict", "str")
    elif var_type == "list":
        # Lists must be given comma separated
        lst = list()
        for list_var in var.split(','):
            lst.append(set_type(list_var, type_2))
        return lst
    elif var_type == "dict":
        # Dicts must be given as comma separated entries of key=value
        dct = dict()
        for dict_entry in var.split(','):
            if dict_entry != '':
                dict_split = dict_entry.split('=')
                dct[dict_split[0]] = set_type(dict_split[1], type_2)
                # Remove the '' entry for empty lists!!!
        return dct
    else:
        debug("Attempted to set type to unknown type " + str(var_type))
