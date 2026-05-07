"""Tests for dependency diagnostics."""

from __future__ import annotations

from common import check_libraries as cl


def test_check_libraries_returns_true_when_all_present(monkeypatch):
    monkeypatch.setattr(cl.importlib, "import_module", lambda _: object())
    assert cl.check_libraries({"requests": "requests"}) is True


def test_check_libraries_returns_false_when_missing(monkeypatch):
    def fake_import(name):
        if name == "missing_mod":
            raise ImportError("missing")
        return object()

    monkeypatch.setattr(cl.importlib, "import_module", fake_import)
    assert cl.check_libraries({"ok": "ok", "missing": "missing_mod"}) is False


def test_main_returns_zero_when_dependencies_ok(monkeypatch):
    monkeypatch.setattr(cl, "check_libraries", lambda _: True)
    assert cl.main() == 0


def test_main_returns_one_when_dependencies_missing(monkeypatch):
    monkeypatch.setattr(cl, "check_libraries", lambda _: False)
    assert cl.main() == 1
