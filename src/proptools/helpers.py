
"""
<ih-property-tools>/src/proptools/helpers.py

Helper items,

"""


all = [
    "auto",
    "auto_fini",
    "auto_fget",
    "auto_fset",
    "auto_fdel",
    "auto_property",
    "isauto",
    "isidentifier",
    "isundef",
]


import os, sys, warnings

from collections.abc import Iterable
from types import MappingProxyType, SimpleNamespace
from typing import Any, Callable, NoReturn, Optional, Self


_ = os.environ.get("PROPTOOLS_HELPERS_DEBUG", "")
try:
    _HELPERS_DEBUG = bool(int(_)) if _ else False
except:
    warnings.warn(f"PROPTOOLS_HELPERS_DEBUG = {_!r}, using False")
    _HELPERS_DEBUG = False


def debug(*args, file=sys.stderr, **kwargs):
    if _HELPERS_DEBUG:
        print(*args, file=file, **kwargs)


class auto:
    "`auto()` class for used to mark that late processing is requested."
    value = None

    def __init__(self, value = None):
        self.value = value
        self.__doc__ = None


def isauto(value):
    return isinstance(value, auto)


def auto_fini(
    name: str,
    private_name: Optional[str] = None,
    private_namespace: Optional[str|SimpleNamespace] = None,
    initial_value: Optional[Any] = None,
):
    """
    `auto_fini` -- generates and returns an fini function.

    An fini function for use in a property, or initializer implementation.

    Parameters
    ----------
    name : str
        The property / attribute name.

    private_name : Optional[str] = None
        The private attribute name.

        If it and `private_namespace` are None, `_{name}` is used.
        If it is None and `private_namespace` is not None, `name` is used.
        If it is an identifier str, then it is used.
        Otherwise a TypeError is thrown.

    private_namespace: Optional[str|SimpleNamespace] = None
        This controls where value is accessed, and effects whether it
        is included as the second (after `self`) argumant, pushing the
        incoming `value` argument to the third position.

        If it is None, then there is no private namespace and no privates
        (second) argument,
        If it is a str, then the private namespace is provided by the
        caller as the second argument.
        If it is a namespace then it, is added to scope assets as 'privates',
        `privates.{private_name}`.

    initial_value: Optional[Any] = None
        This is the value used as the default for initial in fini.

    Returns
    -------
    a fini callback (function) compatible with property.initializer.

    Raises
    ------
    TypeError
        If any of the arguments are not type and value requirements.

    """
    assets = dict(initial_value=initial_value)

    if not private_namespace:
        if private_name is None:
            private_name = "_" + name
        first = f"def {name}(self, value=initial_value):"
        last = f"    self.{private_name} = value"
    elif isidentifier(private_namespace):
        if private_name is None:
            private_name = name
        first = f"def {name}(self, {private_namespace}, value=initial_value):"
        last = f"    {private_namespace}.{private_name} = value"
    elif isinstance(private_namespace, SimpleNamespace):
        if private_name is None:
            private_name = name
        assets["privates"] = private_namespace
        first = f"def {name}(self, value=initial_value):"
        last = f"    privates.{private_name} = value"
    else:
        raise TypeError(
            f"`private_namespace` expects None, a str, or Namespace"
            f", not {private_namespace}",
        )

    source = first + "\n" + last + "\n"
    if _HELPERS_DEBUG:
        print("fini source...")
        print(source)
    code = compile(source, "<auto_fini>", "exec")
    results = {}
    exec(code, assets, results)
    return results[name]


