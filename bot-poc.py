import json
import pprint
from numpy.core.numeric import roll
import websockets
import asyncio
import numpy as np
from collections import deque

uri = 'wss://testnet.binance.vision/ws'

# Store typical price of last n iterations
n = 2
lock_sell = True
rolling_typical_price = deque(maxlen=n)
rolling_sma = deque(maxlen=2)

# Wallet actions

def buy(state, price):
    state['coins'] = state['cash'] / price
    state['cash'] = 0
    state['position'] = 'sell'
    

def sell(state, price):
    state['cash'] = state['coins'] * price
    state['coins'] = 0
    state['position'] = 'buy'

# Wallet Configuration

investment = 100

action = {
    'buy': buy,
    'sell': sell
}

state = {
    'cash': investment,
    'coins': 0,
    'position': 'buy'
}

def calculate_typical_price(h, l, c):
    avg = (h + l + c) / 3
    rolling_typical_price.append(avg)

def simple_moving_average():
    sma = sum(rolling_typical_price) / len(rolling_typical_price)
    rolling_sma.append(sma)

def trend_direction(y1, y2):
    return y2 - y1

def crossover(point_set_1, point_set_2):
    return np.diff(np.sign(point_set_1 - point_set_2))[0]

def handle_kline(kline):
    if kline['x']:
        calculate_typical_price(float(kline['h']), float(kline['l']), float(kline['c']))
        if len(rolling_typical_price) == n:
            simple_moving_average()
            if len(rolling_sma) == 2:
                td = trend_direction(rolling_sma[0], rolling_sma[1])
                lock_sell = td < 0
                point_set_1 = np.array(list(rolling_typical_price)[-2:])
                point_set_2 = np.array(rolling_sma)
                cross = crossover(point_set_1, point_set_2)
                if cross != 0:
                    position = 'buy' if cross > 0 and not lock_sell else 'sell'
                    print(f'Changed position to {position}, lock state {lock_sell}')
                    if state['position'] == position:
                        price = float(kline['c'])
                        take_action = action[state['position']]
                        take_action(state, price)
                        print(  f'Action {position} taken, ' +
                                f'at price {price}, ' +
                                f'fiat state {state["cash"]}, ' +
                                f'coin state {state["coins"]}')
                        pprint.pprint(state)

async def main():
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            'method': 'SUBSCRIBE',
            'params': ['btcusdt@kline_1m'],
            'id': 1
        }))

        print('Pandora\'s Bot running...')
        pprint.pprint(state)

        while True:
            result = json.loads(await websocket.recv())
            if 'result' not in result:
                handle_kline(result['k'])

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())