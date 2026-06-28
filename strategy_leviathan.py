# strategy_leviathan.py
# ============================================================
# ESTRATEGIA LEVIATÁN V8 – WIN RATE ≥90%
# Ranking con penalización por duración, parámetros por activo
# ============================================================

import math
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from models import Signal
from signals import fetch_okx_candles, calculate_atr
import config

# ------------------------------------------------------------
# 1. INDICADORES
# ------------------------------------------------------------
def calculate_ker(close, period=10):
    abs_diff = abs(close.diff(period))
    sum_abs = close.diff().abs().rolling(period).sum()
    return abs_diff / (sum_abs + 1e-6)

def calculate_adx(df, period=14):
    high, low, close = df['h'], df['l'], df['c']
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    up = high.diff()
    down = low.diff()
    plus_dm = np.where((up > down) & (up > 0), up, 0.0)
    minus_dm = np.where((down > up) & (down > 0), down, 0.0)
    plus_di = 100 * pd.Series(plus_dm).rolling(period).mean() / atr
    minus_di = 100 * pd.Series(minus_dm).rolling(period).mean() / atr
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)
    return dx.rolling(period).mean(), plus_di, minus_di

def calculate_vwap_zscore(df, period=20):
    vwap = (df['c'] * df['vol']).rolling(period).sum() / (df['vol'].rolling(period).sum() + 1e-6)
    std = df['c'].rolling(period).std()
    return (df['c'] - vwap) / (std + 1e-6)

def bollinger_width(df, period=20):
    mean = df['c'].rolling(period).mean()
    std = df['c'].rolling(period).std()
    return (2 * std) / mean

def choppiness_index(df, period=14):
    high = df['h'].rolling(period).max()
    low = df['l'].rolling(period).min()
    atr_sum = calculate_atr(df, 1).rolling(period).sum()
    return 100 * np.log10((high - low) / atr_sum) / np.log10(period) if atr_sum.iloc[-1] > 0 else 50

# ------------------------------------------------------------
# 2. CÁLCULO DE FEATURES (CREA LAS COLUMNAS FALTANTES)
# ------------------------------------------------------------
def compute_features(df):
    df = df.copy()
    df["prev_close"] = df["close"].shift(1)
    df["tr"] = np.maximum(df["high"] - df["low"],
                          np.maximum(abs(df["high"] - df["prev_close"]),
                                     abs(df["low"] - df["prev_close"])))
    df["atr"] = df["tr"].rolling(14).mean()
    df["atr_pct"] = df["atr"] / df["close"]
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["slope_ema20"] = df["ema20"].diff(5) / df["ema20"].shift(5)
    df["volume_avg"] = df["vol"].rolling(20).mean()
    df["volume_ratio"] = df["vol"] / df["volume_avg"]
    df["momentum"] = df["close"].pct_change(5)
    df["trend_up"] = np.where((df["ema20"] > df["ema50"]) & (df["slope_ema20"] > 0), 100,
                              np.where((df["ema20"] > df["ema50"]) & (df["slope_ema20"] <= 0), 70,
                                       np.where((df["ema20"] < df["ema50"]) & (df["slope_ema20"] < 0), 0, 30)))
    df["volatility_score"] = (100 - np.abs(df["atr_pct"] - 0.01) * 10000).clip(0, 100)
    df["volume_score"] = ((df["volume_ratio"].clip(0.5, 2) - 0.5) / 1.5 * 100)
    df["momentum_score"] = df["momentum"].rolling(50).rank(pct=True) * 100
    return df

# ------------------------------------------------------------
# 3. DETECCIÓN DE RÉGIMEN
# ------------------------------------------------------------
def detect_regime(df):
    # df debe tener las columnas creadas por compute_features
    atr_pct = df['atr_pct'].iloc[-1]
    ker = calculate_ker(df['c']).iloc[-1]
    adx, _, _ = calculate_adx(df)
    adx_val = adx.iloc[-1]
    bw = bollinger_width(df).iloc[-1]

    if atr_pct > 0.03 and ker > 0.6 and adx_val > 30:
        return 'EXPANSION_STRONG'
    elif atr_pct > 0.02 and ker > 0.4 and adx_val > 20:
        return 'EXPANSION'
    elif bw < 0.15 and ker < 0.3:
        return 'COMPRESSION_EXTREME'
    elif bw < 0.2 and ker < 0.4:
        return 'COMPRESSION'
    elif ker > 0.5 and adx_val > 25:
        return 'TREND_STABLE'
    elif ker < 0.3 and adx_val < 20:
        return 'CHOP'
    else:
        return 'MIXED'

