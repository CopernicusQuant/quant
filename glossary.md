# Financial Glossary / 财务术语表

## P/E — Price-to-Earnings Ratio / 市盈率

**English:** P/E measures how much investors are willing to pay for each unit of a company's earnings. A higher P/E can imply higher expected growth, but may also indicate a more expensive valuation.

**中文：** 市盈率衡量投资者愿意为公司每一单位盈利支付多少价格。较高的市盈率可能反映较高的增长预期，也可能意味着估值较高。

**Formula / 公式：**

```text
P/E = Share Price / Earnings Per Share (EPS)
市盈率 = 股价 / 每股收益（EPS）
```

> P/E is generally not meaningful when earnings are zero or negative.
>
> 当公司盈利为零或为负时，市盈率通常没有参考意义。

## P/S — Price-to-Sales Ratio / 市销率

**English:** P/S compares a company's market value with its revenue. It shows how much investors pay for each unit of sales and is often useful for companies with low or negative earnings.

**中文：** 市销率比较公司的市场价值与营业收入，表示投资者为每一单位销售收入支付多少价格。它常用于盈利较低或亏损的公司。

**Formula / 公式：**

```text
P/S = Share Price / Sales Per Share
市销率 = 股价 / 每股营业收入
```

## P/B — Price-to-Book Ratio / 市净率

**English:** P/B compares a company's market value with its book value (net assets). It shows how much investors pay for each unit of shareholders' equity.

**中文：** 市净率比较公司的市场价值与账面价值（净资产），表示投资者为每一单位股东权益支付多少价格。

**Formula / 公式：**

```text
P/B = Share Price / Book Value Per Share (BVPS)
市净率 = 股价 / 每股净资产（BVPS）
```

## ROE — Return on Equity / 净资产收益率

**English:** ROE measures how effectively a company generates profit from shareholders' equity. A higher ROE generally indicates more efficient use of shareholders' capital.

**中文：** 净资产收益率衡量公司利用股东权益创造利润的效率。较高的 ROE 通常表示公司对股东资本的使用效率较高。

**Formula / 公式：**

```text
ROE = Net Income / Average Shareholders' Equity
净资产收益率 = 净利润 / 平均股东权益
```

> Average shareholders' equity is commonly calculated as the average of beginning and ending shareholders' equity for the period.
>
> 平均股东权益通常取期间期初与期末股东权益的平均值。

**Relationship with P/B and P/E / 与市净率、市盈率的关系：**

```text
ROE = P/B ÷ P/E
净资产收益率 = 市净率 ÷ 市盈率

P/B = P/E × ROE
市净率 = 市盈率 × 净资产收益率
```

This relationship applies when P/B, P/E, and ROE use consistent accounting periods and definitions. In practice, a small difference can occur because ROE often uses average shareholders' equity, while P/B commonly uses ending book value per share.

该关系适用于市净率、市盈率和净资产收益率采用一致的财务期间及计算口径时。实际数值可能略有差异，因为 ROE 常使用平均股东权益，而 P/B 通常使用期末每股净资产。

## SMA — Simple Moving Average / 简单移动平均线

**English:** SMA is the arithmetic average of prices over a fixed number of periods. Each observation receives equal weight, so it smooths price fluctuations but reacts relatively slowly to new prices.

**中文：** 简单移动平均线是固定周期内价格的算术平均值。每个价格的权重相同，因此能够平滑价格波动，但对最新价格的反应相对较慢。

**Formula / 公式：**

```text
SMA(t, n) = (Pₜ + Pₜ₋₁ + ... + Pₜ₋ₙ₊₁) / n
```

Where `P` is the price and `n` is the lookback period. / 其中 `P` 为价格，`n` 为回看周期。

## WMA — Weighted Moving Average / 加权移动平均线

**English:** WMA assigns greater weight to more recent prices. Compared with SMA, it responds more quickly to recent price changes.

**中文：** 加权移动平均线为近期价格赋予更高权重。与 SMA 相比，它对近期价格变化的反应更快。

**Formula / 公式：**

```text
WMA(t, n) = (n × Pₜ + (n - 1) × Pₜ₋₁ + ... + 1 × Pₜ₋ₙ₊₁) / (1 + 2 + ... + n)
```

## EMA — Exponential Moving Average / 指数移动平均线

**English:** EMA gives exponentially greater weight to recent prices. It is commonly used in technical analysis because it is more responsive than SMA while still smoothing short-term noise.

