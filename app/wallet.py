from __future__ import annotations

import json

from app.balance import Balance
from app.log import logger
from app.outputs import Error, Notice, Voucher
from eth_abi import encode
from app.eth_abi_ext import decode_packed

TRANSFER_FUNCTION_SELECTOR = b'\xa9\x05\x9c\xbb'

_accounts = dict[str: Balance]()

def _balance_get(account) -> Balance:
    balance = _accounts.get(account)

    if not balance:
        _accounts[account] = Balance(account)
        balance = _accounts[account]

    return balance


def balance_get(account) -> Balance:
    logger.info(f"Balance for '{account}' retrieved")
    return _balance_get(account)

def erc20_deposit_process(payload:str):
    binary_payload = bytes.fromhex(payload[2:])
    try:
        account, erc20, amount = _erc20_deposit_parse(binary_payload)
        logger.info(f"'{amount} {erc20}' tokens deposited in account '{account}'")
        return _erc20_deposit(account, erc20, amount)
    except ValueError as error:
        error_msg = f"{error}"
        logger.debug(error_msg, exc_info=True)
        return Error(error_msg)


def _erc20_deposit_parse(binary_payload: bytes):
    try:
        input_data = decode_packed(['bool', 'address', 'address', 'uint256'], binary_payload)

        valid = input_data[0]
        if not valid:
            raise ValueError("Invalid deposit with 'False' success flag")

        erc20 = input_data[1]
        account = input_data[2]
        amount = input_data[3]

        return account, erc20, amount
    except Exception as error:
        raise ValueError("Payload does not conform to ERC-20 transfer ABI") from error


def _erc20_deposit(account, erc20, amount):
    balance = _balance_get(account)
    balance._erc20_increase(erc20, amount)

    notice_payload = {
        "type": "erc20deposit",
        "content": {
            "address": account,
            "erc20": erc20,
            "amount": amount
        }
    }
    return Notice(json.dumps(notice_payload))

def erc20_withdraw(account, erc20, amount):
    balance = _balance_get(account)
    balance._erc20_decrease(erc20, amount)

    transfer_payload = TRANSFER_FUNCTION_SELECTOR + \
            encode(['address', 'uint256'], [account, amount])

    logger.info(f"'{amount} {erc20}' tokens withdrawn from '{account}'")
    return Voucher(erc20, transfer_payload)


def erc20_transfer(account, to, erc20, amount):
    try:
        balance = _balance_get(account)
        balance_to = _balance_get(to)

        balance._erc20_decrease(erc20, amount)
        balance_to._erc20_increase(erc20, amount)

        notice_payload = {
            "type": "erc20transfer",
            "content": {
                "from": account,
                "to": to,
                "erc20": erc20,
                "amount": amount
            }
        }
        logger.info(f"'{amount} {erc20}' tokens transferred from '{account}' to '{to}'")
        return Notice(json.dumps(notice_payload))
    except Exception as error:
        error_msg = f"{error}"
        logger.debug(error_msg, exc_info=True)

        return Error(error_msg)