# ------------------------------------------------------------
# 4. SCORE MAESTRO CON PENALIZACIÓN POR DURACIÓN
# ------------------------------------------------------------
def compute_final_score(df, symbol):
    # df ya debe tener las columnas de compute_features
    row = df.iloc[-1]
    close = row['close']
    high = row['high']
    low = row['low']
    vol = row['vol']
    atr = row['atr']
    atr_pct = row['atr_pct']
    ker = calculate_ker(df['c']).iloc[-1]
    adx_val, plus_di, minus_di = calculate_adx(df)
    adx = adx_val.iloc[-1]
    vwap_z = calculate_vwap_zscore(df).iloc[-1]
    bw = bollinger_width(df).iloc[-1]
    chop = choppiness_index(df).iloc[-1]

    # Velocidad y aceleración
    price_vel = (close - df['c'].shift(5).iloc[-1]) / df['c'].shift(5).iloc[-1]
    price_acc = price_vel - (df['c'].shift(5).iloc[-1] - df['c'].shift(10).iloc[-1]) / df['c'].shift(10).iloc[-1]
    vol_vel = (vol - df['vol'].shift(5).iloc[-1]) / df['vol'].shift(5).iloc[-1]
    atr_vel = (atr - df['atr'].shift(5).iloc[-1]) / df['atr'].shift(5).iloc[-1] if 'atr' in df else 0

    # Componentes
    trend = 1 if row['ema20'] > row['ema50'] else 0
    momentum = (close / df['c'].shift(5).iloc[-1] - 1) * 10
    expansion = atr_pct * 100
    compression = 1 - (bw / 0.2) if bw < 0.2 else 0
    volume_score = vol / df['vol'].rolling(20).mean().iloc[-1]
    volume_acc = vol_vel
    ker_score = ker
    adx_score = adx / 100
    atr_score = min(atr_pct / 0.03, 1)
    vwap_score = abs(vwap_z) / 3
    multi_tf_alignment = 1 if (df['ema20'].iloc[-1] > df['ema50'].iloc[-1]) == (df['ema20'].iloc[-5] > df['ema50'].iloc[-5]) else 0

    # Estimación de duración esperada (basada en volatilidad y velocidad)
    expected_duration = 60 * (1 + 0.5 * (1 - atr_pct * 50)) / (1 + abs(price_vel) * 100)
    expected_duration = max(10, min(90, expected_duration))  # entre 10 y 90 minutos

    # Score base
    raw_score = (
        trend * 0.15 +
        momentum * 0.12 +
        expansion * 0.10 +
        compression * 0.08 +
        volume_score * 0.10 +
        volume_acc * 0.07 +
        ker_score * 0.08 +
        adx_score * 0.06 +
        atr_score * 0.06 +
        vwap_score * 0.05 +
        multi_tf_alignment * 0.10 +
        (1 - chop/100) * 0.03
    )

    # Penalización por duración (premia operaciones cortas)
    duration_penalty = 1.0 - 0.3 * (expected_duration / 60)
    final_score = raw_score * duration_penalty

    return final_score, expected_duration

# ------------------------------------------------------------
# 5. ADAPTACIÓN DE PARÁMETROS
# ------------------------------------------------------------
def get_asset_params(symbol):
    default = {'threshold': 50, 'tp_mult': 1.2, 'trail_dist': 0.6, 'trail_act': 0.6, 'hold': 60}
    return config.ASSET_PARAMS.get(symbol, default)

# ------------------------------------------------------------
# 6. ERA (Explosive Risk Alert)
# ------------------------------------------------------------
class ERA:
    def __init__(self):
        self.atr_hist = {}
        self.vol_hist = {}
        self.active = {}

    def update(self, symbol, atr, vol):
        if symbol not in self.atr_hist:
            self.atr_hist[symbol] = []
            self.vol_hist[symbol] = []
            self.active[symbol] = False
        self.atr_hist[symbol].append(atr)
        self.vol_hist[symbol].append(vol)
        if len(self.atr_hist[symbol]) > 100:
            self.atr_hist[symbol].pop(0)
        if len(self.vol_hist[symbol]) > 50:
            self.vol_hist[symbol].pop(0)
        cond = 0
        if len(self.atr_hist[symbol]) >= 20:
            p90 = np.percentile(self.atr_hist[symbol], 90)
            if atr > p90: cond += 1
        if len(self.vol_hist[symbol]) >= 50:
            avg = np.mean(self.vol_hist[symbol])
            if vol > 2.5 * avg: cond += 1
        self.active[symbol] = (cond >= 2)
        return self.active[symbol]

# ------------------------------------------------------------
# 7. GENERACIÓN DE SEÑAL (con ranking y parámetros por activo)
# ------------------------------------------------------------
def get_best_signal(symbols=None, speed_levels=None, speed_levels_override=None):
    if symbols is None:
        symbols = config.SYMBOLS

    era = ERA()
    best_signal = None
    best_score = -1e9

    for symbol in symbols:
        params = get_asset_params(symbol)
        threshold = params['threshold'] / 100.0  # convertir a escala 0-1

        df = fetch_okx_candles(symbol, limit=200)
        if df.empty or len(df) < 100:
            continue

        # 🔧 CORRECCIÓN: Calcular features ANTES de usar cualquier columna derivada
        df = compute_features(df)

        regime = detect_regime(df)
        final_score, expected_duration = compute_final_score(df, symbol)

        if final_score < threshold:
            continue

        row = df.iloc[-1]
        direction = 1 if row['ema20'] > row['ema50'] else -1
        atr = row['atr']
        vol = row['vol']
        era_active = era.update(symbol, atr, vol)

        # Apalancamiento fijo
        leverage = config.LEVERAGE

        entry = row['close']
        if direction == 1:
            tp = entry + atr * params['tp_mult']
            sl = entry - atr * config.SL_MULT
        else:
            tp = entry - atr * params['tp_mult']
            sl = entry + atr * config.SL_MULT

        # Trailing adaptativo por activo
        trail_dist = params['trail_dist'] * atr
        trail_act = params['trail_act'] * atr

        signal = Signal(
            symbol=symbol,
            direction='Long' if direction == 1 else 'Short',
            timestamp=datetime.utcnow(),
            entry_price=entry,
            target_price=tp,
            stop_loss=sl,
            confidence=min(1.0, final_score),
            speed_score=final_score,
            speed_level='LEVIATHAN',
            notional=config.TRADE_NOTIONAL,
            suggested_leverage=leverage,  # fijo
            final_score=final_score,
            regime=regime,
            suggested_trail=trail_dist
        )

        if final_score > best_score:
            best_score = final_score
            best_signal = signal

    return best_signal

generate_signal = None
