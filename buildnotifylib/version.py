from os import getenv

VERSION = "2.1.0"


def version(key='BUILD_LABEL') -> str:
    build = getenv(key)
    label = '' if build is None else '.dev' + build
    return VERSION + label


if __name__ == '__main__':
    print((version()))
