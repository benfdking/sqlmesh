import typing as t
import pytest
import pandas as pd
import datetime
from sqlmesh.core.engine_adapter import AthenaEngineAdapter
from sqlmesh.utils.aws import parse_s3_uri
from tests.core.engine_adapter.integration import TestContext
from sqlglot import exp
from pyathena.error import OperationalError

pytestmark = [pytest.mark.docker, pytest.mark.engine, pytest.mark.postgres]


@pytest.fixture
def mark_gateway() -> t.Tuple[str, str]:
    return "athena", "inttest_athena"


@pytest.fixture
def test_type() -> str:
    return "query"


@pytest.fixture
def s3(engine_adapter: AthenaEngineAdapter) -> t.Any:
    return engine_adapter._s3_client


def s3_list_objects(s3: t.Any, location: str, **list_objects_kwargs: t.Any) -> t.List[str]:
    bucket, prefix = parse_s3_uri(location)
    lst = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
        lst.extend([o["Key"] for o in page.get("Contents", [])])
    return lst


def test_clear_partition_data(ctx: TestContext, engine_adapter: AthenaEngineAdapter, s3: t.Any):
    base_uri = engine_adapter.s3_warehouse_location_or_raise
    assert len(s3_list_objects(s3, base_uri)) == 0

    src_table = ctx.table("src_table")
    test_table = ctx.table("test_table")

    base_data = pd.DataFrame(
        [
            {"id": 1, "ts": datetime.datetime(2023, 1, 1, 12, 13, 14)},
            {"id": 2, "ts": datetime.datetime(2023, 1, 2, 8, 10, 0)},
            {"id": 3, "ts": datetime.datetime(2023, 1, 3, 16, 5, 14)},
        ]
    )

    engine_adapter.ctas(
        table_name=src_table,
        query_or_df=base_data,
    )

    sqlmesh_context, model = ctx.upsert_sql_model(
        f"""
        MODEL (
            name {test_table},
            kind INCREMENTAL_BY_TIME_RANGE (
                time_column ds
            ),
            start '2023-01-01'
        );

        SELECT
            id, ts, (ts::date)::varchar as ds
        FROM {src_table}
        WHERE ts BETWEEN @start_dt AND @end_dt
        """
    )

    plan = sqlmesh_context.plan(no_prompts=True, auto_apply=True)
    assert len(plan.snapshots) == 1
    test_table_snapshot = list(plan.snapshots.values())[0]

    files_before = s3_list_objects(s3, base_uri)
    assert len(files_before) > 0

    # src_table should have no partitions
    with pytest.raises(OperationalError, match=r".*TABLE_NOT_FOUND.*\$partitions"):
        engine_adapter._list_partitions(src_table)

    # test_table physical snapshot table should have 3 partitions
    test_table_physical_name = exp.to_table(test_table_snapshot.table_name())
    partitions = engine_adapter._list_partitions(test_table_physical_name, where=None)
    assert len(partitions) == 3
    assert [p[0] for p in partitions] == [["2023-01-01"], ["2023-01-02"], ["2023-01-03"]]

    assert engine_adapter.fetchone(f"select count(*) from {test_table}")[0] == 3  # type: ignore

    # clear a partition
    assert model.time_column
    engine_adapter._clear_partition_data(
        table=test_table_physical_name,
        where=exp.Between(
            this=model.time_column.column,
            low=exp.Literal.string("2023-01-01"),
            high=exp.Literal.string("2023-01-01"),
        ),
    )
    partitions = engine_adapter._list_partitions(test_table_physical_name, where=None)
    assert len(partitions) == 2
    assert [p[0] for p in partitions] == [["2023-01-02"], ["2023-01-03"]]

    # test that only S3 data for that partition was affected
    files_after = s3_list_objects(s3, base_uri)
    assert len(files_after) == len(files_before) - 1
    assert len([f for f in files_before if "ds=2023-01-01" in f]) == 1
    assert len([f for f in files_after if "ds=2023-01-01" in f]) == 0

    assert engine_adapter.fetchone(f"select count(*) from {test_table}")[0] == 2  # type: ignore


