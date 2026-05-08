#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote


API_BASE = "https://api.porkbun.com/api/json/v3"


def load_env():
    root = Path(__file__).resolve().parents[1]
    candidates = []

    explicit = os.environ.get("PORKBUN_ENV_FILE")
    if explicit:
        candidates.append(Path(explicit).expanduser())

    candidates.extend(
        [
            Path.cwd() / ".env.porkbun",
            root / ".env.porkbun",
        ]
    )

    env_file = next((path for path in candidates if path.exists()), None)
    if env_file is None:
        return

    for raw_line in env_file.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def credentials():
    load_env()
    api_key = os.environ.get("PORKBUN_API_KEY")
    secret_key = os.environ.get("PORKBUN_SECRET_API_KEY")
    if not api_key or not secret_key:
        sys.exit("Missing Porkbun credentials. Fill in .env.porkbun first.")
    return api_key, secret_key


def request_json(path, payload=None, method="POST"):
    api_key, secret_key = credentials()
    url = f"{API_BASE}{path}"

    if payload is None:
        payload = {}
    payload = {
        "apikey": api_key,
        "secretapikey": secret_key,
        **payload,
    }

    body = json.dumps(payload)
    result = subprocess.run(
        [
            "curl",
            "-sS",
            "-X",
            method,
            url,
            "-H",
            "Content-Type: application/json",
            "--data-binary",
            "@-",
        ],
        input=body,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        sys.exit(f"Network error contacting Porkbun: {result.stderr.strip()}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        sys.exit(f"Unexpected Porkbun response: {result.stdout}")


def require_success(data):
    if data.get("status") != "SUCCESS":
        message = data.get("message", "Unknown Porkbun API error")
        code = data.get("code")
        if code:
            sys.exit(f"{message} ({code})")
        sys.exit(message)


def q(value):
    return quote(str(value), safe="")


def display_records(data, raw_json=False):
    if raw_json:
        print(json.dumps(data, indent=2))
        return

    require_success(data)
    records = data.get("records", [])
    if not records:
        print("No editable DNS records found.")
        return

    headers = ["id", "type", "name", "content", "ttl", "prio"]
    rows = []
    for record in records:
        rows.append(
            [
                str(record.get("id", "")),
                str(record.get("type", "")),
                str(record.get("name", "")),
                str(record.get("content", "")),
                str(record.get("ttl", "")),
                str(record.get("prio", "")),
            ]
        )

    widths = [
        min(max(len(row[index]) for row in [headers] + rows), 64)
        for index in range(len(headers))
    ]

    def trim(value, width):
        return value if len(value) <= width else value[: width - 1] + "..."

    print("  ".join(headers[index].ljust(widths[index]) for index in range(len(headers))))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print(
            "  ".join(
                trim(row[index], widths[index]).ljust(widths[index])
                for index in range(len(headers))
            )
        )


def cmd_list(args):
    data = request_json(f"/dns/retrieve/{q(args.domain)}")
    display_records(data, args.json)


def cmd_get(args):
    data = request_json(f"/dns/retrieve/{q(args.domain)}/{q(args.id)}")
    display_records(data, args.json)


def cmd_find(args):
    subdomain = args.name if args.name is not None else ""
    data = request_json(
        f"/dns/retrieveByNameType/{q(args.domain)}/{q(args.type.upper())}/{q(subdomain)}"
    )
    display_records(data, args.json)


def record_payload(args, include_type=True, include_name=True):
    payload = {
        "content": args.content,
        "ttl": args.ttl,
        "prio": args.prio,
    }
    if include_type:
        payload["type"] = args.type.upper()
    if include_name:
        payload["name"] = args.name
    return payload


def cmd_create(args):
    data = request_json(f"/dns/create/{q(args.domain)}", record_payload(args))
    print(json.dumps(data, indent=2))


def cmd_update(args):
    data = request_json(f"/dns/edit/{q(args.domain)}/{q(args.id)}", record_payload(args))
    print(json.dumps(data, indent=2))


def cmd_delete(args):
    if not args.yes:
        sys.exit("Refusing to delete without --yes.")
    data = request_json(f"/dns/delete/{q(args.domain)}/{q(args.id)}")
    print(json.dumps(data, indent=2))


def parser():
    main = argparse.ArgumentParser(
        description="Manage Porkbun DNS records using .env.porkbun credentials."
    )
    subcommands = main.add_subparsers(dest="command", required=True)

    list_cmd = subcommands.add_parser("list", help="List editable DNS records.")
    list_cmd.add_argument("domain")
    list_cmd.add_argument("--json", action="store_true", help="Print raw JSON.")
    list_cmd.set_defaults(func=cmd_list)

    get_cmd = subcommands.add_parser("get", help="Get one DNS record by ID.")
    get_cmd.add_argument("domain")
    get_cmd.add_argument("id")
    get_cmd.add_argument("--json", action="store_true", help="Print raw JSON.")
    get_cmd.set_defaults(func=cmd_get)

    find_cmd = subcommands.add_parser("find", help="Find records by type and name.")
    find_cmd.add_argument("domain")
    find_cmd.add_argument("type")
    find_cmd.add_argument("name", nargs="?", help="Subdomain only; omit for root.")
    find_cmd.add_argument("--json", action="store_true", help="Print raw JSON.")
    find_cmd.set_defaults(func=cmd_find)

    create_cmd = subcommands.add_parser("create", help="Create a DNS record.")
    create_cmd.add_argument("domain")
    create_cmd.add_argument("type")
    create_cmd.add_argument("name", help="Subdomain only; use empty quotes for root.")
    create_cmd.add_argument("content")
    create_cmd.add_argument("--ttl", type=int, default=600)
    create_cmd.add_argument("--prio", type=int, default=0)
    create_cmd.set_defaults(func=cmd_create)

    update_cmd = subcommands.add_parser("update", help="Update a DNS record by ID.")
    update_cmd.add_argument("domain")
    update_cmd.add_argument("id")
    update_cmd.add_argument("type")
    update_cmd.add_argument("name", help="Subdomain only; use empty quotes for root.")
    update_cmd.add_argument("content")
    update_cmd.add_argument("--ttl", type=int, default=600)
    update_cmd.add_argument("--prio", type=int, default=0)
    update_cmd.set_defaults(func=cmd_update)

    delete_cmd = subcommands.add_parser("delete", help="Delete a DNS record by ID.")
    delete_cmd.add_argument("domain")
    delete_cmd.add_argument("id")
    delete_cmd.add_argument("--yes", action="store_true", help="Confirm deletion.")
    delete_cmd.set_defaults(func=cmd_delete)

    return main


def main():
    args = parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
