from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient


ROOT = Path(__file__).resolve().parents[2]
AUTH_PATH = ROOT / "examples" / "authorization-filter.py"

spec = importlib.util.spec_from_file_location("authorization_filter", AUTH_PATH)
assert spec and spec.loader
authorization_filter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(authorization_filter)

SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX", "enterprise-rag-demo")


def credential():
    admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
    if admin_key:
        return AzureKeyCredential(admin_key)
    return DefaultAzureCredential(exclude_interactive_browser_credential=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument(
        "--group-id",
        action="append",
        default=[],
        help="Trusted group GUID. Repeat for multiple groups.",
    )
    args = parser.parse_args()

    security_filter = authorization_filter.build_group_filter(args.group_id)

    client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=credential(),
    )

    results = client.search(
        search_text=args.query,
        filter=security_filter,
        select=["document_id", "title", "classification", "source_uri"],
        top=10,
    )

    print(f"Filter: {security_filter}")
    for result in results:
        print(
            result["document_id"],
            "|",
            result["title"],
            "|",
            result.get("classification", ""),
        )


if __name__ == "__main__":
    main()
