import unittest

from PyQt5 import QtCore

from buildnotifylib.config import Config, Preferences
from buildnotifylib.serverconfig import ServerConfig


class ConfigTest(unittest.TestCase):
    def setUp(self):
        q_settings = QtCore.QSettings("BuildNotifyTest", "BuildNotifyTest")
        q_settings.clear()
        self.config = Config(q_settings)

    def test_should_persist_user_project_excludes(self):
        self.config.set_project_excludes('https://github.com/anaynayak/buildnotify/cctray.xml',
                                         ['buildnotify::test-server'])
        self.assertEqual(['buildnotify::test-server'],
                         self.config.get_project_excludes('https://github.com/anaynayak/buildnotify/cctray.xml'))

    def test_should_persist_empty_user_project_excludes(self):
        self.config.set_project_excludes('https://github.com/anaynayak/buildnotify/cctray.xml', [])
        self.assertEqual([], self.config.get_project_excludes('https://github.com/anaynayak/buildnotify/cctray.xml'))

    def test_should_return_an_empty_list_if_unmapped(self):
        self.assertEqual([],
                         self.config.get_project_excludes('https://github.com/anaynayak/buildnotify/buildnotify.xml'))

    def test_should_store_server_preferences(self):
        self.config.save_server_config(
            ServerConfig('https://github.com/anaynayak/buildnotify/cctray.xml', ['excludedproject'], 'EDT', 'prefix',
                         'user', 'pass'))
        server = self.config.get_server_config("https://github.com/anaynayak/buildnotify/cctray.xml")
        self.assertEqual('user', server.username)
        self.assertEqual('pass', server.password)
        self.assertEqual("https://github.com/anaynayak/buildnotify/cctray.xml", server.url)
        self.assertEqual('EDT', server.timezone)
        self.assertEqual(['excludedproject'], server.excluded_projects)
        self.assertEqual('prefix', server.prefix)
        self.assertEqual(["https://github.com/anaynayak/buildnotify/cctray.xml"], self.config.get_urls())

    def test_should_get_empty_if_missing(self):
        server = self.config.get_server_config('someurl')
        self.assertEqual('', server.username)

    def test_should_return_all_servers(self):
        self.config.save_server_config(ServerConfig('url1', [], 'EDT', 'prefix', 'user', 'pass'))
        self.config.save_server_config(ServerConfig('url2', [], 'EDT', 'prefix', 'user', 'pass'))
        servers = self.config.get_server_configs()
        self.assertEqual(2, len(servers))
        self.assertEqual('http://url1', servers[0].url)
        self.assertEqual('http://url2', servers[1].url)

    def test_should_update_preferences(self):
        self.config.update_preferences(Preferences(['url1'], 300, '/bin/sh', True, False, True, []))

        self.assertEqual(self.config.get_urls(), ['url1'])
        self.assertEqual(self.config.get_interval_in_seconds(), 300)
        self.assertEqual(self.config.get_custom_script(), '/bin/sh')
        self.assertEqual(self.config.get_custom_script_enabled(), True)
        self.assertEqual(self.config.get_sort_by_last_build_time(), False)
        self.assertEqual(self.config.get_sort_by_name(), True)


if __name__ == '__main__':
    unittest.main()
