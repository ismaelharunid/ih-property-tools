

from types import SimpleNamespace


from proptools.helpers import (
    Undef,
    auto,
    auto_fini,
    auto_fget,
    auto_fset,
    auto_fdel,
    debug,
    isundef,
)


def test_auto():

    a = auto()
    assert isinstance(a, auto)
    assert a.value is None

    b = auto("tag")
    assert isinstance(b, auto)
    assert b.value == "tag"


def test_auto_fget_name_only():

    self = SimpleNamespace()
    self._identity = "Ayu"
    fget = auto_fget("identity")
    debug("fget", fget)
    assert callable(fget)
    r = fget(self)
    assert r == "Ayu"
    assert self._identity == "Ayu"


def test_auto_fget_name_private_name():

    self = SimpleNamespace()
    self._private_identity = "Iluh"
    fget = auto_fget("identity", "_private_identity")
    debug("fget", fget)
    assert callable(fget)
    r = fget(self)
    assert r == "Iluh"
    assert self._private_identity == "Iluh"


def test_auto_fget_name_namespace_str():

    self = SimpleNamespace()
    privates = SimpleNamespace()
    privates.identity = "Wayan"
    fget = auto_fget("identity", private_namespace="private_namespace")
    debug("fget", fget)
    assert callable(fget)
    r = fget(self, privates)
    assert r == "Wayan"
    assert privates.identity == "Wayan"


def test_auto_fget_name_namespace():

    self = SimpleNamespace()
    privates = SimpleNamespace()
    privates.identity = "Lia"
    fget = auto_fget("identity", private_namespace=privates)
    debug("fget", fget)
    assert callable(fget)
    r = fget(self)
    assert r == "Lia"
    assert privates.identity == "Lia"


def test_auto_fset_name_only():

    self = SimpleNamespace()
    fset = auto_fset("identity")
    debug("fset", fset)
    assert callable(fset)
    r = fset(self, "Fred")
    assert r is None
    assert self._identity == "Fred"


def test_auto_fset_name_private_name():

    self = SimpleNamespace()
    fset = auto_fset("identity", "_private_identity")
    debug("fset", fset)
    assert callable(fset)
    r = fset(self, "Fred")
    assert r is None
    assert self._private_identity == "Fred"


def test_auto_fset_name_namespace_str():

    self = SimpleNamespace()
    privates = SimpleNamespace()
    fset = auto_fset("identity", private_namespace="private_namespace")
    debug("fset", fset)
    assert callable(fset)
    r = fset(self, privates, "Fred")
    assert r is None
    assert privates.identity == "Fred"


def test_auto_fset_name_private_name_namespace_str():

    self = SimpleNamespace()
    privates = SimpleNamespace()
    fset = auto_fset(
        "identity",
        "private_identity",
        private_namespace="private_namespace",
    )
    debug("fset", fset)
    assert callable(fset)
    r = fset(self, privates, "Fred")
    assert r is None
    assert privates.private_identity == "Fred"

def test_auto_fset_name_namespace():

    self = SimpleNamespace()
    privates = SimpleNamespace()
    fset = auto_fset("identity", private_namespace=privates)
    debug("fset", fset)
    assert callable(fset)
    r = fset(self, "Fred")
    assert r is None
    assert privates.identity == "Fred"


def test_auto_fset_name_private_name_namespace():

    self = SimpleNamespace()
    privates = SimpleNamespace()
    fset = auto_fset(
        "identity",
        "private_identity",
        private_namespace=privates,
    )
    debug("fset", fset)
    assert callable(fset)
    r = fset(self, "Fred")
    assert r is None
    assert privates.private_identity == "Fred"


def test_auto_fset_typing():

    fset = auto_fset("identity", "_identity", [str])
    print("fset", fset)
    assert callable(fset)
    self = SimpleNamespace()
    r = fset(self, "Fred")
    assert r is None
    assert self._identity == "Fred"


def test_auto_fset_cast():

    def Identifier(value):
        if value and isinstance(value, str) and value.isidentifier():
            if not (value.startswith("_") or value.endswith("_")):
                return value
        raise TypeError(f"`value` expects an Identifier, not {value!r}")

    fset = auto_fset("identity", "_identity", Identifier)
    print("fset", fset)
    assert callable(fset)
    self = SimpleNamespace()
    r = fset(self, "Fred")
    assert r is None
    assert self._identity == "Fred"


def test_auto_fini_name_only():

    self = SimpleNamespace()
    fini = auto_fini("identity")
    debug("fini", fini)
    assert callable(fini)
    r = fini(self)
    assert r is None
    assert self._identity is None


def test_auto_fini_name_private_name():

    self = SimpleNamespace()
    fini = auto_fini("identity", "_private_identity")
    debug("fini", fini)
    assert callable(fini)
    r = fini(self)
    assert r is None
    assert self._private_identity is None


def test_auto_fini_name_initial():

    self = SimpleNamespace()
    fini = auto_fini("identity", initial_value="<anonymous>")
    debug("fini", fini)
    assert callable(fini)
    r = fini(self)
    assert r is None
    assert self._identity == "<anonymous>"


def test_auto_fini_name_private_name_initial():

    self = SimpleNamespace()
    fini = auto_fini(
        "identity",
        "_private_identity",
        initial_value="<anonymous>"
    )
    debug("fini", fini)
    assert callable(fini)
    r = fini(self)
    assert r is None
    assert self._private_identity == "<anonymous>"


def test_auto_fini_name_namespace_str_initial():

    self = SimpleNamespace()
    privates = SimpleNamespace()
    fini = auto_fini(
        "identity",
        private_namespace="private_namespace",
        initial_value="Lois",
    )
    debug("fini", fini)
    assert callable(fini)
    r = fini(self, privates)
    assert r is None
    assert privates.identity == "Lois"


def test_auto_fini_name_namespace():

    self = SimpleNamespace()
    privates = SimpleNamespace()
    fini = auto_fini("identity", private_namespace=privates)
    debug("fini", fini)
    assert callable(fini)
    r = fini(self)
    assert r is None
    assert privates.identity is None


def test_auto_fdel_name_only():

    self = SimpleNamespace()
    self._identity = "Ayu"
    fdel = auto_fdel("identity")
    debug("fdel", fdel)
    assert callable(fdel)
    r = fdel(self)
    assert r is None
    assert isundef(getattr(self, "_identity", Undef))


def test_auto_fdel_name_private_name():

    self = SimpleNamespace()
    self._private_identity = "Iluh"
    fdel = auto_fdel("identity", "_private_identity")
    debug("fdel", fdel)
    assert callable(fdel)
    r = fdel(self)
    assert r is None
    assert isundef(getattr(self, "_private_identity", Undef))


def test_auto_fdel_name_namespace_str():

    self = SimpleNamespace()
    privates = SimpleNamespace()
    privates.identity = "Wayan"
    fdel = auto_fdel("identity", private_namespace="private_namespace")
    debug("fdel", fdel)
    assert callable(fdel)
    r = fdel(self, privates)
    assert r is None
    assert isundef(getattr(privates, "identity", Undef))


def test_auto_fdel_name_namespace():

    self = SimpleNamespace()
    privates = SimpleNamespace()
    privates.identity = "Lia"
    fdel = auto_fdel("identity", private_namespace=privates)
    debug("fdel", fdel)
    assert callable(fdel)
    r = fdel(self)
    assert r is None
    assert isundef(getattr(privates, "identity", Undef))


def test_isundef():
    assert isundef(Undef) is True
    assert isundef(None) is False
    assert isundef(False) is False
    assert isundef(0) is False
    assert isundef("text") is False
    assert isundef(list) is False
