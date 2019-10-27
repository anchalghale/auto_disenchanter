''' Module for loot related tasks '''
import logging


def catalog(connection, item_type):
    ''' Parses the item catalog for a item type '''
    logging.info("Getting store item catalog for type %s", item_type)
    url = '/lol-store/v1/catalog?inventoryType=["%s"]' % item_type
    res = connection.get(url)
    return res.json()


def buy(connection, name, item_id, val):
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
    logging.info("Buying %s", name)
    res = connection.post('/lol-purchase-widget/v1/purchaseItems', json=data)
    res_json = res.json()
    if res.status_code == 200:
        return "success"
    return res_json["errorDetails"].popitem()[0]


def buy_champ_by_be(connection, blue_essence):
    ''' Buys all the champions of specific blue essence value '''
    logging.info("Getting champions at costs %d BE", blue_essence)
    res_json = catalog(connection, "CHAMPION")
    filtered = list(filter(lambda m: m["prices"][0]["cost"] == blue_essence, res_json))
    for champ in filtered:
        name = champ["localizations"]["en_GB"]["name"]
        result = buy(connection, name, champ["itemId"], champ["prices"][0]["cost"])
        if result == "validation.item.owned":
            logging.info("Champion already owned")
            continue
        if result == "validation.item.not.enough.currency":
            logging.info("Not enough BE to buy champion")
            break
