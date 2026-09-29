import sys
import types

import pytest


def _fake_tkinter(monkeypatch, selected):
    """Stand in for tkinter entirely, rather than only for askdirectory().

    The previous version of this test monkeypatched the dialog call but let
    the real `tk.Tk()` construct a window, so it could only pass on a
    machine with a display -- it mocked the safe part and exercised the
    part that breaks on a headless host.
    """

    class _FakeRoot:
        def withdraw(self):
            pass

        def attributes(self, *_args):
            pass

        def destroy(self):
            pass

    tk = types.ModuleType("tkinter")
    tk.Tk = _FakeRoot
    tk.TclError = type("TclError", (Exception,), {})

    filedialog = types.ModuleType("tkinter.filedialog")
    filedialog.askdirectory = lambda: selected
    tk.filedialog = filedialog

    monkeypatch.setitem(sys.modules, "tkinter", tk)
    monkeypatch.setitem(sys.modules, "tkinter.filedialog", filedialog)


def test_pick_directory_returns_selected_path(client, monkeypatch):
    _fake_tkinter(monkeypatch, "C:\\Users\\roma-\\repo")

    response = client.post("/api/pick-directory")

    assert response.status_code == 200
    assert response.json() == {"path": "C:\\Users\\roma-\\repo"}


def test_pick_directory_returns_null_when_cancelled(client, monkeypatch):
    _fake_tkinter(monkeypatch, "")

    response = client.post("/api/pick-directory")

    assert response.status_code == 200
    assert response.json() == {"path": None}


def test_pick_directory_is_not_reachable_by_a_plain_get(client):
    # A GET could be fired by any page the user visits with a bare
    # <img src=...>, popping a native dialog on their desktop. The exact
    # code depends on whether a built frontend is mounted (405 from the
    # router, 404 once the static mount owns unmatched paths) -- what
    # matters is that no dialog opens.
    response = client.get("/api/pick-directory")

    assert response.status_code in (404, 405)


def test_pick_directory_reports_unavailable_instead_of_crashing_headless(client, monkeypatch):
    # A slim container or a Linux box without python3-tk.
    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def _no_tkinter(name, *args, **kwargs):
        if name.startswith("tkinter"):
            raise ImportError("No module named 'tkinter'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setitem(sys.modules, "tkinter", None)
    monkeypatch.delitem(sys.modules, "tkinter", raising=False)
    monkeypatch.setattr("builtins.__import__", _no_tkinter)

    response = client.post("/api/pick-directory")

    assert response.status_code == 501
    assert "tkinter" in response.json()["detail"].lower()


@pytest.mark.parametrize("_run", range(2))
def test_pick_directory_is_repeatable(client, monkeypatch, _run):
    # The single-flight lock must be released on every path, or the second
    # call would 409 forever.
    _fake_tkinter(monkeypatch, "C:\\repo")

    assert client.post("/api/pick-directory").status_code == 200
