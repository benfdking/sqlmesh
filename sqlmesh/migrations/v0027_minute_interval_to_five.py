"""Change any interval unit of minute to five_minute."""
import json

import pandas as pd
from sqlglot import exp

from sqlmesh.utils.migration import index_text_type


def migrate(state_sync):  # type: ignore
    engine_adapter = state_sync.engine_adapter
    schema = state_sync.schema
    snapshots_table = "_snapshots"
    if schema:
        snapshots_table = f"{schema}.{snapshots_table}"

    new_snapshots = []

    for name, identifier, version, snapshot, kind_name in engine_adapter.fetchall(
        exp.select("name", "identifier", "version", "snapshot", "kind_name").from_(snapshots_table),
        quote_identifiers=True,
    ):
        parsed_snapshot = json.loads(snapshot)

        node = parsed_snapshot["node"]

        if node.get("interval_unit") == "minute":
            node["interval_unit"] = "five_minute"

        new_snapshots.append(
            {
                "name": name,
                "identifier": identifier,
                "version": version,
                "snapshot": json.dumps(parsed_snapshot),
                "kind_name": kind_name,
            }
        )

    if new_snapshots:
        engine_adapter.delete_from(snapshots_table, "TRUE")

        text_type = index_text_type(engine_adapter.dialect)

        engine_adapter.insert_append(
            snapshots_table,
            pd.DataFrame(new_snapshots),
            columns_to_types={
                "name": exp.DataType.build(text_type),
                "identifier": exp.DataType.build(text_type),
                "version": exp.DataType.build(text_type),
                "snapshot": exp.DataType.build("text"),
                "kind_name": exp.DataType.build(text_type),
            },
            contains_json=True,
        )
