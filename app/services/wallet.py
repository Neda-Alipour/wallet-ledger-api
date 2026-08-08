#  this is sample that copilot generated
# class wallet:
#     def __init__(self, owner: str, balance: float = 0.0) -> None:
#         self.owner = owner
#         self.balance = float(balance)

#     def deposit(self, amount: float) -> float:
#         if amount <= 0:
#             raise ValueError("Deposit amount must be positive")
#         self.balance += amount
#         return self.balance

#     def withdraw(self, amount: float) -> float:
#         if amount <= 0:
#             raise ValueError("Withdrawal amount must be positive")
#         if amount > self.balance:
#             raise ValueError("Insufficient funds")
#         self.balance -= amount
#         return self.balance

#     def transfer(self, amount: float, recipient: "wallet") -> float:
#         if not isinstance(recipient, wallet):
#             raise TypeError("Recipient must be a wallet instance")
#         self.withdraw(amount)
#         recipient.deposit(amount)
#         return self.balance

#     def get_balance(self) -> float:
#         return self.balance

#     def to_dict(self) -> dict:
#         return {"owner": self.owner, "balance": self.balance}