import json


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
                loaded_module = __import__("modules." + module, fromlist=["modules"])
                if hasattr(loaded_module, "required_settings"):
                    Settings.load_settings(loaded_module.required_settings)
                Settings.loaded_modules[module] = loaded_module
                if hasattr(loaded_module, "required_modules"):
                    Settings.load_modules(loaded_module.required_modules)

    # Loads the given settings json files into the settings dictionary
    @staticmethod
    def load_settings(required_settings):
        for required_setting in required_settings:
            if required_setting not in Settings.loaded_settings:
                with open("conf/" + required_setting + ".json") as settings_file:
                    Settings.settings.update(json.load(settings_file))
                    Settings.loaded_settings.add(required_setting)
