import keyring

from test.fake_keyring import InMemoryKeyring


def test_should_use_in_memory_keyring():
    assert isinstance(keyring.get_keyring(), InMemoryKeyring)


def test_should_not_leak_passwords_between_tests_part_one():
    keyring.set_password('svc', 'user', 'secret')


def test_should_not_leak_passwords_between_tests_part_two():
    assert keyring.get_password('svc', 'user') is None
