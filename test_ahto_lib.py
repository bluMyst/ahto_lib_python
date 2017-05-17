import pytest

import ahto_lib

@pytest.mark.parametrize("default,question,response,return_", [
    (True,  "Foo",  "",  True),
    (False, "Bar",  "",  False),
    (True,  "Baz",  "n", False),
    (False, "Qux",  "Y", True),
    (None,  "Quux", "N", False),
    (None,  "Quuz", "y", True)])
def test_yes_no(monkeypatch, default, question, response, return_):
    def new_input(prompt=None):
        if default is None:
            assert prompt.endswith(' [yn]')
        elif default is True:
            assert prompt.endswith(' [Yn]')
        elif default is False:
            assert prompt.endswith(' [yN]')
        else:
            assert False

        assert prompt.startswith(question)
        return response

    monkeypatch.setitem(ahto_lib.__builtins__, 'input', new_input)
    assert ahto_lib.yes_no(default, question) == return_

def test_loading_done(capfd):
    ld = ahto_lib.LoadingDone().__enter__()
    out, err = capfd.readouterr()
    assert out == "Loading... "
    ld.__exit__(None, None, None)
    out, err = capfd.readouterr()
    assert out == 'done.\n'

    ld = ahto_lib.LoadingDone("Testing...").__enter__()
    out, err = capfd.readouterr()
    assert out == "Testing... "
    ld.__exit__(None, None, None)
    out, err = capfd.readouterr()
    assert out == "done.\n"

@pytest.mark.parametrize("len_,message,indicies", [
    (600,  "Testing...", [2, 13, 45, 200, 400]),
    (2,    None,         [0, 1]),
    (99,   "Fooing...",  [0, 13, 67, 98]),
    (9999, None,         [0, 10, 200, 300, 400, 1000, 9998])])
def test_progress_mapper(capfd, len_, indicies, message):
    if message is not None:
        pm = ahto_lib.ProgressMapper(len_, message).__enter__()
    else:
        pm = ahto_lib.ProgressMapper(len_).__enter__()
        message = "Loading..."

    out, err = capfd.readouterr()
    assert out.startswith('\r' + message)

    last_len = None
    for i in indicies:
        pm(i)
        out, err = capfd.readouterr()
        assert out.startswith('\r' + message)
        assert out.find(f"{i+1}/{len_}") != -1

        if last_len is not None:
            assert len(out) >= last_len

        if last_len is None or len(out) > last_len:
            last_len = len(out)

    pm.__exit__(None, None, None)
    out, err = capfd.readouterr()
    assert out.startswith('\r' + message + " done.")
    assert len(out) >= last_len

def test_progress_map(monkeypatch):
    l = list(range(10))

    class DummyProgressMapper(object):
        def __init__(self, items_len, message=None):
            nonlocal l
            assert items_len == len(l)
            assert message == "Foo bar..."

            self.current_state = "init done"

        def __enter__(self):
            assert self.current_state == "init done"
            self.current_state = "enter done"
            return self

        def __call__(self, item_index):
            if item_index == 0:
                assert self.current_state == "enter done"
            else:
                assert self.current_state == ("iteration index", item_index-1)
                nonlocal l
                assert len(l) >= item_index

            self.current_state = ("iteration index", item_index)

        def __exit__(self, *_, **__):
            nonlocal l
            assert self.current_state == ("iteration index", len(l)-1)

    monkeypatch.setattr(ahto_lib, 'ProgressMapper', DummyProgressMapper)

    l = ahto_lib.progress_map(lambda i: i*2, l, "Foo bar...")
    assert l == list(range(0, 20, 2))

def test_not_func():
    def ret_and_args(*args):
        return all(args)

    ret_true     = ahto_lib.not_func(lambda: False)
    ret_false    = ahto_lib.not_func(lambda: True)
    ret_not_arg  = ahto_lib.not_func(lambda arg: arg)
    ret_and_args = ahto_lib.not_func(ret_and_args)

    assert ret_true() == True
    assert ret_false() == False
    assert ret_not_arg(True) == False
    assert ret_not_arg(False) == True
    assert ret_and_args(True) == False
    assert ret_and_args(True, True, True, True, True) == False
    assert ret_and_args(True, True, False, True, True) == True

def test_lazy_property():
    class LazyPropertyTester(object):
        def __init__(self):
            self.count = 0

        @ahto_lib.lazy_property
        def foo(self):
            self.count += 1
            assert self.count == 1
            return 1337

    for _ in range(10):
        assert LazyPropertyTester().foo == 1337

def test_lazy_function():
    times_called = 0

    @ahto_lib.lazy_function
    def f():
        nonlocal times_called
        times_called += 1
        assert times_called == 1
        return True

    for _ in range(10):
        assert f() is True

def test_static_vars():
    @ahto_lib.static_vars(counter=0)
    def accumulator():
        accumulator.counter += 1
        return accumulator.counter

    for i in range(1, 20):
        assert accumulator() == i

def test_any_length_permutation():
    import itertools
    l = list(range(3))
    perms = ahto_lib.any_length_permutation(l)

    assert all(i in perms for i in itertools.permutations(l, 1))
    assert all(i in perms for i in itertools.permutations(l, 2))
    assert all(i in perms for i in itertools.permutations(l, 3))
