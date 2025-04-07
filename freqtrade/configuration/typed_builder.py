from __future__ import annotations

import abc
import dataclasses
import enum
import shutil
import subprocess
import textwrap
import types
import typing
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

from freqtrade.configuration.config_schema import CONF_SCHEMA
from freqtrade.constants import Config


def snake_case_to_pascal_case(snake_str: str) -> str:
    """Convert snake_case to PascalCase."""
    components = snake_str.split("_")
    return "".join(word.capitalize() for word in components)


class ConfigShim(dict[str, typing.Any]):
    """Base config class, providing backwards compatability with the flat dictionary approach."""

    def __post_init__(self):
        dict.__init__(self, self._config)

    def __setitem__(self, key, value):
        raise TypeError("config is assumed to be immutable so items cannot be set")

    def setdefault(self, key, default=None):
        raise TypeError("config is assumed to be immutable so items cannot be set")

    def __delitem__(self, key):
        raise TypeError("config is assumed to be immutable so items cannot be removed")

    def popitem(self):
        raise TypeError("config is assumed to be immutable so items cannot be removed")

    def pop(self, __key):
        raise TypeError("config is assumed to be immutable so items cannot be removed")


class Accessor(enum.Enum):
    """Enum of the ways that elements are accessed within a path."""

    DEFINITION = enum.auto()
    """The definition comes from a shared definition at the top level of the schema."""
    VALUE = enum.auto()
    """The definition comes from a properties on an object in the schema."""
    LIST_ELEMENTS = enum.auto()
    """The definition comes from the items of an array time in the schema."""
    DICT_VALUES = enum.auto()
    """The definition comes from the additionalProperties of an object type in the schema."""


T = typing.TypeVar("T")


class Undefined: ...


UNDEFINED = Undefined()


@dataclasses.dataclass(frozen=True)
class Type(abc.ABC):
    """Base class for the types from the JSON Schema"""

    path: list[str]
    """A path which starts with root_config or the name of a common definition, followed by names or
    '*' for variable dicts/lists."""
    description: str | None
    """Description to include in a docstring."""
    default: typing.Any | Undefined

    @abc.abstractmethod
    def visit_types(self, visitor: typing.Callable[[Type], T]) -> typing.Iterator[T]:
        """Depth-first traversal of the type tree."""

    @property
    @abc.abstractmethod
    def type_annotation(self) -> str:
        """Python annotation string for this type."""


@dataclasses.dataclass(frozen=True)
class Class(Type):
    description: str
    members: dict[str, Type]
    required: frozenset[str]

    def visit_types(self, visitor: typing.Callable[[Type], T]) -> typing.Iterator[T]:
        """Depth-first traversal of the type tree."""
        for member in self.members.values():
            yield from member.visit_types(visitor)
        yield visitor(self)

    @property
    def type_annotation(self) -> str:
        """Python type name."""
        # the number of "*" at the end of the path
        nest_level = 0
        for step in self.path[::-1]:
            if step != "*":
                last_named_step = step
                break
            nest_level += 1
        else:
            raise ValueError(f"no named part in path {self.path}")
        return snake_case_to_pascal_case(last_named_step) + ("Element" * nest_level)


@dataclasses.dataclass(frozen=True)
class Dict(Type):
    """Comes out as something like a dict[str, T]."""

    values: Type

    def visit_types(self, visitor: typing.Callable[[Type], T]) -> typing.Iterator[T]:
        """Depth-first traversal of the type tree."""
        yield visitor(self.values)
        yield visitor(self)

    @property
    def type_annotation(self) -> str:
        """Python type name."""
        return f"dict[str, {self.values.type_annotation}]"


@dataclasses.dataclass(frozen=True)
class List(Type):
    """Comes out as something like a list[T]."""

    elements: Type

    def visit_types(self, visitor: typing.Callable[[Type], T]) -> typing.Iterator[T]:
        """Depth-first traversal of the type tree."""
        yield visitor(self.elements)
        yield visitor(self)

    @property
    def type_annotation(self) -> str:
        """Python type name."""
        return f"list[{self.elements.type_annotation}]"


@dataclasses.dataclass(frozen=True)
class Scalar(Type):
    """Some other type, assuming no further"""

    type: type

    def visit_types(self, visitor: typing.Callable[[Type], T]) -> typing.Iterator[T]:
        """Depth-first traversal of the type tree."""
        yield visitor(self)

    @property
    def type_annotation(self) -> str:
        """Python type name."""
        if isinstance(self.type, type):
            # things like str, int, dict, list, etc.
            return self.type.__name__
        # things like typing.Literal[...],
        return repr(self.type)


