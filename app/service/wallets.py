from decimal import Decimal

from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.enum import CurrencyEnum
from app.models import User
from app.repository import wallets as wallets_repository
from app.schemas import CreateWalletRequest, TotalBalance, WalletResponse
from app.service import exchange_service


async def get_total_balance(db: Session, current_user: User) -> TotalBalance:

    wallets = wallets_repository.get_all_wallets(db, current_user.id)
    total_balance = Decimal(0)
    for wallet in wallets:
        if wallet.currency == CurrencyEnum.RUB:
            total_balance += wallet.balance
        else:
            exchange_rate = await exchange_service.get_exchange_rate(wallet.currency, CurrencyEnum.RUB)
            total_balance += wallet.balance * exchange_rate
        
    return TotalBalance(total_balance=total_balance)
        
 
def create_wallet(db: Session, current_user: User, wallet: CreateWalletRequest) -> WalletResponse:

    if wallets_repository.is_wallet_exist(db, current_user.id, wallet.wallet_name):
        raise HTTPException(
            status_code=400,
            detail=f"Кошелек '{wallet.wallet_name}' уже существует"
        )
    
    wallet = wallets_repository.create_wallet(db, current_user.id, wallet.wallet_name, wallet.initial_balance, wallet.currency)
    
    db.commit()
    
    return WalletResponse.model_validate(wallet)

def get_all_wallets(db: Session, current_user: User) -> list[WalletResponse]:

    wallets = wallets_repository.get_all_wallets(db, current_user.id)
    
    res = []
    for wallet in wallets:
        res.append(WalletResponse.model_validate(wallet))
    return res
