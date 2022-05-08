import requests
import pickle
import signal
import sys

from functools import partial
from typing import List
from time import time
from manifold.markets import Market, BinaryMarket, MultiMarket
from manifold import config


ALL_MARKETS_URL = "https://manifold.markets/api/v0/markets"
SINGLE_MARKET_URL = "https://manifold.markets/api/v0/market/{}"


def get_markets() -> List[Market]:
    json = requests.get(ALL_MARKETS_URL).json()

    # If this fails, the code is out of date.
    all_mechanisms = {x["mechanism"] for x in json}
    assert all_mechanisms == {"cpmm-1", "dpm-2"}

    markets = [BinaryMarket.from_json(x) if 'probability' in x else MultiMarket.from_json(x) for x in json]

    return markets


def get_market(market_id: str) -> Market:
    market = requests.get(SINGLE_MARKET_URL.format(market_id)).json()
    if "probability" in market:
        return BinaryMarket.from_json(market)
    else:
        return MultiMarket.from_json(market)


def get_full_markets() -> List[Market]:
    """Get all markets, including bets and comments.
    Not part of the API, but handy. Takes a while to run.
    """
    markets = get_markets()

    return [get_market(x.id) for x in markets]


def get_full_markets_cached():
    """Get all full markets, and cache the results.
    Cache is not timestamped.
    """
    def cache_objs(full_markets, _signum, _frame):
        pickle.dump(full_markets, config.CACHE_LOC.open('wb'))
        sys.exit(0)

    try:
        full_markets = pickle.load(config.CACHE_LOC.open('rb'))
    except FileNotFoundError:
        full_markets = {}

    # This is unnecessary in hindsight but I'll leave it in unless it gets annoying to support.
    signal.signal(signal.SIGINT, partial(cache_objs, full_markets))

    lite_markets = get_markets()
    print(f"Fetching {len(lite_markets)} markets")
    try:
        for lmarket in lite_markets:
            if lmarket.id in full_markets:
                continue
            else:
                full_market = get_market(lmarket.id)
                full_markets[full_market.id] = {"market": full_market, "cache_time": time()}
    # Happens sometimes, probably a rate limit on their end, just restart the script.
    except ConnectionResetError:
        pass
    pickle.dump(full_markets, config.CACHE_LOC.open('wb'))
    return full_markets