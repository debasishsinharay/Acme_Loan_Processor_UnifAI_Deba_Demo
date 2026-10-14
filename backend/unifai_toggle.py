"""Demo toggle for the code UnifAI inserts.

UnifAI remediation adds a ``unifai_guard`` module to the repo and calls its functions
(``mask_pii``, ``remove_encoded_prompts``, ``sanitize_prompt``, ``find_code_execution``,
...) at the places where a policy applies. This file lets the demo switch those calls
off and on per request, so the same build shows the app with and without UnifAI.

- Nothing UnifAI writes is edited. This module wraps the guard's functions when the
  guard is imported, wherever UnifAI placed it and however many copies there are.
- Toggle on (the default): every guard function runs as UnifAI wrote it.
- Toggle off: ``find_*`` functions report nothing and every other guard function
  returns its input unchanged, which is how the app behaved before remediation.
- The frontend sends ``X-UnifAI: on`` or ``X-UnifAI: off`` with each request.

Keep this file out of the UnifAI scan scope (scan ``backend/agents`` and
``backend/file_parsers``), so remediation never touches it.
"""

from __future__ import annotations

import contextvars
import functools
import importlib.abc
import inspect
import logging
import sys

logger = logging.getLogger(__name__)

HEADER = "X-UnifAI"
_enabled: contextvars.ContextVar[bool] = contextvars.ContextVar("unifai_enabled", default=True)
_WRAPPED = "__unifai_toggle_wrapped__"
# Guard functions that change or return the text: passed through when off.
_TRANSFORM_PREFIXES = ("mask_", "redact_", "remove_", "sanitize_")
# Guard functions that report findings: report none when off.
_FINDER_PREFIX = "find_"


def is_enabled() -> bool:
    return _enabled.get()


def set_enabled(on: bool) -> contextvars.Token:
    return _enabled.set(bool(on))


def enabled_from_header(value: str | None) -> bool:
    """``off`` (or false/0/disabled) turns UnifAI off; anything else, or no header, keeps it on."""
    return (value or "on").strip().lower() not in {"off", "false", "0", "disabled"}


def _wrap(name: str, func):
    finder = name.startswith(_FINDER_PREFIX)

    @functools.wraps(func)
    def wrapper(value, *args, **kwargs):
        if _enabled.get():
            return func(value, *args, **kwargs)
        return [] if finder else value

    setattr(wrapper, _WRAPPED, True)
    return wrapper


def _patch(module) -> None:
    patched = []
    for name, func in list(vars(module).items()):
        if name.startswith("_") or not inspect.isfunction(func) or getattr(func, _WRAPPED, False):
            continue
        if func.__module__ != module.__name__:
            continue
        if name.startswith(_FINDER_PREFIX) or name.startswith(_TRANSFORM_PREFIXES):
            setattr(module, name, _wrap(name, func))
            patched.append(name)
    if patched:
        logger.info("UnifAI toggle: wrapped %d guard functions in %s", len(patched), module.__name__)


def _is_guard(fullname: str) -> bool:
    return fullname.rsplit(".", 1)[-1] == "unifai_guard"


class _GuardFinder(importlib.abc.MetaPathFinder):
    """Wraps each ``unifai_guard`` module as soon as it is imported, before the agents'
    ``from ... unifai_guard import ...`` lines bind its functions."""

    def find_spec(self, fullname, path=None, target=None):
        if not _is_guard(fullname):
            return None
        for finder in sys.meta_path:
            if finder is self or not hasattr(finder, "find_spec"):
                continue
            spec = finder.find_spec(fullname, path, target)
            if spec is not None and spec.loader is not None:
                exec_module = spec.loader.exec_module

                def exec_and_patch(module, _exec=exec_module):
                    _exec(module)
                    _patch(module)

                spec.loader.exec_module = exec_and_patch
                return spec
        return None


def install() -> None:
    """Call once at startup, before the agents are imported."""
    if not any(isinstance(f, _GuardFinder) for f in sys.meta_path):
        sys.meta_path.insert(0, _GuardFinder())
    for name, module in list(sys.modules.items()):
        if module is not None and _is_guard(name):
            _patch(module)
