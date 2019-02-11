import unittest

from abstract.providers import AccuProvider, RP5_Provider, SinoptikProvider
from managers.providermanager import ProviderManager

class FakeProvider():

    name = "FakeProvider"

class ProviderManagerTest (unittest.TestCase):
    """ Unit test for ProviderManager
    """

    def setUp(self):
        self.provider_manager = ProviderManager()

    def test_load_providers(self):
        """ Test loading existing providers
        """

        for provider in [AccuProvider, RP5_Provider, SinoptikProvider]:
            self.provider_manager.add(provider.title, provider)

        self.assertTrue(AccuProvider.title in self.provider_manager._providers.keys())
        self.assertEqual(len(self.provider_manager._providers), 3)

    def test_add(self):
        """ Test adding provider
        """
        self.provider_manager._providers[FakeProvider.name] = FakeProvider()

        self.assertEqual('FakeProvider',
                        self.provider_manager._providers['FakeProvider'].name)

    def test_get(self):
        """ Test getting provider by name
        """
        for item in [AccuProvider, RP5_Provider, SinoptikProvider]:
            provider = self.provider_manager._providers.get(item, None)
            self.assertFalse(provider, None)

    def get_list(self):
        """ Test getting a list of providers """

        providers_list = self._providers.keys()

        self.assertTrue(len(providers_list, 3))

if __name__ == "__main__":
    unittest.main()
