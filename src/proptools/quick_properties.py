
"""
<ih-property-tools>/src/proptools/quick_properties.py

Extended Property class and wrappers,

"""


all = [
    "quick",
]


import os, sys, warnings

from collections.abc import Iterable
from functools import cache, cached_property, wraps
from types import MappingProxyType, SimpleNamespace
from typing import Any, Callable, NoReturn, Optional, Self


from . import helpers


class Property(property): ...  # declaration only


class Property(property):
    "Emulate an enhanced PyProperty_Type() in Objects/descrobject.c"

    fini: Optional[Callable | helpers.auto] = None
    fget: Optional[Callable | helpers.auto] = None
    fset: Optional[Callable | helpers.auto] = None
    fdel: Optional[Callable | helpers.auto] = None
    initial: Any = helpers.Undef
    private_name: Optional[str] = None
    typing: Optional[tuple[type, ...] | Callable] = None

    def __init__(
        self: Self,
        fini: Optional[Callable | helpers.auto] = None,
        fget: Optional[Callable | helpers.auto] = None,
        fset: Optional[Callable | helpers.auto] = None,
        fdel: Optional[Callable | helpers.auto] = None,
        doc: Optional[str] = None,
        typing: Optional[tuple[type, ...] | Callable] = None,
        private_name: Optional[str] = None,
        initial: Optional[Any] = helpers.Undef,
    ) -> NoReturn:
        "Initializer for the Property itself."

        #
        # Validate arguments
        #

        if fini:
            if not (isinstance(fini, helpers.auto) or callable(fini)):
                raise TypeError(
                    f"fini expects a callable, auto or None, not {fini!r}")
        else:
            fini = None

        if fget:
            if not (isinstance(fget, helpers.auto) or callable(fget)):
                raise TypeError(
                    f"fget expects a callable, auto or None, not {fget!r}")
        else:
            fget = None

        if fset:
            if not (isinstance(fset, helpers.auto) or callable(fset)):
                raise TypeError(
                    f"fset expects a callable, auto or None, not {fset!r}")
        else:
            fset = None

        if fset:
            if not (isinstance(fset, helpers.auto) or callable(fset)):
                raise TypeError(
                    f"fset expects a callable, auto or None, not {fset!r}")
        else:
            fset = None

        if fdel:
            if not (isinstance(fdel, helpers.auto) or callable(fdel)):
                raise TypeError(
                    f"fdel expects a callable, auto or None, not {fdel!r}")
        else:
            fdel = None

        if doc is None:
            if fini is not None and fini.__doc__:
                doc = fini.__doc__
            elif fget is not None and fget.__doc__:
                doc = fget.__doc__

        if typing:
            if callable(typing):
                typing_ = typing
            elif isinstance(typing, Iterable):
                typing_ = tuple(typing)
                for i, t in enumerate(typing_):
                    if not isinstance(t, type):
                        raise TypeError(
                            f"expect a type for typing[{i}], not {t!r}")
        else:
            typing_ = None

        if private_name:
            if not (
                isinstance(private_name, str)
                and private_name.isidentifier()
            ):
                raise TypeError(
                    f"private_name expects an identifier or None"
                    f", not {private_name!r}",
                )
        else:
            private_name = None

        # set the attributes from arguments given
        self.fdel = fdel
        self.fget = fget
        self.fini = fini
        self.fset = fset
        self.__doc__ = doc
        self.typing = typing_
        self.initial = initial
        self.private_name = private_name

    def __auto__(self, owner):
        "Expand auto fxxx' and return list, or None if no expansion."
        dirty = False

        fini = self.fini
        if helpers.isauto(self.fini):
            fini = self.__auto_fini__(owner)
            dirty = True

        fget = self.fget
        if helpers.isauto(self.fget):
            fget = self.__auto_fget__(owner)
            dirty = True

        fset = self.fset
        if helpers.isauto(self.fset):
            fset = self.__auto_fset__(owner)
            dirty = True

        fdel = self.fdel
        if helpers.isauto(self.fdel):
            fdel = self.__auto_fdel__(owner)
            dirty = True

        return dirty, [fini, fget, fset, fdel]

    def __auto_fini__(self, owner):
        "expand auto fini."
        def make(private_name, initial):
            def fini(self, value = initial):
                setattr(self, private_name, value)

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
            def fget(self):
                return getattr(self, private_name, initial)

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
            def fset(self, value):
                setattr(self, private_name, value)

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
            def fdel(self, value = initial):
                delattr(self, private_name)

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
        return instance

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
            private_name = "_" + name
        return private_name

    def __set_name__(self, owner, name):
        "Post class-definition call to set name and expand autos."
        self.__name__ = name
        self.private_name = self.__private_name__(name, self.private_name)

        dirty, (fini, fget, fset, fdel) = self.__auto__(owner)
        if dirty:
            cls = type(self)
            prop = cls(
                fini=fini,
                fget=fget,
                fset=fset,
                fdel=fdel,
                doc=self.__doc__,
                typing=self.typing,
                initial=self.initial,
                private_name=self.private_name,
            )
            prop.__name__ = name
            setattr(owner, name, prop)  # sets updated property in owner

    def __initialize__(self, instance, owner=None):
        if instance is None:
            if owner is None:
                raise AttributeError(
                    f"Cannot initialize {self.private_name!r}"
                    f" for property {self.__name__!r}",
                )
            setattr(owner, self.private_name, self.initial)
            return

        if owner is None:
            owner = type(instance)

        if self.fini is None:
            raise AttributeError(
                f"property {self.__name__!r} of {owner.__name__!r}"
                f" object has no initializer",
            )

        self.fini(instance, self.initial)

    def __get__(self, instance, owner=None):
        if instance is None:
            # return the property, same as getattr(owner, name).
            return self

        if self.fget is None:
            raise AttributeError(
                f"property {self.__name__!r} of {owner_name!r}"
                f" object has no getter",
            )

        value = self.fget(instance)
        if helpers.isundef(value):
            oname = type(instance).__name__
            raise AttributeError(
                f"{name!r} of {oname!r} is undefined",
            )

        return value

    def __set__(self, instance, value):
        owner_name = type(instance).__name__
        if self.fset is None:
            raise AttributeError(
                f"property {self.__name__!r} of {owner_name!r}"
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

        self.fset(instance, value)

    def __delete__(self, instance, owner=None):
        owner_name = type(instance).__name__
        if self.fdel is None:
            raise AttributeError(
                f"property {self.__name__!r} of {owner_name!r}"
                f" object has no deleter",
            )

        self.fdel(instance)

    def initializer(self, fini):
        return type(self)(
            fini=fini,
            fget=self.fget,
            fset=self.fset,
            fdel=self.fdel,
            doc=self.__doc__,
            typing=self.typing,
            initial=self.initial,
            private_name=self.private_name,
        )

    def getter(self, fget):
        return type(self)(
            fini=self.fini,
            fget=fget,
            fset=self.fset,
            fdel=self.fdel,
            doc=self.__doc__,
            typing=self.typing,
            initial=self.initial,
            private_name=self.private_name,
        )

    def setter(self, fset):
        return type(self)(
            fini=self.fini,
            fget=self.fget,
            fset=fset,
            fdel=self.fdel,
            doc=self.__doc__,
            typing=self.typing,
            initial=self.initial,
            private_name=self.private_name,
        )

    def deleter(self, fdel):
        return type(self)(
            fini=self.fini,
            fget=self.fget,
            fset=self.fset,
            fdel=fdel,
            doc=self.__doc__,
            typing=self.typing,
            initial=self.initial,
            private_name=self.private_name,
        )


def _iter_initializers(owner: type) -> Iterable[Property]:
    "yield all or owner properties with initializers "
    for attr in vars(owner).values():
        if isinstance(attr, Property):
            if attr.fini:
                yield attr


def initialize_properties(
    self: Self,
    owner: Optional[type]=None,
    properties: Optional[Iterable[Property]]=None,
):
    if owner is None:
        if self is None:
            raise TypeError(f"owner cannot be None is self is None.")

        owner = type(self)

    if properties is None:
        properties = _iter_initializers(owner)

    for prop in properties:
        prop.__initialize__(self, owner)


def quick(prop):
    return Property(prop.fget, prop.fset, prop.fdel, prop.__doc__)


quick.property = Property
quick.initialize = initialize_properties


