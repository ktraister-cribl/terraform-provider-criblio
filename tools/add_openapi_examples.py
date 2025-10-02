#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq


def generate_example(schema: Any) -> Any:
    if not isinstance(schema, CommentedMap):
        return "string"

    # Prefer default or enum where present
    if "default" in schema:
        return schema["default"]
    if "enum" in schema:
        enum_values = schema.get("enum")
        if isinstance(enum_values, list) and enum_values:
            return enum_values[0]

    # Avoid adding example adjacent to $ref-only schemas
    if "$ref" in schema and len(schema.keys()) == 1:
        return None

    schema_type = schema.get("type")
    schema_format = schema.get("format")

    # Strings
    if schema_type == "string" or (
        schema_type is None
        and not any(k in schema for k in ("properties", "items", "allOf", "oneOf", "anyOf"))
    ):
        if schema_format == "email":
            return "user@example.com"
        if schema_format == "uuid":
            return "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        if schema_format in ("date",):
            return "2025-01-01"
        if schema_format in ("date-time", "datetime"):
            return "2025-01-01T12:34:56Z"
        if schema_format in ("uri", "url"):
            return "https://example.com/resource"
        if schema_format == "hostname":
            return "example.com"
        if schema_format == "ipv4":
            return "192.0.2.1"
        if schema_format == "ipv6":
            return "2001:db8::1"
        if schema_format == "byte":
            return "U29tZUJhc2U2NA=="
        if schema_format == "password":
            return "P@ssw0rd!"
        return "string"

    # Numbers
    if schema_type == "integer":
        return 123
    if schema_type == "number":
        return 123.45

    # Boolean
    if schema_type == "boolean":
        return True

    # Array
    if schema_type == "array":
        items_schema = schema.get("items")
        item_example = generate_example(items_schema) if items_schema is not None else "string"
        return CommentedSeq([item_example])

    # Object-like
    if schema_type == "object" or any(k in schema for k in ("properties", "additionalProperties")):
        result = CommentedMap()
        properties = schema.get("properties") or {}
        for property_name, property_schema in properties.items():
            example_value = generate_example(property_schema)
            if example_value is not None:
                result[property_name] = example_value

        additional = schema.get("additionalProperties")
        if isinstance(additional, (dict, CommentedMap)):
            addl_example = generate_example(additional)
            if addl_example is not None:
                result["additionalProp1"] = addl_example
        elif additional is True:
            result["additionalProp1"] = "string"

        return result

    # Compositions
    for key in ("allOf", "oneOf", "anyOf"):
        if key in schema and isinstance(schema[key], list) and schema[key]:
            return generate_example(schema[key][0])

    return "string"


def add_examples_to_schema(schema: Any) -> None:
    if not isinstance(schema, CommentedMap):
        return

    # Avoid placing example on $ref-only
    if "$ref" in schema and len(schema.keys()) == 1:
        return

    if "example" not in schema:
        example_value = generate_example(schema)
        if example_value is not None:
            schema["example"] = example_value

    # Recurse into nested schemas
    properties = schema.get("properties")
    if isinstance(properties, dict):
        for property_schema in properties.values():
            add_examples_to_schema(property_schema)

    items_schema = schema.get("items")
    if isinstance(items_schema, (dict, CommentedMap)):
        add_examples_to_schema(items_schema)

    for key in ("allOf", "oneOf", "anyOf"):
        seq = schema.get(key)
        if isinstance(seq, list):
            for sub_schema in seq:
                add_examples_to_schema(sub_schema)

    additional = schema.get("additionalProperties")
    if isinstance(additional, (dict, CommentedMap)):
        add_examples_to_schema(additional)


def process_media_content(node: Any) -> None:
    if not isinstance(node, CommentedMap):
        return
    content = node.get("content")
    if isinstance(content, dict):
        for media_obj in content.values():
            if isinstance(media_obj, CommentedMap):
                schema = media_obj.get("schema")
                if isinstance(schema, (dict, CommentedMap)):
                    add_examples_to_schema(schema)


def process_document(doc: CommentedMap) -> None:
    components = doc.get("components")
    if isinstance(components, CommentedMap):
        # Schemas
        schemas = components.get("schemas")
        if isinstance(schemas, dict):
            for schema in schemas.values():
                add_examples_to_schema(schema)

        # Parameters
        parameters = components.get("parameters")
        if isinstance(parameters, dict):
            for param in parameters.values():
                if isinstance(param, CommentedMap):
                    schema = param.get("schema")
                    if isinstance(schema, (dict, CommentedMap)):
                        add_examples_to_schema(schema)

        # Headers
        headers = components.get("headers")
        if isinstance(headers, dict):
            for header in headers.values():
                if isinstance(header, CommentedMap):
                    schema = header.get("schema")
                    if isinstance(schema, (dict, CommentedMap)):
                        add_examples_to_schema(schema)

        # Request Bodies
        request_bodies = components.get("requestBodies")
        if isinstance(request_bodies, dict):
            for rb in request_bodies.values():
                process_media_content(rb)

        # Responses
        responses = components.get("responses")
        if isinstance(responses, dict):
            for resp in responses.values():
                process_media_content(resp)

    paths = doc.get("paths")
    if isinstance(paths, dict):
        for path_item in paths.values():
            if not isinstance(path_item, dict):
                continue

            # Path-level parameters
            if "parameters" in path_item and isinstance(path_item["parameters"], list):
                for param in path_item["parameters"]:
                    if isinstance(param, CommentedMap):
                        schema = param.get("schema")
                        if isinstance(schema, (dict, CommentedMap)):
                            add_examples_to_schema(schema)

            for method in ("get", "put", "post", "delete", "options", "head", "patch", "trace"):
                op = path_item.get(method)
                if not isinstance(op, dict):
                    continue

                # Operation-level parameters
                if "parameters" in op and isinstance(op["parameters"], list):
                    for param in op["parameters"]:
                        if isinstance(param, CommentedMap):
                            schema = param.get("schema")
                            if isinstance(schema, (dict, CommentedMap)):
                                add_examples_to_schema(schema)

                # Request body
                if "requestBody" in op:
                    process_media_content(op["requestBody"])

                # Responses
                responses = op.get("responses")
                if isinstance(responses, dict):
                    for resp in responses.values():
                        process_media_content(resp)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="infile", default="/workspace/openapi.yml")
    args = parser.parse_args()

    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = True
    # Prevent any re-wrapping of long lines
    yaml.width = 4096

    with open(args.infile, "r", encoding="utf-8") as f:
        doc = yaml.load(f)

    if not isinstance(doc, CommentedMap):
        print("Root document is not a mapping; aborting.")
        return 2

    process_document(doc)

    with open(args.infile, "w", encoding="utf-8") as f:
        yaml.dump(doc, f)

    return 0


if __name__ == "__main__":
    sys.exit(main())

