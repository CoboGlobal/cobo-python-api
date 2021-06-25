import json
import time
from hashlib import sha256
from urllib.parse import urlencode

import requests

from cobo.signer import ApiSigner
from cobo.signer.LocalSigner import verify_ecdsa_signature


class Client(object):

    def __init__(self, api_key: str, api_signer: ApiSigner, cobo_pub: str, host: str = "https://api.sandbox.cobo.com"):
        self.api_signer = api_signer
        self.api_key = api_key
        self.host = host
        self.cobo_pub = cobo_pub

    def sort_params(self, params):
        params = [(key, val) for key, val in params.items()]

        params.sort(key=lambda x: x[0])
        return urlencode(params)

    def remove_none_value_elements(self, input_dict):
        if type(input_dict) is not dict:
            return None
        result = {}
        for key in input_dict:
            tmp = {}
            if input_dict[key] is not None:
                if type(input_dict[key]).__name__ == 'dict':
                    tmp.update({key: self.remove_none_value_elements(input_dict[key])})
                else:
                    tmp.update({key: input_dict[key]})
            result.update(tmp)
        return result

    def verify_response(self, response):
        content = response.content.decode()
        success = True
        try:
            timestamp = response.headers["BIZ_TIMESTAMP"]
            signature = response.headers["BIZ_RESP_SIGNATURE"]
            success = verify_ecdsa_signature("%s|%s" % (content, timestamp), signature, self.cobo_pub)
        except KeyError:
            pass
        return success, json.loads(content)

    def request(
            self,
            method,
            path,
            params
    ):
        method = method.upper()
        nonce = str(int(time.time() * 1000))
        params = self.remove_none_value_elements(params)
        content = f"{method}|{path}|{nonce}|{self.sort_params(params)}"
        sign = self.api_signer.sign(content)

        headers = {
            "Biz-Api-Key": self.api_key,
            "Biz-Api-Nonce": nonce,
            "Biz-Api-Signature": sign,
        }
        url = f"{self.host}{path}"
        if method == "GET":
            resp = requests.get(url, params=urlencode(params), headers=headers)
        elif method == "POST":
            resp = requests.post(url, data=params, headers=headers)
        else:
            raise Exception("Not support http method")
        verify_success, result = self.verify_response(resp)
        if not verify_success:
            raise Exception("Fatal: verify content error, maybe encounter mid man attack")
        print(result)
        return result

    def get_account_info(self):
        return self.request("GET", "/v1/custody/org_info/", {})

    def get_coin_info(self, coin):
        return self.request("GET", "/v1/custody/coin_info/", {"coin": coin})

    def new_deposit_address(self, coin, native_segwit=False):
        params = {
            "coin": coin
        }
        if native_segwit:
            params.update({"native_segwit": True})
        return self.request("POST", "/v1/custody/new_address/", params)

    def batch_new_deposit_address(self, coin, count, native_segwit=False):
        params = {
            "coin": coin,
            "count": count,
        }
        if native_segwit:
            params.update({"native_segwit": True})
        return self.request("POST", "/v1/custody/new_addresses/", params)

    def verify_deposit_address(self, coin, address):
        return self.request("GET", "/v1/custody/address_info/", {"coin": coin, "address": address})

    def batch_verify_deposit_address(self, coin, addresses):
        return self.request("GET", "/v1/custody/addresses_info/", {"coin": coin, "address": addresses})

    def verify_valid_address(self, coin, address):
        return self.request("GET", "/v1/custody/is_valid_address/", {"coin": coin, "address": address})

    def get_address_history(self, coin):
        return self.request("GET", "/v1/custody/address_history/", {"coin": coin})

    # loop alliance
    def check_loop_address_details(self, coin, address, memo=None):
        params = {
            "coin": coin,
            "address": address,
        }
        if memo is not None:
            params.update({"memo": memo})
        return self.request("GET", "/v1/custody/internal_address_info/", params)

    def verify_loop_address_list(self, coin, addresses):
        return self.request("GET", "/v1/custody/internal_address_info_batch/", {
            "coin": coin,
            "address": addresses,
        })

    def get_transaction_details(self, tx_id):
        return self.request("GET", "/v1/custody/transaction/", {"id": tx_id})

    def get_transactions_by_id(self, coin=None, side=None, address=None,
                               max_id=None, min_id=None, limit=None,
                               include_financial=None):
        params = {
            "coin": coin,
            "side": side,
            "address": address,
            "max_id": max_id,
            "min_id": min_id,
            "limit": limit,
            "include_financial": include_financial
        }
        return self.request("GET", "/v1/custody/transactions_by_id/", {"id": params})

    def get_transactions_by_time(self, coin=None, side=None, address=None,
                                 begin_time=None, end_time=None, limit=None,
                                 include_financial=None):
        params = {
            "coin": coin,
            "side": side,
            "address": address,
            "begin_time": begin_time,
            "end_time": end_time,
            "limit": limit,
            "include_financial": include_financial
        }
        return self.request("GET", "/v1/custody/transactions_by_id/", {"id": params})

    def get_pending_transactions(self, coin=None, side=None,
                                 max_id=None, min_id=None, limit=None):
        params = {
            "coin": coin,
            "side": side,
            "max_id": max_id,
            "min_id": min_id,
            "limit": limit
        }
        return self.request("GET", "/v1/custody/pending_transactions/", {"id": params})

    def get_pending_transaction(self, id):
        return self.request("GET", "/v1/custody/pending_transaction/", {"id": id})

    def get_transaction_history(self, coin=None, side=None, address=None, max_id=None, min_id=None, limit=None,
                                begin_time=None, end_time=None, include_financial=None):
        params = {
            "coin": coin,
            "side": side,
            "address": address,
            "max_id": max_id,
            "min_id": min_id,
            "limit": limit,
            "begin_time": begin_time,
            "end_time": end_time,
            "include_financial": include_financial

        }
        return self.request("GET", "/v1/custody/transaction_history/", params)

    def withdraw(self, coin, address, amount, request_id=None, memo=None, force_external=None, force_internal=None):
        if not request_id:
            request_id = f"sdk_request_id_{sha256(address.encode()).digest().hex()[:8]}_{str(int(time.time() * 1000))}"

        params = {
            "coin": coin,
            "request_id": request_id,
            "address": address,
            "amount": amount,
            "memo": memo,
            "force_external": force_external,
            "force_internal": force_internal
        }

        return self.request("POST", "/v1/custody/new_withdraw_request/", params)

    def query_withdraw_info(self, request_id):
        return self.request("GET", "/v1/custody/withdraw_info_by_request_id/", {"request_id": request_id})

    def get_staking_product_details(self, product_id, language="en"):
        return self.request("GET", "/v1/custody/staking_product/", {"product_id": product_id, "language": language})

    def get_staking_product_list(self, coin=None, language="en"):
        return self.request("GET", "/v1/custody/staking_products/", {"coin": coin, "language": language})

    def stake(self, product_id, amount):
        return self.request("POST", "/v1/custody/staking_stake/", {"product_id": product_id, "amount": amount})

    def unstake(self, product_id, amount):
        return self.request("POST", "/v1/custody/staking_unstake/", {"product_id": product_id, "amount": amount})

    def get_stakings(self, coin=None, language="en"):
        return self.request("GET", "/v1/custody/stakings/", {"coin": coin, "language": language})

    def get_unstakings(self, coin=None):
        return self.request("GET", "/v1/custody/unstakings/", {"coin": coin})

    def get_staking_history(self):
        return self.request("GET", "/v1/custody/staking_history/",{})
