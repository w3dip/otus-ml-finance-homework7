class COMMON_CONFIG:
    CASH = 1_000_000
    COMMISSION = .002
    SEED = 777
    DATA_PATH = './data/'
    SYMBOL = 'ETH/USDT'
    TIMEFRAME = '1h'
    START_DATE = '2020-01-01T00:00:00Z'
    VAL_DATA_OFFSET = 18,
    TEST_DATA_OFFSET = 12,
    ML_TARGET_NEXT_PERIOD_OFFSET = -1
    TA_MAX_STAT = 'Profit Factor'
    BT_BEST_PARAMS_TA_TEST_DATA_FILE = DATA_PATH + 'bt_best_params_test_data.csv'
    TS_FRESH_MIN_WINDOW_SIZE = 5
    TS_FRESH_MAX_WINDOW_SIZE = 60
