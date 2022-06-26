import requests
import pickle
import sys
from time import time
from types import SimpleNamespace
import json
from manifold import config

ALL_MARKETS_URL = "https://manifold.markets/api/v0/markets"
SINGLE_MARKET_URL = "https://manifold.markets/api/v0/market/{}"
BET_URL = "https://manifold.markets/api/v0/bet"

def get_markets():

    batchSize = 1000
    markets = []
    lastMarketID = ""

    while True:
        url = ALL_MARKETS_URL+f'?limit={batchSize}{"&before="+lastMarketID if lastMarketID else ""}'
        print(url)
        response = requests.get(url, timeout=30)
        newMarkets = json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d))
        markets.extend(newMarkets)
        print('have list of',len(markets))
        lastMarketID = newMarkets[-1].id
        if len(newMarkets) < batchSize:
            break
    return markets

def get_market(market_id: str):
    for attempt in range(10):
        try:
            response = requests.get(SINGLE_MARKET_URL.format(market_id), timeout=20)
            return json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d))
        except ConnectionResetError as e:
            print("ConnectionResetError, retrying")
            print(e)
    else:
        print("Get market failed 10 times!")
        print(market_id)

def get_lite_market(market_id: str):
    url = ALL_MARKETS_URL+f'?limit=1&before={market_id}'
    response = requests.get(url, timeout=20)
    return json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d))[0]

def get_market_cached(market_id: str):
    try:
        full_markets = pickle.load(config.CACHE_LOC.open('rb'))
        if market_id in full_markets:
            return full_markets[market_id]
        else:
            # TODO: Update cache
            return get_market(market_id)
    except FileNotFoundError:
        return get_market(market_id)


def get_full_markets():
    """Get all markets, including bets and comments.
    Not part of the API, but handy. Takes a while to run.
    """
    markets = get_markets()

    return [get_market(x.id) for x in markets]


def get_full_markets_cached(use_cache: bool = True):
    """Get all full markets, and cache the results.
    Cache is not timestamped.
    """
    def cache_objs(full_markets, _signum, _frame):
        pickle.dump(full_markets, config.CACHE_LOC.open('wb'))
        sys.exit(0)

    if use_cache:
        try:
            full_markets = pickle.load(config.CACHE_LOC.open('rb'))
        except (FileNotFoundError, ModuleNotFoundError):
            full_markets = {}
    else:
        full_markets = {}    

    # This is unnecessary in hindsight but I'll leave it in unless it gets annoying to support.
    # signal.signal(signal.SIGINT, partial(cache_objs, full_markets))

    print(f'got {len(full_markets)} cached markets')

    lite_markets = get_markets()
    print(f"Fetching {len(lite_markets)} markets")
    for i, lmarket in enumerate(lite_markets):
        if lmarket.id in full_markets:
            continue
        else:
            full_market = get_market(lmarket.id)
            full_markets[full_market.id] = {"market": full_market, "cache_time": time()}
        if i % 500 == 0:
            print(i)
            pickle.dump(full_markets, config.CACHE_LOC.open('wb'))
    pickle.dump(full_markets, config.CACHE_LOC.open('wb'))
    market_list = [x["market"] for x in full_markets.values()]
    return market_list

def place_bet(market_id: str, outcome: str, amount: int, key: str) -> requests.Response:
    r = requests.post(BET_URL, headers={'Content-Type': 'application/json', 'Authorization': 'Key '+key}, json={'contractId':market_id, 'outcome':outcome, 'amount':amount}, timeout=30)
    return r

def flush_cache(): # incomplete - may corrupt your cache
    full_markets = pickle.load(config.CACHE_LOC.open('rb'))
    print(type(full_markets))
    flushed_markets = {item for item in full_markets.items() if not item[1]['market'].isResolved}
    print(f'flushed {len(full_markets)} down to {len(flushed_markets)}')
    pickle.dump(flushed_markets, config.CACHE_LOC.open('wb'))
