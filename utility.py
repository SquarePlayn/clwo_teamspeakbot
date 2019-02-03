# Includes functions that can be used by all modules for any purpose
from settings import Settings

Settings.load_settings({"general"})


# Prints a debug message when it is urgent or when debugging is on
def debug(message, urgency=0):
    if urgency > 0:
        print(message)
        return
    if Settings.settings["general"]["debug"]:
        print(message)


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
