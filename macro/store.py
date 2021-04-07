''' Macro module for store related macros '''
from base.resources import get_json
from client.store import catalog
from logger import Logger


def buy(connection, item_id, price):
    ''' Buys a specific item from the store '''
    data = get_json('buyData')
    data['items'][0]['itemKey']['itemId'] = item_id
    data['items'][0]['purchaseCurrencyInfo']['price'] = price
    response = connection.post('/lol-purchase-widget/v2/purchaseItems', json=data)
    if response.ok:
        return None
    return response.json()


def buy_champ_by_be(logger: Logger, connection, blue_essence):
    ''' Buys all the champions of specific blue essence value '''
    logger.log(f"Getting champions at costs {blue_essence} BE")
    res_json = catalog(connection, "CHAMPION")
    filtered = list(filter(lambda m: m["prices"][0]["cost"] == blue_essence, res_json))
    for champ in filtered:
        if 'en_GB' in champ["localizations"]:
            name = champ["localizations"]["en_GB"]["name"]
        elif 'en_US' in champ["localizations"]:
            name = champ["localizations"]["en_US"]["name"]
        else:
            raise RuntimeError(f'Localizations en_GB or en_US not found. '
                               f'Current values: {list(champ["localizations"].keys())}')
        logger.log(f'Buying {name}...')
        error = buy(connection, champ["itemId"], champ["prices"][0]["cost"])
        if error is not None:
            logger.log(error)
            continue