def test_clear_partition_data_multiple_columns(
    ctx: TestContext, engine_adapter: AthenaEngineAdapter, s3: t.Any
):
    base_uri = engine_adapter.s3_warehouse_location_or_raise

    src_table = ctx.table("src_table")
    test_table = ctx.table("test_table")

    base_data = pd.DataFrame(
        [
            {"id": 1, "ts": datetime.datetime(2023, 1, 1, 12, 13, 14), "system": "dev"},
            {"id": 2, "ts": datetime.datetime(2023, 1, 1, 8, 13, 14), "system": "prod"},
            {"id": 3, "ts": datetime.datetime(2023, 1, 2, 11, 10, 0), "system": "dev"},
            {"id": 4, "ts": datetime.datetime(2023, 1, 2, 8, 10, 0), "system": "dev"},
            {"id": 5, "ts": datetime.datetime(2023, 1, 3, 16, 5, 14), "system": "dev"},
            {"id": 6, "ts": datetime.datetime(2023, 1, 3, 16, 5, 14), "system": "prod"},
        ]
    )

    engine_adapter.ctas(
        table_name=src_table,
        query_or_df=base_data,
    )

    sqlmesh_context, model = ctx.upsert_sql_model(
        f"""
        MODEL (
            name {test_table},
            kind INCREMENTAL_BY_TIME_RANGE (
                time_column ds
            ),
            partitioned_by (ds, system),
            start '2023-01-01'
        );

        SELECT
            id, ts, (ts::date)::varchar as ds, system
        FROM {src_table}
        WHERE ts BETWEEN @start_dt AND @end_dt
        """
    )

    plan = sqlmesh_context.plan(no_prompts=True, auto_apply=True)
    assert len(plan.snapshots) == 1
    test_table_snapshot = list(plan.snapshots.values())[0]
    test_table_physical_name = exp.to_table(test_table_snapshot.table_name())

    partitions = engine_adapter._list_partitions(test_table_physical_name, where=None)
    assert len(partitions) == 5
    assert [p[0] for p in partitions] == [
        ["2023-01-01", "dev"],
        ["2023-01-01", "prod"],
        ["2023-01-02", "dev"],
        ["2023-01-03", "dev"],
        ["2023-01-03", "prod"],
    ]

    files_before = s3_list_objects(s3, base_uri)
    assert len(files_before) > 0

    assert engine_adapter.fetchone(f"select count(*) from {test_table}")[0] == 6  # type: ignore

    # this should clear 2 partitions, ["2023-01-01", "dev"] and ["2023-01-01", "prod"]
    assert model.time_column
    engine_adapter._clear_partition_data(
        table=test_table_physical_name,
        where=exp.Between(
            this=model.time_column.column,
            low=exp.Literal.string("2023-01-01"),
            high=exp.Literal.string("2023-01-01"),
        ),
    )

    partitions = engine_adapter._list_partitions(test_table_physical_name, where=None)
    assert len(partitions) == 3
    assert [p[0] for p in partitions] == [
        ["2023-01-02", "dev"],
        ["2023-01-03", "dev"],
        ["2023-01-03", "prod"],
    ]

    files_after = s3_list_objects(s3, base_uri)
    assert len(files_after) == len(files_before) - 2

    def _match_partition(location_list: t.List[str], match: str):
        return any(match in location for location in location_list)

    assert _match_partition(files_before, "ds=2023-01-01/system=dev")
    assert _match_partition(files_before, "ds=2023-01-01/system=prod")
    assert not _match_partition(files_after, "ds=2023-01-01/system=dev")
    assert not _match_partition(files_after, "ds=2023-01-01/system=prod")

    assert engine_adapter.fetchone(f"select count(*) from {test_table}")[0] == 4  # type: ignore


def test_hive_truncate_table(ctx: TestContext, engine_adapter: AthenaEngineAdapter, s3: t.Any):
    base_uri = engine_adapter.s3_warehouse_location_or_raise

    table_1 = ctx.table("table_one")
    table_2 = ctx.table("table_two")

    base_data = pd.DataFrame(
        [
            {"id": 1, "ts": datetime.datetime(2023, 1, 1, 12, 13, 14), "system": "dev"},
            {"id": 2, "ts": datetime.datetime(2023, 1, 1, 8, 13, 14), "system": "prod"},
            {"id": 3, "ts": datetime.datetime(2023, 1, 2, 11, 10, 0), "system": "dev"},
            {"id": 4, "ts": datetime.datetime(2023, 1, 2, 8, 10, 0), "system": "dev"},
            {"id": 5, "ts": datetime.datetime(2023, 1, 3, 16, 5, 14), "system": "dev"},
            {"id": 6, "ts": datetime.datetime(2023, 1, 3, 16, 5, 14), "system": "prod"},
        ]
    )

    assert len(s3_list_objects(s3, base_uri)) == 0

    engine_adapter.ctas(table_name=table_1, query_or_df=base_data)

    engine_adapter.ctas(table_name=table_2, query_or_df=base_data)

    all_files = s3_list_objects(s3, base_uri)
    assert len(all_files) > 0

    table_1_location = engine_adapter._query_table_s3_location(table_1)
    table_2_location = engine_adapter._query_table_s3_location(table_2)

    table_1_files = s3_list_objects(s3, table_1_location)
    table_2_files = s3_list_objects(s3, table_2_location)

    assert len(table_1_files) < len(all_files)
    assert len(table_2_files) < len(all_files)
    assert len(table_1_files) + len(table_2_files) == len(all_files)

    assert engine_adapter.fetchone(f"select count(*) from {table_1}")[0] == 6  # type: ignore
    engine_adapter._truncate_table(table_1)
    assert len(s3_list_objects(s3, table_1_location)) == 0
    assert len(s3_list_objects(s3, table_2_location)) == len(table_2_files)

    assert engine_adapter.fetchone(f"select count(*) from {table_1}")[0] == 0  # type: ignore
