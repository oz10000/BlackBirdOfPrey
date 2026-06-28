# config.py
# ============================================================
# CONFIGURACIÓN OPTIMIZADA PARA WIN RATE ≥90%
# Apalancamiento fijo 7x, parámetros por activo
# ============================================================

# ---- ACTIVOS (universo elegible) ----
SYMBOLS = ['BTC', 'ETH', 'SOL', 'ADA', 'XRP', 'AVAX']

# ---- CAPITAL Y APALANCAMIENTO FIJO ----
TRADE_NOTIONAL = 1000.0
LEVERAGE = 7                     # Fijo (eliminado dinámico)

# ---- PARÁMETROS POR ACTIVO ----
ASSET_PARAMS = {
    'BTC':  {'threshold': 45, 'tp_mult': 1.2, 'trail_dist': 0.6, 'trail_act': 0.6, 'hold': 60},
    'ETH':  {'threshold': 45, 'tp_mult': 1.2, 'trail_dist': 0.6, 'trail_act': 0.6, 'hold': 60},
    'SOL':  {'threshold': 50, 'tp_mult': 1.1, 'trail_dist': 0.7, 'trail_act': 0.7, 'hold': 55},
    'ADA':  {'threshold': 48, 'tp_mult': 1.1, 'trail_dist': 0.7, 'trail_act': 0.7, 'hold': 55},
    'XRP':  {'threshold': 52, 'tp_mult': 1.0, 'trail_dist': 0.8, 'trail_act': 0.8, 'hold': 50},
    'AVAX': {'threshold': 55, 'tp_mult': 1.0, 'trail_dist': 0.8, 'trail_act': 0.8, 'hold': 45},
}

# ---- PARÁMETROS GENERALES (fallback) ----
TP_MULT = 1.2
SL_MULT = 1.5
ATR_PERIOD = 14
BE_GAIN = 0.0005
BE_UMBRAL = 0.25

TRAILING_ENABLED = True
TRAILING_MODE = 'native'
TRAILING_DISTANCE_ATR = 0.6
TRAILING_ACTIVATION_PROFIT = 0.6

# ---- FILTROS (necesario para signals.py, pero no usado en Leviatán) ----
FILTERS = {}  # vacío, porque Leviatán no usa filtros de PiDelta

# ---- NIVELES DE VELOCIDAD (necesario para validación de config) ----
SPEED_LEVELS = [
    {"nivel": 1, "raw_min": 0.45, "roc_min": 0.30},
    {"nivel": 2, "raw_min": 0.40, "roc_min": 0.25},
    {"nivel": 3, "raw_min": 0.35, "roc_min": 0.20},
    {"nivel": 4, "raw_min": 0.30, "roc_min": 0.15},
    {"nivel": 5, "raw_min": 0.25, "roc_min": 0.10},
    {"nivel": 6, "raw_min": 0.20, "roc_min": 0.05},
]
DEFAULT_SPEED_LEVEL = SPEED_LEVELS[2]  # N3

# ---- PARÁMETROS DE INSTRUMENTOS (para cálculo de tamaño) ----
INSTRUMENT_PARAMS = {
    'BTC': {'ctVal': 0.01, 'lotSz': 0.01, 'minSz': 0.01},
    'ETH': {'ctVal': 0.1, 'lotSz': 0.01, 'minSz': 0.01},
    'SOL': {'ctVal': 1.0, 'lotSz': 0.01, 'minSz': 0.01},
    'ADA': {'ctVal': 100.0, 'lotSz': 0.01, 'minSz': 0.01},
    'XRP': {'ctVal': 100.0, 'lotSz': 0.01, 'minSz': 0.01},
    'AVAX': {'ctVal': 1.0, 'lotSz': 0.1, 'minSz': 0.1},
}

# ---- BACKTEST Y TEST (necesario para signals.py) ----
BACKTEST_SLIPPAGE = 0.0002
TEST_MODE = False
TEST_SPEED_LEVEL = {"nivel": 6, "raw_min": 0.05, "roc_min": 0.01}
TEST_IGNORE_FILTERS = True

# ---- ESTRATEGIA ----
ACTIVE_STRATEGY = 'leviathan'
STRATEGY_MODULES = {
    'production': 'strategy_production',
    'leviathan': 'strategy_leviathan',
    'test_fast': 'strategy_test_fast',
    'test_simple': 'strategy_test_simple',
    'experimental': 'strategy_experimental',
}

# ---- RIESGO Y RECUPERACIÓN ----
MAX_OPEN_POSITIONS = 1
MAX_DAILY_LOSS_PERCENT = 2.0
MAX_WEEKLY_LOSS_PERCENT = 4.0
MAX_POSITION_HOLD_MINUTES = 60
CLOSE_IF_STALLED = True
MAX_REPAIR_ATTEMPTS = 3
MAX_RECONNECT_ATTEMPTS = 3
RECONNECT_BACKOFF = 5
BACKOFF_BASE = 5
MAX_RETRIES_PER_ORDER = 3
ORDER_TIMEOUT = 15
MAX_CONSECUTIVE_ERRORS = 5

# ---- ARCHIVOS Y BLOQUEOS ----
LOCK_FILE = '.lock'
LOCK_TIMEOUT = 10
SYNC_TIME_ENABLED = True

# ---- HORARIO ----
TIME_FILTER_ENABLED = False
TIME_FILTER_START = 12
TIME_FILTER_END = 18
TIME_FILTER_WEEKDAYS = [0, 1, 2, 3, 4]

# ---- CICLO ----
CYCLE_INTERVAL = 10
CYCLE_INTERVAL_TEST = 10
MAX_RUNTIME_SECONDS = 14400

# ---- LOGGING ----
LOG_DIR = 'logs'
LOG_LEVEL = 'INFO'
LOG_CONSOLE = True
LOG_FILE = True
LOG_JSON = True
MAX_LOG_SIZE_MB = 10
MAX_LOG_FILES = 5

# ---- OKX ----
OKX_DEMO = True

# ---- OPTIMIZACIONES DINÁMICAS ----
TP_DYNAMIC = True
TRAILING_ADAPTIVE = True
