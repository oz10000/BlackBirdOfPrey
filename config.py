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

# ---- ESTRATEGIA ----
ACTIVE_STRATEGY = 'leviathan'
STRATEGY_MODULES = {
    'production': 'strategy_production',
    'leviathan': 'strategy_leviathan',
    'test_fast': 'strategy_test_fast',
    'test_simple': 'strategy_test_simple',
    'experimental': 'strategy_experimental',
}

# ---- RIESGO ----
MAX_OPEN_POSITIONS = 1
MAX_DAILY_LOSS_PERCENT = 2.0
MAX_WEEKLY_LOSS_PERCENT = 4.0
MAX_POSITION_HOLD_MINUTES = 60
CLOSE_IF_STALLED = True

# ---- OKX ----
OKX_DEMO = True

# ---- LOGGING ----
LOG_DIR = 'logs'
LOG_LEVEL = 'INFO'
LOG_CONSOLE = True
LOG_FILE = True
LOG_JSON = True
MAX_LOG_SIZE_MB = 10
MAX_LOG_FILES = 5

# ---- CICLO ----
CYCLE_INTERVAL = 10
MAX_RUNTIME_SECONDS = 14400
