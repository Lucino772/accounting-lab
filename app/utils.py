from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from flask import abort

from app.extensions import htmx

T_Ret = TypeVar("T_Ret")
T_Params = ParamSpec("T_Params")


def htmx_only(func: Callable[T_Params, T_Ret]) -> Callable[T_Params, T_Ret]:
    @wraps(func)
    def _wrapper(*args: T_Params.args, **kwargs: T_Params.kwargs) -> T_Ret:
        if not htmx:
            abort(500)
        return func(*args, **kwargs)

    return _wrapper
