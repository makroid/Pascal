import yaml

class Config:
    def __init__(self, config_file):
        with open(config_file, "r") as f:
            config_content = f.read()

        self.config = yaml.load(config_content, Loader=yaml.Loader)

        self.base_path = self.config["base_path"]