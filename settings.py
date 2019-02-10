import json
import os


# Takes care of loading the settings and modules
class Settings:
    loaded_modules = dict()
    loaded_settings = set()
    settings = dict()

    # Loads modules by loading their settings and recursively loading its required modules
    @staticmethod
    def load_modules(modules):
        for module in modules:
            if module not in Settings.loaded_modules:
                try:
                    loaded_module = __import__("modules." + module, fromlist=["modules"])
                    if hasattr(loaded_module, "required_settings"):
                        Settings.load_settings(loaded_module.required_settings)
                    Settings.loaded_modules[module] = loaded_module
                    if hasattr(loaded_module, "required_modules"):
                        Settings.load_modules(loaded_module.required_modules)
                except Exception as e:
                    debug("Exception while loading module "+module+":", repr(e), urgency=20, fatal=True, error=e)

    # Loads the given settings json files into the settings dictionary
    @staticmethod
    def load_settings(required_settings):
        path = os.path.dirname(os.path.realpath(__file__))
        for required_setting in required_settings:
            if required_setting not in Settings.loaded_settings:
                try:
                    with open(path+"/conf/" + required_setting + ".json") as settings_file:
                        data = json.load(settings_file)
                        for key in data:
                            if key in Settings.settings and (type(data[key]) == dict or type(data[key]) == list):
                                Settings.settings[key].update(data[key])
                            else:
                                Settings.settings[key] = data[key]
                        Settings.loaded_settings.add(required_setting)
                except Exception as e:
                    debug("Exception while loading settings "+required_setting+":", repr(e), urgency=20, fatal=True, error=e)


# Import at the bottom to avoid cyclic importing before the Settings class is declared
from utility import debug

