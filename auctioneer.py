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

import wallet as Wallet
from log import logger
from campaign import Campaign, Donation
from outputs import Error, Log, Notice, Output
from encoders import CampaignEncoder, DonationEncoder


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
            campaign_json = json.dumps(
                self._campaigns[campaign_id], cls=CampaignEncoder)
            return Log(campaign_json)
        except Exception:
            return Error(f"Campaign with id {campaign_id} not found")

    def campaign_list_donations(self, campaign_id):
        try:
            campaign = self._campaigns.get(campaign_id)
            if campaign == None:
                raise ValueError(f"Campaign with id {campaign_id} not found")

            return Log(json.dumps(campaign.donations))
        except Exception as error:
            error_msg = f"Failed to list donations for campaign id {campaign_id}. {error}"
            logger.debug(error_msg, exc_info=True)

            return Error(error_msg)

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
                campaign.state = Campaign.FINISHED
                raise ValueError("Campaign already finished")

            if not self._has_enough_funds(campaign.erc20, donor, amount):
                raise ValueError(f"Account {donor} doesn't have enough funds")

            new_donation = Donation(campaign_id, donor, amount, timestamp)
            campaign.donate(new_donation)

            donation_json = json.dumps(new_donation, cls=DonationEncoder)
            logger.info(f"Donation of '{amount} {campaign.erc20}' placed for {campaign_id}")

            return Notice(f'{{"type": "donate", "content": {donation_json}}}')
        except Exception as error:
            error_msg = f"Failed to donate. {error}"
            logger.debug(error_msg, exc_info=True)

            return Error(error_msg)

    # def auction_end(
    #         self, auction_id, rollup_address,
    #         msg_date, msg_sender, withdraw=False):

    #     try:
    #         auction = self._auctions.get(auction_id)

    #         if not auction:
    #             raise ValueError(f"There's no auction with id {auction_id}")
    #         if msg_date < auction.end_date:
    #             raise ValueError(
    #                 f"It can only end after {auction.end_date.isoformat()}")
    #         notice_template = '{{"type": "auction_end", "content": {}}}'
    #         winning_bid = auction.winning_bid
    #         outputs: list[Output] = []

    #         if not winning_bid:
    #             notice_payload = notice_template.format(
    #                 f'{{"auction_id": {auction.id}}}')
    #             notice = Notice(notice_payload)
    #             outputs.append(notice)
    #         else:
    #             output = self._wallet.erc20_transfer(
    #                 account=winning_bid.author,
    #                 to=auction.creator,
    #                 erc20=auction.erc20,
    #                 amount=winning_bid.amount)

    #             if type(output) is Error:
    #                 return output

    #             outputs.append(output)
    #             output = self._wallet.erc721_transfer(
    #                 account=auction.creator,
    #                 to=winning_bid.author,
    #                 erc721=auction.item.erc721,
    #                 token_id=auction.item.token_id)

    #             if type(output) is Error:
    #                 return output

    #             outputs.append(output)
    #             if withdraw and msg_sender == auction.winning_bid.author:
    #                 output = self._wallet.erc721_withdraw(
    #                     rollup_address=rollup_address,
    #                     sender=msg_sender,
    #                     erc721=auction.item.erc721,
    #                     token_id=auction.item.token_id)

    #                 if type(output) is Error:
    #                     return output

    #                 outputs.append(output)

    #             bid_str = json.dumps(winning_bid, cls=BidEncoder)
    #             notice_payload = notice_template.format(bid_str)
    #             notice = Notice(notice_payload)
    #             outputs.append(notice)

    #         auction.finish()
    #         logger.info(f"Auction {auction.id} finished")
    #         return outputs
    #     except Exception as error:
    #         error_msg = f"Failed to end auction. {error}"
    #         logger.debug(error_msg, exc_info=True)
    #         return Error(error_msg)

    # def _seller_owns_item(self, seller, item):
    #     try:
    #         balance = self._wallet.balance_get(seller)
    #         erc721_balance = balance.erc721_get(item.erc721)
    #         if item.token_id in erc721_balance:
    #             return True
    #         return False
    #     except Exception:
    #         return False

    # def _is_item_auctionable(self, item):
    #     for auction in self._auctions.values():
    #         if auction.state != Auction.FINISHED and auction.item == item:
    #             return False
    #     return True

    def _has_enough_funds(self, erc20, donor, amount):
        balance = self._wallet.balance_get(donor)
        erc20_balance = balance.erc20_get(erc20)

        return amount <= erc20_balance
