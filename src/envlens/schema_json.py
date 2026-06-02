from __future__ import annotations

import json
from typing import Any


ENV_SCHEMA_JSON: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://raw.githubusercontent.com/Luckymeyo/envlens/main/schemas/env.schema.json",
    "title": "envlens environment contract",
    "description": "Schema for envlens env.schema.yml and env.schema.json files.",
    "type": "object",
    "propertyNames": {
        "pattern": "^[A-Za-z_][A-Za-z0-9_]*$",
        "description": "Environment variable names should use shell-compatible identifiers.",
    },
    "additionalProperties": {
        "oneOf": [
            {
                "type": "string",
                "enum": ["string", "number", "integer", "boolean", "url", "email", "enum"],
                "description": "Short form: VARIABLE_NAME: string",
            },
            {"$ref": "#/$defs/envSpec"},
        ]
    },
    "$defs": {
        "envSpec": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["string", "number", "integer", "boolean", "url", "email", "enum"],
                    "default": "string",
                },
                "required": {
                    "type": "boolean",
                    "description": "Whether the key must appear in validated env files.",
                },
                "default": {
                    "type": ["string", "number", "boolean", "null"],
                    "description": "Documented default value.",
                },
                "values": {
                    "type": "array",
                    "items": {"type": ["string", "number", "boolean"]},
                    "description": "Allowed values when type is enum.",
                },
                "description": {
                    "type": "string",
                    "description": "Human-readable documentation used by envlens docs.",
                },
                "secret": {
                    "type": "boolean",
                    "description": "Override secret-name inference for this key.",
                },
                "public": {
                    "type": "boolean",
                    "description": "Override public-client-name inference for this key.",
                },
            },
        }
    },
}


def render_env_schema_json() -> str:
    return json.dumps(ENV_SCHEMA_JSON, indent=2, sort_keys=True)