def auto_fget(
    name: str,
    private_name: Optional[str] = None,
    private_namespace: Optional[str|SimpleNamespace] = None,
):
    """
    `auto_fget` -- generates and returns an fget function.

    An fget function for use in a property, or initializer implementation.

    Parameters
    ----------
    name : str
        The property / attribute name.

    private_name : Optional[str] = None
        The private attribute name.

        If it and `private_namespace` are None, `_{name}` is used.
        If it is None and `private_namespace` is not None, `name` is used.
        If it is an identifier str, then it is used.
        Otherwise a TypeError is thrown.

    private_namespace: Optional[str|SimpleNamespace] = None
        This controls where value is accessed, and effects whether it
        is included as the second (after `self`) argumant, pushing the
        incoming `value` argument to the third position.

        If it is None, then there is no private namespace and no privates
        (second) argument,
        If it is a str, then the private namespace is provided by the
        caller as the second argument.
        If it is a namespace then it, is added to scope assets as 'privates',
        `privates.{private_name}`.

    Returns
    -------
    a fget callback (function) compatible with property.getter.

    Raises
    ------
    TypeError
        If any of the arguments are not type and value requirements.

    """
    assets = dict()

    if not private_namespace:
        if private_name is None:
            private_name = "_" + name
        first = f"def {name}(self):"
        last = f"    return self.{private_name}"
    elif isidentifier(private_namespace):
        if private_name is None:
            private_name = name
        first = f"def {name}(self, {private_namespace}):"
        last = f"    return {private_namespace}.{private_name}"
    elif isinstance(private_namespace, SimpleNamespace):
        if private_name is None:
            private_name = name
        assets["privates"] = private_namespace
        first = f"def {name}(self):"
        last = f"    return privates.{private_name}"
    else:
        raise TypeError(
            f"`private_namespace` expects None, a str, or Namespace"
            f", not {private_namespace}",
        )

    source = first + "\n" + last + "\n"
    if _HELPERS_DEBUG:
        debug("fget source...")
        debug(source)
    code = compile(source, "<auto_fget>", "exec")
    results = {}
    exec(code, assets, results)
    return results[name]


def auto_fset(
    name: str,
    private_name: Optional[str] = None,
    typing: Optional[Iterable[type, ...] | Callable] = None,
    private_namespace: Optional[str|SimpleNamespace] = None,
):
    """
    `auto_fset` -- generates and returns an fset function.

    An fset function for use in a property, or setter implementation.

    Parameters
    ----------
    name : str
        The property / attribute name.

    private_name : Optional[str] = None
        The private attribute name.

        If it and `private_namespace` are None, `_{name}` is used.
        If it is None and `private_namespace` is not None, `name` is used.
        If it is an identifier str, then it is used.
        Otherwise a TypeError is thrown.

    typing: Optional[tuple[type, ...] | Callable] = None
        The typing management, can either be a casting function
        that takes a single argument (value), a tuple of types, or
        empty for no typing management. Default: None.

    private_namespace: Optional[str|SimpleNamespace] = None
        This controls where value is accessed, and effects whether it
        is included as the second (after `self`) argumant, pushing the
        incoming `value` argument to the third position.

        If it is None, then there is no private namespace and no privates
        (second) argument,
        If it is a str, then the private namespace is provided by the
        caller as the second argument.
        If it is a namespace then it, is added to scope assets as 'privates',
        `privates.{private_name}`.

    Returns
    -------
    a fset callback (function) compatible with property.setter.

    Raises
    ------
    TypeError
        If any of the arguments are not type and value requirements.

    """
    assets = {}

    if not private_namespace:
        if private_name is None:
            private_name = "_" + name
        first = f"def {name}(self, value):"
        last = f"    self.{private_name} = value"
    elif isidentifier(private_namespace):
        if private_name is None:
            private_name = name
        first = f"def {name}(self, {private_namespace}, value):"
        last = f"    {private_namespace}.{private_name} = value"
    elif isinstance(private_namespace, SimpleNamespace):
        if private_name is None:
            private_name = name
        assets["privates"] = private_namespace
        first = f"def {name}(self, value):"
        last = f"    privates.{private_name} = value"
    else:
        raise TypeError(
            f"`private_namespace` expects None, a str, or Namespace"
            f", not {private_namespace}",
        )

    body = f""
    if not typing:
        body += "\n"

    elif isinstance(typing, Iterable):
        types = tuple(typing)
        assets["types"] = types

        for i, t in enumerate(types):
            if not isinstance(t, type):
                raise ValueError(f"typing[{i}] expects, not {t!r}")

        args = ', '.join(i.__name__ for i in types[:-1])
        if args:
            args += " or "
        args += types[-1].__name__
        body += f"""
    if not isinstance(value, types):
        raise TypeError(f"{name} expects {args}, not {{value!r}}")
"""

    elif callable(typing):
        assets["cast"] = typing
        body += """
    value = cast(value)
"""
    else:
        raise ValueError(
            f"types expects Iterable[type], a callable or None, not {types}"
        )

    source = first + body + last + "\n"
    if _HELPERS_DEBUG:
        debug("fset source...")
        debug(source)
    code = compile(source, "<auto_fset>", "exec")
    results = {}
    exec(code, assets, results)
    return results[name]


