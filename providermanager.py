from providers import AccuProvider, RP5_Provider, SinoptikProvider

class ProviderManager:
    """ Imports providers from providers.py
    """

    def __init__(self):
        self._providers = {}
        self._load_providers()

    def _load_providers(self):
        """ Loads existing providers
        """

        for provider in [AccuProvider, RP5_Provider, SinoptikProvider]:
            self.add(provider.title, provider)

    def add(self, name, provider):
        """ Add provider
        """

        self._providers[name] = provider

    def get(self, name):
        """ Get provider by name
        """

        return self._providers.get(name, None)
