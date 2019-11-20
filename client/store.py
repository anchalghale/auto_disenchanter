''' Module for loot related tasks '''
from connection.league import LeagueConnection


def catalog(connection: LeagueConnection, item_type):
    ''' Parses the item catalog for a item type '''
    url = '/lol-store/v1/catalog?inventoryType=["%s"]' % item_type
    res = connection.get(url)
    return res.json()


def buy(connection: LeagueConnection, item_id, val):
    ''' Buys a specific item from the store '''
    data = {
        'items': [
            {
                'itemKey': {
                    'inventoryType': 'CHAMPION',
                    'itemId': item_id
                },
                'purchaseCurrencyInfo': {
                    'currencyType': 'IP',
                    'price': val,
                    'purchasable': True,
                },
                'quantity': 1
            }
        ]
    }
    connection.post('/lol-purchase-widget/v1/purchaseItems', json=data)
