import asyncio
import pandas as pd
pd.DataFrame.iteritems = pd.DataFrame.items

from tsfresh import extract_features
from tsfresh.utilities.dataframe_functions import roll_time_series
from tsfresh.utilities.dataframe_functions import impute

import ccxt
import time

from datetime import datetime, timedelta, timezone

from pickle import load

from orders import make_order

class COMMON_CONFIG:
    SYMBOL = 'ETH/USDT'
    TIMEFRAME = '1h'
    TS_FRESH_MIN_WINDOW_SIZE = 5
    TS_FRESH_MAX_WINDOW_SIZE = 60

ticker = COMMON_CONFIG.SYMBOL.replace('/', '')

def get_data_from_api(symbol, timeframe, since):
    exchange = ccxt.binance()
    since = exchange.parse8601(since)
    all_ohlcvs = []

    while True:
        try:
            ohlcvs = exchange.fetch_ohlcv(symbol, timeframe, since)
            all_ohlcvs += ohlcvs
            if len(ohlcvs):
                print('Fetched', len(ohlcvs), symbol, timeframe, 'candles from', exchange.iso8601(ohlcvs[0][0]))
                since = ohlcvs[-1][0] + 1
                sleep_interval = exchange.rateLimit / 1000
                print('Sleep for', sleep_interval)
                time.sleep(sleep_interval)
            else:
                break
        except Exception as e:
            print(type(e).__name__, str(e))
    print('Fetched', len(all_ohlcvs), symbol, timeframe, 'candles in total')
    return pd.DataFrame(all_ohlcvs)

def get_start_date():
    current_time = datetime.now(timezone.utc)
    start_date = (current_time - timedelta(days=7)).isoformat()
    return start_date

def get_data():
    start_date = get_start_date()
    print('Start date', start_date)
    data = get_data_from_api(COMMON_CONFIG.SYMBOL, COMMON_CONFIG.TIMEFRAME, start_date)
    data.columns = ['date','open','high','low','close','volume']
    data = data.sort_values(by='date')
    data = data.drop_duplicates(subset='date').reset_index(drop=True)
    data['date'] = pd.to_datetime(data['date'], unit='ms')
    data.set_index('date', inplace=True)
    # Удалим значения где нет объемов
    data = data.drop(data[data['volume']==0.0].index)
    print(data)
    return data

def prepare_data_for_predict(_df):
    df_melted = pd.DataFrame()
    df_melted["timestamp"] = _df.index
    df_melted["close"] = _df['close'].values
    df_melted['symbol'] = ticker

    df_rolled = roll_time_series(df_melted, column_id="symbol", column_sort="timestamp",
                                 min_timeshift=COMMON_CONFIG.TS_FRESH_MIN_WINDOW_SIZE,
                                 max_timeshift=COMMON_CONFIG.TS_FRESH_MAX_WINDOW_SIZE)
    print('Rolled df successfully')

    X = extract_features(df_rolled.drop("symbol", axis=1),
                         column_id="id", column_sort="timestamp", column_value="close",
                         impute_function=impute, show_warnings=False)
    X = X.set_index(X.index.map(lambda x: x[1]), drop=True)
    X.index.name = "last_timestamp"

    print('Features extracted successfully')

    selected_columns = []
    with open("./selected_columns.pkl", "rb") as f:
        selected_columns = load(f)
        print('Loaded selected columns', selected_columns)

    return X[selected_columns]

def load_model():
    with open("model.pkl", "rb") as f:
        model = load(f)
    return model

def get_predictions(model, data_for_predict):
    predictions_df = pd.DataFrame(model.predict(data_for_predict), index=data_for_predict.index,
                                  columns=['MLPredictions'])
    predictions_df = predictions_df.shift(-1).dropna()
    return predictions_df

def merge_predictions_with_data(data, predictions):
    data = data[data.index.isin(predictions.index)]
    result = pd.concat([data.reset_index(), predictions.reset_index(drop=True)], axis=1)
    result["date"] = pd.to_datetime(result["date"])
    result.set_index('date', inplace=True)
    result = result.dropna()
    return result

def main():
    while True:
        data = get_data()
        data_for_predict = prepare_data_for_predict(data)
        model = load_model()
        predictions_df = get_predictions(model, data_for_predict)
        output = merge_predictions_with_data(data, predictions_df)
        current_row = output.iloc[-1]
        print('Get predicted result')
        print(current_row)

        current_close = current_row['close']
        next_close = current_row['MLPredictions']

        if (next_close > current_close):
            make_order(True)

        if (next_close < current_close):
            make_order(False)

        # ждем следующего часа для того, чтобы загрузить новые данные
        time.sleep(60 * 60)

if __name__ == '__main__':
    main()