@dataclasses.dataclass(frozen=True)
class Union(Type):
    alternatives: list[Type]

    def visit_types(self, visitor: typing.Callable[[Type], T]) -> typing.Iterator[T]:
        """Depth-first traversal of the type tree."""
        for alternative in self.alternatives:
            yield from alternative.visit_types(visitor)
        yield visitor(self)

    @property
    def type_annotation(self) -> str:
        """Python type name."""
        return " | ".join(alternative.type_annotation for alternative in self.alternatives)


class ConfigTypeBuilder:
    """Tool to construct a final RootConfig instance from a dictionary of config and the schema.

    This aims to work with the ConfigShim class to provide a low-impact migration path from dict
    based config to typed classes, allowing the new approach to be slowly rolled out and then
    old approach can be deprecated and finally removed with the config classes becoming the
    canonical source of typing.
    """

    def __init__(self, /, root_schema: dict = CONF_SCHEMA):
        self.root_schema = root_schema
        self.root_type = self._build_root_type()

    def render_python_source(self) -> str:
        """Render the source for a module containing typed config."""
        preamble = textwrap.dedent("""\
            from __future__ import annotations

            import dataclasses
            import typing

            from freqtrade.configuration.typed_builder import ConfigShim
        """)
        root_type = self.root_type
        return _maybe_reformat(
            "\n\n".join(
                [preamble, *(chunk for chunk in root_type.visit_types(_render_class) if chunk)]
            )
        )

    def root_config_from_dict(
        self,
        config: Config,
        /,
        module: types.ModuleType | None = None,
    ) -> T:
        """Return a RootConfig instance.

        :param config: config dictionary to populate values from
        :param module: non-default module to use, only used in tests
        """
        if module is None:
            from freqtrade.configuration import typed as module

        return _construct_from_dict(module, self.root_type, config, ["."])

    def _build_root_type(self) -> Class:
        """Build a typed config instance from the given weakly-typed config dict."""
        result = self._build_type(["root_config"], self.root_schema)
        if not isinstance(result, Class):
            raise ValueError(
                f"{result} is not an instance of {Class.__name__} - assumed the root"
                " schema would be for an object with properties"
            )
        self._verify_unique_class_names(result)
        self._verify_simple_unions(result)
        return result

    def _build_type(self, path: list[str], schema: dict) -> Type:
        """
        :param path: path into the root schema/config that the current schema/config is for
        :param schema: (sub)schema for the current path
        """
        nested_path = None
        description = schema.get("description")
        default = schema.get("default", UNDEFINED)
        try:
            match schema:
                case {"type": "object", "properties": properties}:
                    required = frozenset(schema.get("required", []))
                    members = {}
                    for property_name, property_schema in properties.items():
                        nested_path = path + [property_name]
                        members[property_name] = self._build_type(nested_path, property_schema)
                    nested_path = None
                    return Class(path, description, default, members, required)
                case {"type": "object", "additionalProperties": value_schema} if (
                    value_schema is not False
                ):
                    # this will be something like dict[str, T]
                    nested_path = path + ["*"]
                    value_type = self._build_type(nested_path, value_schema)
                    nested_path = None
                    return Dict(path, description, default, value_type)
                case {"type": "array", "items": element_schema}:
                    # this will be list[T]
                    nested_path = path + ["*"]
                    element_type = self._build_type(nested_path, element_schema)
                    nested_path = None
                    return List(path, description, default, element_type)
                case {"$ref": ref}:
                    key = ref.removeprefix("#/definitions/")
                    # reset the path so the generated name reflects the definition name, not where
                    # it is used, as that could in theory be in multiple places with each using a
                    # different name
                    path = [key]
                    return self._build_type(path, self.root_schema["definitions"][key])
                case {"type": [*types_]}:
                    # this is assuming that all union types are comprised of scalars
                    alternate_schema = schema.copy()
                    alternatives = []
                    for type_ in types_:
                        alternate_schema["type"] = type_
                        alternatives.append(self._build_type(path, alternate_schema))
                    return Union(path, description, default, alternatives)
                case {"type": "string", "enum": choices}:
                    # ~special case of string
                    return Scalar(path, description, default, typing.Literal[*choices])
                case {"type": type_} | {"format": type_}:
                    return Scalar(path, description, default, self._PRIMITIVE_TYPE_MAP[type_])
                case _:
                    raise NotImplementedError(f"unhandled schema: {schema}")
        except Exception as e:
            raise ValueError(f"Unable to build config for {nested_path=} {path=}") from e

    _PRIMITIVE_TYPE_MAP = {
        "array": list,
        "boolean": bool,
        "integer": int,
        "ipv4": str,  # defined by `"format": "ipv4"` instead of something like `"type": "ipv4"`
        "number": float,
        "object": dict,
        "string": str,
    }
    """Python type for a JSON Schema scalar type."""

    @staticmethod
    def _verify_simple_unions(root_type: Type):
        """Unions are assumed to be simple as it avoids trying parsing complexities."""
        for union in root_type.visit_types(lambda t: t if isinstance(t, Union) else None):
            if union is None:
                continue
            if count := sum(union.visit_types(lambda t: isinstance(t, Class))):
                raise NotImplementedError(
                    "Dict parsing logic assumes that unions do not contain"
                    f" nested classes, but found {count} under {union.path}"
                )

    @staticmethod
    def _verify_unique_class_names(root_type: Type):
        """Classes have unique annotation names, based on assumptions."""
        class_annotation_to_type = defaultdict(dict)
        for cls in root_type.visit_types(lambda t: t if isinstance(t, Class) else None):
            if cls is None:
                continue
            class_annotation_to_type[cls.type_annotation][id(cls)] = cls
        if issues := {
            cls_name: types
            for cls_name, types in class_annotation_to_type.items()
            if len(types) > 1
        }:
            raise ValueError(f"Found different types with the conflicting class names: {issues}")


