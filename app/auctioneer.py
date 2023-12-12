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
from operator import attrgetter

import app. wallet as Wallet
from app.log import logger
from app.campaign import Campaign, Donation
from app.outputs import Error, Log, Notice, Output
from app.encoders import CampaignEncoder, DonationEncoder


class Auctioneer():

    def __init__(self, wallet: Wallet):
        self._campaigns: dict[int, Campaign] = {}
        self._wallet = wallet

    def campaign_create(
            self, creator: str, erc20: str,
            title: str, description: str, goal: int,
            start_date: datetime, end_date: datetime, current_date: datetime):

        try:
            if start_date < current_date:
                raise ValueError(f"Start date '{start_date.isoformat()}' "
                                 "must be in the future")

            campaign = Campaign(creator, erc20, title, description, start_date, end_date, goal)
            self._campaigns[campaign._id] = campaign

            campaign_json = json.dumps(campaign, cls=CampaignEncoder)
            notice_payload = f'{{"type": "campaign_create", "content": {campaign_json}}}'
            logger.info(f"Campaign {campaign._id} created")

            return Notice(notice_payload)
        except Exception as error:
            error_msg = f"Failed to create campaign. {error}"
            logger.debug(error_msg, exc_info=True)

            return Error(error_msg)

    def campaign_list(self, **kwargs):
        try:
            campaigns = sorted(self._campaigns.values())
            query = kwargs.get("query")
            if query:
                sort = query.get("sort")
                offset = query.get("offset")
                limit = query.get("limit")
                if sort:
                    sort = sort[0]
                    campaigns = sorted(campaigns, key=attrgetter(sort))

                if offset:
                    offset = int(offset[0])
                    campaigns = campaigns[offset:]

                if limit:
                    limit = int(limit[0])
                    campaigns = campaigns[:limit]

            return Log(json.dumps(campaigns, cls=CampaignEncoder))
        except Exception as error:
            error_msg = f"Failed to list campaigns. {error}"
            logger.debug(error_msg, exc_info=True)

            return Error(error_msg)

    def campaign_detail(self, campaign_id):
        try:
            campaign_json = json.dumps(self._campaigns[campaign_id], cls=CampaignEncoder)
            return Log(campaign_json)
        except Exception:
            return Error(f"Campaign with id {campaign_id} not found")

    def campaign_list_donations(self, campaign_id):
        try:
            return Log(json.dumps(self._campaigns[campaign_id].donations, cls=DonationEncoder))
        except Exception:
            return Error(f"Campaign with id {campaign_id} not found")

    def donate(self, donor, campaign_id, amount, timestamp):
        try:
            campaign = self._campaigns.get(campaign_id)

            if not campaign:
                raise ValueError(f"Campaign with id {campaign_id} not found")

            if donor == campaign.creator:
                raise ValueError(f"Account {donor} cannot donate on its own campaign")

            if timestamp < campaign.start_date:
                raise ValueError(f"Donate arrived before campaign start date: '{campaign.start_date.isoformat()}'")

            if timestamp > campaign.end_date or campaign.state == Campaign.FINISHED:
                campaign.finish()
                raise ValueError("Campaign already finished")

            if not self._has_enough_funds(campaign.erc20, donor, amount):
                raise ValueError(f"Account {donor} doesn't have enough funds")

            new_donation = Donation(campaign_id, donor, amount, timestamp)
            campaign.donate(new_donation)

            logger.info(f"Donation of '{amount} {campaign.erc20}' placed for {campaign_id}")

            donation_json = json.dumps(new_donation, cls=DonationEncoder)
            return Notice(f'{{"type": "donate", "content": {donation_json}}}')
        except Exception as error:
            error_msg = f"Failed to donate. {error}"
            logger.debug(error_msg, exc_info=True)

            return Error(error_msg)

    def _has_enough_funds(self, erc20, donor, amount):
        balance = self._wallet.balance_get(donor)
        erc20_balance = balance.erc20_get(erc20)

        return amount <= erc20_balance
