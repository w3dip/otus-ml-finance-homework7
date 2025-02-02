import os

from pybit import exceptions
from pybit.unified_trading import HTTP

API_KEY = os.getenv("BB_API_KEY")
SECRET_KEY = os.getenv("BB_SECRET_KEY")

BASE_ASSET = "ETH"
SYMBOL = "ETHUSDT"

cl = HTTP(
        demo=True,
        #testnet=True,
        api_key=API_KEY,
        api_secret=SECRET_KEY,
        recv_window=60000,
    )

import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

def get_assets(cl : HTTP, coin):
    """
    Получаю остатки на аккаунте по конкретной монете
    :param cl:
    :param coin:
    :return:
    """
    r = cl.get_wallet_balance(accountType="UNIFIED")
    print(r)

    assets = {
        asset.get('coin') : float(asset.get('walletBalance', '0.0'))
        for asset in r.get('result', {}).get('list', [])[0].get('coin', [])
    }
    return assets.get(coin, 0.0)

def round_down(value, decimals):
    """
    Ещё один способ отбросить от float лишнее без округлений
    :return:
    """
    factor = 1 / (10 ** decimals)
    return (value // factor) * factor

def buy():
    r = cl.place_order(
        category="spot",
        symbol=SYMBOL,
        side="Buy",
        orderType="Market",
        qty=10,
        marketUnit="quoteCoin",
    )
    print(r)

def sell():
    #r = cl.get_instruments_info(category="spot", symbol=SYMBOL)
    #print(r)

    #min_qty = r.get('result', {}).get('list', [])[0].get('lotSizeFilter', {}).get('minOrderQty', float('0.0'))
    #print('Минимальный размер актива для продажи', min_qty)

    # Не будем продавать все монеты в портфеле, так как на demo аккаунте есть 1 ETH
    # avbl = get_assets(cl, BASE_ASSET)
    # print(avbl, round_down(avbl, 5))

    #Зададим пока ограниченный объем продажи примерно равный 10 USDT
    #qty = min_qty
    qty = 0.00321

    r = cl.place_order(
        category="spot",
        symbol=SYMBOL,
        side="Sell",
        orderType="Market",
        qty=qty,
        #marketUnit="quoteCoin",
    )
    print(r)

def make_order(buy_order = False):
    try:
        if buy_order:
            buy()
        else:
            sell()
    except exceptions.InvalidRequestError as e:
        print("ByBit API Request Error", e.status_code, e.message, sep=" | ")
    except exceptions.FailedRequestError as e:
        print("HTTP Request Failed", e.status_code, e.message, sep=" | ")
    except Exception as e:
        print(e)

# def main():
#     make_order(True)
#
# if __name__ == '__main__':
#     main()