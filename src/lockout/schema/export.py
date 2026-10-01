"""JSON Schema export for the model format."""

import json
import sys
from pathlib import Path

from lockout.schema.model import Model

SCHEMA_FILE = Path(__file__).with_name("lockout-model.schema.json")


def model_json_schema_text() -> str:
    """Return the JSON Schema of :class:`Model` as stable, sorted-key text."""
    schema = Model.model_json_schema(by_alias=True)
    return json.dumps(schema, indent=2, sort_keys=True) + "\n"


def main() -> None:
    """Regenerate the committed schema file. Run: ``python -m lockout.schema.export``."""
    SCHEMA_FILE.write_text(model_json_schema_text(), encoding="utf-8")
    sys.stdout.write(f"wrote {SCHEMA_FILE}\n")


if __name__ == "__main__":
    main()
