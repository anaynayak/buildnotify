import os


def fake_content():
    return open(os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "/../data/cctray.xml")).read()
