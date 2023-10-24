class Config():

    def __init__(self, config):
        self.token = config["token"]
        self.prefix = config["prefix"]
        self.is_beta = config["is_beta"]
        self.guild_data = {}
        self.convert_dict_to_attribs(config["guild_data"], self.guild_data)

    def convert_dict_to_attribs(self, loaded_dict, attribs, append=None):
        for key, value in loaded_dict.items():
            if type(value) is dict:
                setattr(self, key, {})
                attribs[key] = getattr(self, key)
                self.convert_dict_to_attribs(value, getattr(self, key), append=("_channel" if key in ("channels", "log_channels") else "_role" if key == "roles" else None))
            else:
                if append:
                    key += append
                setattr(self, key, value)
                attribs[key] = getattr(self, key)
