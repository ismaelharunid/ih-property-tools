
"""
<ih-property-tools>/src/proptools/__init__.py

Added support for properties,

"""

__all__ = [
    "auto",
    "auto_fini",
    "auto_fget",
    "auto_fset",
    "auto_fdel",
    "private",
    "quick",
    "isauto",
    "isundef",
]


from .private_properties import private
from .quick_properties import quick
from .helpers import auto, isauto, isundef
from .helpers import auto_fini, auto_fget, auto_fset, auto_fdel


