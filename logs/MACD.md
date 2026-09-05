# MACD 特征设计

## 结论

在已有 **DEMA 20 / 60** 特征的前提下，MACD 建议采用 **12 / 26 / 9** 参数组合，而不是改为 20 / 60 / 9。

该组合能够提供相对 DEMA 更短周期的动量信息，减少与 `dema_spread` 的特征冗余。

---

## 指标定义

当前 MACD 的 `diff` 使用快、慢 EMA 的相对差值，形式上接近 PPO（Percentage Price Oscillator）。

$$
diff_t = \frac{EMA_{fast,t} - EMA_{slow,t}}{EMA_{slow,t}}
$$

对于 12 / 26 周期：

$$
PPO_t = \frac{EMA_{12,t} - EMA_{26,t}}{EMA_{26,t}}
$$

信号线 `dea` 为 `diff` 的 9 日 EMA：

$$
dea_t = EMA_9(diff_t)
$$

柱状图 `hist` 表示 `diff` 与信号线的偏离：

$$
hist_t = diff_t - dea_t
$$

各字段的含义如下：

| 特征        | 含义                                     |
| ----------- | ---------------------------------------- |
| `macd_diff` | 中短期趋势或动量强度                     |
| `macd_dea`  | 平滑后的动量趋势                         |
| `macd_hist` | 动量变化强度，可视为趋势变化或加速度信号 |

---

## 参数选择：12 / 26 / 9

### 与 DEMA 20 / 60 的时间尺度互补

建议的指标组合：

```text
DEMA: 20 / 60
MACD: 12 / 26 / 9
```

对应的特征职责：

| 指标             | 时间尺度 | 主要作用                 |
| ---------------- | -------- | ------------------------ |
| DEMA 20 / 60     | 中期     | 描述趋势结构             |
| MACD 12 / 26 / 9 | 中短期   | 描述动量强弱             |
| MACD Histogram   | 短期变化 | 描述动量的变化方向与速度 |

时间窗口存在一定重叠，但 MACD 12 / 26 相比 DEMA 20 / 60 更敏感，能够补充近期 regime 或 momentum change 的信息。

```text
短期                  中期                    长期
 |---------------------|-----------------------|
 MACD 12
      MACD 26
          DEMA 20
                         DEMA 60
```

### 避免与 DEMA 20 / 60 高度重复

如果 MACD 同样使用 20 / 60 / 9：

```text
DEMA: 20 / 60
MACD: 20 / 60 / 9
```

则 `dema_spread` 与 `macd_diff` 都主要描述快均线相对慢均线的位置：

```text
快均线相对于慢均线的偏离程度
```

两者的平滑方式不同：

- `dema_spread` 基于 DEMA；
- `macd_diff` 基于 EMA。

但其底层市场含义高度相似。LightGBM 可以处理相关性较高的特征，但没有必要主动引入明显冗余的输入变量。

---

## 20 / 60 参数的适用场景

MACD 20 / 60 更适合较长预测周期的目标，例如：

```text
未来 10 个交易日收益
未来 20 个交易日收益
```

对于较短的预测 horizon，例如：

```text
未来 1 日收益
未来 3 日收益
未来 5 日收益
```

20 / 60 往往响应偏慢，特别是 EMA60 对近期价格变化的权重较低。

EMA 的平滑系数为：

$$
\alpha = \frac{2}{span+1}
$$

对于 EMA60：

$$
\alpha = \frac{2}{61} \approx 0.0328
$$

即当天新增价格的权重约为 3.3%。

对于 EMA26：

$$
\alpha = \frac{2}{27} \approx 0.074
$$

即当天新增价格的权重约为 7.4%。

因此，12 / 26 组合对近期趋势切换和动量变化更敏感。

---

## 特征筛选建议

### 保留连续特征

对于 LightGBM，连续变量通常比人工离散化的金叉、死叉信号包含更多信息。

建议优先保留：

```text
macd_diff
macd_hist
macd_hist_change_3d
macd_hist_change_5d
```

其中，`macd_hist_change` 可以区分相同柱状图水平下的不同动量状态：

```text
hist = +0.01，快速上升
hist = +0.01，快速下降
hist = +0.01，基本横盘
```

### 不建议优先使用金叉/死叉特征

金叉和死叉通常可由 MACD 柱状图穿越零轴表达：

```python
macd_gold = (
    (macd_hist.shift(1) < 0) &
    (macd_hist > 0)
)
```

其本质是将连续变化：

```text
-0.001 → +0.002
```

离散为：

```text
gold = 1
```

这会丢失交叉前后的幅度、速度和持续性等信息。因此，`macd_gold` 和 `macd_dead` 的优先级低于 `macd_hist` 及其变化率特征。

### `dea` 的冗余性

若模型已包含：

```text
macd_diff
macd_hist
```

则 `dea` 可以由以下关系恢复：

$$
dea = diff - hist
$$

因此，`macd_dea` 不一定需要单独作为模型输入特征。

---

## 推荐实现

```python
ema_fast = close.ewm(span=12, adjust=False).mean()
ema_slow = close.ewm(span=26, adjust=False).mean()

diff = (ema_fast - ema_slow) / ema_slow
dea = diff.ewm(span=9, adjust=False).mean()
hist = diff - dea

result["macd_diff"] = diff
result["macd_hist"] = hist
result["macd_hist_change_3d"] = hist.diff(3)
result["macd_hist_change_5d"] = hist.diff(5)
```

---

## 推荐特征集合

```text
DEMA
- dema_spread_20_60
- dema_spread_change

MACD / PPO
- macd_diff_12_26
- macd_hist_12_26_9
- macd_hist_change_3d
- macd_hist_change_5d
```

该设计以 DEMA 20 / 60 表示中期趋势结构，以 MACD 12 / 26 / 9 补充较短周期的动量及其变化，在特征信息量和特征正交性之间取得较平衡的结果。
