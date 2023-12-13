import unittest
import time
from cobo_custody.client import Client
from cobo_custody.model.enums import SortFlagEnum
from cobo_custody.signer.local_signer import LocalSigner

from parameterized import param, parameterized
from hashlib import sha256


class ClientTest(unittest.TestCase):
    api_secret = ""
    env = None

    @classmethod
    def setUpClass(cls):
        cls.client = Client(signer=LocalSigner(cls.api_secret),
                            env=cls.env,
                            debug=False)

    # account and address
    def test_get_account_info(self):
        response = self.client.get_account_info()
        self.assertTrue(response.success)

    @parameterized.expand(
        [
            param(coin="XRP"),
        ]
    )
    def test_get_valid_coin_info(self, coin):
        response = self.client.get_coin_info(coin)
        self.assertTrue(response.success)

    @parameterized.expand(
        [
            param(coin="BTC", native_segwit=True, start="bc1"),
            param(coin="BTC", native_segwit=False, start="3"),
            param(coin="BTC", native_segwit=None, start="3"),
        ]
    )
    def test_new_valid_deposit_address(self, coin, native_segwit, start):
        response = self.client.new_deposit_address(coin=coin, native_segwit=native_segwit)
        self.assertTrue(response.success)
        self.assertTrue(response.result["address"].startswith(start))

    @parameterized.expand(
        [
            param(coin="BTC", native_segwit=None, count=2),
        ]
    )
    def test_batch_new_valid_deposit_address(self, coin, native_segwit, count):
        response = self.client.batch_new_deposit_address(coin=coin, native_segwit=native_segwit, count=count)
        self.assertTrue(response.success)

    @parameterized.expand(
        [
            param(coin="BTC", address="38kcymiNQXk8WTWX9tPLRZP9wxvXPXcsFy"),
        ]
    )
    def test_verify_valid_deposit_address(self, coin, address):
        response = self.client.verify_deposit_address(coin, address)
        self.assertTrue(response.success)

    @parameterized.expand(
        [
            param(coin="BTC", addresses="38kcymiNQXk8WTWX9tPLRZP9wxvXPXcsFy,3ApTsekq5XpUtM5CzAKqntHkvoSpYdCDHw"),
        ]
    )
    def test_batch_verify_valid_deposit_address(self, coin, addresses):
        response = self.client.batch_verify_deposit_address(coin, addresses)
        self.assertTrue(response.success)

    @parameterized.expand(
        [
            param(coin="BTC", address="38kcymiNQXk8WTWX9tPLRZP9wxvXPXcsFy")
        ]
    )
    def test_verify_valid_address(self, coin, address):
        response = self.client.verify_valid_address(coin=coin, address=address)
        self.assertTrue(response.success)

    def test_get_valid_address_history(self):
        coin = "BTC"
        response = self.client.get_address_history(coin)
        self.assertTrue(response.success)

        coin = "BTC"
        page_index = "1"
        page_length = "1"
        sort_flag = SortFlagEnum.ASCENDING
        response = self.client.get_address_history(coin, page_index, page_length, sort_flag)
        self.assertTrue(response.success)

    def test_check_loop_address_details(self):
        coin = "XRP"
        address = "rBphERztHKga1cyMgWiDen7WDkbkfn1iPE"
        memo = "3414236551"
        response = self.client.check_loop_address_details(coin=coin, address=address, memo=memo)
        self.assertTrue(response.success)
        self.assertFalse(response.result["is_internal_address"])

        coin = "BTC"
        address = "38kcymiNQXk8WTWX9tPLRZP9wxvXPXcsFy"
        memo = None
        response = self.client.check_loop_address_details(coin=coin, address=address, memo=memo)
        self.assertTrue(response.success)
        self.assertFalse(response.result["is_internal_address"])

    def test_verify_loop_address_list(self):
        coin = "BTC"
        address = "38kcymiNQXk8WTWX9tPLRZP9wxvXPXcsFy,32WT5Thw3o2awNX113EbX9kNHgn7VcuRsi"

        response = self.client.verify_loop_address_list(coin=coin, addresses=address)
        self.assertTrue(response.success)

    def test_get_transaction_details_by_coboID(self):
        cobo_id = "20231206130534000116223000007648"
        response = self.client.get_transaction_details(cobo_id)
        self.assertTrue(response.success)

    def test_get_transaction_by_txid(self):
        tx_id = "0x36cec6c56310172325d0c4ac342447b3b93aa248289fea2e2a6740857a6a59a0"
        response = self.client.get_transaction_by_txid(tx_id)
        self.assertTrue(response.success)

    def test_get_transactions_by_id(self):
        response = self.client.get_transactions_by_id()
        self.assertTrue(response.success)

        coin = "COBO_ETH"
        side = "deposit"
        address = "0xefeff29688deaa32c20cdb4fc54d8285a31ada4e"
        max_id = "20231206130534000116223000007648"
        response = self.client.get_transactions_by_id(coin=coin, side=side, address=address, max_id=max_id)
        self.assertTrue(response.success)

        coin = "COBO_ETH"
        min_id = "20231206130534000116223000007648"
        response = self.client.get_transactions_by_id(coin=coin, min_id=min_id)
        self.assertTrue(response.success)

    def test_get_transactions_by_time(self):
        response = self.client.get_transactions_by_time()
        self.assertTrue(response.success)

        coin = "COBO_ETH"
        side = "deposit"
        address = "0xefeff29688deaa32c20cdb4fc54d8285a31ada4e"
        begin_time = "1701839134"
        response = self.client.get_transactions_by_time(coin=coin, side=side, address=address,
                                                        begin_time=begin_time)
        self.assertTrue(response.success)

        end_time = "1701839134"
        response = self.client.get_transactions_by_time(coin=coin, side=side, address=address, end_time=end_time)
        self.assertTrue(response.success)

    def test_get_transactions_by_time_ex(self):
        response = self.client.get_transactions_by_time_ex()
        self.assertTrue(response.success)

        coins = "COBO_ETH"
        side = 2
        address = "0xefeff29688deaa32c20cdb4fc54d8285a31ada4e"
        status = 900
        begin_time = 1701839134
        end_time = 1701839134
        limit = 10
        offset = 0
        order_by = "created_time"
        order = "ASC"

        response = self.client.get_transactions_by_time_ex(coins=coins,
                                                           side=side,
                                                           address=address,
                                                           status=status,
                                                           begin_time=begin_time,
                                                           end_time=end_time,
                                                           limit=limit,
                                                           offset=offset,
                                                           order=order,
                                                           order_by=order_by)
        self.assertTrue(response.success)

    def test_get_pending_transactions(self):
        response = self.client.get_pending_transactions()
        self.assertTrue(response.success)

        coin = "COBO_ETH"
        side = "deposit"
        max_id = "20231206130534000116223000007648"
        min_id = "20231206130534000116223000007648"
        limit = "1"

        response = self.client.get_pending_transactions(coin=coin,
                                                        side=side,
                                                        max_id=max_id,
                                                        min_id=min_id,
                                                        limit=limit)
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

    def test_get_transactions_by_request_ids(self):
        request_ids = "IntegrationTest-848427217479639409,IntegrationTest-848427217358004633"
        response = self.client.get_transactions_by_request_ids(request_ids=request_ids)
        self.assertTrue(response.success)

    @parameterized.expand(
        [
            param(coin="COBO_ETH", address="0xE410157345be56688F43FF0D9e4B2B38Ea8F7828", memo=None, amount=1),
            param(coin="XLM", address="GBJDU6TPWHKGV7HRLNTIBA46MG3MB5DUG6BISHX3BF7I75H2HLPV6RJX", memo="4e73f03b",
                  amount=1)
        ]
    )
    def test_withdraw(self, coin, address, memo, amount):
        request_id = f"request_id_{sha256(address.encode()).digest().hex()[:8]}_{str(int(time.time() * 1000))}"
        response = self.client.withdraw(coin=coin, address=address, memo=memo, amount=amount, request_id=request_id)
        self.assertTrue(response.success)

    def test_query_withdraw_info(self):
        request_id = "IntegrationTest-848427217479639409"
        response = self.client.query_withdraw_info(request_id)
        self.assertTrue(response.success)

    def test_get_staking_product_list(self):
        response = self.client.get_staking_product_list()
        self.assertTrue(response.success)

    def test_get_staking_product_details(self):
        response = self.client.get_staking_product_list()
        if len(response.result):
            product_id = response.result[0]['product_id']
            response = self.client.get_staking_product_details(product_id)
            self.assertTrue(response.success)
        else:
            self.skipTest("no staking product")

    def test_stake(self):
        response = self.client.get_staking_product_list(coin="TETH")
        if len(response.result) > 0:
            product_id = response.result[0]['product_id']
            response = self.client.stake(product_id, 1000000)
            self.assertTrue(response.success)
        else:
            self.skipTest("no TETH staking product")

    def test_unstake(self):
        response = self.client.get_staking_product_list(coin="TETH")
        if len(response.result) > 0:
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
