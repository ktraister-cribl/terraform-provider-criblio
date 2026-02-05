#!/usr/bin/env python3
import argparse
import json
import sys

import boto3
from boto3.dynamodb.conditions import Attr


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Scan a DynamoDB table and return items where the partition key "
            "contains any target substring and the capacity attribute exists."
        )
    )
    parser.add_argument("--table", required=True, help="DynamoDB table name.")
    parser.add_argument(
        "--partition-key",
        required=True,
        help="Partition key attribute name to search with contains().",
    )
    parser.add_argument(
        "--contains",
        action="append",
        default=[],
        help=(
            "Substring to match with contains(). Repeat for multiple values or "
            "provide a comma-separated list. Defaults to string1,string2,string3."
        ),
    )
    parser.add_argument(
        "--capacity-attr",
        default="capacity",
        help="Attribute name that must exist on each record.",
    )
    parser.add_argument("--region", default=None, help="AWS region override.")
    parser.add_argument("--profile", default=None, help="AWS profile name.")
    parser.add_argument(
        "--max-items",
        type=int,
        default=None,
        help="Stop after returning this many matching items.",
    )
    return parser.parse_args()


def normalize_contains(values):
    if not values:
        return ["string1", "string2", "string3"]
    if len(values) == 1 and "," in values[0]:
        return [v.strip() for v in values[0].split(",") if v.strip()]
    return values


def build_filter_expression(partition_key, substrings, capacity_attr):
    pk_expr = None
    for substring in substrings:
        expr = Attr(partition_key).contains(substring)
        pk_expr = expr if pk_expr is None else pk_expr | expr
    return Attr(capacity_attr).exists() & pk_expr


def scan_table(table, filter_expression, max_items=None):
    items = []
    scan_kwargs = {"FilterExpression": filter_expression}
    while True:
        response = table.scan(**scan_kwargs)
        items.extend(response.get("Items", []))
        if max_items is not None and len(items) >= max_items:
            return items[:max_items]
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            return items
        scan_kwargs["ExclusiveStartKey"] = last_key


def main():
    args = parse_args()
    substrings = normalize_contains(args.contains)
    if not substrings:
        print("No substrings provided for --contains.", file=sys.stderr)
        return 2

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    table = session.resource("dynamodb").Table(args.table)
    filter_expression = build_filter_expression(
        args.partition_key, substrings, args.capacity_attr
    )
    items = scan_table(table, filter_expression, args.max_items)
    json.dump(items, sys.stdout, indent=2, sort_keys=True, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
