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

# TODO: Fix!
#def test_progress_map(capfd):
#    class ProgressMapTester(object):
#        def __init__(self, args_expected):
#            self.args_expected = args_expected
#            self.total_args = len(self.args_expected)
#
#        def __call__(self, arg):
#            nonlocal capfd
#            assert arg == self.args_expected[0]
#            del self.args_expected[0]
#            out, err = capfd.readouterr()
#            assert out.startswith("\rLoading... ")
#            position_in_args = len(self.args_expected) - self.total_args
#            assert out.find(f"{position_in_args+1}/{self.total_args}") != -1
#
#    l = list(range(0, 101, 10))
#    ahto_lib.progress_map(ProgressMapTester(l), l)
#    out, err = capfd.readouterr()
#    assert out.startswith("\rLoading... done.")

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

# TODO: any_length_permutation
# This one's incredibly tricky because order matters with permutations!
