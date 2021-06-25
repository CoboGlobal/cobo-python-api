import unittest

from cobo.client import Client
from cobo.signer.LocalSigner import LocalSigner


class ClientTest(unittest.TestCase):

    def setUp(self):
        self.client = Client("API_KEY",
                             LocalSigner("SECRET_KET"),
                             "COBO_PUB")

    # account and address
    def test_get_account_info(self):
        res = self.client.get_account_info()
        self.assertTrue(res['success'])

    def test_get_coin_info(self):
        res = self.client.get_coin_info("ETH")
        self.assertTrue(res['success'])

    def test_new_deposit_address(self):
        res = self.client.new_deposit_address("BTC")
        self.assertTrue(res['success'])

    def test_batch_new_deposit_address(self):
        res = self.client.batch_new_deposit_address("BTC", 4)
        self.assertTrue(res['success'])

    def test_verify_deposit_address(self):
        res = self.client.verify_deposit_address("ETH", "0x05325e6f9d1f0437bd78a72c2ae084fbb8c039ee")
        self.assertTrue(res['result'])

    def test_batch_verify_deposit_address(self):
        res = self.client.batch_verify_deposit_address("ETH",
                                                       "0x05325e6f9d1f0437bd78a72c2ae084fbb8c039ee,0x05325e6f9d1f0437bd78a72c2ae084fbb8c039e1")
        self.assertTrue(res['result'])

    def test_verify_valid_address(self):
        res = self.client.verify_valid_address("ETH", "0x05325e6f9d1f0437bd78a72c2ae084fbb8c039ee")
        self.assertTrue(res['result'])

    def test_get_address_history(self):
        res = self.client.get_address_history("ETH")
        self.assertTrue(res['success'])
        self.assertTrue(len(res['result']) > 0)

    # loop alliance
    def test_check_loop_address_details(self):
        res = self.client.check_loop_address_details("ETH", "0xe7ebdc5bbb6c99cc8f7f2c1c83ff38aa6647f38a")
        self.assertTrue(res['success'])

    def test_verify_loop_address_list(self):
        res = self.client.verify_loop_address_list("ETH",
                                                   "0xe7ebdc5bbb6c99cc8f7f2c1c83ff38aa6647f38a,0x05325e6f9d1f0437bd78a72c2ae084fbb8c039ee")
        self.assertTrue(res['success'])

    def test_get_transaction_details(self):
        res = self.client.get_transaction_details("20210422193807000343569000002370")
        self.assertTrue(res['success'])

    def test_get_transactions_by_id(self):
        res = self.client.get_transactions_by_id()
        self.assertTrue(res['success'])

    def test_get_transactions_by_time(self):
        res = self.client.get_transactions_by_time()
        self.assertTrue(res['success'])

    def test_get_pending_transactions(self):
        res = self.client.get_pending_transactions()
        self.assertTrue(res['success'])

    def test_get_transaction_history(self):
        res = self.client.get_transaction_history()
        self.assertTrue(res['success'])

    def test_get_pending_transaction(self):
        res = self.client.get_pending_transaction("20200604171238000354106000006405")
        self.assertTrue(res['success'])

    def test_withdraw(self):
        res = self.client.withdraw("TETH", "0xb744adc8d75e115eec8e582eb5e8d60eb0972037", 1)
        self.assertTrue(res['success'])

    def test_query_withdraw_info(self):
        res = self.client.query_withdraw_info("teth29374893624")
        self.assertTrue(res['success'])

    def test_get_staking_product_details(self):
        res = self.client.get_staking_product_list()
        product_id = res['result'][0]['product_id']
        res = self.client.get_staking_product_details(product_id)
        self.assertTrue(res['result'])

    def test_get_staking_product_list(self):
        res = self.client.get_staking_product_list()
        self.assertTrue(res['result'])

    def test_stake(self):
        res = self.client.get_staking_product_list()
        product_id = res['result'][0]['product_id']
        res = self.client.stake(product_id, 1000000)

    def test_unstake(self):
        res = self.client.get_staking_product_list()
        product_id = res['result'][0]['product_id']
        res = self.client.unstake(product_id, 1000000)

    def test_get_stakings(self):
        res = self.client.get_stakings("DASH")
        self.assertTrue(res['success'])

    def test_get_unstakings(self):
        res = self.client.get_unstakings()
        self.assertTrue(res['success'])

    def test_get_staking_history(self):
        res = self.client.get_staking_history()
        self.assertTrue(res['success'])


if __name__ == '__main__':
    unittest.main()
