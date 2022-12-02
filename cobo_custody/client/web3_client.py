import json
import time

from urllib.parse import urlencode

import requests

from cobo_custody.client.api_response import ApiResponse
from cobo_custody.config import Env
from cobo_custody.error.api_error import ApiError
from cobo_custody.signer.api_signer import ApiSigner
from cobo_custody.signer.local_signer import verify_ecdsa_signature


class Web3Client(object):
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

    def batch_web3_new_address(self, chain_code: str, count: int) -> ApiResponse:
        params = {
            "chain_code": chain_code,
            "count": count,
        }
        return self.request("POST", "/v1/custody/web3_add_addresses/", params)

    def get_web3_address_list(self, chain_code: str, page_index: int, page_length: int,
                              sort_flag: int = 0) -> ApiResponse:
        params = {
            "chain_code": chain_code,
            "page_index": page_index,
            "page_length": page_length,
            "sort_flag": sort_flag
        }
        return self.request("GET", "/v1/custody/web3_list_wallet_address/", params)

    def get_web3_wallet_asset_list(self, address: str = None, chain_code: str = None) -> ApiResponse:
        params = {
            "address": address,
            "chain_code": chain_code,
        }
        return self.request("GET", "/v1/custody/web3_list_wallet_assets/", params)

    def get_web3_wallet_nft_list(self, nft_code: str, address: str = None) -> ApiResponse:
        params = {
            "nft_code": nft_code,
            "address": address,
        }
        return self.request("GET", "/v1/custody/web3_list_wallet_nfts/", params)

    def get_web3_wallet_nft_detail(self, nft_code: str, token_id: str) -> ApiResponse:
        params = {
            "nft_code": nft_code,
            "token_id": token_id,
        }
        return self.request("GET", "/v1/custody/web3_wallet_nft_detail/", params)

    def get_web3_supported_chains(self) -> ApiResponse:
        params = {}
        return self.request("GET", "/v1/custody/web3_supported_chains/", params)

    def get_web3_supported_coins(self, chain_code: str) -> ApiResponse:
        params = {"chain_code": chain_code}
        return self.request("GET", "/v1/custody/web3_supported_coins/", params)

    def get_web3_supported_nft_collections(self) -> ApiResponse:
        params = {}
        return self.request("GET", "/v1/custody/web3_supported_nft_collections/", params)

    def get_web3_supported_contracts(self, chain_code: str) -> ApiResponse:
        params = {"chain_code": chain_code}
        return self.request("GET", "/v1/custody/web3_supported_contracts/", params)

    def get_web3_supported_contract_methods(self, chain_code: str, contract_address: str) -> ApiResponse:
        params = {"chain_code": chain_code, "contract_address": contract_address}
        return self.request("GET", "/v1/custody/web3_supported_contract_methods/", params)

    def web3_withdraw(self, coin: str, request_id: str, from_addr: str, to_addr: str, amount: int) -> ApiResponse:
        params = {"coin": coin, "request_id": request_id, "from_addr": from_addr, "to_addr": to_addr, "amount": amount}
        return self.request("POST", "/v1/custody/web3_withdraw/", params)

    def get_web3_withdraw_transaction(self, request_id: str) -> ApiResponse:
        params = {"request_id": request_id}
        return self.request("GET", "/v1/custody/web3_get_withdraw_transaction/", params)

    def web3_contract(self, chain_code: str, request_id: str, wallet_addr: str, contract_addr: str, method_id: str,
                      method_name: str, args: str, amount: int = 0) -> ApiResponse:
        params = {"chain_code": chain_code,
                  "request_id": request_id,
                  "wallet_addr": wallet_addr,
                  "contract_addr": contract_addr,
                  "method_id": method_id,
                  "method_name": method_name,
                  "args": args,
                  "amount": amount, }
        return self.request("POST", "/v1/custody/web3_contract/", params)

    def get_web3_contract_transaction(self, request_id: str) -> ApiResponse:
        params = {"request_id": request_id}
        return self.request("GET", "/v1/custody/web3_get_contract_transaction/", params)

    def list_web3_wallet_transactions(self, address: str, coin: str = None, max_id: str = None, min_id: str = None,
                                      limit: int = 50) -> ApiResponse:
        params = {"address": address, "coin": coin, "max_id": max_id, "min_id": min_id, "limit": limit}
        return self.request("GET", "/v1/custody/web3_list_wallet_transactions/", params)
