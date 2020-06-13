import os


def fake_content():
    path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "/../data/cctray.xml")
    return open(path, encoding='utf-8').read()
