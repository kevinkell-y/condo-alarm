import yaml


class ConfigStore:
    def __init__(self, path="config.yaml"):
        self.path = path

    def load(self):
        with open(self.path, "r") as f:
            return yaml.safe_load(f)

    def save(self, config):
        with open(self.path, "w") as f:
            yaml.safe_dump(config, f, sort_keys=False)

    def update_siren_settings(self, volume=None, muted=None):
        config = self.load()

        if "siren_settings" not in config:
            config["siren_settings"] = {}

        if volume is not None:
            config["siren_settings"]["default_volume"] = str(volume).upper()

        if muted is not None:
            config["siren_settings"]["default_muted"] = bool(muted)

        self.save(config)