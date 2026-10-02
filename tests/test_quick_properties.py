

from types import SimpleNamespace


from proptools.helpers import (
    Undef,
    auto,
    debug,
    isauto,
    isundef,
)

from proptools import quick


def test_quick_property_assign():

    class X:

        p = quick.property(
            auto(),
            auto(),
            auto(),
            auto(),
            doc="X is a Test prop.",
            initial=None,
        )

        def __init__(self):
            quick.initialize(self)

    assert hasattr(X, "p")
    assert isinstance(X.p, property)
    assert isinstance(X.p, quick.property)
    assert X.p.fini
    assert X.p.fget
    assert X.p.fset
    assert X.p.fdel
    assert X.p.private_name == "_p"
    assert X.p.__name__ == "p"
    assert X.p.__doc__ == "X is a Test prop."

    x = X()
    #assert isundef(x._p)
    assert x.p is None

    x.p = "Wookie"
    assert x._p == "Wookie"
    assert x.p == "Wookie"

    del x.p
    try:
        assert x._p is None
    except:
        pass
    assert x.p is None


