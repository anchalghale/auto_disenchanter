''' Macro module for store related macros '''
from client.store import catalog

from gui.logger import Logger


def buy(connection, item_id, val):
    ''' Buys a specific item from the store '''
    data = {
        "items": [
            {
                "itemKey": {
                    "inventoryType": "CHAMPION",
                    "itemId": item_id
                },
                "purchaseCurrencyInfo": {
                    "currencyType": "IP",
                    "price": val,
                    "purchasable": True,
                },
                "quantity": 1
            }
        ]
    }
    res = connection.post('/lol-purchase-widget/v1/purchaseItems', json=data)
    res_json = res.json()
    if res.status_code == 200:
        return "success"
    return res_json["errorDetails"].popitem()[0] if 'errorDetails' in res_json else 'error'


def buy_champ_by_be(logger: Logger, connection, blue_essence):
    ''' Buys all the champions of specific blue essence value '''
    logger.log(f"Getting champions at costs {blue_essence} BE")
    res_json = catalog(connection, "CHAMPION")
    filtered = list(filter(lambda m: m["prices"][0]["cost"] == blue_essence, res_json))
    for champ in filtered:
        name = champ["localizations"]["en_GB"]["name"]
        logger.log(f'Buying {name}...')
        result = buy(connection, champ["itemId"], champ["prices"][0]["cost"])
        if result == "error":
            logger.log("Error buying champion.")
            continue
        if result == "validation.item.owned":
            logger.log("Champion already owned")
            continue
        if result == "validation.item.not.enough.currency":
            logger.log("Not enough BE to buy champion")
            break
