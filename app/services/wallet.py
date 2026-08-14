from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.wallet import Wallet
from app.models.user import User

from app.schemas.wallet import Currency

DEFAULT_WALLET_CURRENCIES = (
    Currency.USD,
    Currency.EUR,
    Currency.GBP,
)

class WalletNotFoundError(Exception):
    pass

class InsufficientBalanceError(Exception):
    pass


class WalletService:
    def __init__(self, db: Session):
            self.db = db

    def create_wallets(
        self,
        user_id: str,
        currencies: list[Currency] | None = None,
    ) -> list[Wallet]:

        currencies = currencies or list(DEFAULT_WALLET_CURRENCIES)
        wallets = [Wallet(user_id=user_id, currency=c, balance=0) for c in currencies]
        self.db.add_all(wallets)
        self.db.flush()  # Ensure wallets are added

        return wallets

    def get_wallet_by_user_id(
        self,
        user_id: UUID,
        wallet_id: UUID,
    ) -> Wallet:

        wallet = self.db.execute(
            select(Wallet).where(
                Wallet.id == wallet_id,
                Wallet.user_id == user_id,
            )
        ).scalar_one_or_none()

        if wallet is None:
            raise WalletNotFoundError()

        return wallet

    def get_wallet_by_id(
            self,
            wallet_id: UUID,
        ) -> Wallet:
    
            wallet = self.db.execute(
                select(Wallet).where(
                    Wallet.id == wallet_id,
                )
            ).scalar_one_or_none()
    
            if wallet is None:
                raise WalletNotFoundError()
    
            return wallet

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
        # user_id: UUID,
        amount: Decimal,
    ) -> Wallet:

        stmt = (
            update(Wallet)
            .where(
                Wallet.id == wallet_id,
                # Wallet.user_id == user_id,
            )
            .values(balance=Wallet.balance + amount)
            .returning(Wallet)
        )

        wallet = self.db.execute(stmt).scalar_one_or_none()

        if wallet is None:
            raise WalletNotFoundError()

        return wallet

    def decrease_balance(
        self,
        wallet_id: UUID,
        # user_id: UUID,
        amount: Decimal,
    ) -> Wallet:
        
        # wallet_exists = self.db.execute(
        #     select(Wallet).where(
        #         Wallet.id == wallet_id,
        #         # Wallet.user_id == user_id,
        #     )
        # ).scalar_one_or_none()

        # if wallet_exists is None:
        #     raise WalletNotFoundError()
        
        # Wallet.balance >= amount means if the balance is $50, a withdrawal of $100 simply updates zero rows. So the opration is atomic.
        stmt = (
            update(Wallet)
            .where(
                Wallet.id == wallet_id,
                # Wallet.user_id == user_id,
                Wallet.balance >= amount,
            )
            .values(balance=Wallet.balance - amount)
            .returning(Wallet)
        )

        wallet = self.db.execute(stmt).scalar_one_or_none()

        if wallet is None:
            raise InsufficientBalanceError()

        return wallet

    