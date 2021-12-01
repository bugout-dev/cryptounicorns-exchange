import json
import os
from typing import Any, Dict
from tqdm import tqdm

from .bugout_util import publish_json
from .unicorns import UnicornMetadata
from .settings import cu_contract

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)


def _load_cu_metadata_from_json():
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(basedir, "cu_metadata.json")
    with open(path, "r") as f:
        return json.load(f)


def _upload_genesis_unicorn(unicorn_metadata: Dict[str, Any]):
    unicorn_metadata["owner"] = cu_contract.ownerOf(unicorn_metadata["token_id"])
    tags = [
        f"{key}:{value}"
        for key, value in unicorn_metadata.items()
        if key != "attributes"
    ]
    if "attributes" in unicorn_metadata:
        if "Mythic" in unicorn_metadata["attributes"]:
            tags.append(f"Mythic:{unicorn_metadata['attributes']['Mythic']}")
    title = f"{unicorn_metadata['name']}, token_id:{unicorn_metadata['token_id']}"
    publish_json(
        title=title,
        tags=tags,
        content=unicorn_metadata,
    )


def genesis_upload():
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for unicorn_metadata in tqdm(_load_cu_metadata_from_json()):
            futures.append(executor.submit(_upload_genesis_unicorn, unicorn_metadata))
        for future in tqdm(as_completed(futures), total=len(futures)):
            future.result()


def process_unicorn_metadata(unicorn_metadata: UnicornMetadata):
    pass


def update_unicorn_metadata(unicorn_metadata: UnicornMetadata):
    pass
