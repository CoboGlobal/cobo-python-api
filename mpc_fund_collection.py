from cobo_custody.client.mpc_client import MPCClient
from cobo_custody.config import DEVELOP_ENV
from cobo_custody.config import DEVELOP_TEST_DATA

from cobo_custody.signer.local_signer import LocalSigner
import time


class MPCFundCollection:
    mpc_api_secret = ""
    ENV = DEVELOP_ENV
    TEST_DATA = DEVELOP_TEST_DATA

    def __init__(self):
        self.mpc_client = MPCClient(signer=LocalSigner(self.mpc_api_secret),
                                    env=self.ENV,
                                    debug=False)

    def fund_collection(self, coin: str, to_addr: str, to_amount: int, fee_from_addr: str) -> bool:
        if to_amount < 0:
            return False

        resp = self.mpc_client.is_valid_address(coin=coin, address=to_addr)
        if not resp or not resp.success or not resp.result:
            return False

        fee_resp = self.mpc_client.estimate_fee(coin=coin, amount=to_amount, address=to_addr)
        if not resp:
            return False

        page_index = 0
        page_length = 50
        # 获取余额总数
        balance_resp = self.mpc_client.list_balances(coin=coin, page_index=page_index, page_length=page_length)
        if not balance_resp or not balance_resp.success or int(balance_resp.result.get('total')) <= 0:
            return False
        balance_total = int(balance_resp.result.get('total'))
        # 获取所有余额数据
        all_balances = []
        while page_index * page_length < balance_total:
            balance_resp = self.mpc_client.list_balances(coin=coin, page_index=page_index, page_length=page_length)
            all_balances.extend(balance_resp.result.get('coin_data'))
            page_index += page_length

        # 钱包下所有余额总额汇总。若余额地址和toAddr相同，则余额不作为归集金额。
        all_balance_amount = 0
        for balance in all_balances:
            if balance.get('address') == to_addr:
                continue

            all_balance_amount += balance.get('balance')

        if all_balance_amount > to_amount:
            transfer_all_amount = 0
            for balance in all_balances:
                if balance.get('address') == to_addr:
                    continue

                if fee_resp.result.get('fee_coin') == coin:
                    # 归集币种和手续费币种一致
                    transfer_all_amount += self.transfer(coin=coin, from_addr=balance.get('address'), to_addr=to_addr, to_amount=to_amount - transfer_all_amount)
                else:
                    transfer_all_amount += self.token_transfer(coin=coin, from_addr=balance.get('address'), to_addr=to_addr, fee_addr=fee_from_addr, to_amount=to_amount - transfer_all_amount)

                if transfer_all_amount > to_amount:
                    return True

            # 归集币种和手续费币种一致时，若由于交易费用缺少导致总转账金额小于需要转账金额，直接从其他地址提取到toAddr
            return transfer_all_amount > to_amount
        else:
            return False

    """
    代币转账
    具体实现逻辑如下：
    1. 校验fromAddr是否属于apikey对应的custody钱包，是否有余额。如果余额不存在或者余额为0，则直接返回，归集金额为0。
    2. 根据地址余额、待归集金额计算出实际可以归集的余额。
    3. 预估手续费，校验该地址是否有足够的手续费，手续费不够，则需要从feeAddr向fromAddr转账，以保证资金归集时，fromAddr有足够的手续费。
    4. fromAddr向toAddr转账，转账受理成功后，即可认为归集受理成功，最终金额以custody回调为准。
    """
    def token_transfer(self, coin: str, from_addr: str, to_addr: str, fee_addr: str, to_amount: int) -> int:
        mpc_balance = self.mpc_client.get_balance(address=from_addr, coin=coin)
        if not mpc_balance or not mpc_balance.success or not mpc_balance.result.get('coin_data', []):
            return 0

        balance = int(mpc_balance.result.get('coin_data', [])[0].get('balance', 0))
        if balance <= 0:
            return 0

        real_to_amount = to_amount
        if balance < to_amount:
            real_to_amount = balance

        # 预估手续费
        estimate_fee_resp = self.mpc_client.estimate_fee(coin=coin, amount=real_to_amount, from_address=from_addr, address=to_addr)
        if not estimate_fee_resp or not estimate_fee_resp.success or not estimate_fee_resp.result:
            return 0

        gas_limit = estimate_fee_resp.result.get('average', {}).get('gas_limit', 0)
        gas_price = estimate_fee_resp.result.get('average', {}).get('gas_price', 0)
        gas_fee = gas_limit * gas_price
        fee_coin = estimate_fee_resp.result.get('fee_coin')

        # 校验feeAddr有充足的手续费
        fee_addr_balance_resp = self.mpc_client.get_balance(address=fee_addr, coin=fee_coin)
        if not fee_addr_balance_resp or not fee_addr_balance_resp.success or not fee_addr_balance_resp.result.get('coin_data', []):
            return 0
        if fee_addr_balance_resp.result.get('coin_data', [])[0].get('balance') < gas_fee:
            return 0

        # fromAddr 交易手续费用不足时，补充交易手续费
        from_addr_fee_balancer_resp = self.mpc_client.get_balance(address=from_addr, coin=fee_coin)
        if not from_addr_fee_balancer_resp or not from_addr_fee_balancer_resp.success:
            return 0
        from_addr_fee_balance = 0
        if from_addr_fee_balancer_resp.result.get('coin_data', []):
            from_addr_fee_balance = from_addr_fee_balancer_resp.result.get('coin_data', [])[0].get('balance')
        if from_addr_fee_balance < gas_fee:
            request_id = str(int(time.time() * 1000))
            transfer_fee_resp = self.mpc_client.create_transaction(coin=fee_coin, request_id=request_id, from_addr=fee_addr, to_addr=from_addr, amount=gas_fee - from_addr_fee_balance)
            if not transfer_fee_resp or not transfer_fee_resp.success:
                return 0

        # 注意：如果需要补充手续费，需要check手续费到账后，再进行转账操作。
        # fromAddr转账toAddr
        request_id = str(int(time.time() * 1000))
        transfer_resp = self.mpc_client.create_transaction(coin=coin, request_id=request_id, from_addr=from_addr, to_addr=to_addr, amount=real_to_amount)
        if not transfer_resp or not transfer_resp.success:
            return 0
        else:
            return real_to_amount

    """
    主币转账
    具体实现逻辑如下：
    1. 校验fromAddr是否属于apikey对应的custody钱包，是否有余额。如果余额不存在或者余额为0，则直接返回，归集金额为0。
    2. 根据地址余额、待归集金额、交易手续费计算出实际可以归集的余额。
    3. fromAddr向toAddr转账，转账受理成功后，即可认为归集受理成功，最终金额以custody回调为准。
    """
    def transfer(self, coin: str, from_addr: str, to_addr: str, to_amount: int) -> int:
        request_id = str(int(time.time() * 1000))
        mpc_balance = self.mpc_client.get_balance(address=from_addr, coin=coin)
        if not mpc_balance or not mpc_balance.success or not mpc_balance.result.get('coin_data', []):
            return 0

        balance = int(mpc_balance.result.get('coin_data', [])[0].get('balance', 0))
        if balance <= 0:
            return 0

        # 预估手续费
        estimate_fee_resp = self.mpc_client.estimate_fee(coin=coin, from_address=from_addr, address=to_addr)
        if not estimate_fee_resp or not estimate_fee_resp.success or not estimate_fee_resp.result:
            return 0

        gas_limit = estimate_fee_resp.result.get('average', {}).get('gas_limit', 0)
        gas_price = estimate_fee_resp.result.get('average', {}).get('gas_price', 0)
        gas_fee = gas_limit * gas_price
        # 如果余额小于或等于手续费，则不再归集
        if balance < gas_fee:
            return 0

        real_to_amount = to_amount
        if to_amount > balance - gas_fee:
            real_to_amount = balance - gas_fee
        # 可以指定交易费用
        resp = self.mpc_client.create_transaction(coin=coin, request_id=request_id, from_addr=from_addr, to_addr=to_addr, amount=real_to_amount)
        if resp.success:
            return real_to_amount
        else:
            return 0
