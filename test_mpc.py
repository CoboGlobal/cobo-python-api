from cobo_custody.client.mpc_client import MPCClient
from cobo_custody.config import DEV_ENV
from cobo_custody.config import DEV_TEST_DATA

import unittest
from cobo_custody.signer.local_signer import LocalSigner
import sys
import argparse
import time


class MPCClientTest(unittest.TestCase):
    mpc_api_secret = ""
    ENV = DEV_ENV
    TEST_DATA = DEV_TEST_DATA

    def setUp(self):
        self.mpc_client = MPCClient(signer=LocalSigner(self.mpc_api_secret),
                                    env=self.ENV,
                                    debug=False)

    def test_get_supported_chains(self):
        response = self.mpc_client.get_supported_chains()
        print(response)
        self.assertTrue(response.success)

    def test_get_supported_coins(self):
        chain_code = "GETH"
        response = self.mpc_client.get_supported_coins(chain_code=chain_code)
        print(response)
        self.assertTrue(response.success)

    def test_get_wallet_supported_coins(self):
        response = self.mpc_client.get_wallet_supported_coins()
        print(response)
        self.assertTrue(response.success)

    def test_is_valid_address(self):
        coin = "GETH"
        address = "0x3ede1e59a3f3a66de4260df7ba3029b515337e5c"
        response = self.mpc_client.is_valid_address(coin=coin, address=address)
        print(response)
        self.assertTrue(response.success)

    def test_generate_addresses(self):
        chain_code = "GETH"
        count = 2
        response = self.mpc_client.generate_addresses(chain_code=chain_code, count=count)
        print(response)
        self.assertTrue(response.success)

    def test_update_address_description(self):
        coin = "GETH"
        address = "0x6da78aece2d350ca4078ee66a61c3f4cc49eb9bf"
        description = "test1"
        response = self.mpc_client.update_address_description(coin=coin, address=address, description=description)
        print(response)
        self.assertTrue(response.success)

    def test_list_addresses(self):
        chain_code = "GETH"
        response = self.mpc_client.list_addresses(chain_code=chain_code)
        print(response)
        self.assertTrue(response.success)

    def test_get_balance(self):
        address = "0x3ede1e59a3f3a66de4260df7ba3029b515337e5c"
        coin = "GETH"
        response = self.mpc_client.get_balance(address=address, coin=coin)
        print(response)
        self.assertTrue(response.success)

    def test_list_balances(self):
        coin = "GETH"
        chain_code = "GETH"
        page_index = 0
        page_length = 50
        response = self.mpc_client.list_balances(coin=coin, chain_code=chain_code, page_index=page_index, page_length=page_length)
        print(response)
        self.assertTrue(response.success)

    def test_create_transaction(self):
        coin = "GETH"
        request_id = str(int(time.time() * 1000))
        from_addr = "0x3ede1e59a3f3a66de4260df7ba3029b515337e5c"
        to_addr = "0xEEACb7a5e53600c144C0b9839A834bb4b39E540c"
        amount = "10"
        response = self.mpc_client.create_transaction(coin=coin, request_id=request_id, from_addr=from_addr,
                                                      to_addr=to_addr, amount=amount)
        print(response)
        self.assertTrue(response.success)

    def test_create_transaction_gas_station(self):
        coin = "GETH"
        request_id = str(int(time.time() * 1000))
        from_addr = "0x3ede1e59a3f3a66de4260df7ba3029b515337e5c"
        to_addr = "0xEEACb7a5e53600c144C0b9839A834bb4b39E540c"
        amount = "10"
        response = self.mpc_client.create_transaction(coin=coin, request_id=request_id, from_addr=from_addr,
                                                      to_addr=to_addr, amount=amount, auto_fuel=2)
        print(response)
        self.assertTrue(response.success)

    def test_transactions_by_request_ids(self):
        request_ids = "1668678820274"
        response = self.mpc_client.transactions_by_request_ids(request_ids=request_ids)
        print(response)
        self.assertTrue(response.success)

    def test_transactions_by_tx_hash(self):
        tx_hash = "0x1e14311142db1f5b02e587f0e00643f7fd460c81e73dffff65cf501123fb99dd"
        response = self.mpc_client.transactions_by_tx_hash(tx_hash=tx_hash)
        print(response)
        self.assertTrue(response.success)

    def test_list_transactions(self):
        response = self.mpc_client.list_transactions()
        print(response)
        self.assertTrue(response.success)

    def test_list_tss_node_requests(self):
        response = self.mpc_client.list_tss_node_requests()
        print(response)
        self.assertTrue(response.success)

    def test_list_spendable(self):
        coin = "BTC"
        response = self.mpc_client.list_spendable(coin=coin)
        print(response)
        self.assertTrue(response.success)

    def test_estimate_fee(self):
        coin = "GETH"
        amount = 10000
        address = "0xEEACb7a5e53600c144C0b9839A834bb4b39E540c"
        response = self.mpc_client.estimate_fee(coin=coin, amount=amount, address=address)
        print(response)
        self.assertTrue(response.success)

    def test_retry_double_check(self):
        request_id = "123"
        response = self.mpc_client.retry_double_check(request_id=request_id)
        print(response)
        self.assertFalse(response.success)

    def test_sign_messages_by_request_ids(self):
        request_ids = "1690349242683,1690268795963,1690187858862"
        response = self.mpc_client.sign_messages_by_request_ids(request_ids=request_ids)
        print(response)

    def test_sign_messages_by_cobo_ids(self):
        cobo_ids = "20230726132723000341052000008222,20230725150636000308867000003494,20230725135301000361318000002480"
        response = self.mpc_client.sign_messages_by_cobo_ids(cobo_ids=cobo_ids)
        print(response)

    def test_get_max_send_amount(self):
        response = self.mpc_client.get_max_send_amount(coin="GETH", fee_rate=0, to_address='0xEEACb7a5e53600c144C0b9839A834bb4b39E540c')
        print(response)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument("--env", nargs='?', default="develop")
        parser.add_argument("--mpcApiSecret", type=str, required=True)
        args = parser.parse_args()
        env = args.env if args.env else "develop"
        mpc_api_secret = args.mpcApiSecret

        MPCClientTest.mpc_api_secret = mpc_api_secret
        MPCClientTest.ENV = DEV_ENV
        MPCClientTest.TEST_DATA = DEV_TEST_DATA

    # unittest.main()
    runner = unittest.TextTestRunner()
    suite = unittest.TestLoader().loadTestsFromTestCase(MPCClientTest)
    runner.run(suite)
