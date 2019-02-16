""" Provider Manager """

from abstract.providers import AccuProvider, RP5_Provider, SinoptikProvider
import abstract.abstract


class ProviderManager(abstract.abstract.Manager):
    """ Container for providers """

    def __init__(self):
        self._providers = {}
        self._load_providers()

    def _load_providers(self):
        """ Loads existing providers """

        for provider in [AccuProvider, RP5_Provider, SinoptikProvider]:
            self.add(provider.title, provider)

    def add(self, name, provider):
        """ Add provider
            :param name: provider title
            :param provider: provider instance
        """

        self._providers[name] = provider

    def get(self, name):
        """ Get provider by name
            :param name: provider name
            :return: provider instance
        """

        return self._providers.get(name, None)

    def get_list(self):
        """ Gets list of providers
            :return: providers list
            :rtype: list
        """

        return self._providers.keys()