**中文：** 指数移动平均线以指数方式为近期价格赋予更高权重。它常用于技术分析，因为相较于 SMA，它对价格变化更敏感，同时仍能平滑短期噪声。

**Formula / 公式：**

```text
EMAₜ = α × Pₜ + (1 - α) × EMAₜ₋₁
α = 2 / (n + 1)
```

Where `α` is the smoothing factor and `n` is the selected period. / 其中 `α` 为平滑系数，`n` 为选定周期。

## DEMA — Double Exponential Moving Average / 双重指数移动平均线

**English:** DEMA combines an EMA with an EMA of that EMA to reduce the lag of a standard EMA. Despite its name, it is not simply an EMA calculated over twice as many periods.

**中文：** 双重指数移动平均线结合 EMA 与 EMA 的 EMA，以减少标准 EMA 的滞后性。尽管名称中有“双重”，它并不是将 EMA 的周期简单加倍。

**Formula / 公式：**

```text
DEMA(t, n) = 2 × EMA(P, n) - EMA(EMA(P, n), n)
```

DEMA is generally more responsive than EMA, but may also be more sensitive to short-term price noise. / DEMA 通常比 EMA 反应更快，但也可能对短期价格噪声更敏感。

## KAMA — Kaufman's Adaptive Moving Average / 考夫曼自适应移动平均线

**English:** KAMA adjusts its smoothing rate according to market efficiency. It moves faster in a clear trend and slows down in a noisy or sideways market.

**中文：** 考夫曼自适应移动平均线会根据市场效率调整平滑速度：在趋势明确时反应更快，在震荡或噪声较多时变得更平滑。

**Formula / 公式：**

```text
KAMAₜ = KAMAₜ₋₁ + SCₜ × (Pₜ - KAMAₜ₋₁)

ERₜ = |Pₜ - Pₜ₋ₙ| / Σ|Pᵢ - Pᵢ₋₁|
SCₜ = [ERₜ × (FastSC - SlowSC) + SlowSC]²

FastSC = 2 / (fast period + 1)
SlowSC = 2 / (slow period + 1)
```

`ER` is the efficiency ratio: it is higher when prices move directionally and lower when prices are choppy. Common parameters use an `ER` period of 10, a fast period of 2, and a slow period of 30. / `ER` 为效率比率：价格单向移动时较高，频繁震荡时较低。常见参数为 ER 周期 10、快速周期 2、慢速周期 30。

### Moving Average Types and Crossover Signals / 不同均线与交叉信号

不同均线会产生不同信号：

| 类型 | 特点             | 金叉/死叉出现时间              |
| ---- | ---------------- | ------------------------------ |
| SMA  | 更平滑，但较滞后 | 较晚                           |
| EMA  | 对近期价格更敏感 | 较早，也更容易出现假信号       |
| WMA  | 近期价格权重较高 | 通常介于 SMA 与 EMA 的表现之间 |

通常应让短期和长期均线使用**同一种计算方式**，例如 `SMA(50)` 与 `SMA(200)`，或 `EMA(12)` 与 `EMA(26)`；不建议混用 `SMA(50)` 和 `EMA(200)`，因为它们的权重结构不同，信号不容易解释。

## Golden Cross / 金叉

**English:** A golden cross occurs when a short-term moving average crosses above a long-term moving average. It is commonly interpreted as a potential bullish trend signal.

**中文：** 金叉是指短期移动平均线向上穿越长期移动平均线，通常被视为潜在的看涨趋势信号。

**Condition / 条件：**

```text
Short MAₜ > Long MAₜ
and
Short MAₜ₋₁ ≤ Long MAₜ₋₁
```

For example, a 50-day SMA crossing above a 200-day SMA is often called a golden cross. / 例如，50 日 SMA 上穿 200 日 SMA 常被称为金叉。

## Death Cross / 死叉

**English:** A death cross occurs when a short-term moving average crosses below a long-term moving average. It is commonly interpreted as a potential bearish trend signal.

**中文：** 死叉是指短期移动平均线向下跌破长期移动平均线，通常被视为潜在的看跌趋势信号。

**Condition / 条件：**

```text
Short MAₜ < Long MAₜ
and
Short MAₜ₋₁ ≥ Long MAₜ₋₁
```

For example, a 50-day SMA crossing below a 200-day SMA is often called a death cross. Neither signal guarantees future price direction and both can lag the market. / 例如，50 日 SMA 下穿 200 日 SMA 常被称为死叉。这两类信号均不能保证未来价格方向，并且可能滞后于市场。
