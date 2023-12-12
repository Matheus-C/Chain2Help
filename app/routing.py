# Copyright 2022 Cartesi Pte. Ltd.
#
# SPDX-License-Identifier: Apache-2.0
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import json
from datetime import datetime
from urllib.parse import parse_qs, urlparse

import app.wallet as Wallet
from app.auctioneer import Auctioneer
from app.encoders import BalanceEncoder
from app.log import logger
from app.outputs import Error, Log
from app.util import hex2str
from routes import Mapper

class DefaultRoute():

    def execute(self, match_result, request=None):
        return Error("Operation not implemented")

class AdvanceRoute(DefaultRoute):

    def _parse_request(self, request):
        self._msg_sender = request["metadata"]["msg_sender"]
        self._msg_timestamp = datetime.fromtimestamp(request["metadata"]["timestamp"])
        request_payload = json.loads(hex2str(request["payload"]))
        self._request_args = request_payload["args"]

    def execute(self, match_result, request=None):
        if request:
            self._parse_request(request)


class WalletRoute(AdvanceRoute):

    def __init__(self, wallet: Wallet):
        self._wallet = wallet


class DepositRoute(WalletRoute):

    def execute(self, match_result, request=None):
        return self._wallet.erc20_deposit_process(request)

class BalanceRoute(WalletRoute):

    def execute(self, match_result, request=None):
        account = match_result["account"]
        balance = self._wallet.balance_get(account)
        return Log(json.dumps(balance, cls=BalanceEncoder))

class AuctioneerRoute(AdvanceRoute):

    def __init__(self, auctioneer):
        self._auctioneer: Auctioneer = auctioneer

class CreateCampaignRoute(AuctioneerRoute):

    def _parse_request(self, request):
        super()._parse_request(request)
        self._request_args["erc20"] = self._request_args["erc20"].lower()
        self._request_args["start_date"] = datetime.fromtimestamp(self._request_args["start_date"])
        self._request_args["end_date"] = datetime.fromtimestamp(self._request_args["end_date"])

    def execute(self, match_result, request=None):
        super().execute(match_result, request)
        return self._auctioneer.campaign_create(self._msg_sender,
                                               self._request_args.get("erc20"),
                                               self._request_args.get("title"),
                                               self._request_args.get("description"),
                                               self._request_args.get("goal"),
                                               self._request_args.get("start_date"),
                                               self._request_args.get("end_date"),
                                               self._msg_timestamp)

class InspectRoute(DefaultRoute):

    def __init__(self, auctioneer):
        self._auctioneer: Auctioneer = auctioneer

class ListCampaignsRoute(InspectRoute):

    def _parse_request(self, request):
        url = urlparse(hex2str(request["payload"]))
        self._query = parse_qs(url.query)

    def execute(self, match_result, request=None):
        self._parse_request(request)
        return self._auctioneer.campaign_list(query=self._query)

class DetailCampaignRoute(InspectRoute):

    def execute(self, match_result, request=None):
        return self._auctioneer.campaign_detail(int(match_result["campaign_id"]))

class ListCampaignDonationsRoute(InspectRoute):

    def execute(self, match_result, request=None):
        return self._auctioneer.campaign_list_donations(int(match_result["campaign_id"]))

class DonateRoute(AuctioneerRoute):

    def execute(self, match_result, request=None):
        super().execute(match_result, request)
        return self._auctioneer.donate(self._msg_sender, self._request_args.get("campaign_id"),
                                        self._request_args.get("amount"), self._msg_timestamp)

class Router():

    def __init__(self, wallet, auctioneer):
        self._controllers = {
            "campaign_create": CreateCampaignRoute(auctioneer),
            "campaign_list": ListCampaignsRoute(auctioneer),
            "campaign_detail": DetailCampaignRoute(auctioneer),
            "campaign_donations": ListCampaignDonationsRoute(auctioneer),
            "donate": DonateRoute(auctioneer),
            "deposit": DepositRoute(wallet),
            "balance": BalanceRoute(wallet),
        }

        self._route_map = Mapper()
        self._route_map.connect(None, "create", controller="campaign_create", action="execute")
        self._route_map.connect(None, "campaign", controller="campaign_list", action="execute")
        self._route_map.connect(None, "campaign/{campaign_id}", controller="campaign_detail", action="execute")
        self._route_map.connect(None, "campaign/{campaign_id}/donations", controller="campaign_donations", action="execute")
        self._route_map.connect(None, "donate", controller="donate", action="execute")
        self._route_map.connect(None, "deposit", controller="deposit", action="execute")
        self._route_map.connect(None, "balance/{account}", controller="balance", action="execute")

    def process(self, route, request=None):
        route = route.lower()
        match_result = self._route_map.match(route)
        if match_result is None:
            return Error(f"Operation '{route}' is not supported")
        else:
            controller = self._controllers.get(match_result["controller"])
            logger.info(f"Executing operation '{route}'")
            return controller.execute(match_result, request)
