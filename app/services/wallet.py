from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.wallet import Wallet
from app.models.user import User


class WalletNotFoundError(Exception):
    pass

class WalletService:
    def __init__(self, db: Session):
            self.db = db

    def get_active_wallet(
        self,
        user: User,
        wallet_id: UUID | None = None,
    ) -> Wallet:

        if wallet_id is not None:
            wallet = self.db.execute(
                select(Wallet).where(
                    Wallet.id == wallet_id,
                    Wallet.user_id == user.id,
                )
            ).scalar_one_or_none()

            if wallet is None:
                raise WalletNotFoundError()

            return wallet

        wallet = self.db.execute(
            select(Wallet)
            .where(Wallet.user_id == user.id)
            .order_by(Wallet.created_at.asc())
            .limit(1)
        ).scalar_one_or_none()

        if wallet is None:
            raise WalletNotFoundError()

        return wallet

    def increase_balance(
        self,
        wallet_id: UUID,
        user_id: UUID,
        amount: Decimal,
    ) -> Wallet:

        stmt = (
            update(Wallet)
            .where(
                Wallet.id == wallet_id,
                Wallet.user_id == user_id,
            )
            .values(balance=Wallet.balance + amount)
            .returning(Wallet)
        )

        wallet = self.db.execute(stmt).scalar_one_or_none()

        if wallet is None:
            raise WalletNotFoundError()

        return wallet