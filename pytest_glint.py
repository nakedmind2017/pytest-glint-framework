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