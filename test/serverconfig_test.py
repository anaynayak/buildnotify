from buildnotifylib.serverconfig import ServerConfig


def test_should_cleanup_url():
    assert ServerConfig('http://url.com:9800/cc.xml', [], '', '', '', '').url == 'http://url.com:9800/cc.xml'
    assert ServerConfig('url.com:9800/cc.xml', [], '', '', '', '').url == 'http://url.com:9800/cc.xml'
    assert ServerConfig('url.com/cc.xml', [], '', '', '', '').url == 'http://url.com/cc.xml'
    assert ServerConfig('localhost:8080/cc.xml', [], '', '', '', '').url == 'http://localhost:8080/cc.xml'
    assert ServerConfig('http://localhost:8080/cc.xml', [], '', '', '', '').url == 'http://localhost:8080/cc.xml'
    assert ServerConfig('https://localhost:8080/cc.xml', [], '', '', '', '').url == 'https://localhost:8080/cc.xml'
    assert ServerConfig('file://localhost:8080/cc.xml', [], '', '', '', '').url == 'file://localhost:8080/cc.xml'
