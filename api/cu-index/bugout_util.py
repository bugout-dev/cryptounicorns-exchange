import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, cast
import logging
import requests
from bugout.journal import SearchOrder
from .unicorns import UnicornMetadata

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


def unicorn_metadata_to_json(unicorn: UnicornMetadata) -> Dict[str, Any]:
    return {
        "token_id": unicorn.token_id,
        "metadata_url": unicorn.metadata_url,
        "image_url": unicorn.image_url,
        "name": unicorn.name,
        "metadata_version": unicorn.metadata_version,
        "attributes": unicorn.attributes,
        "owner": unicorn.owner,
    }


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

        unicorns = bugout_client.search(
            UNICORNS_BUGOUT_ADMIN_ACCESS_TOKEN,
            UNICORNS_BUGOUT_DATA_JOURNAL_ID,
            query,
            limit=1,
            timeout=30.0,
            order=SearchOrder.DESCENDING,
        )
        if not unicorns.results:
            logger.warning("There is no summaries in Bugout")
            return None

        unicorn_content = unicorns.results[0]
        content = cast(str, unicorn_content.content)
        breakpoint()
        return unicorn_json_to_metadata(json.loads(content))
    except Exception as e:
        logger.error(f"Failed to get summary from Bugout : {e}")
        return None


def update_metadata_of_unicorn(unicorn: UnicornMetadata) -> None:

    unicorn_json = unicorn_metadata_to_json(unicorn)
    publish_json(
        title=f"{unicorn.name} metadata",
        content=unicorn_json,
        tags=["metadata"],
        wait=True,
    )
