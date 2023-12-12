from __future__ import annotations

class Balance():
    def __init__(self, account: str, erc20: dict[str: int] = None):
        self._account = account
        self._erc20 = erc20 if erc20 else {}

    def erc20_get(self, erc20: str) -> int:
        return self._erc20.get(erc20, 0)

    def _erc20_increase(self, erc20: str, amount: int):
        if amount < 0:
            raise ValueError(
                f"Failed to increase {erc20} balance for {self._account}. "
                f"{amount} should be a positive number")

        self._erc20[erc20] = self._erc20.get(erc20, 0) + amount

    def _erc20_decrease(self, erc20: str, amount: int):
        if amount < 0:
            raise ValueError(
                f"Failed to decrease {erc20} balance for {self._account}. "
                f"{amount} should be a positive number")

        erc20_balance = self._erc20.get(erc20, 0)
        if erc20_balance < amount:
            raise ValueError(
                f"Failed to decrease {erc20} balance for {self._account}. "
                f"Not enough funds to decrease {amount}")

        self._erc20[erc20] = erc20_balance - amount
