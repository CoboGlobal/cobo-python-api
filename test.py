from cobo_custody.config import SANDBOX_ENV as ENV
from cobo_custody.config import SANDBOX_TEST_DATA as TEST_DATA
# from cobo_custody.config import PROD_ENV as ENV
# from cobo_custody.config import PROD_TEST_DATE as TEST_DATA

import unittest
from cobo_custody.client import Client
from cobo_custody.signer.local_signer import LocalSigner
from parameterized import param, parameterized

class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = Client(signer=LocalSigner("apiSecret"),
                             env=ENV,
                             debug=True)

    # account and address
    def test_get_account_info(self):
        response = self.client.get_account_info()
        self.assertTrue(response.success)

    @parameterized.expand(
        [
            param(coin="BTC"),
            param(coin="ETH"),
            param(coin="ETH_USDT"),
            param(coin="XRP"),
        ]
    )
    def test_get_valid_coin_info(self, coin):
        response = self.client.get_coin_info(coin)
        self.assertTrue(response.success)

    @parameterized.expand(
        [
            param(coin="BTTB")
        ]
    )
    def test_get_invalid_coin_info(self, coin):
        response = self.client.get_coin_info(coin)
        self.assertFalse(response.success)
        # Coin BTTB not supported, please add it on admin web.
        self.assertEqual(response.exception.errorCode, 12002)

    @parameterized.expand(
        [
            param(coin="BTC", native_segwit=True),
            param(coin="BTC", native_segwit=False),
            param(coin="ETH", native_segwit=False),
            param(coin="ETH_USDT", native_segwit=False),
            param(coin="XRP", native_segwit=False),
        ]
    )
    def test_new_valid_deposit_address(self, coin, native_segwit):
        response = self.client.new_deposit_address(coin=coin, native_segwit=native_segwit)
        self.assertTrue(response.success)

    @parameterized.expand(
        [
            param(coin="BTTB", native_segwit=True),
            param(coin="ETTE", native_segwit=False)
        ]
    )
    def test_new_invalid_deposit_address(self, coin, native_segwit):
        response = self.client.new_deposit_address(coin=coin, native_segwit=native_segwit)
        self.assertFalse(response.success)
        # Coin BTTB not supported, please add it on admin web.
        self.assertEqual(response.exception.errorCode, 12002)


    @parameterized.expand(
        [
            param(coin="BTC", native_segwit=True, count=2),
            param(coin="BTC", native_segwit=False, count=2),
            param(coin="ETH", native_segwit=False, count=2),
            param(coin="ETH_USDT", native_segwit=False, count=2),
            param(coin="XRP", native_segwit=False, count=2),
        ]
    )
    def test_batch_new_valid_deposit_address(self, coin, native_segwit, count):
        response = self.client.batch_new_deposit_address(coin=coin,native_segwit=native_segwit, count=count)
        print(response)
        self.assertTrue(response.success)

    @parameterized.expand(
        [
            param(coin="BTTB", native_segwit=True, count=2),
            param(coin="ETTE", native_segwit=False, count=2)
        ]
    )
    def test_batch_new_invalid_deposit_address(self, coin, native_segwit, count):
        response = self.client.batch_new_deposit_address(coin=coin,native_segwit=native_segwit, count=count)
        self.assertFalse(response.success)
        # Coin BTTB not supported, please add it on admin web.
        self.assertEqual(response.exception.errorCode, 12002)

    @parameterized.expand(
        [
            param(coin="BTC", address=TEST_DATA["deposit_address"]["BTC"]),
            param(coin="XRP", address=TEST_DATA["deposit_address"]["XRP"])
        ]
    )
    def test_verify_valid_deposit_address(self, coin, address):
        response = self.client.verify_deposit_address(coin=coin, address=address)
        self.assertTrue(response.success)

    @parameterized.expand(
        [
            param(coin="BTC", address="3Kd5rjiLtvpHv5nhYQNTTeRLgrz4om32PJ"),
            param(coin="XRP", address="rndm7RphBZG6CpZvKcG9AjoFbSvcKhwLCx")
        ]
    )
    def test_verify_invalid_deposit_address(self, coin, address):
        response = self.client.verify_deposit_address(coin=coin, address=address)
        self.assertFalse(response.success)
        self.assertEqual(response.exception.errorCode, 12015)

    @parameterized.expand(
        [
            param(coin="BTC", addresses=TEST_DATA["deposit_addresses"]["BTC"], count=2),
            param(coin="XRP", addresses=TEST_DATA["deposit_addresses"]["XRP"], count=2)
        ]
    )
    def test_batch_verify_valid_deposit_address(self, coin, addresses, count):
        response = self.client.batch_verify_deposit_address(coin=coin, addresses=addresses)
        self.assertTrue(response.success)
        self.assertEqual(len(response.result["addresses"].split(",")), count)

    @parameterized.expand(
        [
            param(coin="BTC", addresses="3Kd5rjiLtvpHv5nhYQNTTeRLgrz4om32PJ,bc1q9unqc738dxjg5mk8zqtz33zg59cahrj29s24lp", count=0),
            param(coin="XRP", addresses="rndm7RphBZG6CpZvKcG9AjoFbSvcKhwLCx,rrBD4sBsxrpzbohAEYWH4moPSsoxupWLA|00000000", count=0)
        ]
    )
    def test_batch_verify_invalid_deposit_address(self, coin, addresses, count):
        response = self.client.batch_verify_deposit_address(coin=coin, addresses=addresses)
        self.assertTrue(response.success)
        self.assertEqual(len(response.result["addresses"]), count)

    @parameterized.expand(
        [
            param(coin="BTC", address="3Kd5rjiLtvpHv5nhYQNTTeRLgrz4om32PJ"),
            param(coin="BTC", address="bc1q9unqc738dxjg5mk8zqtz33zg59cahrj29s24lp"),
            param(coin="ETH", address="0xE410157345be56688F43FF0D9e4B2B38Ea8F7828"),
            param(coin="ETH_USDT", address="0xEEACb7a5e53600c144C0b9839A834bb4b39E540c"),
            param(coin="XRP", address="rndm7RphBZG6CpZvKcG9AjoFbSvcKhwLCx"),
            param(coin="XRP", address="rGNXLMNHkUEtoo7qkCSHEm2sfMo8F969oZ|2200701580")
        ]
    )
    def test_verify_valid_address(self, coin, address):
        response = self.client.verify_valid_address(coin=coin, address=address)
        self.assertTrue(response.success)

    @parameterized.expand(
        [
            param(coin="BTC", address="0xE410157345be56688F43FF0D9e4B2B38Ea8F7828"),
            param(coin="XRP", address="rBWpYJhuJWBPAkzJ4kYQqHShSkkF3rgeDE"),
        ]
    )
    def test_verify_invalid_address(self, coin, address):
        response = self.client.verify_valid_address(coin, address)
        self.assertTrue(response.success)
        self.assertFalse(response.result)

    @parameterized.expand(
        [
            param(coin="BTC"),
            param(coin="ETH"),
            param(coin="ETH_USDT"),
            param(coin="XRP"),
        ]
    )
    def test_get_valid_address_history(self, coin):
        response = self.client.get_address_history(coin=coin)
        self.assertTrue(response.success)
        self.assertTrue(len(response.result) > 0)

    @parameterized.expand(
        [
            param(coin="BTTB"),
        ]
    )
    def test_get_invalid_address_history(self, coin):
        response = self.client.get_address_history(coin=coin)
        self.assertFalse(response.success)
        # Coin BTTB not supported, please add it on admin web.
        self.assertEqual(response.exception.errorCode, 12002)


    @parameterized.expand(
        [
            param(coin="BTC", address=TEST_DATA["loop_address"]["BTC"], memo=None),
            param(coin="XRP", address=TEST_DATA["loop_address"]["XRP"].split("|")[0], memo=TEST_DATA["loop_address"]["XRP"].split("|")[1]),
        ]
    )
    def test_check_loop_address_details(self, coin, address, memo=None):
        response = self.client.check_loop_address_details(coin=coin, address=address, memo=memo)
        self.assertTrue(response.success)
        self.assertTrue(response.result["is_internal_address"])

    @parameterized.expand(
        [
            param(coin="BTC", addresses=TEST_DATA["loop_addresses"]["BTC"]),
            param(coin="XRP", addresses=TEST_DATA["loop_addresses"]["XRP"]),
        ]
    )
    def test_verify_loop_address_list(self, coin, addresses):
        response = self.client.verify_loop_address_list(coin=coin, addresses=addresses)
        self.assertTrue(response.success)
        for address_info in response.result:
            self.assertTrue(address_info["is_internal_address"])

    def test_get_transaction_details(self):
        response = self.client.get_transaction_details(TEST_DATA["tx_id"])
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
        response = self.client.get_pending_transactions()
        if len(response.result):
            pending_id = response.result[0]["id"]
            response = self.client.get_pending_transaction(id=pending_id)
            self.assertTrue(response.success)
        else:
            self.skipTest("no pending transactions")

    @parameterized.expand(
        [
            param(coin="COBO_ETH", address="0xE410157345be56688F43FF0D9e4B2B38Ea8F7828",memo=None, amount=1),
            param(coin="XRP", address="rndm7RphBZG6CpZvKcG9AjoFbSvcKhwLCx",memo=None, amount=1),
            param(coin="XRP", address="rGNXLMNHkUEtoo7qkCSHEm2sfMo8F969oZ",memo="2200701580", amount=1)
        ]
    )
    def test_withdraw(self, coin, address, memo, amount):
        response = self.client.withdraw(coin=coin, address=address, memo=memo, amount=amount)
        self.assertTrue(response.success)

    def test_query_withdraw_info(self):
        response = self.client.query_withdraw_info(TEST_DATA["withdraw_id"])
        self.assertTrue(response.success)

    def test_get_staking_product_list(self):
        response = self.client.get_staking_product_list()
        self.assertTrue(response.success)

    def test_get_staking_product_details(self):
        response = self.client.get_staking_product_list()
        product_id = response.result[0]['product_id']
        response = self.client.get_staking_product_details(product_id)
        self.assertTrue(response.success)

    def test_stake(self):
        response = self.client.get_staking_product_list(coin="TETH")
        if len(response.result)>0:
            product_id = response.result[0]['product_id']
            response = self.client.stake(product_id, 1000000)
            self.assertTrue(response.success)
        else:
            self.skipTest("no TETH staking product")

    def test_unstake(self):
        response = self.client.get_staking_product_list(coin="TETH")
        if len(response.result)>0:
            product_id = response.result[0]['product_id']
            response = self.client.unstake(product_id, 1000000)
            self.assertTrue(response.success)
        else:
            self.skipTest("no TETH staking product")

    def test_get_stakings(self):
        response = self.client.get_stakings()
        self.assertTrue(response.success)

    def test_get_unstakings(self):
        response = self.client.get_unstakings()
        self.assertTrue(response.success)

    def test_get_staking_history(self):
        response = self.client.get_staking_history()
        self.assertTrue(response.success)


if __name__ == '__main__':
    unittest.main()
