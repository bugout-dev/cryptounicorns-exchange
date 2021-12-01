import os

from bugout.app import Bugout
from web3 import Web3
from .contract_util import CuContract

# Bugout
BUGOUT_BROOD_URL = os.environ.get("BUGOUT_BROOD_URL", "https://auth.bugout.dev")
BUGOUT_SPIRE_URL = os.environ.get("BUGOUT_SPIRE_URL", "https://spire.bugout.dev")
bugout_client = Bugout(brood_api_url=BUGOUT_BROOD_URL, spire_api_url=BUGOUT_SPIRE_URL)


UNICORNS_CONTRACT_ADDRESS = os.environ.get(
    "UNICORNS_CONTRACT_ADDRESS", "0xdC0479CC5BbA033B3e7De9F178607150B3AbCe1f"
)
if UNICORNS_CONTRACT_ADDRESS == "":
    raise Exception("CU_CONTRACT_ADDRESS environment variable is not set!")


UNICORNS_WEB3_PROVIDER_PATH = os.environ.get("UNICORNS_WEB3_PROVIDER_PATH", "")
if UNICORNS_WEB3_PROVIDER_PATH == "":
    raise Exception("UNICORNS_WEB3_PROVIDER_PATH environment variable is not set!")

web3_client = Web3(Web3.HTTPProvider(UNICORNS_WEB3_PROVIDER_PATH))
cu_contract = CuContract(UNICORNS_CONTRACT_ADDRESS, web3_client)


UNICORNS_BUGOUT_DATA_JOURNAL_ID = os.environ.get("UNICORNS_BUGOUT_DATA_JOURNAL_ID", "")
if UNICORNS_BUGOUT_DATA_JOURNAL_ID == "":
    raise Exception("UNICORNS_BUGOUT_DATA_JOURNAL_ID environment variable is not set!")

UNICORNS_BUGOUT_ADMIN_ACCESS_TOKEN = os.environ.get(
    "UNICORNS_BUGOUT_ADMIN_ACCESS_TOKEN", ""
)
if UNICORNS_BUGOUT_ADMIN_ACCESS_TOKEN == "":
    raise Exception(
        "UNICORS_BUGOUT_ADMIN_ACCESS_TOKEN environment variable is not set!"
    )

UNICORNS_HUMBUG_TOKEN = os.environ.get("UNICORNS_HUMBUG_TOKEN", "")
if UNICORNS_HUMBUG_TOKEN == "":
    raise Exception("UNICORNS_HUMBUG_TOKEN environment variable is not set!")
