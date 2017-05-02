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
