import unittest
import time
from cobo_custody.signer.local_signer import LocalSigner
from cobo_custody.client.mpc_client import MPCClient


class MPCClientTest(unittest.TestCase):
    mpc_api_secret = ""
    env = None

    @classmethod
    def setUpClass(cls):
        cls.mpc_client = MPCClient(signer=LocalSigner(cls.mpc_api_secret),
                                   env=cls.env,
                                   debug=False)

    def test_get_supported_chains(self):
        response = self.mpc_client.get_supported_chains()
        # print(response)
        self.assertTrue(response.success)

    def test_get_supported_coins(self):
        chain_code = "GETH"
        response = self.mpc_client.get_supported_coins(chain_code=chain_code)
        # print(response)
        self.assertTrue(response.success)

    def test_get_wallet_supported_coins(self):
        response = self.mpc_client.get_wallet_supported_coins()
        # print(response)
        self.assertTrue(response.success)

    def test_is_valid_address(self):
        coin = "GETH"
        address = "0x3ede1e59a3f3a66de4260df7ba3029b515337e5c"
        response = self.mpc_client.is_valid_address(coin=coin, address=address)
        # print(response)
        self.assertTrue(response.success)

    def test_generate_addresses(self):
        chain_code = "GETH"
        count = 2
        response = self.mpc_client.generate_addresses(chain_code=chain_code, count=count)
        # print(response)
        self.assertTrue(response.success)

    def test_update_address_description(self):
        coin = "GETH"
        address = "0x6a060efe0ff887f4e24dc2d2098020abf28bcce4"
        description = "test"
        response = self.mpc_client.update_address_description(coin=coin, address=address, description=description)
        # print(response)
        self.assertTrue(response.success)

    def test_list_addresses(self):
        chain_code = "GETH"
        response = self.mpc_client.list_addresses(chain_code=chain_code)
        # print(response)
        self.assertTrue(response.success)

    def test_get_balance(self):
        address = "0x6a060efe0ff887f4e24dc2d2098020abf28bcce4"
        coin = "GETH"
        response = self.mpc_client.get_balance(address=address, coin=coin)
        # print(response)
        self.assertTrue(response.success)

    def test_list_balances(self):
        coin = "GETH"
        chain_code = "GETH"
        page_index = 0
        page_length = 50
        response = self.mpc_client.list_balances(coin=coin, chain_code=chain_code, page_index=page_index,
                                                 page_length=page_length)
        # print(response)
        self.assertTrue(response.success)

    def test_create_transaction(self):
        coin = "GETH"
        request_id = str(int(time.time() * 1000))
        from_addr = "0x6a060efe0ff887f4e24dc2d2098020abf28bcce4"
        to_addr = "0x6a060efe0ff887f4e24dc2d2098020abf28bcce4"
        amount = "10"
        response = self.mpc_client.create_transaction(coin=coin, request_id=request_id, from_addr=from_addr,
                                                      to_addr=to_addr, amount=amount)
        # print(response)
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
        request_ids = "web_send_by_user_453_1702345165920"
        response = self.mpc_client.transactions_by_request_ids(request_ids=request_ids)
        # print(response)
        self.assertTrue(response.success)

    def test_transactions_by_tx_hash(self):
        tx_hash = "0xc8592ef7821b1d21d92309f902a583cf4f64bbcf500056e663c9e95900f31bbe"
        response = self.mpc_client.transactions_by_tx_hash(tx_hash=tx_hash)
        # print(response)
        self.assertTrue(response.success)

    def test_list_transactions(self):
        response = self.mpc_client.list_transactions()
        # print(response)
        self.assertTrue(response.success)

    # 有bug，待解决；https://pha.1cobo.com/T58503
    def test_list_tss_node_requests(self):
        self.skipTest("有bug，待解决")
        response = self.mpc_client.list_tss_node_requests()
        print(response)
        self.assertTrue(response.success)

    def test_list_spendable(self):
        coin = "GETH"
        response = self.mpc_client.list_spendable(coin=coin)
        # print(response)
        self.assertTrue(response.success)

    def test_estimate_fee(self):
        coin = "GETH"
        amount = 10000
        address = "0xEEACb7a5e53600c144C0b9839A834bb4b39E540c"
        response = self.mpc_client.estimate_fee(coin=coin, amount=amount, address=address)
        # print(response)
        self.assertTrue(response.success)

    def test_retry_double_check(self):
        request_id = "web_send_by_user_453_1702345165920"
        response = self.mpc_client.retry_double_check(request_id=request_id)
        # print(response)
        self.assertFalse(response.success)

    def test_sign_messages_by_request_ids(self):
        request_ids = "web_send_by_user_453_1702345165920,1702350828108"
        response = self.mpc_client.sign_messages_by_request_ids(request_ids=request_ids)
        # print(response)
        self.assertTrue(response.success)

    def test_sign_messages_by_cobo_ids(self):
        cobo_ids = "20231212111349000140669000006194,20231212094205000140669000003110"
        response = self.mpc_client.sign_messages_by_cobo_ids(cobo_ids=cobo_ids)
        # print(response)
        self.assertTrue(response.success)