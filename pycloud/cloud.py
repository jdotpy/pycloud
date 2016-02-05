from quickconfig import Configuration

class ImproperlyConfigured(ValueError):
    pass

class PyCloud():
    required_settings = ('name',)

    def __init__(self, config):
        if not isinstance(config, Configuration):
            config = Configuration(config)
        self.config = config
        self._validation()

    def _validation(self):
        for setting in self.required_settings:
            if self.config.get(setting) is None:
                raise ImproperlyConfigured('Improperly configured: Missing {} setting'.format(setting))
