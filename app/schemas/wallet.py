from enum import Enum

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class WalletReadItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    currency: str
    balance: Decimal
    created_at: datetime


class WalletsRead(BaseModel):
    wallet: WalletReadItem
    wallets: list[WalletReadItem]