import json


# Takes care of loading the settings
class Settings:
    loaded_settings = set()
    settings = dict()

    @staticmethod
    def load_settings(required_settings):
        for required_setting in required_settings:
            if required_setting not in Settings.loaded_settings:
                with open("conf/" + required_setting + ".json") as settings_file:
                    Settings.settings.update(json.load(settings_file))
                    Settings.loaded_settings.add(required_setting)
