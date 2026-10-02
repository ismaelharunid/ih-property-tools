

from types import SimpleNamespace


from proptools.helpers import (
    Undef,
    auto,
    debug,
    isauto,
    isundef,
)

from proptools import private


def test_private_property_assign():

    class X:

        p = private.property(
            auto(),
            auto(),
            auto(),
            auto(),
            doc="X is a Test prop.",
            initial=None,
        )

        def __init__(self):
            private.initialize(self)

    assert hasattr(X, "p")
    assert isinstance(X.p, property)
    assert isinstance(X.p, private.property)
    assert X.p.fini
    assert X.p.fget
    assert X.p.fset
    assert X.p.fdel
    assert X.p.private_name == "p"
    assert X.p.__name__ == "p"
    assert X.p.__doc__ == "X is a Test prop."

    x = X()
    assert x.p is None

    x.p = "Wookie"
    assert x.p == "Wookie"

    del x.p
    assert x.p is None


def test_private_dot_property():

    class X:

        @private.property
        def a(self, privates, initial=None):
            privates.a = 0

        @a.getter
        def a(self, privates):
            return privates.a

        def __init__(self):
            private.initialize(self)

    x = X()
    assert x.a == 0