def auto_fdel(
    name: str,
    private_name: Optional[str] = None,
    private_namespace: Optional[str|SimpleNamespace] = None,
):
    """
    `auto_fdel` -- generates and returns an fdel function.

    An fdel function for use in a property, or initializer implementation.

    Parameters
    ----------
    name : str
        The property / attribute name.

    private_name : Optional[str] = None
        The private attribute name.

        If it and `private_namespace` are None, `_{name}` is used.
        If it is None and `private_namespace` is not None, `name` is used.
        If it is an identifier str, then it is used.
        Otherwise a TypeError is thrown.

    private_namespace: Optional[str|SimpleNamespace] = None
        This controls where value is accessed, and effects whether it
        is included as the second (after `self`) argumant, pushing the
        incoming `value` argument to the third position.

        If it is None, then there is no private namespace and no privates
        (second) argument,
        If it is a str, then the private namespace is provided by the
        caller as the second argument.
        If it is a namespace then it, is added to scope assets as 'privates',
        `privates.{private_name}`.

    Returns
    -------
    a fdel callback (function) compatible with property.deleter.

    Raises
    ------
    TypeError
        If any of the arguments are not type and value requirements.

    """
    assets = dict()

    if not private_namespace:
        if private_name is None:
            private_name = "_" + name
        first = f"def {name}(self):"
        last = f"    del self.{private_name}"
    elif isidentifier(private_namespace):
        if private_name is None:
            private_name = name
        first = f"def {name}(self, {private_namespace}):"
        last = f"    del {private_namespace}.{private_name}"
    elif isinstance(private_namespace, SimpleNamespace):
        if private_name is None:
            private_name = name
        assets["privates"] = private_namespace
        first = f"def {name}(self):"
        last = f"    del privates.{private_name}"
    else:
        raise TypeError(
            f"`private_namespace` expects None, a str, or Namespace"
            f", not {private_namespace}",
        )

    source = first + "\n" + last + "\n"
    if _HELPERS_DEBUG:
        debug("fdel source...")
        debug(source)
    code = compile(source, "<auto_fdel>", "exec")
    results = {}
    exec(code, assets, results)
    return results[name]


def _create_secrets_getter(secrets_lut={}):
    def secrets_getter(key):
        if key in secrets_lut:
            return secrets_lut[key]
        _secrets = secrets_lut[key] = {}
        return _secrets
    return secrets_getter


def create_secret_instance_namespace_getter(cls):
    "Create a secret namespace wrapper for an instance."
    def _factory(secrets):
        "Creates and returns a secret namespace getter for a given instance."
        def get_secret_namespace(self):
            if self in secrets:
                return secrets[self]
            secret_namespace = secrets[self] = SimpleNamespace()
            return secret_namespace
        return get_secret_namespace

    _secrets_getter = _create_secrets_getter()
    return _factory(_secrets_getter(cls))


def isidentifier(value):
    return (
        value and isinstance(value, str) and value.isidentifier()
        and not (value.startswith("_") or value.endswith("_"))
    )


def _undef_singleton():
    "Returns an UndefinedType singleton instance."
    class UndefinedType:

        def __bool__(self):
            raise TypeError(f"Undef has no Boolean state")

        def __repr__(self):
            return "Undef"

    return UndefinedType()


Undef = _undef_singleton()


def isundef(value):
    return value is Undef


