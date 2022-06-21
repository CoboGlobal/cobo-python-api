import unittest

from cobo_custody.client import Client
from cobo_custody.config import SANDBOX
from cobo_custody.signer.local_signer import LocalSigner


class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = Client(signer=LocalSigner("apiSecret"),
                             env=SANDBOX,
                             debug=True)

    # account and address
    def test_get_account_info(self):
        response = self.client.get_account_info()
        self.assertTrue(response.success)

    def test_get_coin_info(self):
        response = self.client.get_coin_info("ETH")
        self.assertTrue(response.success)

    def test_new_deposit_address(self):
        response = self.client.new_deposit_address("BTC")
        self.assertTrue(response.success)

    def test_batch_new_deposit_address(self):
        response = self.client.batch_new_deposit_address("BTC", 4)
        self.assertTrue(response.success)

    def test_verify_deposit_address(self):
        response = self.client.verify_deposit_address("ETH", "0x05325e6f9d1f0437bd78a72c2ae084fbb8c039ee")
        self.assertTrue(response.success)

    def test_batch_verify_deposit_address(self):
        response = self.client.batch_verify_deposit_address("ETH",
                                                            "0x05325e6f9d1f0437bd78a72c2ae084fbb8c039ee,0x05325e6f9d1f0437bd78a72c2ae084fbb8c039e1")
        self.assertTrue(response.success)

    def test_verify_valid_address(self):
        response = self.client.verify_valid_address("ETH", "0x05325e6f9d1f0437bd78a72c2ae084fbb8c039ee")
        self.assertTrue(response.success)

    def test_get_address_history(self):
        response = self.client.get_address_history("ETH")
        self.assertTrue(response.success)
        self.assertTrue(len(response.result) > 0)

    # loop alliance
    def test_check_loop_address_details(self):
        response = self.client.check_loop_address_details("ETH", "0xe7ebdc5bbb6c99cc8f7f2c1c83ff38aa6647f38a")
        self.assertTrue(response.success)

    def test_verify_loop_address_list(self):
        response = self.client.verify_loop_address_list("ETH",
                                                        "0xe7ebdc5bbb6c99cc8f7f2c1c83ff38aa6647f38a,0x05325e6f9d1f0437bd78a72c2ae084fbb8c039ee")
        self.assertTrue(response.success)

    def test_get_transaction_details(self):
        response = self.client.get_transaction_details("20210422193807000343569000002370")
        self.assertTrue(response.success)

    def test_get_transaction_by_txid(self):
        response = self.client.get_transaction_by_txid("0x5d5396c3992ed524bf68a22a7ab6ae503f034")
        self.assertTrue(response.success)

    def test_get_transactions_by_id(self):
        response = self.client.get_transactions_by_id()
        self.assertTrue(response.success)

    def test_get_transactions_by_time(self):
        response = self.client.get_transactions_by_time()
        self.assertTrue(response.success)

    def test_get_pending_transactions(self):
        response = self.client.get_pending_transactions()
        self.assertTrue(response.success)

    def test_get_transaction_history(self):
        response = self.client.get_transaction_history()
        self.assertTrue(response.success)

    def test_get_pending_transaction(self):
        response = self.client.get_pending_transaction("20200604171238000354106000006405")
        self.assertTrue(response.success)

    def test_withdraw(self):
        response = self.client.withdraw("TETH", "0xb744adc8d75e115eec8e582eb5e8d60eb0972037", 1)
        self.assertTrue(response.success)

    def test_query_withdraw_info(self):
        response = self.client.query_withdraw_info("teth29374893624")
        self.assertTrue(response.success)

    def test_get_staking_product_details(self):
        response = self.client.get_staking_product_list()
        product_id = response.result[0]['product_id']
        response = self.client.get_staking_product_details(product_id)
        self.assertTrue(response.success)

    def test_get_staking_product_list(self):
        response = self.client.get_staking_product_list()
        self.assertTrue(response.success)

    def test_stake(self):
        response = self.client.get_staking_product_list()
        product_id = response.result[0]['product_id']
        response = self.client.stake(product_id, 1000000)

    def test_unstake(self):
        response = self.client.get_staking_product_list()
        product_id = response.result[0]['product_id']
        response = self.client.unstake(product_id, 1000000)

    def test_get_stakings(self):
        response = self.client.get_stakings("DASH")
        self.assertTrue(response.success)

    def test_get_unstakings(self):
        response = self.client.get_unstakings()
        self.assertTrue(response.success)

    def test_get_staking_history(self):
        response = self.client.get_staking_history()
        self.assertTrue(response.success)


if __name__ == '__main__':
    unittest.main()
