import logging
import json

import requests

logger = logging.getLogger(__name__)


class Coin:
    COIN_MARKET_API = "https://api.coingecko.com/api/v3/"

    def __init__(self, coin_id: str, currency: str='usd'):
        self._coin_id = coin_id
        self._symbol = ''
        self._name = ''
        self._current_usd_price = 0.0
        self._last_usd_price = 0.0
        self._day_change_percent = 0.0
        self._currency = currency
        self.update_coin_info()

    def update_coin_info(self):
        try:
            if not self._coin_id:
                logger.error("No coin id provided")

            response = requests.get(f"{self.COIN_MARKET_API}/coins/{self._coin_id}")

            if response.status_code == 200:
                data = json.loads(response.content)
                market_data = data.get('market_data', {})
                self._symbol = data.get('symbol')
                self._name = data.get('name')
                self._current_usd_price = \
                    float(market_data['current_price'].get(self._currency, 0.0))
                self._day_change_percent = \
                    float(market_data['price_change_percentage_24h_in_currency'].get(self._currency, 0.0))

            elif response.status_code == 404:
                logger.error('Invalid coin id')

        except:
            logger.exception('Cannot retrieve coin data due to an exception')

    @property
    def symbol(self):
        return self._symbol
    
    @property
    def name(self):
        return self._name

    @property
    def current_usd_price(self):
        return self._current_usd_price

    @property
    def day_change_percent(self):
        return self._day_change_percent
