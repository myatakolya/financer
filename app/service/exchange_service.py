from decimal import Decimal
import aiohttp
import requests

from typing import Dict, Tuple

from app.enum import CurrencyEnum

FALLBACK_RATES: Dict[Tuple[str,str], Decimal] = {
    (CurrencyEnum.USD, CurrencyEnum.RUB): Decimal(str(78.0)),     # USD -> RUB
    (CurrencyEnum.USD, CurrencyEnum.EUR): Decimal(str(0.98)),     # USD -> EUR
    (CurrencyEnum.RUB, CurrencyEnum.USD): Decimal(str(0.0128)),   # RUB -> USD
    (CurrencyEnum.RUB, CurrencyEnum.EUR): Decimal(str(0.0097)),   # RUB -> EUR
    (CurrencyEnum.EUR, CurrencyEnum.RUB): Decimal(str(103.26)),   # EUR -> RUB
    (CurrencyEnum.EUR, CurrencyEnum.USD): Decimal(str(1.087))     # EUR -> USD
}

async def get_exchange_rate(base: CurrencyEnum, target: CurrencyEnum) -> Decimal:
    
    url = f'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base}.json'
    
    timeout = aiohttp.ClientTimeout(total=5.0)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                base_map = data.get(base, {})
                rate = base_map.get(target)
        
        if rate is not None and isinstance(rate, (int, float, Decimal)):
            return Decimal(rate)
        
        raise KeyError('Курс не найден')
        
    except Exception:
       return FALLBACK_RATES.get((base, target), Decimal(1)) 
    
    
    