def _render_docstring(docstring: str) -> str:
    """Return a docstring with a single level of indentation."""
    return f'    """{docstring.replace("\n", "\n    ")}"""'


def _render_class(cls: Type) -> str:
    """Render a class into string form that can be evaluated in the context of the typed module."""
    if not isinstance(cls, Class):
        return ""
    # TODO: look at using dataclass(init=False) to see if that would tidy the interface
    lines = [
        "@dataclasses.dataclass(frozen=True, slots=True)",
        f"class {cls.type_annotation}(ConfigShim):",
        "    _config: dict[str, typing.Any]",
    ]
    if cls.description:
        lines.append(_render_docstring(cls.description))
    for name, member in cls.members.items():
        if not (
            name in cls.required
            or (cls.default is not UNDEFINED and name in cls.default)
            or member.default not in (UNDEFINED, None)
        ):
            extra_annotation = " | None"
        else:
            extra_annotation = ""
        lines.append(f"    {name}: {member.type_annotation}{extra_annotation}")
        if member.description:
            # use Sphinx style docstrings which are picked up by some IDEs
            lines.append(_render_docstring(member.description))
    return "\n".join(lines)


def _construct_from_dict(
    module: types.ModuleType,
    type_: Type,
    config: object,
    path: list[str],
) -> object:
    """Build a config object from the dictionary form and its distilled schema."""
    # handle defaulting here
    if config is None:
        return None
    if config is UNDEFINED and type_.default is not UNDEFINED:
        return _construct_from_dict(module, type_, deepcopy(type_.default), path)
    match type_:
        case Class(members=members, required=required, default=default):
            if not isinstance(config, dict):
                raise ValueError(f"Expected a dict at {path} but got {type(config)}")
            cls = getattr(module, type_.type_annotation)
            kwargs = {"_config": config}
            for member_name, member_type in members.items():
                nested_path = path + [member_name]
                if member_name not in config:
                    # TODO: check this is reasonable/expected behaviour, as it effectively merges
                    #  the given value with the default
                    if default is UNDEFINED:
                        member_default = UNDEFINED
                    else:
                        member_default = default.get(member_name, UNDEFINED)
                    if (
                        member_name in required
                        and member_default is UNDEFINED
                        and member_type.default is UNDEFINED  # default may come from lower down
                    ):
                        raise ValueError(f"Missing required value for {nested_path}")
                    if member_default is UNDEFINED:
                        member_config = None
                    else:
                        member_config = deepcopy(member_default)
                else:
                    member_config = config[member_name]
                kwargs[member_name] = _construct_from_dict(
                    module, member_type, member_config, nested_path
                )
            return cls(**kwargs)
        case List(elements=element_type):
            if not isinstance(config, list):
                raise ValueError(f"Expected a list at {path} but got {type(config)}")
            return [
                _construct_from_dict(module, element_type, element, path + [i])
                for i, element in enumerate(config or [])
            ]
        case Dict(values=value_type):
            if not isinstance(config, dict):
                raise ValueError(f"Expected a dict at {path} but got {type(config)}")
            return {
                _construct_from_dict(module, value_type, value, path + [key])
                for key, value in config.items()
            }
        case Union():
            # no type validation on as assuming that is already done in the dict creation, and
            # the assumption that the union does not need further parsing of classes is done by
            # the ConfigTypeBuilder
            return config
        case Scalar():
            return config


def _maybe_reformat(code: str) -> str:
    """If ruff is available, format the given string with it."""
    if shutil.which("ruff") is None:
        # this should be installed in the dev environment
        return code
    result = subprocess.run(
        ["ruff", "format", "--stdin-filename", "config.py", "-"],
        input=code,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def rebuild_typed():
    """Write out the types.py file to reflect the schema."""
    typed_path = Path(__file__).parent / "typed.py"
    typed_path.write_text(ConfigTypeBuilder().render_python_source())


if __name__ == "__main__":
    rebuild_typed()
