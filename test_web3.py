import json

from cobo_custody.client.web3_client import Web3Client
from cobo_custody.config import DEV_ENV
from cobo_custody.config import DEV_TEST_DATA

import unittest
from cobo_custody.signer.local_signer import LocalSigner
import sys
import argparse
import time


class Web3ClientTest(unittest.TestCase):
    web3_api_secret = ""
    ENV = DEV_ENV
    TEST_DATA = DEV_TEST_DATA

    def setUp(self):
        self.web3_client = Web3Client(signer=LocalSigner(self.web3_api_secret),
                                    env=self.ENV,
                                    debug=False)

    def test_get_web3_supported_chains(self):
        response = self.web3_client.get_web3_supported_chains()
        print(response)
        self.assertTrue(response.success)

    def test_get_web3_supported_coins(self):
        chain_code = "GETH"
        response = self.web3_client.get_web3_supported_coins(chain_code=chain_code)
        print(response)
        self.assertTrue(response.success)

    def test_get_web3_supported_nft_collections(self):
        response = self.web3_client.get_web3_supported_nft_collections()
        print(response)
        self.assertTrue(response.success)

    def test_get_web3_supported_contracts(self):
        chain_code = "GETH"
        response = self.web3_client.get_web3_supported_contracts(chain_code=chain_code)
        print(response)
        self.assertTrue(response.success)

    def test_get_web3_supported_contract_methods(self):
        chain_code = "GETH"
        contract_address = "0x7851dcc90e79f3f2c59915e7f4d6fabd8d3d305b"
        response = self.web3_client.get_web3_supported_contract_methods(chain_code=chain_code, contract_address=contract_address)
        print(response)
        self.assertTrue(response.success)

    def test_batch_web3_new_address(self):
        chain_code = "GETH"
        count = 2
        response = self.web3_client.batch_web3_new_address(chain_code=chain_code, count=count)
        print(response)
        self.assertTrue(response.success)

    def test_get_web3_address_list(self):
        chain_code = "GETH"
        page_index = 0
        page_length = 20
        response = self.web3_client.get_web3_address_list(chain_code=chain_code, page_index=page_index, page_length=page_length)
        print(response)
        self.assertTrue(response.success)

    def test_get_web3_wallet_asset_list(self):
        address = "0xd387292d5be73c8b9d6d3a4dcdd49e00edf75b6a"
        chain_code = "GETH"
        response = self.web3_client.get_web3_wallet_asset_list(address=address, chain_code=chain_code)
        print(response)
        self.assertTrue(response.success)

    def test_get_web3_wallet_nft_list(self):
        nft_code = "NFT_RETH_PROOF_MOONBIRDS"
        address = "0xd387292d5be73c8b9d6d3a4dcdd49e00edf75b6a"
        response = self.web3_client.get_web3_wallet_nft_list(nft_code=nft_code, address=address)
        print(response)
        self.assertTrue(response.success)

    def test_get_web3_wallet_nft_detail(self):
        nft_code = "NFT_RETH_PROOF_MOONBIRDS"
        token_id = "148"
        response = self.web3_client.get_web3_wallet_nft_detail(nft_code=nft_code, token_id=token_id)
        print(response)
        self.assertTrue(response.success)

    def test_web3_withdraw(self):
        coin = "ETH"
        request_id = str(int(time.time() * 1000))
        from_addr = "0xd2176409a1ac767824921e45b7ee300745cb1e3f"
        to_addr = "0xD2176409a1Ac767824921e45B7Ee300745cB1e3f"
        amount = 1
        response = self.web3_client.web3_withdraw(coin=coin, request_id=request_id, from_addr=from_addr,
                                                  to_addr=to_addr, amount=amount)
        print(response)
        self.assertTrue(response.success)

    def test_get_web3_withdraw_transaction(self):
        request_id = "1665303298935"
        response = self.web3_client.get_web3_withdraw_transaction(request_id=request_id)
        print(response)
        self.assertTrue(response.success)

    def test_web3_contract(self):
        chain_code = "GETH"
        request_id = str(int(time.time() * 1000))
        wallet_addr = "0xd2176409a1ac767824921e45b7ee300745cb1e3f"
        contract_addr = "0xa4e8c3ec456107ea67d3075bf9e3df3a75823db0"
        method_id = "0xa9059cbb"
        method_name = "transfer"
        args = json.dumps(["0x040149e133077aebcfe4594e00638135eb4bc77f", 1])
        amount = 0
        response = self.web3_client.web3_contract(chain_code=chain_code, request_id=request_id, wallet_addr=wallet_addr,
                                                  contract_addr=contract_addr, method_id=method_id, method_name=method_name,
                                                  args=args, amount=amount)
        print(response)
        self.assertTrue(response.success)

    def test_get_web3_contract_transaction(self):
        request_id = "1664239624441"
        response = self.web3_client.get_web3_contract_transaction(request_id=request_id)
        print(response)
        self.assertTrue(response.success)

    def test_list_web3_wallet_transactions(self):
        address = "0xd2176409a1ac767824921e45b7ee300745cb1e3f"
        chain_code = "GETH"
        response = self.web3_client.list_web3_wallet_transactions(address=address, chain_code=chain_code)
        print(response)
        self.assertTrue(response.success)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument("--env", nargs='?', default="develop")
        parser.add_argument("--web3ApiSecret", type=str, required=True)
        args = parser.parse_args()
        env = args.env if args.env else "develop"
        web3_api_secret = args.web3ApiSecret

        Web3ClientTest.web3_api_secret = web3_api_secret
        Web3ClientTest.ENV = DEV_ENV
        Web3ClientTest.TEST_DATA = DEV_TEST_DATA

    # unittest.main()
    runner = unittest.TextTestRunner()
    suite = unittest.TestLoader().loadTestsFromTestCase(Web3ClientTest)
    runner.run(suite)