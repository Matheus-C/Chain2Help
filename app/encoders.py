from datetime import datetime
from json import JSONEncoder

from app.balance import Balance
from app.campaign import Campaign, Donation


class PrivatePropertyEncoder(JSONEncoder):
    def _normalize_keys(self, dict: dict):
        new_dict = {}
        for item in dict.items():
            new_key = item[0][1:]
            new_dict[new_key] = item[1]
        return new_dict


class CampaignEncoder(PrivatePropertyEncoder):
    def default(self, o):
        if isinstance(o, Campaign):
            props = o.__dict__.copy()
            props = self._normalize_keys(props)
            props["founds"] = o.founds
            del props["donations"]
            return props
        elif isinstance(o, Donation):
            return DonationEncoder().default(o)
        elif isinstance(o, datetime):
            return DatetimeEncoder().default(o)

        return JSONEncoder.encode(self, o)


class DonationEncoder(PrivatePropertyEncoder):
    def default(self, o):
        if isinstance(o, Donation):
            props = o.__dict__.copy()
            props = self._normalize_keys(props)
            return props
        elif isinstance(o, datetime):
            return DatetimeEncoder().default(o)

        return JSONEncoder.encode(self, o)


class DatetimeEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.timestamp()

        return JSONEncoder.encode(self, o)


class BalanceEncoder(PrivatePropertyEncoder):
    def default(self, o):
        if isinstance(o, Balance):
            props = o.__dict__.copy()
            props = self._normalize_keys(props)
            del props["account"]
            return props
        elif isinstance(o, set):
            return list(o)

        return JSONEncoder.encode(self, o)
