from os import getenv

VERSION = "1.0.4"


def version(key='CIRCLE_BUILD_NUM'):
    build = getenv(key)
    label = '' if build is None else '.dev' + build
    return VERSION + label


if __name__ == '__main__':
    print(version())
