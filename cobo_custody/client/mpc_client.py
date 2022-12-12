import json
import time

from urllib.parse import urlencode

import requests

from cobo_custody.client.api_response import ApiResponse
from cobo_custody.config import Env
from cobo_custody.error.api_error import ApiError
from cobo_custody.signer.api_signer import ApiSigner
from cobo_custody.signer.local_signer import verify_ecdsa_signature


class MPCClient(object):
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

    def verify_response(self, response: requests.Response) -> (bool, dict):
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
        nonce = str(int(time.time() * 1000))
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

    def get_mpc_supported_chains(self):
        params = {}
        return self.request("GET", "/v1/custody/mpc/get_supported_chains/", params)

    def get_mpc_supported_coins(self, chain_code: str) -> ApiResponse:
        params = {"chain_code": chain_code}
        return self.request("GET", "/v1/custody/mpc/get_supported_coins/", params)

    def get_mpc_main_address(self, chain_code: str) -> ApiResponse:
        params = {"chain_code": chain_code}
        return self.request("GET", "/v1/custody/mpc/get_main_address/", params)

    def mpc_batch_generate_addresses(self, chain_code: str, count: int) -> ApiResponse:
        params = {
            "chain_code": chain_code,
            "count": count,
        }
        return self.request("POST", "/v1/custody/mpc/generate_addresses/", params)

    def get_mpc_address_list(self, chain_code: str, start_id: str, end_id: str, limit: int = None,
                             sort: int = 0) -> ApiResponse:
        params = {
            "chain_code": chain_code,
            "start_id": start_id,
            "end_id": end_id,
            "limit": limit,
            "sort": sort
        }
        return self.request("GET", "/v1/custody/mpc/list_addresses/", params)

    def get_mpc_balance(self, address: str, chain_code: str = None, coin: str = None) -> ApiResponse:
        params = {
            "address": address,
            "chain_code": chain_code,
            "coin": coin,
        }
        return self.request("GET", "/v1/custody/mpc/get_balance/", params)

    def get_mpc_spendable_list(self, coin: str, address: str = None) -> ApiResponse:
        params = {
            "coin": coin,
            "address": address,
        }
        return self.request("GET", "/v1/custody/mpc/list_spendable/", params)

    def mpc_create_transaction(self, coin: str, request_id: str, amount: int, from_addr: str = None,
                               to_addr: str = None,
                               to_address_details: str = None, fee: int = None, gas_price: int = None,
                               gas_limit: int = None, extra_parameters: str = None) -> ApiResponse:
        params = {
            "coin": coin,
            "request_id": request_id,
            "from_address": from_addr,
            "to_address": to_addr,
            "amount": amount,
            "to_address_details": to_address_details,
            "fee": fee,
            "gas_price": gas_price,
            "gas_limit": gas_limit,
            "extra_parameters": extra_parameters,
        }
        return self.request("POST", "/v1/custody/mpc/create_transaction/", params)

    def mpc_drop_transaction(self, cobo_id: str, fee: int = None, gas_price: int = None,
                             gas_limit: int = None) -> ApiResponse:
        params = {
            "cobo_id": cobo_id,
            "fee": fee,
            "gas_price": gas_price,
            "gas_limit": gas_limit,
        }
        return self.request("POST", "/v1/custody/mpc/drop_transaction/", params)

    def mpc_speedup_transaction(self, cobo_id: str, fee: int = None, gas_price: int = None,
                                gas_limit: int = None) -> ApiResponse:
        params = {
            "cobo_id": cobo_id,
            "fee": fee,
            "gas_price": gas_price,
            "gas_limit": gas_limit,
        }
        return self.request("POST", "/v1/custody/mpc/speedup_transaction/", params)

    def get_mpc_transactions_by_request_ids(self, request_ids: str, status: int = None) -> ApiResponse:
        params = {"request_ids": request_ids, "status": status}
        return self.request("GET", "/v1/custody/mpc/transactions_by_request_ids/", params)

    def get_mpc_transactions_by_cobo_ids(self, cobo_ids: str, status: int = None) -> ApiResponse:
        params = {"cobo_ids": cobo_ids, "status": status}
        return self.request("GET", "/v1/custody/mpc/transactions_by_cobo_ids/", params)

    def get_mpc_transactions_by_tx_hash(self, tx_hash: str, transaction_type: int = None) -> ApiResponse:
        params = {"tx_hash": tx_hash, "transaction_type": transaction_type}
        return self.request("GET", "/v1/custody/mpc/transactions_by_tx_hash/", params)

    def list_mpc_wallet_transactions(self, start_time: int = None, end_time: int = None, status: int = None,
                                     order: str = None, transaction_type: int = None, coins: str = None,
                                     from_address: str = None, to_address: str = None, limit: int = 50) -> ApiResponse:
        params = {
            "start_time": start_time,
            "end_time": end_time,
            "status": status,
            "order": order,
            "transaction_type": transaction_type,
            "coins": coins,
            "from_address": from_address,
            "to_address": to_address,
            "limit": limit
        }
        return self.request("GET", "/v1/custody/mpc/list_transactions/", params)

    def estimate_mpc_fee(self, coin: str, amount: int, address: str) -> ApiResponse:
        params = {"coin": coin, "amount": amount, "address": address}
        return self.request("GET", "/v1/custody/mpc/estimate_fee/", params)

    def list_mpc_tss_node_requests(self, request_type: int = None, status: int = None) -> ApiResponse:
        params = {"request_type": request_type, "status": status}
        return self.request("GET", "/v1/custody/mpc/list_tss_node_requests/", params)
