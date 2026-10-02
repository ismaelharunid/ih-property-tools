
ih-property-tools
=================

A part of the `comprehensive-code-cooker` project.

A set of extended property classes that offer auto initialization,
and truly private attributes via an external namespace.  Additionally,
property factories for simple mutable and non-mutable, private and
normal properties in the sub-module `tools`.  These allow you to
declare all your properties on a single line.

There is example and test code in the github repository, plus
generated document.  Check those out for more details information.
It can (or should be by the time you read this) installed using pip.
There are no dependencies other than having python3.6 or greater
installed in your environment.

ih-property-tools is under the GPL3.0 license and all module source
code is available within the limits of the license.


Installation
------------

pip install ih-property-tools

    or

git clone {git_repository_clone_url}


Usage
-----

There are two extended properties available from proptools for this
version.  These are initialized and private which both can be imported
from the proptools module, or simple import proptools and use them
as proptools.initialized and proptools.private.


### initialized properties

Basic usage for initialized properties, there are 2 variations for
implementation, with simple and moderate complexity.  Note the
decorator for the constructors is optional, but then you must declare
within the class space and call InitializedProperty.__init_properties__
manually from the constructor.  If you planned to manually initialize
your properties in the constructor, you might as well just use the
builtin.property decorator instead.

    ```python
    from proptools import initialized


    class SimplePerson:
        "Using @initialized @property assumes getter, not initializer."

        @initialized
        @property
        def name(self):
            return self._name or "<anonymous>"

        @name.initializer
        def name(self):
            self._name = None

        @name.setter
        def name(self, name):
            self._name = name

        @name.deleter
        def name(self):
            raise NotImplemented(f"Don't make them nameless!")

        @initialized.initialize_all__init__
        def __init__(self):
            pass

    simple_person = SimplePerson()
    print("# simple_person.name", simple_person.name)
    # simple_person.name <anonymous>

    simple_person.name = "Fred"
    print("# simple_person.name", simple_person.name)
    # simple_person.name Fred
    ```

    ```python
    from proptools import initialized


    class ModeratePerson:
        "Using @initialized.property assumes initializer, not getter."

        @initialized.property
        def name(self):
            "initializer for property name."
            self._name = None

        @name.getter
        def name(self):
            "getter for property name."
            return self._name or "<anonymous>"

        @name.setter
        def name(self, name):
            "setter for property name."
            self._name = name

        @name.deleter
        def name(self):
            "deleter for property name."
            raise NotImplemented(f"Don't make them nameless!")

        @initialized.initialize_all__new__
        def __new__(cls):
            return super().__new__(cls)

    moderate_person = ModeratePerson()
    print("# moderate_person.name", moderate_person.name)
    # moderate_person.name <anonymous>

    moderate_person.name = "Lois"
    print("# moderate_person.name", moderate_person.name)
    # moderate_person.name Lois
    ```

### private properties

Private properties use a separate namespace then the instance
they are referenced from, making them truly (or at least much
closer to being) private.  The main difference for private
properties is that the functions: fini, fget, fset and fdel,
all expect both `self` and `private` arguments.  You don't
have to worry about what or where private is, it's out there
in the ether, but available and passed to the wrapper function.
So the initializer would be:

    `def name(self, privates): private.name = None`

or:

    `def name(self, privates, initial=None): private.name = initial`

and the getter would be:

    `def name(self, privates): return private.name`

and the setter would be:

    `def name(self, privates. value): private.name = value`

As with initialized properties, private follow the same convention
of `@private` `@property` creates a private getter, while
`@private.property` creates a private initializer.

    ```python
    from proptools import private


    class SimplePerson:
        "Using @initialized @property assumes getter, not initializer."

        @private
        @property
        def name(self, privates):
            return privates.name or "<anonymous>"

        @name.initializer
        def name(self, privates):
            privates.name = None

        @name.setter
        def name(self, privates, name):
            privates.name = name

        @name.deleter
        def name(self, privates):
            raise NotImplemented(f"Don't make them nameless!")

        @initialized.initialize_all__init__
        def __init__(self):
            pass

    simple_person = SimplePerson()
    print("# simple_person.name", simple_person.name)
    # simple_person.name <anonymous>

    simple_person.name = "Fred"
    print("# simple_person.name", simple_person.name)
    # simple_person.name Fred
    ```

    ```python
    from proptools import private


    class ModeratePerson:
        "Using @initialized.property assumes initializer, not getter."

        @private.property
        def name(self, privates):
            "initializer for property name."
            privates.name = None

        @name.getter
        def name(self, privates):
            "getter for property name."
            return privates.name or "<anonymous>"

        @name.setter
        def name(self, privates, name):
            "setter for property name."
            privates.name = name

        @name.deleter
        def name(self, privates):
            "deleter for property name."
            raise NotImplemented(f"Don't make them nameless!")

        @initialized.initialize_all__new__
        def __new__(cls):
            return super().__new__(cls)

    moderate_person = ModeratePerson()
    print("# moderate_person.name", moderate_person.name)
    # moderate_person.name <anonymous>

    moderate_person.name = "Lois"
    print("# moderate_person.name", moderate_person.name)
    # moderate_person.name Lois
    ```


The `tools` sub-module
----------------------

The tools module has a handful of short-hand property creators,
plus a few helpers for sanity testing.

### `proptools.define_property` for single a property definition

    proptools.define_property(
        "property_name",  # the property access name.
        typing?,  # the property type hinting or casting.
        default?,  # the initial value of the property after initialization.
        private_name?,  # the private name used with the property.
        private_namespace=auto(),  # the namespace used for the private var.
        fini=auto(),  # either None, auto() or an actual initializer.
        fget=auto(),  # either None, auto() or an actual getter.
        fset=auto(),  # either None, auto() or an actual setter.
        fdel=auto(),  # either None, auto() or an actual deleter.
    )

### `proptools.define_properties` for multiple a property definitions

This creates multiple properties of the same type and configuration.

    proptools.define_properties(
        [property definition, ...], see `@tools.define_property`.
        default_typing?,  # the property type hinting or casting.
        auto_fini=auto(),  # True or False for generating initializer.
        auto_fget=auto(),  # True or False for generating getter.
        auto_fset=auto(),  # True or False for generating setter.
        auto_fdel=auto(),  # True or False for generating deleter.
    )


### `proptools.sanity`

When in non-production mode, `sanity` will raise warnings for non-compliant
property behavior. such as getters that don't return a value, or setters,
initializers and deleters that do.  In addition checking that the
initialized value is what is expected.

<example usage with and without auto()>


### `proptools.auto`

`auto` is available from main module, and serves different purposes depending
on where it is used.  Typically, it is used simply as `auto()`, and creates
a symbol which is later processed to fill in or generate auto-values and
methods.

When used in lieu of actual `f` property functions. it auto generates,
the function based on what type it is (fini, fget, fset, fdel).

For property names in namespaces, it generates a the same name as the
property itself, or a sunder version (`name` => `_name`) for non-namespace
(non-private) properties.

For the namespace argument, it creates a secret namespace which is
accessible using the instance as a key retrieve it.

