# -*- coding: utf-8 -*-
import shutil
try:
    from pathlib import Path
except ImportError:
    # Python 2 backport
    from pathlib2 import Path
try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch
import pytest

import glint


@pytest.fixture
def path_exists():
    patcher = patch.object(Path, 'exists', return_value=False)
    yield patcher.start()
    patcher.stop()


@pytest.fixture
def path_mkdir():
    patcher = patch.object(Path, 'mkdir')
    yield patcher.start()
    patcher.stop()


@pytest.fixture
def path_stub():
    patcher = patch('pathlib.Path', autospec=Path)
    _path_stub = patcher.start().return_value
    _path_stub.exists.return_value = False
    _path_stub.__truediv__.return_value = _path_stub
    yield _path_stub
    patcher.stop()


@pytest.fixture(scope='session')
def main():
    patcher = patch('glint.get_main')
    yield patcher.start().return_value
    patcher.stop()


@pytest.fixture
def get_setting(request, main):
    patcher = patch.object(main, 'get_setting')
    gs = patcher.start()
    if request.cls and hasattr(request.cls, 'settings'):
        gs.side_effect = lambda x: request.cls.settings.get(x)
    elif hasattr(request.module, 'settings'):
        gs.side_effect = lambda x: request.module.settings.get(x)

    yield
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


class _patch_gcmd():
    def __init__(self, command_name, new=None, **kwargs):
        self.command_name = command_name
        self.new = new
        self.kwargs = kwargs
        self._old_handler = None
        self._patcher = None

    def __enter__(self):
        """Perform the patch."""
        try:
            self._old_handler = glint.api.commands.get_command_handler(self.command_name)
        except glint.GlintError:
            pass

        if not self.new:
            self.new = MagicMock(**self.kwargs)

        glint.register_command(self.command_name, self.new, force=True)
        return self.new

    def __exit__(self, *exc_info):
        """Undo the patch."""
        if self._old_handler:
            glint.register_command(self.command_name, self._old_handler, force=True)

    def start(self):
        """Activate a patch, returning any created mock."""
        return self.__enter__()

    def stop(self):
        """Stop an active patch."""
        return self.__exit__()


@pytest.fixture
def patch_gcmd():
    return _patch_gcmd


@pytest.fixture
def get_cache_data():
    patcher = patch('glint.get_cache_data', return_value={})
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


class InstanceMatcher:
    def __init__(self, klass_or_type):
        self.klass_or_type = klass_or_type

    def __repr__(self):
        return repr(self.klass_or_type)

    def __eq__(self, obj):
        return isinstance(obj, self.klass_or_type)


@pytest.fixture(scope='session')
def instance_matcher():
    return InstanceMatcher


class _xdict(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._not_given = {}

    def __repr__(self):
        items = []
        for k, v in self.items():
            items.append('{k!r}: {v!r}'.format(k=k, v=v))
        for k, v in self._not_given.items():
            items.append('{k!r}: {v!r}'.format(k=k, v=v))
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
    return _xdict
