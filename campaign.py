import itertools
from datetime import datetime

class Donation:
    def __init__(self, campaign_id: int, author: str, amount: int, timestamp: datetime):
        if amount <= 0:
            raise ValueError(f"Amount ({amount}) must be greater than zero")

        self._campaign_id = campaign_id
        self._author = author
        self._amount = amount
        self._timestamp = timestamp

    @property
    def campaign_id(self):
        return self.campaign_id

    @property
    def author(self):
        return self._author

    @property
    def amount(self):
        return self._amount

    @property
    def timestamp(self):
        return self._timestamp

    def __eq__(self, other):
        return (self.author == other.author
                and self.campaign_id == other.campaign_id
                and self.amount == other.amount
                and self.timestamp == other.timestamp)

    def __ne__(self, other):
        return not (self == other)

class Campaign:
    CREATED = 0
    STARTED = 1
    FINISHED = 2

    _id = itertools.count()

    def __init__(self, creator: str, erc20: str, title: str, description: str,
                 start_date: datetime, end_date: datetime, goal: int):
        if end_date <= start_date:
            raise ValueError(f"End date ({end_date}) must be after start date ({start_date})")
        if goal <= 0:
            raise ValueError("Goal must be greater than zero")

        self._id = next(self._id)
        self._state = Campaign.CREATED
        self._creator = creator
        self._erc20 = erc20
        self._title = title
        self._description = description
        self._start_date = start_date
        self._end_date = end_date
        self._goal = goal
        self._donations: list[Donation] = []

    @property
    def id(self):
        return self._id

    @property
    def state(self):
        return self._state

    @property
    def creator(self):
        return self._creator

    @property
    def erc20(self):
        return self._erc20

    @property
    def title(self):
        return self._title

    @property
    def description(self):
        return self._description

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    @property
    def goal(self):
        return self._goal

    @property
    def donations(self):
        return self._donations

    def __lt__(self, other):
        return (self.id < other.id)

    def donate(self, donation: Donation):
        if self.state == Campaign.FINISHED:
            raise ValueError("The campaign has already been finished")

        if donation.campaign_id != self.id:
            raise ValueError(f"Campaign id ({donation.campaign_id}) does not match")

        self._donations.append(donation)

        if self.state == Campaign.CREATED:
            self._state = Campaign.STARTED

    def finish(self):
        self._state = Campaign.FINISHED