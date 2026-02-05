#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  dynamodb_scan_capacity.sh --table TABLE --partition-key ATTR [options]

Options:
  -t, --table           DynamoDB table name (required)
  -k, --partition-key   Partition key attribute name (required)
  -c, --contains        Substring to match (repeatable or comma-separated)
  -a, --capacity-attr   Attribute that must NOT exist (default: capacity)
  -r, --region          AWS region override
  -p, --profile         AWS profile name
  -m, --max-items       Stop after returning this many items
  -h, --help            Show this help

Examples:
  ./dynamodb_scan_capacity.sh -t my-table -k pk \
    -c string1 -c string2 -c string3

  ./dynamodb_scan_capacity.sh -t my-table -k pk \
    -c "string1,string2,string3" -a capacity
EOF
}

trim() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "$value"
}

join_by() {
  local IFS="$1"
  shift
  printf '%s' "$*"
}

table=""
partition_key=""
capacity_attr="capacity"
region=""
profile=""
max_items=""
contains_list=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    -t|--table)
      table="$2"
      shift 2
      ;;
    -k|--partition-key)
      partition_key="$2"
      shift 2
      ;;
    -c|--contains)
      contains_list+=("$2")
      shift 2
      ;;
    -a|--capacity-attr)
      capacity_attr="$2"
      shift 2
      ;;
    -r|--region)
      region="$2"
      shift 2
      ;;
    -p|--profile)
      profile="$2"
      shift 2
      ;;
    -m|--max-items)
      max_items="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$table" || -z "$partition_key" ]]; then
  echo "Both --table and --partition-key are required." >&2
  usage >&2
  exit 2
fi

if ! command -v aws >/dev/null 2>&1; then
  echo "aws CLI is required but not found in PATH." >&2
  exit 127
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required but not found in PATH." >&2
  exit 127
fi

if [[ ${#contains_list[@]} -eq 0 ]]; then
  contains_list=("string1" "string2" "string3")
elif [[ ${#contains_list[@]} -eq 1 && "${contains_list[0]}" == *","* ]]; then
  IFS=',' read -r -a contains_list <<< "${contains_list[0]}"
fi

expr_parts=()
expr_values_entries=()
idx=1
for raw in "${contains_list[@]}"; do
  value="$(trim "$raw")"
  if [[ -z "$value" ]]; then
    continue
  fi
  placeholder=":s${idx}"
  expr_parts+=("contains(#pk, ${placeholder})")
  expr_values_entries+=("\"${placeholder}\": {\"S\": \"${value//\"/\\\"}\"}")
  idx=$((idx + 1))
done

if [[ ${#expr_parts[@]} -eq 0 ]]; then
  echo "No valid --contains values provided." >&2
  exit 2
fi

pk_expr="$(join_by " OR " "${expr_parts[@]}")"
filter_expression="attribute_not_exists(#cap) AND (${pk_expr})"
expr_names="$(printf '{"#pk":"%s","#cap":"%s"}' "$partition_key" "$capacity_attr")"
expr_values="{"
expr_values+="$(join_by "," "${expr_values_entries[@]}")"
expr_values+="}"

aws_args=()
if [[ -n "$region" ]]; then
  aws_args+=(--region "$region")
fi
if [[ -n "$profile" ]]; then
  aws_args+=(--profile "$profile")
fi

items='[]'
exclusive_start_key=""

while :; do
  scan_args=(
    dynamodb scan
    --table-name "$table"
    --filter-expression "$filter_expression"
    --expression-attribute-names "$expr_names"
    --expression-attribute-values "$expr_values"
    --output json
  )
  if [[ -n "$exclusive_start_key" ]]; then
    scan_args+=(--exclusive-start-key "$exclusive_start_key")
  fi

  response="$(aws "${aws_args[@]}" "${scan_args[@]}")"
  page_items="$(printf '%s' "$response" | jq '.Items')"
  items="$(jq -s '.[0] + .[1]' <(printf '%s' "$items") <(printf '%s' "$page_items"))"

  if [[ -n "$max_items" ]]; then
    count="$(printf '%s' "$items" | jq 'length')"
    if (( count >= max_items )); then
      items="$(printf '%s' "$items" | jq ".[0:${max_items}]")"
      break
    fi
  fi

  last_key="$(printf '%s' "$response" | jq -c '.LastEvaluatedKey // empty')"
  if [[ -z "$last_key" || "$last_key" == "null" ]]; then
    break
  fi
  exclusive_start_key="$last_key"
done

printf '%s\n' "$items"
