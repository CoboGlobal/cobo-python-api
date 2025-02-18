import json
import time
from typing import Tuple, List
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

    def get_supported_chains(self):
        params = {}
        return self.request("GET", "/v1/custody/mpc/get_supported_chains/", params)

    def get_supported_coins(self, chain_code: str) -> ApiResponse:
        params = {"chain_code": chain_code}
        return self.request("GET", "/v1/custody/mpc/get_supported_coins/", params)

    def get_supported_nft_collections(self, chain_code: str) -> ApiResponse:
        params = {"chain_code": chain_code}
        return self.request("GET", "/v1/custody/mpc/get_supported_nft_collections/", params)

    def get_wallet_supported_coins(self) -> ApiResponse:
        params = {}
        return self.request("GET", "/v1/custody/mpc/get_wallet_supported_coins/", params)

    def get_coin_info(self, coin: str) -> ApiResponse:
        return self.request("GET", "/v1/custody/mpc/coin_info/", {"coin": coin})

    def is_valid_address(self, coin: str, address: str) -> ApiResponse:
        params = {"coin": coin, "address": address}
        return self.request("GET", "/v1/custody/mpc/is_valid_address/", params)

    def get_main_address(self, chain_code: str) -> ApiResponse:
        params = {"chain_code": chain_code}
        return self.request("GET", "/v1/custody/mpc/get_main_address/", params)

    def generate_addresses(self, chain_code: str, count: int, encoding: int = None) -> ApiResponse:
        params = {
            "chain_code": chain_code,
            "count": count,
            "encoding": encoding
        }
        return self.request("POST", "/v1/custody/mpc/generate_addresses/", params)

    def generate_address_memo(self, chain_code: str, address: str, count: int) -> ApiResponse:
        params = {
            "chain_code": chain_code,
            "address": address,
            "count": count,
        }
        return self.request("POST", "/v1/custody/mpc/generate_address_memo/", params)

    def update_address_description(self, coin: str, address: str, description: str) -> ApiResponse:
        params = {
            "coin": coin,
            "address": address,
            "description": description,
        }
        return self.request("POST", "/v1/custody/mpc/update_address_description/", params)

    def list_addresses(self, chain_code: str, start_id: str = None, end_id: str = None, limit: int = None,
                       sort: int = None) -> ApiResponse:
        params = {
            "chain_code": chain_code,
            "start_id": start_id,
            "end_id": end_id,
            "limit": limit,
            "sort": sort
        }
        return self.request("GET", "/v1/custody/mpc/list_addresses/", params)

    def get_balance(self, address: str, chain_code: str = None, coin: str = None) -> ApiResponse:
        params = {
            "address": address,
            "chain_code": chain_code,
            "coin": coin
        }
        return self.request("GET", "/v1/custody/mpc/get_balance/", params)

    def list_balances(self, page_index: int, page_length: int, coin: str = None, chain_code: str = None) -> ApiResponse:
        params = {
            "coin": coin,
            "chain_code": chain_code,
            "page_index": page_index,
            "page_length": page_length
        }
        return self.request("GET", "/v1/custody/mpc/list_balances/", params)

    def list_spendable(self, coin: str, address: str = None) -> ApiResponse:
        params = {
            "address": address,
            "coin": coin,
        }
        return self.request("GET", "/v1/custody/mpc/list_spendable/", params)

    def create_transaction(self, coin: str, request_id: str, amount: str, from_addr: str = None,
                           to_addr: str = None, to_address_details: str = None, fee: float = None,
                           gas_price: int = None, gas_limit: int = None, operation: int = None,
                           extra_parameters: str = None, max_fee: int = None,
                           max_priority_fee: int = None, fee_amount: int = None, remark: str = None,
                           auto_fuel: int = 0, memo: str = "") -> ApiResponse:
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
            "operation": operation,
            "extra_parameters": extra_parameters,
            "max_fee": max_fee,
            "max_priority_fee": max_priority_fee,
            "fee_amount": fee_amount,
            "remark": remark,
            "auto_fuel": auto_fuel,
            "memo": memo,
        }
        return self.request("POST", "/v1/custody/mpc/create_transaction/", params)

    def sign_message(self, chain_code: str, request_id: str, from_addr: str,
                     sign_version: int, extra_parameters: str) -> ApiResponse:
        params = {
            "chain_code": chain_code,
            "request_id": request_id,
            "from_address": from_addr,
            "sign_version": sign_version,
            "extra_parameters": extra_parameters,
        }
        return self.request("POST", "/v1/custody/mpc/sign_message/", params)

    def drop_transaction(self, cobo_id: str, request_id: str, gas_price: int = None, gas_limit: int = None,
                         fee: float = None, fee_amount: int = None, auto_fuel: int = 0, extra_parameters: str = None) -> ApiResponse:
        params = {
            "cobo_id": cobo_id,
            "gas_price": gas_price,
            "gas_limit": gas_limit,
            "request_id": request_id,
            "fee": fee,
            "fee_amount": fee_amount,
            "auto_fuel": auto_fuel,
            "extra_parameters": extra_parameters,
        }
        return self.request("POST", "/v1/custody/mpc/drop_transaction/", params)

    def speedup_transaction(self, cobo_id: str, request_id: str, gas_price: int = None, gas_limit: int = None,
                            fee: float = None, fee_amount: int = None, auto_fuel: int = 0, extra_parameters: str = None) -> ApiResponse:
        params = {
            "cobo_id": cobo_id,
            "gas_price": gas_price,
            "gas_limit": gas_limit,
            "request_id": request_id,
            "fee": fee,
            "fee_amount": fee_amount,
            "auto_fuel": auto_fuel,
            "extra_parameters": extra_parameters,
        }
        return self.request("POST", "/v1/custody/mpc/speedup_transaction/", params)

    def transactions_by_request_ids(self, request_ids: str, status: int = None) -> ApiResponse:
        params = {"request_ids": request_ids, "status": status}
        return self.request("GET", "/v1/custody/mpc/transactions_by_request_ids/", params)

    def transactions_by_cobo_ids(self, cobo_ids: str, status: int = None) -> ApiResponse:
        params = {"cobo_ids": cobo_ids, "status": status}
        return self.request("GET", "/v1/custody/mpc/transactions_by_cobo_ids/", params)

    def transactions_by_tx_hash(self, tx_hash: str, transaction_type: int = None) -> ApiResponse:
        params = {"tx_hash": tx_hash, "transaction_type": transaction_type}
        return self.request("GET", "/v1/custody/mpc/transactions_by_tx_hash/", params)

    def list_transactions(self, start_time: int = None, end_time: int = None, status: int = None,
                          order: str = None, order_by: str = None, transaction_type: int = None,
                          coins: str = None,
                          from_address: str = None, to_address: str = None, limit: int = 50) -> ApiResponse:
        params = {
            "start_time": start_time,
            "end_time": end_time,
            "status": status,
            "order": order,
            "order_by": order_by,
            "transaction_type": transaction_type,
            "coins": coins,
            "from_address": from_address,
            "to_address": to_address,
            "limit": limit
        }
        return self.request("GET", "/v1/custody/mpc/list_transactions/", params)

    def estimate_fee(self, coin: str, amount: int = None, address: str = None, replace_cobo_id: str = None,
                     from_address: str = None,
                     to_address_details: str = None, fee: float = None, gas_price: int = None, gas_limit: int = None,
                     extra_parameters: str = None) -> ApiResponse:
        params = {"coin": coin, "amount": amount, "address": address, "replace_cobo_id": replace_cobo_id,
                  "from_address": from_address, "to_address_details": to_address_details, "fee": fee,
                  "gas_price": gas_price, "gas_limit": gas_limit, "extra_parameters": extra_parameters}
        return self.request("POST", "/v1/custody/mpc/estimate_fee/", params)

    def list_tss_node_requests(self, request_type: int = None, status: int = None) -> ApiResponse:
        params = {"request_type": request_type, "status": status}
        return self.request("GET", "/v1/custody/mpc/list_tss_node_requests/", params)

    def retry_double_check(self, request_id: str) -> ApiResponse:
        params = {"request_id": request_id}
        return self.request("POST", "/v1/custody/mpc/retry_double_check/", params)

    def list_tss_node(self) -> ApiResponse:
        return self.request("GET", "/v1/custody/mpc/list_tss_node/", {})

    def sign_messages_by_request_ids(self, request_ids: str) -> ApiResponse:
        params = {"request_ids": request_ids}
        return self.request("GET", "/v1/custody/mpc/sign_messages_by_request_ids/", params)

    def sign_messages_by_cobo_ids(self, cobo_ids: str) -> ApiResponse:
        params = {"cobo_ids": cobo_ids}
        return self.request("GET", "/v1/custody/mpc/sign_messages_by_cobo_ids/", params)

    def get_max_send_amount(self, coin: str, fee_rate: float, to_address: str, from_address: str = None):
        params = {"coin": coin, "fee_rate": fee_rate, "to_address": to_address}
        if from_address:
            params["from_address"] = from_address
        return self.request("GET", "/v1/custody/mpc/get_max_send_amount/", params)

    def lock_spendable(self, coin: str, tx_hash: str, vout_n: int):
        params = {"coin": coin, "tx_hash": tx_hash, "vout_n": vout_n}
        return self.request("POST", "/v1/custody/mpc/lock_spendable/", params)

    def unlock_spendable(self, coin: str, tx_hash: str, vout_n: int):
        params = {"coin": coin, "tx_hash": tx_hash, "vout_n": vout_n}
        return self.request("POST", "/v1/custody/mpc/unlock_spendable/", params)

    def get_rare_satoshis(self, coin: str, tx_hash: str, vout_n: int):
        params = {"coin": coin, "tx_hash": tx_hash, "vout_n": vout_n}
        return self.request("GET", "/v1/custody/mpc/get_rare_satoshis/", params)

    def get_utxo_assets(self, coin: str, tx_hash: str, vout_n: int):
        params = {"coin": coin, "tx_hash": tx_hash, "vout_n": vout_n}
        return self.request("GET", "/v1/custody/mpc/get_utxo_assets/", params)

    def get_ordinals_inscription(self, inscription_id: str):
        params = {"inscription_id": inscription_id}
        return self.request("GET", "/v1/custody/mpc/get_ordinals_inscription/", params)

    def babylon_prepare_staking(self, request_id: str, stake_info: str, fee_rate: float, max_staking_fee: int = None):
        params = {"request_id": request_id, "stake_info": stake_info, "fee_rate": fee_rate, "max_staking_fee": max_staking_fee}
        return self.request("POST", "/v1/custody/mpc/babylon/prepare_staking/", params)

    def babylon_replace_staking_fee(self, request_id: str, related_request_id: str, fee_rate: float, max_staking_fee: int = None):
        params = {"request_id": request_id, "related_request_id": related_request_id, "fee_rate": fee_rate, "max_staking_fee": max_staking_fee}
        return self.request("POST", "/v1/custody/mpc/babylon/replace_staking_fee/", params)

    def babylon_drop_staking(self, request_id: str, related_request_id: str, fee_rate: float, max_staking_fee: int = None):
        params = {"request_id": request_id, "related_request_id": related_request_id, "fee_rate": fee_rate, "max_staking_fee": max_staking_fee}
        return self.request("POST", "/v1/custody/mpc/babylon/drop_staking/", params)

    def babylon_broadcast_staking_transaction(self, request_id: str):
        params = {"request_id": request_id}
        return self.request("POST", "/v1/custody/mpc/babylon/broadcast_staking_transaction/", params)

    def babylon_batch_broadcast_staking_transaction(self, request_ids: List[str]):
        params = {"request_ids": ','.join(request_ids)}
        return self.request("POST", "/v1/custody/mpc/babylon/batch_broadcast_staking_transaction/", params)

    def babylon_get_staking_info(self, request_id: str):
        params = {"request_id": request_id}
        return self.request("GET", "/v1/custody/mpc/babylon/get_staking_info/", params)

    def babylon_list_waiting_broadcast_transactions(self, asset_coin: str, address: str):
        params = {"asset_coin": asset_coin, "address": address}
        return self.request("GET", "/v1/custody/mpc/babylon/list_waiting_broadcast_transactions/", params)

    def babylon_list_transactions_by_status(self, status: int, address: str = None, min_cobo_id: str = None, limit: int = None):
        params = {"status": status, "address": address, "min_cobo_id": min_cobo_id, "limit": limit}
        return self.request("GET", "/v1/custody/mpc/babylon/list_transactions_by_status/", params)

    def babylon_unbonding(self, request_id: str, staking_request_id: str):
        params = {"request_id": request_id, "staking_request_id": staking_request_id}
        return self.request("POST", "/v1/custody/mpc/babylon/unbonding/", params)

    def babylon_withdraw(self, request_id: str, fee_rate: float, max_fee_amount: int = None, unbonding_request_id: str = None, staking_request_id: str = None):
        params = {"request_id": request_id, "fee_rate": fee_rate, "max_fee_amount": max_fee_amount, "unbonding_request_id": unbonding_request_id, "staking_request_id": staking_request_id}
        return self.request("POST", "/v1/custody/mpc/babylon/withdraw/", params)

    def get_approval_details(self,  request_id: str):
        params = {"request_id": request_id}
        return self.request("GET", "/v1/custody/mpc/get_approval_details/", params)

    def list_eligibles(self, status: str = None, min_id: str = None, limit: int = None) -> ApiResponse:
        params = {
            "status": status,
            "min_id": min_id,
            "limit": limit
        }
        return self.request("GET", "/v1/custody/mpc/babylon/airdrops/list_eligibles/", params)

    def submit_registration(self, btc_address: str, babylon_address: str) -> ApiResponse:
        params = {
            "btc_address": btc_address,
            "babylon_address": babylon_address
        }
        return self.request("POST", "/v1/custody/mpc/babylon/airdrops/submit_registration/", params)

    def list_registrations(self, status: str = None, btc_address: str = None, min_id: str = None, limit: int = None) -> ApiResponse:
        params = {
            "status": status,
            "btc_address": btc_address,
            "min_id": min_id,
            "limit": limit
        }
        return self.request("GET", "/v1/custody/mpc/babylon/airdrops/list_registrations/", params)

    def get_registration(self, registration_id: str) -> ApiResponse:
        params = {
            "registration_id": registration_id
        }
        return self.request("GET", "/v1/custody/mpc/babylon/airdrops/get_registration/", params)
