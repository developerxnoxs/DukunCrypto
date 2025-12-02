# Technical Indicators Guide

This document explains the technical indicators used by the AI Trading Analysis Bots.

## Table of Contents

- [Exponential Moving Average (EMA)](#exponential-moving-average-ema)
- [Bollinger Bands](#bollinger-bands)
- [Relative Strength Index (RSI)](#relative-strength-index-rsi)
- [MACD](#macd)
- [Fibonacci Retracement](#fibonacci-retracement)

---

## Exponential Moving Average (EMA)

### What is EMA?

The Exponential Moving Average gives more weight to recent prices, making it more responsive to new information than a Simple Moving Average (SMA).

### Parameters Used

| EMA | Period | Color | Purpose |
|-----|--------|-------|---------|
| EMA20 | 20 | Blue | Short-term trend |
| EMA50 | 50 | Orange | Medium-term trend |

### How to Interpret

- **Price above both EMAs**: Bullish trend
- **Price below both EMAs**: Bearish trend
- **EMA20 crosses above EMA50**: Golden cross (bullish signal)
- **EMA20 crosses below EMA50**: Death cross (bearish signal)

### Formula

```
EMA = Price(today) × k + EMA(yesterday) × (1 − k)
where k = 2 / (N + 1), N = period
```

---

## Bollinger Bands

### What are Bollinger Bands?

Bollinger Bands are volatility indicators consisting of a middle band (SMA) and two outer bands that are standard deviations away from the middle band.

### Parameters Used

| Band | Calculation | Color |
|------|-------------|-------|
| Upper | SMA20 + (2 × σ) | Purple (dashed) |
| Middle | SMA20 | Purple (dashed) |
| Lower | SMA20 - (2 × σ) | Purple (dashed) |

### How to Interpret

- **Price near upper band**: Potentially overbought
- **Price near lower band**: Potentially oversold
- **Band squeeze**: Low volatility, potential breakout coming
- **Band expansion**: High volatility, strong trend

### Formula

```
Middle Band = SMA(20)
Upper Band = SMA(20) + (2 × Standard Deviation)
Lower Band = SMA(20) - (2 × Standard Deviation)
```

---

## Relative Strength Index (RSI)

### What is RSI?

RSI is a momentum oscillator that measures the speed and magnitude of recent price changes to evaluate overbought or oversold conditions.

### Parameters Used

| Setting | Value |
|---------|-------|
| Period | 14 |
| Overbought Level | 70 |
| Oversold Level | 30 |

### How to Interpret

| RSI Value | Interpretation |
|-----------|----------------|
| > 70 | Overbought - potential sell signal |
| < 30 | Oversold - potential buy signal |
| 50 | Neutral |

### Additional Signals

- **Bullish Divergence**: Price makes lower low, RSI makes higher low
- **Bearish Divergence**: Price makes higher high, RSI makes lower high

### Formula

```
RSI = 100 - (100 / (1 + RS))
RS = Average Gain / Average Loss (over 14 periods)
```

---

## MACD

### What is MACD?

Moving Average Convergence Divergence (MACD) is a trend-following momentum indicator that shows the relationship between two moving averages.

### Parameters Used

| Component | Calculation | Color |
|-----------|-------------|-------|
| MACD Line | EMA12 - EMA26 | Blue |
| Signal Line | EMA9 of MACD | Red |
| Histogram | MACD - Signal | Green/Red |

### How to Interpret

| Signal | Interpretation |
|--------|----------------|
| MACD crosses above Signal | Bullish signal |
| MACD crosses below Signal | Bearish signal |
| Histogram turning positive | Momentum shifting bullish |
| Histogram turning negative | Momentum shifting bearish |

### Divergence

- **Bullish Divergence**: Price makes lower low, MACD makes higher low
- **Bearish Divergence**: Price makes higher high, MACD makes lower high

### Formula

```
MACD Line = EMA(12) - EMA(26)
Signal Line = EMA(9) of MACD Line
Histogram = MACD Line - Signal Line
```

---

## Fibonacci Retracement

### What is Fibonacci Retracement?

Fibonacci retracement levels are horizontal lines that indicate potential support and resistance levels based on the Fibonacci sequence.

### Levels Used

| Level | Percentage | Significance |
|-------|------------|--------------|
| 0% | High | Recent high |
| 23.6% | - | First retracement level |
| 38.2% | - | Shallow retracement |
| 50% | - | Mid-point (not Fibonacci, but commonly used) |
| 61.8% | - | Golden ratio - key level |
| 100% | Low | Recent low |

### How to Interpret

- **In uptrend**: Look for support at Fib levels during pullbacks
- **In downtrend**: Look for resistance at Fib levels during rallies
- **61.8% level**: Often the most significant - deep retracement
- **38.2% level**: Shallow retracement, strong trend continuation

### Calculation

```
Fibonacci Level = High - (High - Low) × Ratio
```

---

## Using Indicators Together

### Confluence

The most reliable signals occur when multiple indicators align:

1. **Strong Buy Signal**:
   - RSI < 30 (oversold)
   - Price at lower Bollinger Band
   - MACD bullish crossover
   - Price near Fibonacci support (38.2% or 61.8%)

2. **Strong Sell Signal**:
   - RSI > 70 (overbought)
   - Price at upper Bollinger Band
   - MACD bearish crossover
   - Price near Fibonacci resistance

### Risk Management

Always use stop losses and proper position sizing. Technical indicators are tools to aid decision-making, not guarantees of market direction.

---

## Disclaimer

Technical analysis is not a guarantee of future performance. Always do your own research and consider your risk tolerance before making trading decisions.
