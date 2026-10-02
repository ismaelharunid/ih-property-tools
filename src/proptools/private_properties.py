
"""
<ih-property-tools>/src/proptools/private_properties.py

Extended Property class and wrappers,

"""


all = [
    "private",
]


import os, sys, warnings

from collections.abc import Iterable
from functools import cache, cached_property, wraps
from types import MappingProxyType, SimpleNamespace
from typing import Any, Callable, NoReturn, Optional, Self


from . import helpers
from .quick_properties import Property, initialize_properties


class PrivateProperty(Property):
    "A version of Property with an extra `privates` argument for each fxxx."

    def __auto_fini__(self, owner):
        "expand auto fini."
        def make(private_name, initial):
            def fini(self, privates, value = initial):
                setattr(privates, private_name, value)

            if self.fini:
                try:
                    fini.__name__ = self.fini.__name__
                except AttributeError:
                    pass
                if self.fini.__doc__:
                    fini.__doc__ = self.fini.__doc__

            return fini

        return make(self.private_name, self.initial)

    def __auto_fget__(self, owner):
        "expand auto fget."
        def make(private_name, initial):
            def fget(self, privates):
                return getattr(privates, private_name, initial)

            if self.fget:
                try:
                    fget.__name__ = self.fget.__name__
                except AttributeError:
                    pass
                if self.fget.__doc__:
                    fget.__doc__ = self.fget.__doc__

            return fget

        return make(self.private_name, self.initial)

    def __auto_fset__(self, owner):
        "expand auto fset."
        def make(private_name):
            def fset(self, privates, value):
                setattr(privates, private_name, value)

            if self.fset:
                try:
                    fset.__name__ = self.fset.__name__
                except AttributeError:
                    pass
                if self.fset.__doc__:
                    fset.__doc__ = self.fset.__doc__

            return fset

        return make(self.private_name)

    def __auto_fdel__(self, owner):
        "expand auto fdel."
        def make(private_name, initial):
            def fdel(self, privates, value = initial):
                delattr(privates, private_name)

            if self.fdel:
                try:
                    fdel.__name__ = self.fdel.__name__
                except AttributeError:
                    pass
                if self.fdel.__doc__:
                    fdel.__doc__ = self.fdel.__doc__

            return fdel

        return make(self.private_name, self.initial)

    def __privates__(
        self: Self,
        owner: type,
        instance: Property,
    ):
        """
        Create and return a private instance namespace getter based on owner.

        Arguments
        ---------
        self : Self
            The propery instance
        owner : class
            The owner class of instance.

        Returns
        -------
        : Callable
            A private instance namespace getter.

        Raises
        ------
        : TypeError
            Raised if passed arguments are of wrong type or value.
        """
        if not isinstance(owner, type):
            raise TypeError(f"owner expects a type, not {owner!r}")

        get_privates = helpers.create_secret_instance_namespace_getter(owner)
        return get_privates(instance)

    def __private_name__(self, name, private_name: Optional[str] = None):
        """
        Returns the private_name associated with name.

        Arguments
        ---------
        self : Self
            The propery instance
        name : str
            The property name within the owner class
        private_name : Optional[str]
            The attribute name within the private space
        private_name : object
            The private attribute name for accessing attribute
        """
        if self.private_name:
            return self.private_name
        if private_name is None:
            private_name = name
        return private_name

    def __initialize__(self, instance, owner=None):
        if instance is None:
            if owner is None:
                raise AttributeError(
                    f"Cannot initialize {private_name!r}"
                    f" for property {self.__name__!r}",
                )
            setattr(owner, private_name, self.initial)
            return

        if owner is None:
            owner = type(instance)

        if self.fini is None:
            raise AttributeError(
                f"property {self.__name__!r} of {owner.__name__!r}"
                f" object has no initializer",
            )

        privates = self.__privates__(owner, instance)
        self.fini(instance, privates, self.initial)

    def __get__(self, instance, owner=None):
        private_name = self.__private_name__(self.__name__)
        if instance is None:
            # return the property, same as getattr(owner, name).
            return self

        if owner is None:
            owner = type(instance)

        if self.fget is None:
            raise AttributeError(
                f"property {self.__name__!r} of {owner.__name__!r}"
                f" object has no getter",
            )

        privates = self.__privates__(owner, instance)
        value = self.fget(instance, privates)
        if helpers.isundef(value):
            oname = type(instance).__name__
            raise AttributeError(
                f"{name!r} of {oname!r} is undefined",
            )

        return value

    def __set__(self, instance, value, owner=None):
        if instance is None:
            raise TypeError(
                f"Directly set owner {self.__name__!r} attribute"
                f" is not allowed"
            )
            return self

        private_name = self.__private_name__(self.__name__)
        if owner is None:
            owner = type(instance)

        if self.fset is None:
            raise AttributeError(
                f"property {self.__name__!r} of {owner.__name__!r}"
                f" object has no setter",
            )

        if self.typing:
            error = None
            if callable(self.typing):
                try:
                    value = self.typing(value)
                except ValueError as err:
                    error = f"{self.typing.__name__}({value!r})"
            elif not isinstance(value, self.typing):
                types = ', '.join(i.__name__ for i in self.typing[:-1])
                if types:
                    types += " or "
                types += self.typing[-1].__name__
                error = f" expects {types}, not {value}"

            if error:
                raise ValueError(
                    f"property {self.__name__!r} of {owner_name!r} {error}",
                )

        privates = self.__privates__(owner, instance)
        self.fset(instance, privates, value)

    def __delete__(self, instance, owner=None):
        if owner is None:
            owner = type(instance)
        if self.fdel is None:
            raise AttributeError(
                f"property {self.__name__!r} of {owner_name!r}"
                f" object has no deleter",
            )
        if owner is None:
            owner = type(self)

        privates = self.__privates__(owner, instance)
        self.fdel(instance, privates)


def private(prop):
    return PrivateProperty(prop.fget, prop.fset, prop.fdel, prop.__doc__)


private.property = PrivateProperty
private.initialize = initialize_properties


