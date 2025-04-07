import sys
import textwrap
import types
from pathlib import Path

import pytest

from freqtrade.configuration import typed, typed_builder
from freqtrade.configuration.typed_builder import ConfigShim


def test_verify_class_names():
    """Non-unique class names results in a failure."""
    # there are two members with the name "conflicting_member_class" that refer to different classes
    # so they generate conflicting names
    schema = {
        "type": "object",
        "properties": {
            "conflicting_member_class": {
                "type": "object",
                "properties": {},
            },
            "nested_class_2": {
                "type": "object",
                "properties": {
                    "conflicting_member_class": {
                        "type": "object",
                        "properties": {},
                    },
                },
            },
        },
    }
    with pytest.raises(
        ValueError, match="^Found different types with the conflicting class names: "
    ):
        typed_builder.ConfigTypeBuilder(schema)._build_root_type()


def test_verify_simple_unions():
    """Unions with come Class under them results in a failure."""
    schema = {
        "type": "object",
        "properties": {
            "trouble_union": {
                "type": ["object", "integer"],
                "properties": {},
            },
        },
    }
    with pytest.raises(
        NotImplementedError,
        match=r"^Dict parsing logic assumes that unions do not contain nested"
        r" classes, but found 1 under \['root_config', 'trouble_union'\]$",
    ):
        typed_builder.ConfigTypeBuilder(schema)


def module_from_schema(
    monkeypatch,
    schema: dict,
) -> tuple[typed_builder.ConfigTypeBuilder, types.ModuleType]:
    """Construct a module from the schema."""
    builder = typed_builder.ConfigTypeBuilder(schema)
    root_type = builder.root_type
    rendered = builder.render_python_source()

    # load the module so it can be used
    module = types.ModuleType("test_rendering")
    monkeypatch.setitem(sys.modules, "test_rendering", module)
    bytecode = compile(rendered, filename="test_rendering", mode="exec")
    exec(bytecode, module.__dict__)

    return builder, module


def test_required_parameters(monkeypatch):
    """Omission of a required parameter that does not have a default results in a failure."""
    schema = {
        "type": "object",
        "properties": {
            "required_1": {"type": "number"},
        },
        "required": ["required_1"],
    }
    builder, module = module_from_schema(monkeypatch, schema)
    # omitting a required field that does not have a default will result in an exception
    with pytest.raises(
        ValueError,
        match=r"^Missing required value for \['.', 'required_1'\]$",
    ):
        builder.root_config_from_dict({}, module=module)
    # parsing a required field in is ok
    builder.root_config_from_dict({"required_1": 2.0}, module=module)


@pytest.mark.parametrize("required", [True, False], ids=["required", "optional"])
def test_defaulting_parameters(monkeypatch, required: bool):
    """Omission of any parameter with a default results in a copy of the default being used."""
    schema = {
        "type": "object",
        "properties": {
            "member": {"type": "object"},
        },
        "required": ["member"] if required else [],
        "default": {"member": {"junk": 1}},
    }
    builder, module = module_from_schema(monkeypatch, schema)

    # omitting a required field that does not have a default will result in an exception
    result = builder.root_config_from_dict({}, module=module)
    assert result.member == schema["default"]["member"]
    # the defaults are deep copies
    assert result.member is not schema["default"]["member"]

    # parsing a required field in is ok
    config = {"member": {"chosen": True}}
    result = builder.root_config_from_dict(config, module=module)
    # explicitly provided config values are taken as is
    assert result.member is config["member"]


def test_rendering(monkeypatch):
    """Rendered code is valid python and class annotations can be used to look up types."""
    schema = {
        "type": "object",
        "properties": {
            "field_1": {"type": "string"},
            "nested_class_1": {
                "type": "object",
                "properties": {
                    "nested_field_1": {"type": "integer"},
                },
            },
        },
    }
    builder, module = module_from_schema(monkeypatch, schema)

    root_cls = getattr(module, builder.root_type.type_annotation)
    assert issubclass(root_cls, ConfigShim)
    nested_cls = getattr(module, builder.root_type.members["nested_class_1"].type_annotation)
    assert issubclass(nested_cls, ConfigShim)


def test_rendered_optionals(monkeypatch):
    """Optional values show as nullable."""
    schema = {
        "type": "object",
        "properties": {
            "nullable": {"type": "integer"},
            "nullable_enum": {"type": "string", "enum": ["first", "second"]},
            # default comes from inner type
            "default1": {"type": "integer", "default": 1},
            # default comes from the container type
            "default2": {"type": "integer"},
        },
        "required": ["required"],
        "default": {"default2": 2},
    }
    builder, module = module_from_schema(monkeypatch, schema)

    source = builder.render_python_source()
    assert source == textwrap.dedent("""\
        from __future__ import annotations

        import dataclasses
        import typing

        from freqtrade.configuration.typed_builder import ConfigShim


        @dataclasses.dataclass(frozen=True, slots=True)
        class RootConfig(ConfigShim):
            _config: dict[str, typing.Any]
            nullable: int | None
            nullable_enum: typing.Literal["first", "second"] | None
            default1: int
            default2: int
    """)


def test_typed_up_to_date():
    """types.py is up to date with the rendering that would be produced from the schema."""
    source = typed_builder.ConfigTypeBuilder().render_python_source()
    assert Path(typed.__file__).read_text() == source, "rebuild_typed() call required"
