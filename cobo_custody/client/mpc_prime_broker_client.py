import json
import time
from typing import Tuple
from urllib.parse import urlencode

import requests

from cobo_custody.client.api_response import ApiResponse
from cobo_custody.config import Env
from cobo_custody.error.api_error import ApiError
from cobo_custody.signer.api_signer import ApiSigner
from cobo_custody.signer.local_signer import verify_ecdsa_signature


class MPCPrimeBrokerClient(object):
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

    def create_binding(self, user_id: str):
        params = {
            "user_id": user_id,
        }
        return self.request("POST", "/v1/custody/guard/create_binding/", params)

    def query_binding(self, binder_id: str):
        params = {
            "binder_id": binder_id,
        }
        return self.request("GET", "/v1/custody/guard/query_binding/", params)

    def query_user_auth(self, user_id: str):
        params = {
            "user_id": user_id,
        }
        return self.request("GET", "/v1/custody/guard/query_user_auth/", params)

    def bind_addresses(self, user_id: str, addresses: str):
        params = {
            "user_id": user_id,
            "addresses": addresses,
        }
        return self.request("POST", "/v1/custody/guard/bind_addresses/", params)

    def change_binding(self, user_id: str):
        params = {
            "user_id": user_id,
        }
        return self.request("POST", "/v1/custody/guard/change_binding/", params)

    def unbind_binding(self, user_id: str):
        params = {
            "user_id": user_id,
        }
        return self.request("POST", "/v1/custody/guard/unbind_binding/", params)

    def query_statement(self, statement_id: str):
        params = {
            "statement_id": statement_id,
        }
        return self.request("GET", "/v1/custody/guard/query_statement/", params)
