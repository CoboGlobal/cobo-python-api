import json
import time
from hashlib import sha256
from typing import Tuple
from urllib.parse import urlencode

import requests

from cobo_custody.client.api_response import ApiResponse
from cobo_custody.config import Env
from cobo_custody.error.api_error import ApiError
from cobo_custody.signer.api_signer import ApiSigner
from cobo_custody.signer.local_signer import verify_ecdsa_signature
from cobo_custody.model.enums import SortFlagEnum


class Client(object):

    def __init__(self, signer: ApiSigner, env: Env, debug: bool = False):
        self.api_signer = signer
        self.env = env
        self.debug = debug

    def sort_params(self, params: dict) -> str:
        params = [(key, val) for key, val in params.items()]

        params.sort(key=lambda x: x[0])
        return urlencode(params)

    def remove_none_value_elements(self, input_dict: dict) -> dict:
        if type(input_dict) is not dict:
            return {}
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

    def verify_response(self, response: requests.Response) -> Tuple[bool, dict]:
        content = response.content.decode()
        success = True
        try:
            timestamp = response.headers["BIZ_TIMESTAMP"]
            signature = response.headers["BIZ_RESP_SIGNATURE"]
            if self.debug:
                print(f"response <<<<<<<< \n content: {content}\n headers: {response.headers} \n")
            success = verify_ecdsa_signature("%s|%s" % (content, timestamp), signature, self.env.coboPub)
        except KeyError:
            pass
        return success, json.loads(content)

    def request(
            self,
            method: str,
            path: str,
            params: dict
    ) -> ApiResponse:
        method = method.upper()
        nonce = str(int(time.time() * 1000 * 1000))
        params = self.remove_none_value_elements(params)
        content = f"{method}|{path}|{nonce}|{self.sort_params(params)}"
        sign = self.api_signer.sign(content)

        headers = {
            "Biz-Api-Key": self.api_signer.get_public_key(),
            "Biz-Api-Nonce": nonce,
            "Biz-Api-Signature": sign,
        }
        url = f"{self.env.host}{path}"
        if self.debug:
            print(f"request >>>>>>>>\n method: {method} \n url: {url} \n params: {params} \n headers: {headers} \n")

        if method == "GET":
            resp = requests.get(url, params=urlencode(params), headers=headers)
        elif method == "POST":
            resp = requests.post(url, data=params, headers=headers)
        else:
            raise Exception("Not support http method")
        verify_success, result = self.verify_response(resp)
        if not verify_success:
            raise Exception("Fatal: verify content error, maybe encounter mid man attack")

        success = result['success']
        if success:
            return ApiResponse(True, result['result'], None)
        else:
            exception = ApiError(result['error_code'], result['error_message'], result['error_id'])
            return ApiResponse(False, None, exception)

    def get_account_info(self) -> ApiResponse:
        return self.request("GET", "/v1/custody/org_info/", {})

    def get_coin_info(self, coin: str) -> ApiResponse:
        return self.request("GET", "/v1/custody/coin_info/", {"coin": coin})

    def get_supported_coins(self) -> ApiResponse:
        return self.request("GET", "/v1/custody/get_supported_coins/", {})

    def new_deposit_address(self, coin: str, native_segwit: bool = False) -> ApiResponse:
        params = {
            "coin": coin
        }
        if native_segwit:
            params.update({"native_segwit": True})
        return self.request("POST", "/v1/custody/new_address/", params)

    def batch_new_deposit_address(self, coin: str, count: int, native_segwit: bool = False) -> ApiResponse:
        params = {
            "coin": coin,
            "count": count,
        }
        if native_segwit:
            params.update({"native_segwit": True})
        return self.request("POST", "/v1/custody/new_addresses/", params)

    def verify_deposit_address(self, coin: str, address: str) -> ApiResponse:
        return self.request("GET", "/v1/custody/address_info/", {"coin": coin, "address": address})

    def batch_verify_deposit_address(self, coin: str, addresses: str) -> ApiResponse:
        return self.request("GET", "/v1/custody/addresses_info/", {"coin": coin, "address": addresses})

    def verify_valid_address(self, coin: str, address: str) -> ApiResponse:
        return self.request("GET", "/v1/custody/is_valid_address/", {"coin": coin, "address": address})

    def get_address_history(self, coin: str, page_index=None, page_length=None,
                            sort_flag=SortFlagEnum.DESCENDING) -> ApiResponse:
        return self.request("GET", "/v1/custody/address_history/", {
            "coin": coin, "page_index": page_index, "page_length": page_length, "sort_flag": sort_flag.value})

    # loop alliance
    def check_loop_address_details(self, coin: str, address: str, memo: str = None) -> ApiResponse:
        params = {
            "coin": coin,
            "address": address,
        }
        if memo is not None:
            params.update({"memo": memo})
        return self.request("GET", "/v1/custody/internal_address_info/", params)

    def verify_loop_address_list(self, coin: str, addresses: str) -> ApiResponse:
        return self.request("GET", "/v1/custody/internal_address_info_batch/", {
            "coin": coin,
            "address": addresses,
        })

    def get_transaction_details(self, tx_id: str) -> ApiResponse:
        return self.request("GET", "/v1/custody/transaction/", {"id": tx_id})

    def get_transaction_by_txid(self, txid: str) -> ApiResponse:
        return self.request("GET", "/v1/custody/transaction_by_txid/", {"txid": txid})

    def get_transactions_by_id(self, coin: str = None, side: str = None, address: str = None,
                               max_id: str = None, min_id: str = None, limit: str = None,
                               include_financial: str = None) -> ApiResponse:
        params = {
            "coin": coin,
            "side": side,
            "address": address,
            "max_id": max_id,
            "min_id": min_id,
            "limit": limit,
            "include_financial": include_financial
        }
        return self.request("GET", "/v1/custody/transactions_by_id/", params)

    def get_transactions_by_time(self, coin: str = None, side: str = None, address: str = None,
                                 begin_time: str = None, end_time: str = None, limit: str = None,
                                 include_financial: str = None) -> ApiResponse:
        params = {
            "coin": coin,
            "side": side,
            "address": address,
            "begin_time": begin_time,
            "end_time": end_time,
            "limit": limit,
            "include_financial": include_financial
        }
        return self.request("GET", "/v1/custody/transactions_by_time/", params)

    def get_transactions_by_time_ex(self, coins: str = None, side: int = None, address: str = None,
                                    status: int = None,
                                    begin_time: int = None, end_time: int = None, limit: int = None,
                                    offset: int = None, order_by: str = None, order: str = None) -> ApiResponse:
        params = {
            "coins": coins,
            "side": side,
            "address": address,
            "status": status,
            "begin_time": begin_time,
            "end_time": end_time,
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "order": order,
        }
        return self.request("GET", "/v1/custody/transactions_by_time_ex/", params)

    def get_pending_transactions(self, coin: str = None, side: str = None,
                                 max_id: str = None, min_id: str = None, limit: str = None) -> ApiResponse:
        params = {
            "coin": coin,
            "side": side,
            "max_id": max_id,
            "min_id": min_id,
            "limit": limit
        }
        return self.request("GET", "/v1/custody/pending_transactions/", params)

    def get_pending_transaction(self, id: str) -> ApiResponse:
        return self.request("GET", "/v1/custody/pending_transaction/", {"id": id})

    def get_transactions_by_request_ids(self, request_ids: str) -> ApiResponse:
        return self.request("GET", "/v1/custody/transactions_by_request_ids/", {"request_ids": request_ids})

    def get_transaction_history(self, coin: str = None, side: str = None, address: str = None, max_id: str = None,
                                min_id: str = None, limit: str = None,
                                begin_time: str = None, end_time: str = None,
                                include_financial: str = None) -> ApiResponse:
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

    def withdraw(self, coin: str, address: str, amount: int, request_id: str = None, memo: str = None,
                 force_external: str = None, force_internal: str = None, remark: str = None) -> ApiResponse:
        if not request_id:
            request_id = f"sdk_request_id_{sha256(address.encode()).digest().hex()[:8]}_{str(int(time.time() * 1000))}"

        params = {
            "coin": coin,
            "request_id": request_id,
            "address": address,
            "amount": amount,
            "memo": memo,
            "force_external": force_external,
            "force_internal": force_internal,
            "remark": remark
        }

        return self.request("POST", "/v1/custody/new_withdraw_request/", params)

    def query_withdraw_info(self, request_id: str) -> ApiResponse:
        return self.request("GET", "/v1/custody/withdraw_info_by_request_id/", {"request_id": request_id})

    def get_staking_product_details(self, product_id: str, language: str = "en") -> ApiResponse:
        return self.request("GET", "/v1/custody/staking_product/", {"product_id": product_id, "language": language})

    def get_staking_product_list(self, coin: str = None, language: str = "en") -> ApiResponse:
        return self.request("GET", "/v1/custody/staking_products/", {"coin": coin, "language": language})

    def stake(self, product_id: str, amount: int) -> ApiResponse:
        return self.request("POST", "/v1/custody/staking_stake/", {"product_id": product_id, "amount": amount})

    def unstake(self, product_id: str, amount: int) -> ApiResponse:
        return self.request("POST", "/v1/custody/staking_unstake/", {"product_id": product_id, "amount": amount})

    def get_stakings(self, coin: str = None, language: str = "en") -> ApiResponse:
        return self.request("GET", "/v1/custody/stakings/", {"coin": coin, "language": language})

    def get_unstakings(self, coin: str = None) -> ApiResponse:
        return self.request("GET", "/v1/custody/unstakings/", {"coin": coin})

    def get_staking_history(self) -> ApiResponse:
        return self.request("GET", "/v1/custody/staking_history/", {})
