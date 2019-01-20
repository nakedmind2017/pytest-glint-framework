# -*- coding: utf-8 -*-
import shutil
from unittest.mock import patch

import pytest


@pytest.fixture(scope='session')
def main():
    patcher = patch('glint.get_main')
    yield patcher.start().return_value
    patcher.stop()


@pytest.fixture(scope='session')
def engine():
    patcher = patch('glint.get_current_engine')
    yield patcher.start().return_value
    patcher.stop()


def use_rpc_stub(decorated=None, **kwargs):
    return (decorated if decorated else lambda x: x)


@pytest.fixture(scope='session')
def no_rpc():
    patcher = patch('glint.use_rpc', side_effect=use_rpc_stub)
    yield patcher.start()
    patcher.stop()


@pytest.fixture
def test_glint_dir(request):
    test_dir = getattr(request.module, 'glint_root', None)
    if test_dir:
        try:
            shutil.rmtree(str(test_dir))
        except WindowsError:
            pass

        test_dir.mkdir(parents=True)

    yield test_dir

    if test_dir:
        try:
            shutil.rmtree(str(test_dir))
        except WindowsError:
            pass


class Bunch:
    """ Use this for mocking named tuples or any DTOs. """
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


@pytest.fixture
def bunch():
    return Bunch


class _xdict(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._not_given = {}

    def __repr__(self):
        items = []
        for k, v in self.items():
            items.append(f'{k!r}: {v!r}')
        for k, v in self._not_given.items():
            items.append(f'{k!r}: {v!r}')
        return '{' + ', '.join(items) + '}'

    def __eq__(self, obj):
        is_equal = True
        for k, v in obj.items():
            try:
                if self[k] != v:
                    is_equal = False
            except KeyError:
                self._not_given[k] = v

        return is_equal


@pytest.fixture
def xdict():
    return _xdict()
