import unittest
from buildnotifylib.config import Config

class ConfigTest(unittest.TestCase):
    def test_should_persist_user_project_excludes(self):
        config = Config()
        config.set_project_excludes('http://bitbucket.org/Anay/buildnotify/cctray.xml', ['buildnotify::test-server'])
        self.assertEquals(['buildnotify::test-server'], config.get_project_excludes('http://bitbucket.org/Anay/buildnotify/cctray.xml'))
    
    def test_should_persist_empty_user_project_excludes(self):
        config = Config()
        config.set_project_excludes('http://bitbucket.org/Anay/buildnotify/cctray.xml', [])
        self.assertEquals([], config.get_project_excludes('http://bitbucket.org/Anay/buildnotify/cctray.xml'))

    def test_should_return_an_empty_list_if_unmapped(self):
        config = Config()
        self.assertEquals([], config.get_project_excludes('http://bitbucket.org/Anay/buildnotify/buildnotify.xml'))
    
if __name__ == '__main__':
    unittest.main()

