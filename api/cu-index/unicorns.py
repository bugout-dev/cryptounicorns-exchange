from dataclasses import dataclass
import dataclasses
from typing import List, Optional
import requests
import json
from tqdm import tqdm
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
import time


from web3 import Web3
from .contract_util import CuContract

# Examle of adult unicorn metadata


@dataclass
class UnicornMetadata:
    token_id: int
    metadata_url: str
    image_url: str
    name: str
    metadata_version: str
    attributes: Optional[dict] = None
    owner: Optional[str] = None


def _fetch_unicorn_from_uri(token_id: int, token_uri: str) -> UnicornMetadata:
    retry_count = 10
    current_sleep_time = 1

    for i in range(retry_count):
        try:
            res = requests.get(token_uri, timeout=10)
            if res.status_code != 200:
                raise Exception(f"Status code != 200 {token_uri}")
            unicorn_json = json.loads(res.text)
            unicorn = UnicornMetadata(
                token_id=token_id,
                metadata_url=token_uri,
                image_url=unicorn_json["image"],
                name=unicorn_json["name"],
                metadata_version=unicorn_json["metadata_version"],
                attributes={},
            )
            for attribute in unicorn_json["attributes"]:
                unicorn.attributes[attribute["trait_type"]] = attribute["value"]
            return unicorn
        except Exception as e:
            if i == retry_count - 1:
                print(f"Failed to fetch unicorn from {token_uri}:\n{e}")
                exit(1)

            time.sleep(current_sleep_time)


def _fetch_unicorn(cu_contract: CuContract, token_id: int) -> UnicornMetadata:
    print(f"Fetching metadata for {token_id}")
    return _fetch_unicorn_from_uri(token_id, cu_contract.tokenURI(token_id))


def _get_unicorns_metadata(
    cu_contract: CuContract, unicorn_ids: List[int], workers: int = 1
) -> list:
    """
    Get all the token uri from the contract
    """
    all_unicorns_metadata = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        for i in unicorn_ids:
            futures.append(executor.submit(_fetch_unicorn, cu_contract, i))
        for future in tqdm(as_completed(futures), total=len(futures)):
            all_unicorns_metadata.append(future.result())
    return all_unicorns_metadata


def get_all_unicorns_metadata(cu_contract: CuContract) -> list:
    """
    Get all the token uri from the contract
    """
    all_unicorn_ids = [i for i in range(1, cu_contract.totalSupply() + 1)]
    all_unicorns_metadata = []
    for i in _get_unicorns_metadata(
        cu_contract,
        all_unicorn_ids,
        workers=20,
    ):
        all_unicorns_metadata.append(i)
    return all_unicorns_metadata


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def craw_to_json():
    web3_client = Web3(
        Web3.HTTPProvider(
            "https://polygon-mainnet.infura.io/v3/be7152a5afaa46fba75bbc9ed5f2bc0c"
        )
    )
    cu_contract = CuContract("0xdC0479CC5BbA033B3e7De9F178607150B3AbCe1f", web3_client)
    all_unicorns_metadata = get_all_unicorns_metadata(cu_contract)

    # save to json file
    with open("cu_metadata.json", "w") as outfile:
        json.dump(all_unicorns_metadata, outfile, cls=EnhancedJSONEncoder)
