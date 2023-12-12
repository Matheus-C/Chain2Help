from os import environ
import requests
import json
import util
from urllib.parse import urlparse

from eth_abi_ext import decode_packed
from eth_abi.abi import encode

import wallet
from auctioneer import Auctioneer
from encoders import BalanceEncoder
from outputs import Error, Log, Output
from routing import Router
from log import logger

logger.info("Chain2Help started")

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

TRANSFER_FUNCTION_SELECTOR = b'\xa9\x05\x9c\xbb'
ERC20_PORTAL_ADDRESS = "0x9C21AEb2093C32DDbC53eEF24B873BDCd1aDa1DB".lower()

def send_request(output):
    if isinstance(output, Output):
        request_type = type(output).__name__.lower()
        endpoint = request_type
        if isinstance(output, Error):
            endpoint = "report"
            logger.warning(util.hex2str(output.payload))
        elif isinstance(output, Log):
            endpoint = "report"

        logger.debug(f"Sending {request_type}")
        response = requests.post(rollup_server + f"/{endpoint}",
                                 json=output.__dict__)
        logger.debug(f"Received {output.__dict__} status {response.status_code} "
                     f"body {response.content}")
    else:
        for item in output:
            send_request(item)

def post(endpoint, json):
    response = requests.post(f"{rollup_server}/{endpoint}", json=json)
    logger.info(f"Received {endpoint} status {response.status_code} body {response.content}")

def handle_advance(data):
    logger.info(f"Received advance request data {data}")

    try:
        sender = data["metadata"]["msg_sender"].lower()
        payload = data["payload"]

        if sender == ERC20_PORTAL_ADDRESS:
            return router.process("deposit", payload)

        try:
            str_payload = util.hex2str(payload)
            payload = json.loads(str_payload)

            return router.process(payload["method"], data)
        except Exception as error:
            error_msg = f"Failed to process command '{str_payload}'. {error}"
            logger.debug(error_msg, exc_info=True)

            return Error(error_msg)

    except  Exception as e:
        error_msg = f"Failed to process request data '{data}'. {e}"
        return Error(error_msg)


def handle_inspect(data):
    logger.debug(f"Received inspect request data {data}")
    try:
        url = urlparse(util.hex2str(data["payload"]))
        return router.process(url.path, data)
    except Exception as error:
        error_msg = f"Failed to process inspect request. {error}"
        logger.debug(error_msg, exc_info=True)

        return Error(error_msg)


handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}

auctioneer = Auctioneer(wallet)
router = Router(wallet, auctioneer)

while True:
    logger.info("Sending finish")
    response = requests.post(rollup_server + "/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        data = rollup_request["data"]

        handler = handlers[rollup_request["request_type"]]
        output = handler(rollup_request["data"])

        finish["status"] = "accept"
        if isinstance(output, Error):
            finish["status"] = "reject"

        send_request(output)
