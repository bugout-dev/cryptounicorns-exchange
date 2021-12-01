import os

from web3 import Web3


def _laod_cu_abi():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, "cu_abi.json"), "r") as ifp:
        return ifp.read()


class CuContract:
    def __init__(self, address: str, web3_client: Web3):
        self.address = web3_client.toChecksumAddress(address)
        self.web3_client = web3_client
        self.contract = self.web3_client.eth.contract(
            address=self.address, abi=_laod_cu_abi()
        )

    def balanceOf(self, address: str) -> int:
        return self.contract.functions.balanceOf(address).call()

    def tokenURI(self, token_id: int) -> str:
        return self.contract.functions.tokenURI(token_id).call()

    def ownerOf(self, token_id: int) -> str:
        return self.contract.functions.ownerOf(token_id).call()

    def tokenOfOwnerByIndex(self, owner: str, index: int) -> int:
        return self.contract.functions.tokenOfOwnerByIndex(owner, index).call()

    def totalSupply(self) -> int:
        return self.contract.functions.totalSupply().call()
