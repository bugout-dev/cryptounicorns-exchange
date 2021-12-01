from dataclasses import asdict
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, cast
import logging
import requests
from bugout.journal import SearchOrder, TagsAction
from .unicorns import UnicornMetadata

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)

from .settings import (
    UNICORNS_BUGOUT_ADMIN_ACCESS_TOKEN,
    UNICORNS_BUGOUT_DATA_JOURNAL_ID,
    UNICORNS_HUMBUG_TOKEN,
    bugout_client,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def publish_json(
    title: str,
    content: Dict[str, Any],
    tags: Optional[List[str]] = None,
    wait: bool = True,
    created_at: Optional[str] = None,
) -> None:
    spire_api_url = os.environ.get(
        "MOONSTREAM_SPIRE_API_URL", "https://spire.bugout.dev"
    ).rstrip("/")
    report_url = f"{spire_api_url}/humbug/reports"

    if tags is None:
        tags = []

    headers = {
        "Authorization": f"Bearer {UNICORNS_HUMBUG_TOKEN}",
    }
    request_body = {
        "title": title,
        "content": json.dumps(content),
        "tags": tags,
    }
    if created_at is not None:
        request_body["created_at"] = created_at

    query_parameters = {"sync": wait}

    response = requests.post(
        report_url, headers=headers, json=request_body, params=query_parameters
    )

    response.raise_for_status()


def unicorn_json_to_metadata(unicorn_json: Dict[str, Any]) -> UnicornMetadata:
    return UnicornMetadata(
        token_id=unicorn_json["token_id"],
        metadata_url=unicorn_json["metadata_url"],
        image_url=unicorn_json["image_url"],
        name=unicorn_json["name"],
        metadata_version=unicorn_json.get("metadata_version"),
        attributes=unicorn_json.get("attributes"),
        owner=unicorn_json.get("owner"),
    )


def get_unicorn_by_id(token_id: int) -> Optional[Tuple[str, UnicornMetadata]]:
    try:
        query = f"#token_id:{token_id}"

        response = bugout_client.search(
            UNICORNS_BUGOUT_ADMIN_ACCESS_TOKEN,
            UNICORNS_BUGOUT_DATA_JOURNAL_ID,
            query,
            limit=1,
            timeout=30.0,
            order=SearchOrder.DESCENDING,
        )
        if not response.results:
            logger.warning("There is no summaries in Bugout")
            return None

        result = response.results[0]
        unicorn_content = cast(str, result.content)
        entry_id = result.entry_url.split("/")[-1]
        return entry_id, unicorn_json_to_metadata(json.loads(unicorn_content))
    except Exception as e:
        logger.error(f"Failed to get summary from Bugout : {e}")
        return None


def _tags_for_json_unicorn(unicorn_metadata: Dict[str, Any]) -> List[str]:
    lifecycle = unicorn_metadata.get("attributes", {}).get("Lifecycle", "-")
    mythic = "-"
    if "attributes" in unicorn_metadata:
        mythic = unicorn_metadata["attributes"].get("Mythic", "Common")
    tags = [
        f"Lifecycle:{lifecycle}",
        f"Mythic:{mythic}",
        f"token_id:{unicorn_metadata['token_id']}",
        f"owner: {unicorn_metadata.get('owner')}",
        f"metadata_version: {unicorn_metadata.get('metadata_version')}",
    ]
    return tags


def _update_entry_of_unicorn(entry_id: str, unicorn: UnicornMetadata) -> None:

    unicorn_json = asdict(unicorn)
    try:
        bugout_client.update_entry_content(
            UNICORNS_BUGOUT_ADMIN_ACCESS_TOKEN,
            UNICORNS_BUGOUT_DATA_JOURNAL_ID,
            entry_id,
            tags=_tags_for_json_unicorn(unicorn_json),
            title=f"{unicorn.name}, token_id: {unicorn.token_id}",
            content=json.dumps(unicorn_json),
            tags_action=TagsAction.replace,
        )
        logger.info(f"Updated metadata of unicorn {unicorn.token_id}")
    except Exception as e:
        logger.error(f"Failed to update metadata of unicorn: {e}")


def get_all_unicorns() -> List[UnicornMetadata]:
    try:
        # TODO since clien doens't support limit-offset, using search for now
        limit = 1000
        current_offset = 0
        entries = []
        while True:
            response = bugout_client.search(
                UNICORNS_BUGOUT_ADMIN_ACCESS_TOKEN,
                UNICORNS_BUGOUT_DATA_JOURNAL_ID,
                "",
                limit=limit,
                offset=current_offset,
                order=SearchOrder.DESCENDING,
            )
            if not response.results:
                break
            entries.extend(response.results)
            logger.info(f"Already got {len(entries)} entries")
            current_offset += limit
    except Exception as e:
        logger.error(f"Failed to unicorns from bugout: {e}")
        raise e

    unicorns = []
    for entry in entries:
        unicorn_json = cast(str, entry.content)
        unicorn = unicorn_json_to_metadata(json.loads(unicorn_json))
        unicorns.append(unicorn)
    logger.info(f"Got {len(unicorns)} unicorns")
    return unicorns


def _genesis_unicorns_update():
    def _update(unicorn_id: int) -> None:
        entry_id, unicorn = get_unicorn_by_id(1)
        _update_entry_of_unicorn(entry_id, unicorn)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for unicorn_id in range(1, 10000 + 1):
            futures.append(executor.submit(_update, unicorn_id))
        for future in as_completed(futures):
            future.result()
